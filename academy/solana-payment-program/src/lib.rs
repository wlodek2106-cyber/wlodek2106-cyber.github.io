//! Experimental, not deployed. Do not use with real funds.
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint::ProgramResult, program::{invoke, invoke_signed},
    program_error::ProgramError, program_pack::Pack,
    pubkey::Pubkey, rent::Rent, system_instruction, system_program, sysvar::Sysvar,
};
use spl_token::state::{Account as TokenAccount, AccountState, Mint};
use std::str::FromStr;

#[cfg(not(feature = "no-entrypoint"))]
solana_program::entrypoint!(process_instruction);

const TREASURY: &str = "57S7TryAMhxRq5sMSyZxTkyCmzT8tPFKfXjzZwvmv5db";
const USDC: &str = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";
const SEED: &[u8] = b"zrl-paid-v1";
const RECEIPT_LEN: usize = 105;
const DUPLICATE: ProgramError = ProgramError::Custom(1);

#[derive(Debug, PartialEq)]
struct Payment { reference: Pubkey, recipient: Pubkey, cents: u64 }

fn parse(data: &[u8]) -> Result<Payment, ProgramError> {
    if data.len()!=73 || data[0]!=1 { return Err(ProgramError::InvalidInstructionData); }
    let reference=Pubkey::new_from_array(data[1..33].try_into().unwrap());
    let recipient=Pubkey::new_from_array(data[33..65].try_into().unwrap());
    let cents=u64::from_le_bytes(data[65..73].try_into().unwrap());
    if reference==Pubkey::default() || recipient==Pubkey::default() { return Err(ProgramError::InvalidInstructionData); }
    split(cents)?;
    Ok(Payment { reference, recipient, cents })
}

fn split(cents: u64) -> Result<(u64,u64), ProgramError> {
    if !(1..=100_000_000).contains(&cents) { return Err(ProgramError::InvalidInstructionData); }
    let gross=cents.checked_mul(10_000).ok_or(ProgramError::ArithmeticOverflow)?;
    let fee=gross/20;
    Ok((gross-fee,fee))
}

pub fn receipt_address(program: &Pubkey,payer: &Pubkey,reference: &Pubkey) -> (Pubkey,u8) {
    Pubkey::find_program_address(&[SEED,payer.as_ref(),reference.as_ref()],program)
}

fn token(account: &AccountInfo, mint: &Pubkey, owner: &Pubkey) -> Result<TokenAccount,ProgramError> {
    if account.owner!=&spl_token::id() { return Err(ProgramError::IllegalOwner); }
    let t=TokenAccount::unpack(&account.try_borrow_data()?)?;
    if t.mint!=*mint || t.owner!=*owner || t.state!=AccountState::Initialized {
        return Err(ProgramError::InvalidAccountData);
    }
    Ok(t)
}

pub fn process_instruction(program_id: &Pubkey, accounts: &[AccountInfo], data: &[u8]) -> ProgramResult {
    let p=parse(data)?;
    let (net,fee)=split(p.cents)?;
    // payer, receipt PDA, source, worker, treasury, mint, token, system.
    if accounts.len()!=8 { return Err(ProgramError::InvalidArgument); }
    let mut a=accounts.iter();
    let payer=next_account_info(&mut a)?;
    let receipt=next_account_info(&mut a)?;
    let source=next_account_info(&mut a)?;
    let freelancer=next_account_info(&mut a)?;
    let treasury=next_account_info(&mut a)?;
    let mint=next_account_info(&mut a)?;
    let token_program=next_account_info(&mut a)?;
    let system=next_account_info(&mut a)?;
    let treasury_owner=Pubkey::from_str(TREASURY).map_err(|_|ProgramError::InvalidArgument)?;
    let usdc=Pubkey::from_str(USDC).map_err(|_|ProgramError::InvalidArgument)?;
    if !payer.is_signer { return Err(ProgramError::MissingRequiredSignature); }
    if ![payer,receipt,source,freelancer,treasury].iter().all(|x|x.is_writable) ||
       token_program.key!=&spl_token::id() || !token_program.executable ||
       system.key!=&system_program::id() || !system.executable ||
       mint.key!=&usdc || mint.owner!=&spl_token::id() ||
       payer.key==&p.recipient || payer.key==&treasury_owner || p.recipient==treasury_owner {
        return Err(ProgramError::InvalidArgument);
    }
    for i in 0..accounts.len() {
        for j in i+1..accounts.len() {
            if accounts[i].key==accounts[j].key { return Err(ProgramError::InvalidArgument); }
        }
    }
    let (expected,bump)=receipt_address(program_id,payer.key,&p.reference);
    if receipt.key!=&expected { return Err(ProgramError::InvalidSeeds); }
    // Permanent receipt. No close/reset instruction exists.
    if receipt.owner==program_id { return Err(DUPLICATE); }
    if receipt.owner!=&system_program::id() || !receipt.data_is_empty() {
        return Err(ProgramError::InvalidAccountData);
    }
    let m=Mint::unpack(&mint.try_borrow_data()?)?;
    if !m.is_initialized || m.decimals!=6 { return Err(ProgramError::InvalidAccountData); }
    let src=token(source,&usdc,payer.key)?;
    token(freelancer,&usdc,&p.recipient)?;
    token(treasury,&usdc,&treasury_owner)?;
    if src.amount<net+fee { return Err(ProgramError::InsufficientFunds); }
    // Handle a pre-funded empty system-owned PDA without allowing rent dust
    // to prevent payment. Allocate and assign only with canonical PDA seeds.
    let bump_seed=[bump];
    let seeds: &[&[u8]]=&[SEED,payer.key.as_ref(),p.reference.as_ref(),&bump_seed];
    let minimum=Rent::get()?.minimum_balance(RECEIPT_LEN);
    let top_up=minimum.saturating_sub(receipt.lamports());
    if top_up>0 {
        invoke(&system_instruction::transfer(payer.key,receipt.key,top_up),
            &[payer.clone(),receipt.clone(),system.clone()])?;
    }
    invoke_signed(&system_instruction::allocate(receipt.key,RECEIPT_LEN as u64),
        &[receipt.clone(),system.clone()],&[seeds])?;
    invoke_signed(&system_instruction::assign(receipt.key,program_id),
        &[receipt.clone(),system.clone()],&[seeds])?;
    for (dst,amount) in [(freelancer,net),(treasury,fee)] {
        let ix=spl_token::instruction::transfer_checked(
            token_program.key,source.key,mint.key,dst.key,payer.key,&[],amount,6)?;
        invoke(&ix,&[source.clone(),mint.clone(),dst.clone(),payer.clone(),token_program.clone()])?;
    }
    // Both transfers and the receipt commit atomically or all roll back.
    let mut out=receipt.try_borrow_mut_data()?;
    if out.len()!=RECEIPT_LEN { return Err(ProgramError::InvalidAccountData); }
    out[0]=1;
    out[1..33].copy_from_slice(payer.key.as_ref());
    out[33..65].copy_from_slice(p.reference.as_ref());
    out[65..97].copy_from_slice(p.recipient.as_ref());
    out[97..105].copy_from_slice(&p.cents.to_le_bytes());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn exact_fee_and_bounds() {
        assert_eq!(split(100_000).unwrap(),(950_000_000,50_000_000));
        assert_eq!(split(1).unwrap(),(9500,500));
        assert_eq!(split(100_000_000).unwrap(),(950_000_000_000,50_000_000_000));
        assert!(split(0).is_err());
        assert!(split(100_000_001).is_err());
        assert!(split(u64::MAX).is_err());
    }
    #[test]
    fn receipt_is_bound_to_program_payer_reference() {
        let program=Pubkey::new_unique();
        let payer=Pubkey::new_unique();
        let reference=Pubkey::new_unique();
        let (address,bump)=receipt_address(&program,&payer,&reference);
        assert_eq!(address,Pubkey::create_program_address(&[SEED,payer.as_ref(),reference.as_ref(),&[bump]],&program).unwrap());
        assert_ne!(address,receipt_address(&program,&Pubkey::new_unique(),&reference).0);
        assert_ne!(address,receipt_address(&program,&payer,&Pubkey::new_unique()).0);
        assert_ne!(address,receipt_address(&Pubkey::new_unique(),&payer,&reference).0);
    }
    #[test]
    fn instruction_data_is_exact() {
        let r=Pubkey::new_unique();let w=Pubkey::new_unique();
        let mut data=vec![1];data.extend(r.to_bytes());data.extend(w.to_bytes());data.extend(100_000u64.to_le_bytes());
        assert_eq!(parse(&data).unwrap(),Payment{reference:r,recipient:w,cents:100_000});
        assert!(parse(&data[..72]).is_err());
        data.push(0);assert!(parse(&data).is_err());
    }
    #[test]
    fn configured_addresses_parse() {
        assert_ne!(Pubkey::from_str(TREASURY).unwrap(),Pubkey::from_str(USDC).unwrap());
    }
}

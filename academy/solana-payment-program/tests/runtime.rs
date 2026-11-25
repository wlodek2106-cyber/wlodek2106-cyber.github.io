//! Synthetic bank runtime only. No RPC, key persistence, real USDC or deployment.
use solana_program::{program_option::COption,program_pack::Pack,pubkey::Pubkey,system_program};
use solana_program_test::{processor,ProgramTest,ProgramTestContext};
use solana_sdk::{
    account::Account, compute_budget::ComputeBudgetInstruction,
    instruction::{AccountMeta,Instruction,InstructionError},
    signature::{Keypair,Signer}, transaction::{Transaction,TransactionError},
};
use spl_token::state::{Account as TokenAccount,AccountState,Mint};
use std::str::FromStr;
use zer0life_payment_prototype::{process_instruction,receipt_address};

const GROSS:u64=1_000_000_000;
const NET:u64=950_000_000;
const FEE:u64=50_000_000;
const CENTS:u64=100_000;

fn mint_key()->Pubkey { Pubkey::from_str("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v").unwrap() }
fn treasury_owner()->Pubkey { Pubkey::from_str("57S7TryAMhxRq5sMSyZxTkyCmzT8tPFKfXjzZwvmv5db").unwrap() }
fn system_account(lamports:u64)->Account {
    Account{lamports,data:vec![],owner:system_program::id(),executable:false,rent_epoch:0}
}
fn mint_account()->Account {
    let mut data=vec![0;Mint::LEN];
    Mint::pack(Mint{mint_authority:COption::None,supply:u64::MAX,decimals:6,is_initialized:true,freeze_authority:COption::None},&mut data).unwrap();
    Account{lamports:10_000_000,data,owner:spl_token::id(),executable:false,rent_epoch:0}
}
fn token_account(mint:Pubkey,owner:Pubkey,amount:u64)->Account {
    let mut data=vec![0;TokenAccount::LEN];
    TokenAccount::pack(TokenAccount{mint,owner,amount,delegate:COption::None,state:AccountState::Initialized,is_native:COption::None,delegated_amount:0,close_authority:COption::None},&mut data).unwrap();
    Account{lamports:10_000_000,data,owner:spl_token::id(),executable:false,rent_epoch:0}
}
struct Fixture {
    ctx:ProgramTestContext, program:Pubkey,payer:Keypair,worker:Pubkey,
    source:Pubkey,dest:Pubkey,treasury:Pubkey,wrong_dest:Pubkey,overflow_treasury:Pubkey,wrong_mint:Pubkey,
    prefunded_ref:Pubkey,
}
impl Fixture {
    async fn new()->Self {
        let program=Pubkey::new_unique();
        let payer=Keypair::new();
        let worker=Pubkey::new_unique();
        let source=Pubkey::new_unique();let dest=Pubkey::new_unique();let treasury=Pubkey::new_unique();
        let wrong_dest=Pubkey::new_unique();let overflow_treasury=Pubkey::new_unique();let wrong_mint=Pubkey::new_unique();
        let prefunded_ref=Pubkey::new_unique();
        let mut pt=ProgramTest::default();
        if std::env::var("ZER0LIFE_TEST_SBF").as_deref()==Ok("1") {
            // No native fallback: missing or incompatible SBF must fail the test.
            let dir=std::env::var("BPF_OUT_DIR").expect("BPF_OUT_DIR required for SBF test");
            assert!(std::path::Path::new(&dir).join("zer0life_payment_prototype.so").is_file());
            pt.prefer_bpf(true);
            pt.add_program("zer0life_payment_prototype",program,None);
            println!("ZER0LIFE execution mode: compiled SBF");
        } else {
            pt.prefer_bpf(false);
            pt.add_program("zer0life_payment_prototype",program,processor!(process_instruction));
            println!("ZER0LIFE execution mode: native");
        }
        // SPL token stays native in this isolated fixture.
        pt.prefer_bpf(false);
        pt.add_program("spl_token",spl_token::id(),processor!(spl_token::processor::Processor::process));
        pt.add_account(payer.pubkey(),system_account(1_000_000_000));
        pt.add_account(mint_key(),mint_account());
        pt.add_account(wrong_mint,mint_account());
        pt.add_account(source,token_account(mint_key(),payer.pubkey(),GROSS*4));
        pt.add_account(dest,token_account(mint_key(),worker,0));
        pt.add_account(treasury,token_account(mint_key(),treasury_owner(),0));
        pt.add_account(wrong_dest,token_account(mint_key(),Pubkey::new_unique(),0));
        // Deliberately impossible supply fixture to force the second SPL CPI to overflow.
        pt.add_account(overflow_treasury,token_account(mint_key(),treasury_owner(),u64::MAX));
        pt.add_account(receipt_address(&program,&payer.pubkey(),&prefunded_ref).0,system_account(10_000_000));
        let ctx=pt.start_with_context().await;
        Self{ctx,program,payer,worker,source,dest,treasury,wrong_dest,overflow_treasury,wrong_mint,prefunded_ref}
    }
    fn receipt(&self,r:Pubkey)->Pubkey {receipt_address(&self.program,&self.payer.pubkey(),&r).0}
    fn ix(&self,r:Pubkey,cents:u64,dest:Pubkey,treasury:Pubkey,mint:Pubkey)->Instruction {
        let mut data=vec![1];data.extend(r.to_bytes());data.extend(self.worker.to_bytes());data.extend(cents.to_le_bytes());
        Instruction{program_id:self.program,accounts:vec![
            AccountMeta::new(self.payer.pubkey(),true),AccountMeta::new(self.receipt(r),false),
            AccountMeta::new(self.source,false),AccountMeta::new(dest,false),
            AccountMeta::new(treasury,false),AccountMeta::new_readonly(mint,false),
            AccountMeta::new_readonly(spl_token::id(),false),AccountMeta::new_readonly(system_program::id(),false),
        ],data}
    }
    async fn send(&mut self,ix:Instruction,nonce:u32)->Result<(),TransactionError> {
        let blockhash=self.ctx.banks_client.get_latest_blockhash().await.unwrap();
        // Different compute budget instruction => distinct transaction signature even with same blockhash.
        let tx=Transaction::new_signed_with_payer(
            &[ComputeBudgetInstruction::set_compute_unit_limit(200_000+nonce),ix],
            Some(&self.payer.pubkey()),&[&self.payer],blockhash);
        self.ctx.banks_client.process_transaction(tx).await.map_err(|e|e.unwrap())
    }
    async fn amount(&mut self,k:Pubkey)->u64 {
        let a=self.ctx.banks_client.get_account(k).await.unwrap().unwrap();
        TokenAccount::unpack(&a.data).unwrap().amount
    }
    async fn balances(&mut self)->(u64,u64,u64) {
        let (s,d,t)=(self.source,self.dest,self.treasury);
        (self.amount(s).await,self.amount(d).await,self.amount(t).await)
    }
    async fn receipt_account(&mut self,r:Pubkey)->Option<Account> {
        let k=self.receipt(r);self.ctx.banks_client.get_account(k).await.unwrap()
    }
}
#[tokio::test]
async fn payment_runtime_replay_validation_and_atomic_rollback() {
    let mut f=Fixture::new().await;
    let r=Pubkey::new_unique();
    let ix=f.ix(r,CENTS,f.dest,f.treasury,mint_key());
    f.send(ix.clone(),1).await.unwrap();
    assert_eq!(f.balances().await,(GROSS*3,NET,FEE));
    let receipt=f.receipt_account(r).await.unwrap();
    assert_eq!(receipt.owner,f.program);assert_eq!(receipt.data.len(),105);
    assert_eq!(receipt.data[0],1);
    assert_eq!(&receipt.data[1..33],f.payer.pubkey().as_ref());
    assert_eq!(&receipt.data[33..65],r.as_ref());
    assert_eq!(&receipt.data[65..97],f.worker.as_ref());
    assert_eq!(&receipt.data[97..105],&CENTS.to_le_bytes());
    let error=f.send(ix,2).await.unwrap_err();
    assert_eq!(error,TransactionError::InstructionError(1,InstructionError::Custom(1)));
    assert_eq!(f.balances().await,(GROSS*3,NET,FEE));

    // A pre-funded empty PDA can still become a permanent receipt.
    let pref=f.prefunded_ref;
    let ix=f.ix(pref,CENTS,f.dest,f.treasury,mint_key());
    f.send(ix,3).await.unwrap();
    assert_eq!(f.balances().await,(GROSS*2,NET*2,FEE*2));
    assert_eq!(f.receipt_account(pref).await.unwrap().owner,f.program);

    // Wrong token owner, mint, malformed amount, and insufficient balance are rejected.
    for (n,cents,dst,mint) in [(4,CENTS,f.wrong_dest,mint_key()),(5,CENTS,f.dest,f.wrong_mint),(6,0,f.dest,mint_key()),(7,CENTS*3,f.dest,mint_key())] {
        let r=Pubkey::new_unique();
        let ix=f.ix(r,cents,dst,f.treasury,mint);
        assert!(f.send(ix,n).await.is_err());
        assert!(f.receipt_account(r).await.is_none());
        assert_eq!(f.balances().await,(GROSS*2,NET*2,FEE*2));
    }
    // The first transfer and PDA creation must be rolled back if the second transfer fails.
    let r=Pubkey::new_unique();
    let ix=f.ix(r,CENTS,f.dest,f.overflow_treasury,mint_key());
    assert!(f.send(ix,8).await.is_err());
    assert!(f.receipt_account(r).await.is_none());
    assert_eq!(f.balances().await,(GROSS*2,NET*2,FEE*2));
    let overflow=f.overflow_treasury;
    assert_eq!(f.amount(overflow).await,u64::MAX);
}

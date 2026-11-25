"""Offline experiment. No RPC, private keys, broadcasting or production integration."""
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.instruction import AccountMeta,Instruction
from solders.message import Message
from solders.transaction import Transaction
from marketplace_contract_preview import instruction_data,candidate_matches,SYSTEM
from marketplace_split import TOKEN, key
from payment_policy import TREASURY,USDC_MINT

def receipt_address(program,payer,reference):
    p,a,r=(Pubkey.from_string(key(k)) for k in (program,payer,reference))
    if len({p,a,r})!=3 or Pubkey.default() in (p,a,r):
        raise ValueError("Distinct nonzero program, payer and reference required")
    address,bump=Pubkey.find_program_address([b"zrl-paid-v1",bytes(a),bytes(r)],p)
    return str(address),bump

def unsigned_preview(program,payer,recipient,reference,cents,source,destination,treasury):
    # No configured production program ID exists. This function is only in the lab.
    pda,_=receipt_address(program,payer,reference)
    if len({program,payer,recipient,reference,pda,source,destination,treasury,TREASURY,USDC_MINT,TOKEN,SYSTEM})!=12:
        raise ValueError("Distinct account identities required")
    fields=[payer,pda,source,destination,treasury,USDC_MINT,TOKEN,SYSTEM]
    accounts=[AccountMeta(Pubkey.from_string(key(k)),i==0,i<5) for i,k in enumerate(fields)]
    instruction=Instruction(Pubkey.from_string(key(program)),instruction_data(reference,recipient,cents),accounts)
    message=Message.new_with_blockhash([instruction],Pubkey.from_string(key(payer)),Hash.default())
    return bytes(Transaction.new_unsigned(message))

def verify_fixture(tx,receipt,program,sig,payer,recipient,reference,cents,issued):
    pda,_=receipt_address(program,payer,reference)
    return candidate_matches(tx,receipt,program,pda,sig,payer,recipient,reference,cents,issued)

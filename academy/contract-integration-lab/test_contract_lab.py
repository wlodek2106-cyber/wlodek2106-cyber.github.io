import unittest
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.hash import Hash
from solders.signature import Signature
from contract_lab import receipt_address,unsigned_preview
from marketplace_contract_preview import instruction_data,SYSTEM
from marketplace_split import TOKEN
from payment_policy import USDC_MINT

def synthetic(n):
    return str(Pubkey.from_bytes(bytes([n])*32))

class LabTests(unittest.TestCase):
    def test_pda(self):
        program,payer,ref=[synthetic(i) for i in (11,12,13)]
        pda,bump=receipt_address(program,payer,ref)
        computed=Pubkey.create_program_address([b"zrl-paid-v1",bytes(Pubkey.from_string(payer)),bytes(Pubkey.from_string(ref)),bytes([bump])],Pubkey.from_string(program))
        self.assertEqual(str(computed),pda)
        self.assertFalse(computed.is_on_curve())
        self.assertNotEqual(receipt_address(program,payer,synthetic(14))[0],pda)
        self.assertNotEqual(receipt_address(program,synthetic(14),ref)[0],pda)
        self.assertNotEqual(receipt_address(synthetic(14),payer,ref)[0],pda)
        with self.assertRaises(ValueError): receipt_address(program,payer,payer)
    def test_unsigned_abi(self):
        program,payer,recipient,ref,source,dest,treasury=[synthetic(i) for i in range(11,18)]
        raw=unsigned_preview(program,payer,recipient,ref,100000,source,dest,treasury)
        tx=Transaction.from_bytes(raw);msg=tx.message
        self.assertEqual(list(tx.signatures),[Signature.default()])
        self.assertEqual(msg.recent_blockhash,Hash.default())
        self.assertEqual(msg.header.num_required_signatures,1)
        self.assertEqual(str(msg.account_keys[0]),payer)
        self.assertEqual(len(msg.instructions),1)
        ix=msg.instructions[0];pda,_=receipt_address(program,payer,ref)
        self.assertEqual(str(msg.account_keys[ix.program_id_index]),program)
        self.assertEqual([str(msg.account_keys[i]) for i in ix.accounts],[payer,pda,source,dest,treasury,USDC_MINT,TOKEN,SYSTEM])
        self.assertEqual(bytes(ix.data),instruction_data(ref,recipient,100000))
        with self.assertRaises(ValueError): unsigned_preview(program,payer,recipient,ref,100000,source,dest,dest)
        with self.assertRaises(ValueError): unsigned_preview(program,payer,recipient,ref,0,source,dest,treasury)

if __name__=="__main__":
    unittest.main()

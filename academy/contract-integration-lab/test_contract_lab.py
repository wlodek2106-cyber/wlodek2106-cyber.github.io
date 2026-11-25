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


class MarketplaceBoundaryTests(unittest.TestCase):
    def setUp(self):
        import base64
        from datetime import datetime, timezone
        from marketplace_boundary import IssuedInvoice
        from marketplace_contract_preview import receipt_data
        from marketplace_split import split
        from payment_policy import TREASURY
        self.program, payer, recipient, ref, source, dest, fee = [synthetic(i) for i in range(21,28)]
        self.invoice = IssuedInvoice(payer, recipient, ref, 10000, datetime.fromtimestamp(100, timezone.utc))
        self.sig = str(Signature.from_bytes(bytes([32])*64))
        pda, _ = receipt_address(self.program, payer, ref)
        keys = [payer,pda,source,dest,fee,USDC_MINT,TOKEN,SYSTEM,self.program]
        amounts = split(self.invoice.quote_cents)
        def enc(raw):
            from marketplace_split import ALPHABET
            n = int.from_bytes(raw, "big")
            out = ""
            while n:
                n,r = divmod(n,58)
                out = ALPHABET[r] + out
            return "1" * (len(raw)-len(raw.lstrip(bytes([0])))) + out
        def transfer(to, amount):
            return {"programIdIndex":6,"accounts":[2,5,to,0],
                    "data":enc(bytes([12])+amount.to_bytes(8,"little")+bytes([6]))}
        def balance(i, owner, value):
            return {"accountIndex":i,"mint":USDC_MINT,"owner":owner,
                    "uiTokenAmount":{"decimals":6,"amount":str(value)}}
        self.tx = {"slot":150,"blockTime":101,
                   "transaction":{"signatures":[self.sig],"message":{"accountKeys":keys,
                   "header":{"numRequiredSignatures":1,"numReadonlySignedAccounts":0,"numReadonlyUnsignedAccounts":4},
                   "instructions":[{"programIdIndex":8,"accounts":list(range(8)),
                   "data":enc(instruction_data(ref,recipient,self.invoice.quote_cents))}]}},
                   "meta":{"err":None,"innerInstructions":[{"index":0,"instructions":[
                   transfer(3,amounts["freelancer_atomic"]),transfer(4,amounts["fee_atomic"])]}],
                   "preTokenBalances":[balance(2,payer,amounts["gross_atomic"]),balance(3,recipient,0),balance(4,TREASURY,0)],
                   "postTokenBalances":[balance(2,payer,0),balance(3,recipient,amounts["freelancer_atomic"]),balance(4,TREASURY,amounts["fee_atomic"])]}}
        self.status = {"context":{"slot":160},"value":[{"slot":150,"confirmationStatus":"finalized","confirmations":None,"err":None}]}
        self.receipt = {"context":{"slot":160},"value":{"owner":self.program,"executable":False,"lamports":1,
                        "data":[base64.b64encode(receipt_data(payer,ref,recipient,self.invoice.quote_cents)).decode(),"base64"]}}

    def verdict(self):
        from marketplace_boundary import verify_finalized_snapshot
        return verify_finalized_snapshot(self.invoice,self.program,self.sig,self.status,self.tx,self.receipt)

    def test_matching_finalized_invoice(self):
        self.assertTrue(self.verdict())

    def test_missing_or_unfinalized_status(self):
        self.status["value"][0]["confirmationStatus"]="confirmed"
        self.assertFalse(self.verdict())
        self.status["value"]=[None]
        self.assertFalse(self.verdict())

    def test_stale_receipt_context(self):
        self.receipt["context"]["slot"]=149
        self.assertFalse(self.verdict())

    def test_mismatched_transaction_slot(self):
        self.status["value"][0]["slot"]=151
        self.assertFalse(self.verdict())

    def test_wrong_invoice_reference(self):
        from dataclasses import replace
        self.invoice=replace(self.invoice,reference=synthetic(41))
        self.assertFalse(self.verdict())

    def test_wrong_quote(self):
        from dataclasses import replace
        self.invoice=replace(self.invoice,quote_cents=20000)
        self.assertFalse(self.verdict())

    def test_wrong_receipt_owner(self):
        self.receipt["value"]["owner"]=synthetic(42)
        self.assertFalse(self.verdict())

    def test_wrong_fee_balance(self):
        self.tx["meta"]["postTokenBalances"][2]["uiTokenAmount"]["amount"]="1"
        self.assertFalse(self.verdict())

    def test_failed_transaction(self):
        self.tx["meta"]["err"]={"InstructionError":[0,"Custom"]}
        self.assertFalse(self.verdict())

    def test_pre_issuance_transaction(self):
        self.tx["blockTime"]=99
        self.assertFalse(self.verdict())


    def scan(self, rows=None, recorded=None, missing=False, outage=False):
        from copy import deepcopy
        from marketplace_contract_reconcile import reconcile_fixture
        pda,_=receipt_address(self.program,self.invoice.payer,self.invoice.reference)
        if rows is None:
            rows=[{"signature":self.sig,"slot":150,"confirmationStatus":"finalized","err":None}]
        calls=[]
        def rpc(method,params):
            calls.append((method,params))
            if method=="getSignaturesForAddress":
                self.assertEqual(params[0],pda)
                self.assertEqual(params[1]["limit"],5)
                return rows
            if method=="getAccountInfo":
                self.assertEqual(params[0],pda)
                return {"context":{"slot":160},"value":None} if missing else self.receipt
            if method=="getSignatureStatuses":
                self.assertTrue(params[1]["searchTransactionHistory"])
                return self.status
            if method=="getTransaction":
                if outage:
                    raise TimeoutError()
                tx=deepcopy(self.tx)
                tx["transaction"]["signatures"]=[params[0]]
                return tx
            raise AssertionError(method)
        result=reconcile_fixture(rpc,self.invoice,self.program,recorded)
        self.assertFalse(result["safe_to_retry"])
        self.assertFalse(result["settlement_authorized"])
        return result,calls

    def test_reconcile_candidate_at_canonical_pda(self):
        result,calls=self.scan()
        self.assertEqual(result["state"],"candidate")
        self.assertEqual(result["matches"],[self.sig])
        self.assertEqual(len(calls),4)

    def test_reconcile_repeated_history_row(self):
        row={"signature":self.sig,"slot":150,"confirmationStatus":"finalized","err":None}
        result,_=self.scan([row,row])
        self.assertEqual(result["checked"],1)
        self.assertFalse(result["conflict"])

    def test_reconcile_conflicting_signatures(self):
        second=str(Signature.from_bytes(bytes([33])*64))
        rows=[{"signature":s,"slot":150,"confirmationStatus":"finalized","err":None} for s in (self.sig,second)]
        result,_=self.scan(rows)
        self.assertEqual(result["state"],"conflict")
        self.assertTrue(result["conflict"])

    def test_reconcile_conflict_with_recorded_signature(self):
        second=str(Signature.from_bytes(bytes([33])*64))
        result,_=self.scan(recorded=second)
        self.assertEqual(result["state"],"conflict")

    def test_reconcile_recorded_signature(self):
        result,_=self.scan(recorded=self.sig)
        self.assertEqual(result["state"],"recorded")

    def test_reconcile_missing_receipt(self):
        result,_=self.scan(missing=True)
        self.assertEqual(result["state"],"incomplete")

    def test_reconcile_rpc_outage(self):
        result,_=self.scan(outage=True)
        self.assertEqual(result["state"],"incomplete")

    def test_reconcile_empty_history(self):
        result,_=self.scan([])
        self.assertEqual(result["state"],"not_found")

    def test_reconcile_truncated_history(self):
        row={"signature":self.sig,"slot":150,"confirmationStatus":"finalized","err":None}
        result,_=self.scan([row]*5)
        self.assertTrue(result["incomplete"])
        self.assertEqual(result["state"],"incomplete")

    def test_reconcile_recorded_not_found(self):
        result,_=self.scan([],recorded=self.sig)
        self.assertEqual(result["state"],"recorded_unverified")

if __name__=="__main__":
    unittest.main()

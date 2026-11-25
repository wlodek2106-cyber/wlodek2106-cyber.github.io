"""Offline ABI/receipt validation for the experimental contract. NOT a settlement route.

The caller must supply a trusted audited program ID and canonical PDA derived
by a reviewed Solana SDK, never client input. No RPC, signing, DB or activation.
"""
import base64
from marketplace_split import decode58,key,split,signature,TOKEN,COMPUTE
from payment_policy import USDC_MINT,TREASURY
SYSTEM="11111111111111111111111111111111"

def instruction_data(reference,recipient,cents):
    split(cents)
    return bytes([1])+decode58(key(reference))+decode58(key(recipient))+cents.to_bytes(8,"little")

def receipt_data(payer,reference,recipient,cents):
    split(cents)
    return bytes([1])+decode58(key(payer))+decode58(key(reference))+decode58(key(recipient))+cents.to_bytes(8,"little")

def receipt_matches(account,program,payer,reference,recipient,cents):
    try:
        key(program)
        if len({payer,recipient,TREASURY,reference})!=4: return False
        if account["owner"]!=program or account["executable"] is not False: return False
        if type(account["lamports"]) is not int or account["lamports"]<=0: return False
        data=account["data"]
        return (len(data)==2 and data[1]=="base64" and len(data[0])==140 and
            base64.b64decode(data[0],validate=True)==receipt_data(payer,reference,recipient,cents))
    except (ValueError,TypeError,KeyError,IndexError,AttributeError,OverflowError):
        return False

def candidate_matches(tx,receipt,program,pda,sig,payer,recipient,reference,cents,issued):
    """Conservative fixture matcher for expected ABI, two token CPIs and receipt.
    No trust in client-supplied program or PDA; both must come from trusted config.
    This is not proof of finality, PDA derivation, or deployed bytecode identity.
    """
    try:
        for k in (program,pda,payer,recipient,reference): key(k)
        signature(sig)
        if len({program,pda,payer,recipient,reference,TREASURY,USDC_MINT,TOKEN,SYSTEM})!=9: return False
        if not receipt_matches(receipt,program,payer,reference,recipient,cents): return False
        amounts=split(cents);tr=tx["transaction"];m=tr["message"];meta=tx["meta"];h=m["header"]
        if meta["err"] is not None or tx["blockTime"]<int(issued.timestamp()) or tr["signatures"]!=[sig]: return False
        keys=m["accountKeys"]
        if len(keys)!=len(set(keys)) or keys[0]!=payer or h["numRequiredSignatures"]!=1 or h["numReadonlySignedAccounts"]!=0: return False
        if m.get("addressTableLookups") or any(meta.get("loadedAddresses",{}).get(k) for k in ("readonly","writable")): return False
        def index(i):
            if type(i) is not int or not 0<=i<len(keys): raise ValueError("Invalid index")
            return i
        ro=len(keys)-h["numReadonlyUnsignedAccounts"]
        if not 5<=ro<=len(keys): return False
        outer=[]
        for i,ix in enumerate(m["instructions"]):
            pid=keys[index(ix["programIdIndex"])]
            if pid==COMPUTE and not ix["accounts"]: continue
            if pid!=program: return False
            outer.append((i,ix))
        if len(outer)!=1: return False
        i,ix=outer[0];ac=[index(j) for j in ix["accounts"]]
        if len(ac)!=8 or len(set(ac))!=8 or decode58(ix["data"])!=instruction_data(reference,recipient,cents): return False
        pay,rec,src,dst,fee,mint,token,system=ac
        if pay!=0 or keys[rec]!=pda or keys[mint]!=USDC_MINT or keys[token]!=TOKEN or keys[system]!=SYSTEM: return False
        if not all(0<j<ro for j in (rec,src,dst,fee)): return False
        if not all(ro<=j for j in (mint,token,system,index(ix["programIdIndex"]))): return False
        groups=meta["innerInstructions"]
        if len(groups)!=1 or groups[0]["index"]!=i: return False
        transfers=[]
        for inner in groups[0]["instructions"]:
            pid=keys[index(inner["programIdIndex"])]
            accounts=[index(j) for j in inner["accounts"]]
            data=decode58(inner["data"])
            if pid==SYSTEM:
                if rec not in accounts or not all(j in (0,rec) for j in accounts): return False
                continue
            if pid!=TOKEN or len(data)!=10 or data[0]!=12 or data[9]!=6: return False
            transfers.append((accounts,int.from_bytes(data[1:9],"little")))
        if transfers!=[([src,mint,dst,0],amounts["freelancer_atomic"]),([src,mint,fee,0],amounts["fee_atomic"])]: return False
        def balances(which):
            out={}
            for b in meta[which]:
                if b["mint"]!=USDC_MINT: continue
                j=index(b["accountIndex"]);v=b["uiTokenAmount"]
                if j in out or v["decimals"]!=6: raise ValueError("Invalid token balances")
                out[j]=(b["owner"],int(v["amount"]))
                if out[j][1]<0: raise ValueError("Negative balance")
            return out
        before,after=balances("preTokenBalances"),balances("postTokenBalances")
        for j,owner,delta in [(src,payer,-amounts["gross_atomic"]),(dst,recipient,amounts["freelancer_atomic"]),(fee,TREASURY,amounts["fee_atomic"])]:
            if before[j][0]!=owner or after[j][0]!=owner or after[j][1]-before[j][1]!=delta: return False
        return True
    except (ValueError,TypeError,KeyError,IndexError,AttributeError,OverflowError):
        return False

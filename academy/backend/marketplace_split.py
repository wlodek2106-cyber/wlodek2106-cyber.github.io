"""Pure SPL USDC split policy and finalized raw transaction validation."""
from payment_policy import TREASURY,USDC_MINT
ALPHABET="123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
TOKEN="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
COMPUTE="ComputeBudget111111111111111111111111111111"

def decode58(value):
    if not isinstance(value,str) or not 1<=len(value)<=128: raise ValueError("Invalid base58")
    n=0
    for c in value: n=n*58+ALPHABET.index(c)
    return b"\x00"*(len(value)-len(value.lstrip("1")))+n.to_bytes((n.bit_length()+7)//8,"big")

def key(value):
    if len(decode58(value))!=32: raise ValueError("Invalid Solana wallet")
    return value

def signature(value):
    if len(decode58(value))!=64: raise ValueError("Invalid transaction signature")
    return value

def split(cents):
    if type(cents) is not int or not 1<=cents<=100000000: raise ValueError("Invalid quote")
    gross=cents*10000
    fee=gross*5//100
    return {"gross_atomic":gross,"fee_atomic":fee,"freelancer_atomic":gross-fee}

def matches(tx,sig,payer,recipient,reference,cents,created):
    """Only exact, finalized, successful two-transfer legacy SPL transaction.
    RPC commitment is requested by caller. No inner transfers or arbitrary programs."""
    try:
        signature(sig)
        for k in (payer,recipient,reference,TREASURY): key(k)
        if len({payer,recipient,reference,TREASURY})!=4: return False
        amounts=split(cents); meta=tx["meta"]; tr=tx["transaction"]
        if meta["err"] is not None or tx["blockTime"]<int(created.timestamp()) or tr["signatures"]!=[sig]: return False
        m=tr["message"]; keys=m["accountKeys"]; h=m["header"]
        if not isinstance(keys,list) or not 1<=len(keys)<=256 or len(keys)!=len(set(keys)): return False
        for account in keys: key(account)
        if type(h["numRequiredSignatures"]) is not int or h["numRequiredSignatures"]!=1 or keys[0]!=payer or type(h["numReadonlySignedAccounts"]) is not int or h["numReadonlySignedAccounts"]!=0: return False
        if type(h["numReadonlyUnsignedAccounts"]) is not int or not 1<=h["numReadonlyUnsignedAccounts"]<len(keys): return False
        if m.get("addressTableLookups") or any(meta.get("loadedAddresses",{}).get(k) for k in ("writable","readonly")): return False
        ro=len(keys)-h["numReadonlyUnsignedAccounts"]
        if reference not in keys or not ro<=keys.index(reference)<len(keys): return False
        if any(x.get("instructions") for x in (meta.get("innerInstructions") or [])): return False
        def balances(which):
            out={}
            for b in meta.get(which,[]):
                if b.get("mint")!=USDC_MINT: continue
                if b["uiTokenAmount"]["decimals"]!=6 or not b.get("owner"): raise ValueError("Invalid token balance")
                idx=b["accountIndex"]
                if type(idx) is not int or not 0<=idx<len(keys) or idx in out: raise ValueError("Invalid account index")
                amount=b["uiTokenAmount"]["amount"]
                if not isinstance(amount,str) or not 1<=len(amount)<=20 or not amount.isascii() or not amount.isdecimal() or int(amount)>2**64-1: raise ValueError("Invalid token amount")
                out[idx]=(key(b["owner"]),int(amount))
            return out
        pre,post=balances("preTokenBalances"),balances("postTokenBalances")
        def delta(i,owner):
            if i not in pre or i not in post or pre[i][0]!=owner or post[i][0]!=owner: raise ValueError("Invalid owner")
            return post[i][1]-pre[i][1]
        expected={TREASURY:amounts["fee_atomic"],recipient:amounts["freelancer_atomic"]}
        seen=set(); sources={}
        for ix in m["instructions"]:
            program=ix["programIdIndex"]
            if type(program) is not int or not ro<=program<len(keys): return False
            p=keys[program]
            if p==COMPUTE:
                if ix["accounts"]: return False
                continue
            if p!=TOKEN: return False
            ac=ix["accounts"]; data=decode58(ix["data"])
            if len(ac)!=5 or len(data)!=10 or data[0]!=12 or data[9]!=6: return False
            src,mint,dst,authority,ref=ac
            if not all(type(i) is int and 0<=i<len(keys) for i in ac): return False
            if not 1<=src<ro or not 1<=dst<ro or src==dst or keys[mint]!=USDC_MINT or authority!=0 or keys[ref]!=reference: return False
            owner=post[dst][0]; value=int.from_bytes(data[1:9],"little")
            if owner not in expected or owner in seen or value!=expected[owner] or delta(dst,owner)!=value: return False
            seen.add(owner); sources[src]=sources.get(src,0)+value
        return seen==set(expected) and sum(sources.values())==amounts["gross_atomic"] and all(delta(i,payer)==-v for i,v in sources.items())
    except (KeyError,TypeError,ValueError,IndexError,AttributeError,OverflowError): return False

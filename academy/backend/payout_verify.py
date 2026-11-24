"""Verify finalized, direct SPL USDC payout from the configured treasury.
No signing, private keys or transaction submission."""
import json,os
from urllib.request import Request,urlopen
from payment_policy import TREASURY,USDC_MINT
TOKEN_PROGRAM="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

def matches(tx,signature,wallet,amount,not_before):
    if wallet==TREASURY or type(amount) is not int or amount<=0: return False
    try:
        meta=tx["meta"]
        if meta["err"] is not None or tx["blockTime"]<int(not_before.timestamp()): return False
        tr=tx["transaction"]
        if tr["signatures"][0]!=signature: return False
        msg=tr["message"];keys=msg["accountKeys"]
        if not any(k["pubkey"]==TREASURY and k["signer"] is True for k in keys): return False
        def accounts(which,owner):
            return {keys[b["accountIndex"]]["pubkey"]:int(b["uiTokenAmount"]["amount"])
                    for b in meta.get(which,[]) if b.get("owner")==owner and b.get("mint")==USDC_MINT and b["uiTokenAmount"]["decimals"]==6}
        srcpre=accounts("preTokenBalances",TREASURY);srcpost=accounts("postTokenBalances",TREASURY)
        dstpre=accounts("preTokenBalances",wallet);dstpost=accounts("postTokenBalances",wallet)
        if sum(srcpre.values())-sum(srcpost.values())!=amount or sum(dstpost.values())-sum(dstpre.values())!=amount: return False
        matched=[]
        for ix in msg["instructions"]:
            if ix.get("programId")!=TOKEN_PROGRAM: continue
            parsed=ix.get("parsed",{});info=parsed.get("info",{})
            if parsed.get("type")=="transferChecked":
                token=info.get("tokenAmount",{})
                if info.get("mint")!=USDC_MINT or token.get("decimals")!=6: continue
                value=int(token["amount"])
            elif parsed.get("type")=="transfer": value=int(info["amount"])
            else: continue
            src=info.get("source");dst=info.get("destination")
            if info.get("authority")==TREASURY and src in srcpre and dst in dstpost and value==amount:
                if srcpre[src]-srcpost.get(src,0)==amount and dstpost[dst]-dstpre.get(dst,0)==amount:
                    matched.append(ix)
        return len(matched)==1
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False

def verify(signature,wallet,amount,not_before):
    payload={"jsonrpc":"2.0","id":1,"method":"getTransaction","params":[signature,{"encoding":"jsonParsed","commitment":"finalized","maxSupportedTransactionVersion":0}]}
    rpc=os.getenv("ACADEMY_SOLANA_RPC","https://api.mainnet-beta.solana.com")
    with urlopen(Request(rpc,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"}),timeout=15) as resp:
        tx=json.load(resp).get("result")
    return matches(tx,signature,wallet,amount,not_before)

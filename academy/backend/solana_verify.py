import json
import os
import re
from urllib.request import Request,urlopen
from payment_policy import TREASURY,USDC_MINT,validate_amount

def verify_usdc(signature,expected,reference,created_at,expires_at):
    if not isinstance(signature,str) or not re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{64,88}",signature):
        raise ValueError("Invalid signature")
    payload={"jsonrpc":"2.0","id":1,"method":"getTransaction","params":[signature,{"encoding":"jsonParsed","commitment":"finalized","maxSupportedTransactionVersion":0}]}
    url=os.environ.get("ACADEMY_SOLANA_RPC","https://api.mainnet-beta.solana.com")
    with urlopen(Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"}),timeout=15) as response:
        tx=json.load(response).get("result")
    if not tx or not tx.get("meta") or tx["meta"]["err"] is not None:
        return False
    timestamp=tx.get("blockTime")
    if timestamp is None or not int(created_at.timestamp())<=timestamp<=int(expires_at.timestamp()):
        return False
    msg=tx["transaction"]["message"]
    keys=msg["accountKeys"]
    if not any(k["pubkey"]==reference and not k["signer"] and not k["writable"] for k in keys):
        return False
    if tx["transaction"]["signatures"][0]!=signature:
        return False
    def balances(items):
        return sum(int(b["uiTokenAmount"]["amount"]) for b in items if b.get("owner")==TREASURY and b.get("mint")==USDC_MINT and b["uiTokenAmount"]["decimals"]==6)
    meta=tx["meta"]
    destinations={keys[b["accountIndex"]]["pubkey"] for b in meta.get("postTokenBalances",[]) if b.get("owner")==TREASURY and b.get("mint")==USDC_MINT and b["uiTokenAmount"]["decimals"]==6}
    # Require the invoice reference on the actual outer SPL transfer instruction.
    # jsonParsed may omit extra reference accounts, so fetch the raw compiled message.
    payload["params"][1]["encoding"]="json"
    with urlopen(Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"}),timeout=15) as response:
        raw=json.load(response).get("result")
    if not raw or raw["transaction"]["signatures"][0]!=signature or raw["meta"]["err"] is not None:
        return False
    message=raw["transaction"]["message"]
    loaded=raw["meta"].get("loadedAddresses",{})
    addresses=message["accountKeys"]+loaded.get("writable",[])+loaded.get("readonly",[])
    matched=False
    for ix in message["instructions"]:
        if addresses[ix["programIdIndex"]]!="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
            continue
        accounts=[addresses[i] for i in ix["accounts"]]
        alphabet="123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        encoded=ix.get("data","")
        n=0
        for c in encoded:
            n=n*58+alphabet.index(c)
        data=b"\x00"*(len(encoded)-len(encoded.lstrip("1")))+n.to_bytes((n.bit_length()+7)//8,"big")
        # SPL Transfer (3) or TransferChecked (12), exact amount and destination.
        if len(data)==9 and data[0]==3:
            destination_index=1
            minimum_accounts=3
        elif len(data)==10 and data[0]==12 and data[9]==6 and len(accounts)>=4 and accounts[1]==USDC_MINT:
            destination_index=2
            minimum_accounts=4
        else:
            continue
        if len(accounts)>minimum_accounts and reference in accounts[minimum_accounts:] and accounts[destination_index] in destinations and int.from_bytes(data[1:9],"little")==expected:
            matched=True
    if not matched:
        return False
    return validate_amount(expected,balances(meta.get("postTokenBalances",[]))-balances(meta.get("preTokenBalances",[])))

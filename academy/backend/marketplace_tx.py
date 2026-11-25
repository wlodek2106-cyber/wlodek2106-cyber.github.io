"""Minimal unsigned legacy Solana Pay transaction; no signing or broadcasting."""
import base64,json,os
from urllib.request import Request,urlopen
from payment_policy import TREASURY,USDC_MINT
from marketplace_split import key,decode58,split,TOKEN

ORIGIN="https://zer0life-academy.onrender.com"

def pay_url(reference):
    from urllib.parse import quote
    return "solana:"+quote(ORIGIN+"/marketplace-pay/request/"+key(reference),safe=":/")

def unsigned(payer,source,worker_account,treasury_account,reference,cents):
    keys=[payer,source,worker_account,treasury_account,USDC_MINT,reference,TOKEN]
    if len(set(keys))!=7: raise ValueError("Distinct transaction accounts required")
    rawkeys=b"".join(decode58(key(k)) for k in keys)
    amounts=split(cents)
    def ix(dst,amount):
        data=bytes([12])+amount.to_bytes(8,"little")+bytes([6])
        return bytes([6,5,1,4,dst,0,5,len(data)])+data
    # Compact-u16 lengths are single bytes for this fixed seven-account message.
    msg=bytes([1,0,3,7])+rawkeys+bytes(32)+bytes([2])+ix(2,amounts["freelancer_atomic"])+ix(3,amounts["fee_atomic"])
    return base64.b64encode(bytes([1])+bytes(64)+msg).decode("ascii")

def rpc(method,params):
    url=os.getenv("ACADEMY_SOLANA_RPC","https://api.mainnet-beta.solana.com")
    body={"jsonrpc":"2.0","id":1,"method":method,"params":params}
    with urlopen(Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"}),timeout=6) as r:
        result=json.load(r)
    if "error" in result: raise RuntimeError("RPC unavailable")
    return result["result"]

def token_accounts(owner,minimum=0):
    result=rpc("getTokenAccountsByOwner",[key(owner),{"mint":USDC_MINT},{"encoding":"jsonParsed","commitment":"finalized"}])
    accounts=[]
    for x in result["value"]:
        info=x["account"]["data"]["parsed"]["info"]
        amount=info["tokenAmount"]
        if x["account"]["owner"]==TOKEN and info["owner"]==owner and info["mint"]==USDC_MINT and info["state"]=="initialized" and amount["decimals"]==6 and int(amount["amount"])>=minimum:
            accounts.append((int(amount["amount"]),key(x["pubkey"])))
    if not accounts: raise ValueError("Existing initialized USDC account required")
    return sorted(accounts,key=lambda x:(-x[0],x[1]))[0][1]

def build(payer,recipient,reference,cents):
    if len({payer,recipient,TREASURY,reference})!=4: raise ValueError("Distinct wallets required")
    source=token_accounts(payer,split(cents)["gross_atomic"])
    dst=token_accounts(recipient)
    fee=token_accounts(TREASURY)
    return unsigned(payer,source,dst,fee,reference,cents)

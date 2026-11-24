import os
import json
from urllib.request import Request, urlopen
from accounts import authenticate
from database import transaction
from settlement import settle

def discover(token, invoice):
    if os.getenv("ACADEMY_PAYMENTS_ENABLED")!="true" or os.getenv("ACADEMY_CHECKOUT_READY")!="true":
        raise PermissionError("Payments closed")
    student=authenticate(token)
    if student is None:
        raise PermissionError("Authentication required")
    with transaction() as cur:
        cur.execute("SELECT reference,signature,plan FROM payment_invoices WHERE id=%s AND student_id=%s",(invoice,student))
        row=cur.fetchone()
    if not row:
        raise ValueError("Invoice not found")
    reference,signature,plan=row
    if signature:
        return {"paid":True,"plan":plan}
    payload={"jsonrpc":"2.0","id":1,"method":"getSignaturesForAddress","params":[reference,{"commitment":"finalized","limit":10}]}
    url=os.environ.get("ACADEMY_SOLANA_RPC","https://api.mainnet-beta.solana.com")
    with urlopen(Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"}),timeout=15) as response:
        result=json.load(response)
    if "error" in result:
        raise RuntimeError("Payment network unavailable")
    for item in result.get("result",[]):
        if item.get("err") is not None:
            continue
        try:
            return settle(token,invoice,item["signature"])
        except ValueError:
            continue
    return {"paid":False,"status":"pending"}

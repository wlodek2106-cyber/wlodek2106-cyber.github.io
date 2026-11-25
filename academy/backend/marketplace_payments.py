"""Staged marketplace payment records; no private keys or transaction broadcasting."""
import os,json,re
from urllib.request import Request,urlopen
from payment_policy import TREASURY,USDC_MINT
from marketplace_split import split,key,signature,matches
from student_business import ident
from database import transaction
from accounts import authenticate

def enabled():
    return os.getenv("ACADEMY_MARKETPLACE_PAYMENTS_ENABLED")=="true"

def job_info(cur,sid,jid,lock=False):
    cur.execute("""SELECT j.client_id,a.student_id,j.status,a.quote_cents,j.payment_mode
        FROM academy_jobs j JOIN academy_job_applications a ON a.job_id=j.id AND a.id=j.selected_application
        WHERE j.id=%s"""+(" FOR UPDATE OF j" if lock else ""),(jid,))
    row=cur.fetchone()
    if not row or sid not in row[:2]: raise PermissionError("Selected parties only")
    return row

def preview(cur,sid,b):
    jid=ident(b["id"]);client,worker,status,cents,mode=job_info(cur,sid,jid)
    cur.execute("SELECT recipient FROM academy_job_payment_wallets WHERE job_id=%s",(jid,))
    wallet=cur.fetchone()
    cur.execute("SELECT payer,recipient,reference,created_at,signature,paid_at FROM academy_job_payments WHERE job_id=%s",(jid,))
    row=cur.fetchone()
    return {"role":"client" if sid==client else "freelancer","status":status,"mode":mode,"enabled":enabled(),"network":"solana-mainnet","mint":USDC_MINT,"treasury":TREASURY,**split(cents),"recipient":wallet[0] if wallet else None,"invoice":{"payer":row[0],"recipient":row[1],"reference":row[2],"created_at":row[3].isoformat(),"signature":row[4],"paid_at":row[5].isoformat() if row[5] else None} if row else None}

def wallet(cur,sid,b):
    if not enabled(): raise PermissionError("Marketplace payments closed")
    jid=ident(b["id"]);client,worker,status,_,mode=job_info(cur,sid,jid,True)
    if sid!=worker or mode!="split" or status not in ("assigned","delivered") or b.get("confirm") is not True: raise PermissionError()
    recipient=key(b["wallet"])
    if recipient==TREASURY: raise ValueError("Freelancer wallet must differ from treasury")
    cur.execute("SELECT 1 FROM academy_job_payments WHERE job_id=%s",(jid,))
    if cur.fetchone(): raise ValueError("Invoice wallet is locked")
    cur.execute("INSERT INTO academy_job_payment_wallets(job_id,recipient) VALUES (%s,%s) ON CONFLICT(job_id) DO UPDATE SET recipient=EXCLUDED.recipient",(jid,recipient))
    return {"saved":True}

def create(cur,sid,b):
    if not enabled(): raise PermissionError("Marketplace payments closed")
    jid=ident(b["id"]);client,worker,status,cents,mode=job_info(cur,sid,jid,True)
    if sid!=client or mode!="split" or status!="delivered" or b.get("confirm") is not True: raise PermissionError()
    payer=key(b["payer"]);recipient=key(b["recipient"])
    if len({payer,recipient,TREASURY})!=3: raise ValueError("Wallets must be distinct")
    cur.execute("SELECT recipient FROM academy_job_payment_wallets WHERE job_id=%s",(jid,))
    row=cur.fetchone()
    if not row or row[0]!=recipient: raise ValueError("Recipient changed; review again")
    cur.execute("SELECT payer,recipient FROM academy_job_payments WHERE job_id=%s",(jid,))
    previous=cur.fetchone()
    if previous and previous!=(payer,recipient): raise ValueError("Invoice locked; contact support")
    if not previous:
        from checkout import reference_key
        cur.execute("""INSERT INTO academy_job_payments(job_id,client_id,freelancer_id,payer,recipient,treasury,reference,quote_cents)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",(jid,client,worker,payer,recipient,TREASURY,reference_key(),cents))
    return preview(cur,sid,b)

def verify_chain(sig,payer,recipient,reference,cents,created):
    rpc=os.getenv("ACADEMY_SOLANA_RPC","https://api.mainnet-beta.solana.com")
    payload={"jsonrpc":"2.0","id":1,"method":"getTransaction","params":[sig,{"encoding":"json","commitment":"finalized","maxSupportedTransactionVersion":0}]}
    with urlopen(Request(rpc,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"}),timeout=12) as response:
        tx=json.load(response).get("result")
    return matches(tx,sig,payer,recipient,reference,cents,created)

def settle(token,b):
    if not enabled(): raise PermissionError("Marketplace payments closed")
    sid=authenticate(token)
    if sid is None: raise PermissionError()
    jid=ident(b["id"]);sig=signature(b["signature"])
    with transaction() as cur:
        client,worker,status,cents,mode=job_info(cur,sid,jid)
        if sid!=client or mode!="split": raise PermissionError()
        cur.execute("SELECT payer,recipient,reference,quote_cents,created_at,signature,treasury FROM academy_job_payments WHERE job_id=%s",(jid,))
        row=cur.fetchone()
    if not row: raise ValueError("No invoice")
    payer,recipient,reference,cents,created,previous,treasury=row
    if previous:
        if previous==sig:return {"paid":True}
        raise ValueError("Already paid; do not pay again")
    if treasury!=TREASURY or status!="delivered" or not verify_chain(sig,payer,recipient,reference,cents,created): raise ValueError("Payment not verified")
    with transaction() as cur:
        client,worker,status,_,mode=job_info(cur,sid,jid,True)
        cur.execute("SELECT signature FROM academy_job_payments WHERE job_id=%s FOR UPDATE",(jid,))
        previous=cur.fetchone()[0]
        if previous:
            if previous==sig:return {"paid":True}
            raise ValueError("Already paid")
        if status!="delivered": raise ValueError("Order changed; contact support")
        cur.execute("SELECT 1 FROM payment_invoices WHERE signature=%s",(sig,))
        if cur.fetchone(): raise ValueError("Signature already used")
        cur.execute("UPDATE academy_job_payments SET signature=%s,paid_at=now() WHERE job_id=%s",(sig,jid))
    return {"paid":True}

def treasury_report(cur):
    cur.execute("""SELECT count(*),COALESCE(sum(quote_cents*10000),0),COALESCE(sum(quote_cents*500),0),
        COALESCE(sum(quote_cents*500) FILTER(WHERE paid_at>=date_trunc('day',now() AT TIME ZONE 'UTC') AT TIME ZONE 'UTC'),0),
        COALESCE(sum(quote_cents*500) FILTER(WHERE paid_at>=date_trunc('month',now() AT TIME ZONE 'UTC') AT TIME ZONE 'UTC'),0),
        COALESCE(sum(quote_cents*500) FILTER(WHERE paid_at>=date_trunc('year',now() AT TIME ZONE 'UTC') AT TIME ZONE 'UTC'),0)
        FROM academy_job_payments WHERE paid_at IS NOT NULL""")
    n,g,f,day,month,year=cur.fetchone()
    cur.execute("SELECT job_id,quote_cents,signature,paid_at FROM academy_job_payments WHERE paid_at IS NOT NULL ORDER BY paid_at DESC LIMIT 100")
    items=[{"job_id":j,**split(c),"signature":s,"paid_at":t.isoformat()} for j,c,s,t in cur.fetchall()]
    return {"enabled":enabled(),"wallet":TREASURY,"network":"solana-mainnet","paid_count":n,"gross_atomic":str(g),"fee_atomic":str(f),"day_atomic":str(day),"month_atomic":str(month),"year_atomic":str(year),"items":items}

def dispatch(token,action,b):
    if action=="settle": return settle(token,b)
    if action=="treasury":
        from partners import owner
        owner(token)
        with transaction() as cur:return treasury_report(cur)
    sid=authenticate(token)
    if sid is None: raise PermissionError()
    with transaction() as cur:
        if action=="preview": return preview(cur,sid,b)
        if action=="wallet": return wallet(cur,sid,b)
        if action=="create": return create(cur,sid,b)
    raise ValueError("Invalid action")

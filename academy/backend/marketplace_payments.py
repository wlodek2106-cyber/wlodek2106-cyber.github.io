"""Staged marketplace payment records; no private keys or transaction broadcasting."""
import os,json,re
from urllib.request import Request,urlopen
from payment_policy import TREASURY,USDC_MINT
from marketplace_split import split,key,signature,matches
from marketplace_reconcile import scan
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
    cur.execute("SELECT payer,recipient,reference,created_at,signature,paid_at,issued_at FROM academy_job_payments WHERE job_id=%s",(jid,))
    row=cur.fetchone()
    return {"role":"client" if sid==client else "freelancer","status":status,"mode":mode,"enabled":enabled(),"network":"solana-mainnet","mint":USDC_MINT,"treasury":TREASURY,**split(cents),"recipient":wallet[0] if wallet else None,"invoice":{"payer":row[0],"recipient":row[1],"reference":row[2] if sid==client else None,"created_at":row[3].isoformat(),"signature":row[4],"paid_at":row[5].isoformat() if row[5] else None,"issued":row[6] is not None} if row else None}

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

def request_info(cur,reference,account=None):
    if not enabled(): raise PermissionError("Marketplace payments closed")
    reference=key(reference)
    cur.execute("""SELECT p.job_id,p.payer,p.recipient,p.quote_cents,p.issued_at,p.paid_at,
        p.created_at>now()-interval '15 minutes',p.treasury,j.status,j.payment_mode
        FROM academy_job_payments p JOIN academy_jobs j ON j.id=p.job_id WHERE p.reference=%s""",(reference,))
    row=cur.fetchone()
    if not row or row[4] or row[5] or not row[6] or row[7]!=TREASURY or row[8]!="delivered" or row[9]!="split": raise PermissionError("Request unavailable")
    if account is not None and key(account)!=row[1]: raise PermissionError("Wrong payer")
    return row

def request_transaction(reference,method,b):
    from marketplace_tx import ORIGIN,build
    if method=="GET":
        with transaction() as cur: request_info(cur,reference)
        return {"label":"ZER0LIFE Academy · 95/5 USDC","icon":ORIGIN+"/academy-icon.svg"}
    account=key(b["account"])
    with transaction() as cur: row=request_info(cur,reference,account)
    jid,payer,recipient,cents=row[:4]
    encoded=build(payer,recipient,reference,cents)
    with transaction() as cur:
        # Serialize against revision, acceptance and concurrent issuance.
        cur.execute("SELECT id FROM academy_jobs WHERE id=%s FOR UPDATE",(jid,))
        request_info(cur,reference,account)
        cur.execute("UPDATE academy_job_payments SET issued_at=now() WHERE job_id=%s AND issued_at IS NULL RETURNING job_id",(jid,))
        if not cur.fetchone(): raise ValueError("Request already issued; reconcile before retry")
    return {"transaction":encoded,"message":"USDC payment: 95% freelancer, 5% Zer0Life. Check both recipients and amounts before signing."}

def qr(token,b):
    if not enabled(): raise PermissionError("Marketplace payments closed")
    sid=authenticate(token)
    if sid is None: raise PermissionError()
    jid=ident(b["id"])
    with transaction() as cur:
        p=preview(cur,sid,b)
        if p["role"]!="client" or not p["invoice"]: raise PermissionError()
        reference=p["invoice"]["reference"]
        request_info(cur,reference)
    from marketplace_tx import pay_url
    from io import BytesIO
    from qrcode.image.svg import SvgPathImage
    import qrcode,base64
    url=pay_url(reference);buf=BytesIO()
    qrcode.make(url,image_factory=SvgPathImage).save(buf)
    return {"url":url,"svg_base64":base64.b64encode(buf.getvalue()).decode("ascii")}

def verify_chain(sig,payer,recipient,reference,cents,created):
    rpc=os.getenv("ACADEMY_SOLANA_RPC","https://api.mainnet-beta.solana.com")
    payload={"jsonrpc":"2.0","id":1,"method":"getTransaction","params":[sig,{"encoding":"json","commitment":"finalized","maxSupportedTransactionVersion":0}]}
    with urlopen(Request(rpc,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"}),timeout=12) as response:
        tx=json.load(response).get("result")
    return matches(tx,sig,payer,recipient,reference,cents,created)

def reconcile_rpc(method,params):
    rpc=os.getenv("ACADEMY_SOLANA_RPC","https://api.mainnet-beta.solana.com")
    payload={"jsonrpc":"2.0","id":1,"method":method,"params":params}
    with urlopen(Request(rpc,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"}),timeout=2) as response:
        result=json.load(response)
    if "error" in result or "result" not in result: raise RuntimeError("RPC unavailable")
    return result["result"]

def reconcile(token,b,admin=False):
    if admin:
        from partners import owner
        owner(token)
    else:
        sid=authenticate(token)
        if sid is None: raise PermissionError()
    jid=ident(b["id"])
    with transaction() as cur:
        if not admin: job_info(cur,sid,jid)
        cur.execute("SELECT payer,recipient,reference,quote_cents,issued_at,signature,treasury FROM academy_job_payments WHERE job_id=%s",(jid,))
        row=cur.fetchone()
    if not row or not row[4] or row[6]!=TREASURY: raise ValueError("No issued request")
    # Remains available for existing issued requests even when new payments are closed.
    return scan(reconcile_rpc,*row[:6])

def settle(token,b):
    sid=authenticate(token)
    if sid is None: raise PermissionError()
    jid=ident(b["id"]);sig=signature(b["signature"])
    with transaction() as cur:
        client,worker,status,cents,mode=job_info(cur,sid,jid)
        if sid!=client or mode!="split": raise PermissionError()
        cur.execute("SELECT payer,recipient,reference,quote_cents,issued_at,signature,treasury FROM academy_job_payments WHERE job_id=%s",(jid,))
        row=cur.fetchone()
    if not row: raise ValueError("No invoice")
    payer,recipient,reference,cents,created,previous,treasury=row
    if previous:
        if previous==sig:return {"paid":True}
        raise ValueError("Already paid; do not pay again")
    if created is None or treasury!=TREASURY or status!="delivered" or not verify_chain(sig,payer,recipient,reference,cents,created): raise ValueError("Payment not verified")
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
    cur.execute("SELECT job_id,quote_cents,issued_at,created_at FROM academy_job_payments WHERE paid_at IS NULL ORDER BY created_at DESC LIMIT 100")
    pending=[{"job_id":j,**split(c),"issued_at":i.isoformat() if i else None,"created_at":t.isoformat()} for j,c,i,t in cur.fetchall()]
    return {"pending":pending,"enabled":enabled(),"wallet":TREASURY,"network":"solana-mainnet","paid_count":n,"gross_atomic":str(g),"fee_atomic":str(f),"day_atomic":str(day),"month_atomic":str(month),"year_atomic":str(year),"items":items}

def dispatch(token,action,b):
    if action=="settle": return settle(token,b)
    if action=="qr": return qr(token,b)
    if action=="reconcile": return reconcile(token,b)
    if action=="admin-reconcile": return reconcile(token,b,True)
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

"""Manual payment reconciliation queue. Never sends funds or grants access."""
import re,uuid
from accounts import authenticate
from database import transaction
from partners import owner
from payment_policy import TREASURY
from solana_verify import verify_usdc

def validate(invoice,signature):
    try: invoice=str(uuid.UUID(invoice))
    except (ValueError,TypeError,AttributeError): raise ValueError("Invalid invoice")
    if not isinstance(signature,str) or not re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{64,88}",signature):
        raise ValueError("Invalid signature")
    return invoice,signature

def submit_record(cur,sid,invoice,signature):
    invoice,signature=validate(invoice,signature)
    cur.execute("SELECT id FROM payment_invoices WHERE id=%s AND student_id=%s FOR UPDATE",(invoice,sid))
    if not cur.fetchone(): raise PermissionError("Invoice unavailable")
    cur.execute("SELECT id,status FROM payment_support WHERE invoice_id=%s AND signature=%s",(invoice,signature))
    row=cur.fetchone()
    if row: return {"id":row[0],"status":row[1]}
    cur.execute("SELECT count(*) FROM payment_support WHERE invoice_id=%s",(invoice,))
    if cur.fetchone()[0]>=5: raise ValueError("Ticket limit reached")
    cur.execute("INSERT INTO payment_support(invoice_id,signature) VALUES (%s,%s) RETURNING id",(invoice,signature))
    return {"id":cur.fetchone()[0],"status":"open"}

def submit(token,invoice,signature):
    sid=authenticate(token)
    if sid is None: raise PermissionError("Authentication required")
    with transaction() as cur: return submit_record(cur,sid,invoice,signature)

def items(cur,sid=None,after=0):
    if type(after) is not int or not 0<=after<=9223372036854775807: raise ValueError("Invalid cursor")
    cur.execute("""SELECT t.id,t.invoice_id,t.signature,t.status,t.note,t.created_at,i.plan,i.amount_atomic,i.student_id,i.signature,t.verification,t.checked_at
        FROM payment_support t JOIN payment_invoices i ON i.id=t.invoice_id
        WHERE (%s::bigint IS NULL OR i.student_id=%s) AND t.id>%s ORDER BY t.id LIMIT 51""",(sid,sid,after))
    rows=cur.fetchall()
    out=[{"id":i,"invoice":str(inv),"signature":sig,"status":st,"note":n,"created_at":c.isoformat(),"plan":p,
        "amount_atomic":str(a),"student_id":s,"invoice_signature":isig,"verification":v,"checked_at":checked.isoformat() if checked else None}
        for i,inv,sig,st,n,c,p,a,s,isig,v,checked in rows[:50]]
    return {"items":out,"next_after":out[-1]["id"] if len(rows)>50 else None}

def student_items(token,after):
    sid=authenticate(token)
    if sid is None: raise PermissionError("Authentication required")
    with transaction() as cur: return items(cur,sid,after)

def admin_items(token,after):
    owner(token)
    with transaction() as cur: return items(cur,None,after)

def check(token,ticket):
    admin=owner(token)
    if type(ticket) is not int or ticket<1 or ticket>9223372036854775807: raise ValueError("Invalid ticket")
    with transaction() as cur:
        cur.execute("""SELECT t.signature,i.amount_atomic,i.reference,i.created_at,i.expires_at,i.asset,i.recipient
          FROM payment_support t JOIN payment_invoices i ON i.id=t.invoice_id WHERE t.id=%s""",(ticket,))
        row=cur.fetchone()
    if not row: raise ValueError("Ticket unavailable")
    sig,amount,ref,created,expiry,asset,recipient=row
    # Exact existing invoice verifier, not a claim that a non-matching transfer did not occur.
    verified=asset=="USDC" and recipient==TREASURY and verify_usdc(sig,amount,ref,created,expiry)
    state="matched" if verified else "not_matched"
    with transaction() as cur:
        cur.execute("UPDATE payment_support SET verification=%s,checked_at=now(),checked_by=%s WHERE id=%s",(state,admin,ticket))
    return {"verification":state}

def resolve_record(cur,admin,ticket,note):
    if type(ticket) is not int or not 1<=ticket<=9223372036854775807: raise ValueError("Invalid ticket")
    if not isinstance(note,str) or not 5<=len(note.strip())<=1000 or "\x00" in note: raise ValueError("Resolution note required")
    cur.execute("UPDATE payment_support SET status='closed',note=%s,closed_at=now(),closed_by=%s WHERE id=%s AND status='open' RETURNING id",(note.strip(),admin,ticket))
    if not cur.fetchone(): raise ValueError("Open ticket unavailable")
    return {"closed":True}
def resolve(token,ticket,note):
    admin=owner(token)
    with transaction() as cur: return resolve_record(cur,admin,ticket,note)

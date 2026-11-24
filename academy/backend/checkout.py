import secrets
import uuid
from accounts import authenticate
from database import transaction
from payment_policy import quote,course_amount,PRICES
from referrals import discount_eligible
from solana_pay import payment_url

def reference_key():
    alphabet="123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    raw=secrets.token_bytes(32)
    n=int.from_bytes(raw,"big")
    out=""
    while n:
        n,i=divmod(n,58)
        out=alphabet[i]+out
    return "1"*(len(raw)-len(raw.lstrip(b"\x00")))+out

def create_invoice(token,plan):
    student=authenticate(token)
    if student is None:
        raise PermissionError("Authentication required")
    quote(plan,"USDC")
    ref=reference_key()
    invoice=str(uuid.uuid4())
    with transaction() as cur:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(student,))
        cur.execute("SELECT 1 FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL",(student,))
        if cur.fetchone():
            raise ValueError("Already enrolled")
        cur.execute("SELECT 1 FROM payment_invoices WHERE student_id=%s AND paid_at IS NULL AND expires_at>now()",(student,))
        if cur.fetchone():
            raise ValueError("An active invoice already exists")
        q=quote(plan,"USDC",discount_eligible(cur,student))
        cur.execute("INSERT INTO payment_invoices(id,student_id,plan,asset,amount_atomic,reference,recipient,expires_at) VALUES (%s,%s,%s,'USDC',%s,%s,%s,now()+interval '15 minutes') RETURNING expires_at",(invoice,student,plan,q["amount_atomic"],ref,q["recipient"]))
        expiry=cur.fetchone()[0].isoformat()
        return {"id":invoice,"expires_at":expiry,"url":payment_url(plan,ref,q["amount_atomic"]),"amount_atomic":q["amount_atomic"]}

def active_invoice(token):
    student=authenticate(token)
    if student is None:
        raise PermissionError("Authentication required")
    with transaction() as cur:
        cur.execute("SELECT id,plan,reference,amount_atomic,expires_at FROM payment_invoices WHERE student_id=%s AND paid_at IS NULL AND expires_at>now() ORDER BY created_at DESC LIMIT 1",(student,))
        row=cur.fetchone()
    if not row:
        return {"invoice":None}
    invoice,plan,ref,amount,expiry=row
    return {"invoice":{"id":str(invoice),"url":payment_url(plan,ref,amount),"amount_atomic":amount,"expires_at":expiry.isoformat()}}

def prices(token):
    student=authenticate(token)
    if student is None: raise PermissionError("Authentication required")
    with transaction() as cur:
        discount=discount_eligible(cur,student)
    return {"discount_percent":5 if discount else 0,"prices":{p:course_amount(p,discount) for p in PRICES}}

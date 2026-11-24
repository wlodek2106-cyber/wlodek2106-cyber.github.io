"""Manual, single-tier partner commissions; no automatic transfers or custody."""
import os
from accounts import authenticate
from database import transaction
from urllib.parse import urlsplit
from referrals import overview
ALPHABET="123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def base58_valid(s,size):
    if not isinstance(s,str) or not 1<=len(s)<=90 or any(c not in ALPHABET for c in s): return False
    n=0
    for c in s: n=n*58+ALPHABET.index(c)
    return (n.bit_length()+7)//8+len(s)-len(s.lstrip("1"))==size
def commission(amount):
    if type(amount) is not int or amount<=0: raise ValueError("Invalid amount")
    return amount*30//100
def user(token):
    sid=authenticate(token)
    if sid is None: raise PermissionError("Sign in required")
    return sid
def owner(token):
    sid=user(token)
    # Numeric, explicitly provisioned owner identity; never trust self-registered email alone.
    if os.getenv("ACADEMY_ADMIN_ENABLED")!="true" or str(sid) not in {x.strip() for x in os.getenv("ACADEMY_PARTNER_ADMIN_IDS","").split(",") if x.strip()}:
        raise PermissionError("Partner administrator required")
    return sid
def apply(token,profile,wallet,consent):
    sid=user(token)
    if not isinstance(profile,str) or len(profile)>500 or consent is not True or not base58_valid(wallet,32):
        raise ValueError("Valid profile, Solana wallet and consent required")
    url=urlsplit(profile.strip())
    if url.scheme!="https" or not url.hostname or url.username or url.password: raise ValueError("HTTPS social profile required")
    with transaction() as cur:
        cur.execute("""INSERT INTO influencer_partners(student_id,profile_url,wallet) VALUES (%s,%s,%s)
        ON CONFLICT(student_id) DO NOTHING RETURNING student_id""",(sid,profile.strip(),wallet))
        if not cur.fetchone(): raise ValueError("Application already exists")
    return {"status":"pending"}
SALES="""SELECT i.id,i.plan,i.amount_atomic,i.paid_at,p.id,p.status
FROM influencer_partners a JOIN referrals r ON r.referrer_id=a.student_id
JOIN payment_invoices i ON i.student_id=r.student_id AND i.asset='USDC' AND i.paid_at IS NOT NULL
JOIN enrollments e ON e.student_id=r.student_id AND e.payment_signature=i.signature AND e.paid_at IS NOT NULL
LEFT JOIN influencer_payouts p ON p.invoice_id=i.id
WHERE a.student_id=%s AND a.status='approved' AND r.created_at>=a.approved_at AND i.paid_at>=a.approved_at"""
def dashboard(token):
    sid=user(token)
    with transaction() as cur:
        cur.execute("SELECT status,profile_url,wallet FROM influencer_partners WHERE student_id=%s",(sid,))
        a=cur.fetchone()
        if not a: return {"status":"not_applied","sales":[]}
        cur.execute(SALES+" ORDER BY i.paid_at DESC LIMIT 200",(sid,))
        sales=[{"invoice":str(i),"plan":pl,"amount_atomic":amt,"commission_atomic":commission(amt),"date":t.isoformat(),"request_id":pid,"status":status or "available"} for i,pl,amt,t,pid,status in cur.fetchall()]
    return {"status":a[0],"profile":a[1],"wallet":a[2],"sales":sales,"code":overview(token)["code"] if a[0]=="approved" else None}
def request(token,invoice):
    sid=user(token)
    with transaction() as cur:
        cur.execute("SELECT wallet FROM influencer_partners WHERE student_id=%s AND status='approved' FOR UPDATE",(sid,))
        row=cur.fetchone()
        if not row: raise PermissionError("Approved partner required")
        cur.execute(SALES+" AND i.id=%s",(sid,invoice))
        sale=cur.fetchone()
        if not sale: raise PermissionError("Eligible sale required")
        cur.execute("""INSERT INTO influencer_payouts(invoice_id,partner_id,amount_atomic,wallet)
        VALUES (%s,%s,%s,%s) ON CONFLICT(invoice_id) DO NOTHING RETURNING id""",(invoice,sid,commission(sale[2]),row[0]))
        inserted=cur.fetchone()
        if not inserted: raise ValueError("Already requested")
    return {"id":inserted[0],"status":"pending"}
def queue(token):
    owner(token)
    with transaction() as cur:
        cur.execute("SELECT student_id,profile_url,wallet,status FROM influencer_partners ORDER BY created_at DESC LIMIT 200")
        apps=[{"id":i,"profile":u,"wallet":w,"status":s} for i,u,w,s in cur.fetchall()]
        cur.execute("""SELECT p.id,p.invoice_id,p.partner_id,p.amount_atomic,p.wallet,p.status,p.payout_signature,i.signature
        FROM influencer_payouts p JOIN payment_invoices i ON i.id=p.invoice_id ORDER BY p.created_at DESC LIMIT 200""")
        payouts=[{"id":i,"invoice":str(inv),"partner":sid,"amount_atomic":n,"wallet":w,"status":s,"payout_signature":sig,"sale_signature":sale} for i,inv,sid,n,w,s,sig,sale in cur.fetchall()]
    return {"applications":apps,"payouts":payouts}
def decide(token,kind,identifier,action,signature=None):
    admin=owner(token)
    if type(identifier) is not int or identifier<1: raise ValueError("Invalid identifier")
    with transaction() as cur:
        if kind=="application" and action in ("approve","reject"):
            cur.execute("""UPDATE influencer_partners SET status=%s,reviewed_by=%s,approved_at=CASE WHEN %s='approve' THEN now() ELSE NULL END
            WHERE student_id=%s AND status='pending'""",("approved" if action=="approve" else "rejected",admin,action,identifier))
        elif kind=="payout" and action in ("approve","reject"):
            cur.execute("UPDATE influencer_payouts SET status=%s,reviewed_by=%s,reviewed_at=now() WHERE id=%s AND status='pending'",("approved" if action=="approve" else "rejected",admin,identifier))
        elif kind=="payout" and action=="mark_paid":
            if not base58_valid(signature,64): raise ValueError("Solana transaction signature required")
            cur.execute("""UPDATE influencer_payouts SET status='paid',payout_signature=%s,paid_at=now(),paid_by=%s
            WHERE id=%s AND status='approved' AND NOT EXISTS(SELECT 1 FROM payment_invoices WHERE signature=%s)""",(signature,admin,identifier,signature))
        else: raise ValueError("Invalid action")
        if cur.rowcount!=1: raise ValueError("Invalid state transition")
    return {"updated":True}

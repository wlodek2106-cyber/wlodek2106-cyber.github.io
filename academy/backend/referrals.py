"""Private referral attribution; no commission, payout or financial promise."""
import re,secrets

def normalize(code):
    if code is None or code=="": return None
    if not isinstance(code,str) or not re.fullmatch(r"[0-9a-f]{24}",code):
        raise ValueError("Invalid referral code")
    return code

def attribute(cur,student,code):
    if not code: return
    cur.execute("SELECT student_id FROM referral_codes WHERE code=%s",(code,))
    row=cur.fetchone()
    if row and row[0]!=student:
        cur.execute("INSERT INTO referrals(student_id,referrer_id) VALUES (%s,%s) ON CONFLICT(student_id) DO NOTHING",(student,row[0]))

def overview(token):
    from accounts import authenticate
    from database import transaction
    student=authenticate(token)
    if student is None: raise PermissionError("Sign in required")
    with transaction() as cur:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(student,))
        cur.execute("SELECT code FROM referral_codes WHERE student_id=%s",(student,))
        row=cur.fetchone()
        if not row:
            code=secrets.token_hex(12)
            cur.execute("INSERT INTO referral_codes(student_id,code) VALUES (%s,%s)",(student,code))
        else: code=row[0]
        cur.execute("""SELECT count(*),count(*) FILTER (WHERE e.paid_at IS NOT NULL)
            FROM referrals r LEFT JOIN enrollments e ON e.student_id=r.student_id WHERE r.referrer_id=%s""",(student,))
        invited,paid=cur.fetchone()
    return {"code":code,"registered":invited,"paid":paid,"commissions_enabled":False}

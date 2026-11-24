import re
from database import transaction
from security import hash_password, verify_password, new_session, session_digest

def register(email,password,first_name=None,last_name=None,referral=None):
    from referrals import normalize,attribute
    referral=normalize(referral)
    if first_name is not None or last_name is not None:
        if not all(isinstance(n,str) and 1<=len(n.strip())<=100 and n.isprintable() for n in (first_name,last_name)):
            raise ValueError('Invalid name')
        first_name,last_name=first_name.strip(),last_name.strip()
    email=email.strip().lower()
    if len(email)>254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",email):
        raise ValueError("Invalid email")
    hashed=hash_password(password)
    with transaction() as cur:
        cur.execute("INSERT INTO students(email,password_hash,first_name,last_name) VALUES (%s,%s,%s,%s) ON CONFLICT(email) DO NOTHING RETURNING id",(email,hashed,first_name,last_name))
        row=cur.fetchone()
        if not row:
            raise ValueError("Registration unavailable")
        attribute(cur,row[0],referral)
        return row[0]

def login(email,password):
    with transaction() as cur:
        cur.execute("SELECT id,password_hash FROM students WHERE email=%s",(email.strip().lower(),))
        row=cur.fetchone()
        if not row or not verify_password(password,row[1]):
            raise ValueError("Invalid credentials")
        token,digest=new_session()
        cur.execute("INSERT INTO student_sessions(token_digest,student_id,expires_at) VALUES (%s,%s,now()+interval '12 hours')",(digest,row[0]))
        return token

def authenticate(token):
    if not isinstance(token,str) or len(token)>128:
        return None
    with transaction() as cur:
        cur.execute("SELECT student_id FROM student_sessions WHERE token_digest=%s AND revoked_at IS NULL AND expires_at>now()",(session_digest(token),))
        row=cur.fetchone()
        return row[0] if row else None

def logout(token):
    with transaction() as cur:
        cur.execute("UPDATE student_sessions SET revoked_at=now() WHERE token_digest=%s",(session_digest(token),))
# HTTP integration must enforce TLS, request limits, rate limiting and email verification.

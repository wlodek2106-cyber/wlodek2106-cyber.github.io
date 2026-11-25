import re
from database import transaction
from security import hash_password, verify_password, new_session, session_digest

def register(email,password,first_name=None,last_name=None,referral=None,hire_source=None,campaign_source=None):
    from referrals import normalize,attribute
    referral=normalize(referral)
    from acquisition import normalize as normalize_source
    hire_source=normalize_source(hire_source)
    campaign_source=normalize_source(campaign_source)
    if first_name is not None or last_name is not None:
        if not all(isinstance(n,str) and 1<=len(n.strip())<=100 and n.isprintable() for n in (first_name,last_name)):
            raise ValueError('Invalid name')
        first_name,last_name=first_name.strip(),last_name.strip()
    email=email.strip().lower()
    if len(email)>254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",email):
        raise ValueError("Invalid email")
    hashed=hash_password(password)
    with transaction() as cur:
        cur.execute("INSERT INTO students(email,password_hash,first_name,last_name,hire_source,campaign_source) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT(email) DO NOTHING RETURNING id",(email,hashed,first_name,last_name,hire_source,campaign_source))
        row=cur.fetchone()
        if not row:
            raise ValueError("Registration unavailable")
        sid=row[0]
        stem=re.sub(r"[^A-Za-z0-9]+","-",f"{first_name or ''}-{last_name or ''}").lower()[:28].strip("-")
        username="zer0life" if sid==24 else (stem or "member")+"-"+str(sid)
        cur.execute("UPDATE students SET username=%s WHERE id=%s",(username,sid))
        attribute(cur,sid,referral)
        return row[0]

def login(email,password,code=None):
    with transaction() as cur:
        identifier=email.strip().lower()
        if "@" in identifier and not identifier.startswith("@"):
            cur.execute("SELECT id,password_hash FROM students WHERE email=%s FOR UPDATE",(identifier,))
        else:
            cur.execute("SELECT id,password_hash FROM students WHERE username=%s FOR UPDATE",(identifier.removeprefix("@"),))
        row=cur.fetchone()
        if not row or not verify_password(password,row[1]):
            raise ValueError("Invalid credentials")
        verify_mfa(cur,row[0],code)
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

def change_password(token,current_password,new_password,code=None):
    if not isinstance(token,str) or len(token)>128:
        raise PermissionError("Authentication required")
    if current_password==new_password:
        raise ValueError("Choose a different password")
    new_hash=hash_password(new_password)
    with transaction() as cur:
        cur.execute("SELECT student_id FROM student_sessions WHERE token_digest=%s AND revoked_at IS NULL AND expires_at>now()",(session_digest(token),))
        row=cur.fetchone()
        if not row: raise PermissionError("Authentication required")
        student=row[0]
        cur.execute("SELECT password_hash FROM students WHERE id=%s FOR UPDATE",(student,))
        row=cur.fetchone()
        if not row or not verify_password(current_password,row[0]):
            raise PermissionError("Invalid credentials")
        cur.execute("SELECT 1 FROM student_sessions WHERE token_digest=%s AND revoked_at IS NULL AND expires_at>now()",(session_digest(token),))
        if not cur.fetchone(): raise PermissionError("Session expired")
        verify_mfa(cur,student,code)
        cur.execute("UPDATE students SET password_hash=%s WHERE id=%s",(new_hash,student))
        cur.execute("DELETE FROM student_passkeys WHERE student_id=%s",(student,))
        cur.execute("DELETE FROM passkey_challenges WHERE student_id=%s",(student,))
        cur.execute("UPDATE student_sessions SET revoked_at=now() WHERE student_id=%s AND revoked_at IS NULL",(student,))
    return {"changed":True,"sign_in_required":True}

def logout(token):
    with transaction() as cur:
        cur.execute("UPDATE student_sessions SET revoked_at=now() WHERE token_digest=%s",(session_digest(token),))
# HTTP integration must enforce TLS, request limits, rate limiting and email verification.

def verify_mfa(cur,student,code):
    from mfa import consume
    cur.execute("SELECT secret,last_counter,recovery_digests FROM student_mfa WHERE student_id=%s FOR UPDATE",(student,))
    row=cur.fetchone()
    if row and row[0]:
        last,digests=consume(*row,code)
        cur.execute("UPDATE student_mfa SET last_counter=%s,recovery_digests=%s WHERE student_id=%s",(last,digests,student))

def mfa_status(token):
    student=authenticate(token)
    if student is None: raise PermissionError("Authentication required")
    with transaction() as cur:
        cur.execute("SELECT secret IS NOT NULL,cardinality(recovery_digests) FROM student_mfa WHERE student_id=%s",(student,))
        row=cur.fetchone()
    return {"enabled":bool(row and row[0]),"recovery_remaining":row[1] if row else 0}

def lock_account(cur,token,password):
    if not isinstance(token,str) or len(token)>128: raise PermissionError("Authentication required")
    digest=session_digest(token)
    cur.execute("SELECT s.id,s.email,s.password_hash FROM students s JOIN student_sessions t ON t.student_id=s.id WHERE t.token_digest=%s AND t.revoked_at IS NULL AND t.expires_at>now() FOR UPDATE OF s",(digest,))
    row=cur.fetchone()
    if not row or not verify_password(password,row[2]): raise PermissionError("Invalid credentials")
    cur.execute("SELECT 1 FROM student_sessions WHERE token_digest=%s AND revoked_at IS NULL AND expires_at>now()",(digest,))
    if not cur.fetchone(): raise PermissionError("Session expired")
    return row[:2]

def mfa_begin(token,password):
    from mfa import new_secret,uri
    with transaction() as cur:
        student,email=lock_account(cur,token,password)
        cur.execute("SELECT secret FROM student_mfa WHERE student_id=%s",(student,))
        row=cur.fetchone()
        if row and row[0]: raise ValueError("Already enabled")
        secret=new_secret()
        cur.execute("""INSERT INTO student_mfa(student_id,pending_secret,pending_until) VALUES (%s,%s,now()+interval '10 minutes')
            ON CONFLICT(student_id) DO UPDATE SET pending_secret=EXCLUDED.pending_secret,pending_until=EXCLUDED.pending_until""",(student,secret))
    return {"secret":secret,"uri":uri(secret,email),"expires_minutes":10}

def mfa_confirm(token,password,code):
    from mfa import check,new_recovery,recovery_digest
    with transaction() as cur:
        student,_=lock_account(cur,token,password)
        cur.execute("SELECT pending_secret FROM student_mfa WHERE student_id=%s AND secret IS NULL AND pending_until>now() FOR UPDATE",(student,))
        row=cur.fetchone()
        if not row: raise ValueError("Setup expired")
        counter=check(row[0],code)
        if counter is None: raise ValueError("Invalid authenticator code")
        recovery=new_recovery()
        cur.execute("""UPDATE student_mfa SET secret=pending_secret,last_counter=%s,recovery_digests=%s,pending_secret=NULL,pending_until=NULL WHERE student_id=%s""",(counter,[recovery_digest(x) for x in recovery],student))
        cur.execute("UPDATE student_sessions SET revoked_at=now() WHERE student_id=%s AND revoked_at IS NULL",(student,))
    return {"enabled":True,"recovery_codes":recovery,"sign_in_required":True}

def mfa_disable(token,password,code):
    with transaction() as cur:
        student,_=lock_account(cur,token,password)
        cur.execute("SELECT secret FROM student_mfa WHERE student_id=%s",(student,))
        row=cur.fetchone()
        if not row or not row[0]: raise ValueError("Not enabled")
        verify_mfa(cur,student,code)
        cur.execute("DELETE FROM student_mfa WHERE student_id=%s",(student,))
        cur.execute("UPDATE student_sessions SET revoked_at=now() WHERE student_id=%s AND revoked_at IS NULL",(student,))
    return {"enabled":False,"sign_in_required":True}

def profile(token):
    from learning import owner_preview
    sid=authenticate(token)
    if sid is None: raise PermissionError("Sign in required")
    with transaction() as cur:
        cur.execute("""SELECT s.first_name,s.last_name,s.username,e.plan,
            EXISTS(SELECT 1 FROM payment_invoices i WHERE i.student_id=s.id
            AND i.signature=e.payment_signature AND i.asset='USDC' AND i.paid_at IS NOT NULL AND e.paid_at IS NOT NULL)
            FROM students s LEFT JOIN enrollments e ON e.student_id=s.id WHERE s.id=%s""",(sid,))
        row=cur.fetchone()
    if not row: raise PermissionError("Sign in required")
    first,last,username,plan,paid=row
    return {"id":sid,"name":" ".join(x for x in (first,last) if x) or username or "Member",
        "username":username,"badge":"owner" if owner_preview(sid) else "paid" if paid else None,
        "paid_plan":plan if paid else None}

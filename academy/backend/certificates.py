import secrets
from accounts import authenticate
from database import transaction

def issue_certificate(token):
    student=authenticate(token)
    if student is None:
        raise PermissionError("Authentication required")
    with transaction() as cur:
        cur.execute("SELECT id FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL FOR UPDATE",(student,))
        row=cur.fetchone()
        if not row:
            raise PermissionError("Paid enrollment required")
        eid=row[0]
        cur.execute("SELECT count(*) FROM lesson_progress WHERE enrollment_id=%s AND score>=80",(eid,))
        if cur.fetchone()[0]!=30:
            raise PermissionError("Complete all 30 lessons")
        cur.execute("INSERT INTO certificates(enrollment_id,verification_code) VALUES (%s,%s) ON CONFLICT(enrollment_id) DO NOTHING",(eid,secrets.token_urlsafe(24)))
        cur.execute("SELECT verification_code,issued_at FROM certificates WHERE enrollment_id=%s",(eid,))
        code,issued=cur.fetchone()
        return {"code":code,"issued_at":issued.isoformat(),"program":"AI Creator Professional Program"}
def verify_certificate(code):
    with transaction() as cur:
        cur.execute("SELECT issued_at FROM certificates WHERE verification_code=%s",(code,))
        row=cur.fetchone()
        return {"valid":bool(row),"issued_at":row[0].isoformat() if row else None}

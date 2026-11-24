import secrets
from accounts import authenticate
from database import transaction

def issue_completed(cur,eid):
    cur.execute("""SELECT s.first_name,s.last_name,max(p.passed_at),count(p.lesson)
        FROM enrollments e JOIN students s ON s.id=e.student_id
        JOIN lesson_progress p ON p.enrollment_id=e.id
        WHERE e.id=%s AND e.paid_at IS NOT NULL AND p.score>=80
        GROUP BY s.first_name,s.last_name""",(eid,))
    row=cur.fetchone()
    if not row or row[3]!=30 or not row[0] or not row[1]:
        return None
    name=row[0]+" "+row[1]
    cur.execute("INSERT INTO certificates(enrollment_id,verification_code,issued_at,recipient_name) VALUES (%s,%s,%s,%s) ON CONFLICT(enrollment_id) DO NOTHING",(eid,secrets.token_urlsafe(24),row[2],name))
    cur.execute("UPDATE certificates SET recipient_name=%s,issued_at=%s WHERE enrollment_id=%s AND recipient_name IS NULL",(name,row[2],eid))
    cur.execute("INSERT INTO certificate_email_outbox(enrollment_id) VALUES (%s) ON CONFLICT DO NOTHING",(eid,))
    cur.execute("SELECT verification_code,issued_at,recipient_name FROM certificates WHERE enrollment_id=%s",(eid,))
    code,issued,recipient=cur.fetchone()
    return {"code":code,"issued_at":issued.isoformat(),"recipient_name":recipient,"program":"AI Creator Professional Program"}

def issue_certificate(token):
    student=authenticate(token)
    if student is None:
        raise PermissionError("Authentication required")
    with transaction() as cur:
        cur.execute("SELECT id FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL FOR UPDATE",(student,))
        row=cur.fetchone()
        result=issue_completed(cur,row[0]) if row else None
        if not result:
            raise PermissionError("Complete all 30 lessons and provide your name")
        return result

def verify_certificate(code):
    with transaction() as cur:
        cur.execute("SELECT issued_at FROM certificates WHERE verification_code=%s",(code,))
        row=cur.fetchone()
        return {"valid":bool(row),"issued_at":row[0].isoformat() if row else None}

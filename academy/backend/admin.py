import os
from accounts import authenticate
from database import transaction

def statistics(token):
    student=authenticate(token)
    if student is None:
        raise PermissionError("Authentication required")
    allowed={s.strip().lower() for s in os.getenv("ACADEMY_ADMIN_EMAILS","").split(",") if s.strip()}
    with transaction() as cur:
        cur.execute("SELECT email FROM students WHERE id=%s",(student,))
        row=cur.fetchone()
        if not row or row[0].lower() not in allowed:
            raise PermissionError("Administrator required")
        result={}
        for name,query in (
            ("students","SELECT count(*) FROM students"),
            ("paid_enrollments","SELECT count(*) FROM enrollments WHERE paid_at IS NOT NULL"),
            ("completed_lessons","SELECT count(*) FROM lesson_progress"),
            ("exam_attempts","SELECT count(*) FROM quiz_attempts"),
            ("certificates","SELECT count(*) FROM certificates")):
            cur.execute(query)
            result[name]=cur.fetchone()[0]
        cur.execute("SELECT plan,count(*) FROM enrollments WHERE paid_at IS NOT NULL GROUP BY plan")
        result["plans"]=dict(cur.fetchall())
        return result
# Admin allowlist must remain empty until owner identity and email verification are configured.

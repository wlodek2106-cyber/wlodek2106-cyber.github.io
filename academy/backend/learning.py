from database import transaction
from accounts import authenticate
from progression import eligible
from datetime import datetime, timezone

def student_progress(token):
    student=authenticate(token)
    if student is None:
        raise PermissionError("Authentication required")
    with transaction() as cur:
        cur.execute("SELECT id,plan,paid_at FROM enrollments WHERE student_id=%s",(student,))
        enrollment=cur.fetchone()
        if not enrollment:
            return {"paid":False,"lessons":[{"day":n,"unlocked":False,"completed":False} for n in range(1,31)]}
        eid,plan,paid=enrollment
        cur.execute("SELECT lesson,passed_at FROM lesson_progress WHERE enrollment_id=%s",(eid,))
        passed=dict(cur.fetchall())
        now=datetime.now(timezone.utc)
        return {"paid":paid is not None,"plan":plan,"lessons":[{"day":n,"unlocked":eligible(n,paid,passed,now),"completed":n in passed} for n in range(1,31)]}

def require_lesson(token,day):
    if type(day) is not int or not 1<=day<=30:
        raise ValueError("Invalid lesson")
    progress=student_progress(token)
    if not progress["lessons"][day-1]["unlocked"]:
        raise PermissionError("Lesson locked")
    return True

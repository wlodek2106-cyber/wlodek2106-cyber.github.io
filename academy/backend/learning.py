from database import transaction
from accounts import authenticate
from progression import eligible
from datetime import datetime, timezone
import os

def owner_preview(student):
    # Complimentary QA access is limited to the explicitly provisioned account.
    # Never use a client-supplied ID, email, or payment marker as authorization.
    return (student == 24 and os.getenv("ACADEMY_ADMIN_ENABLED") == "true"
            and str(student) in {x.strip() for x in os.getenv("ACADEMY_PARTNER_ADMIN_IDS","").split(",") if x.strip()})

def ensure_preview_enrollment(cur, student):
    if not owner_preview(student):
        raise PermissionError("Owner preview required")
    # No paid_at, payment_signature, invoice or financial event is created.
    cur.execute("INSERT INTO enrollments(student_id,plan) VALUES (%s,'elite') ON CONFLICT(student_id) DO NOTHING",(student,))

def student_progress(token):
    student=authenticate(token)
    if student is None:
        raise PermissionError("Authentication required")
    preview=owner_preview(student)
    with transaction() as cur:
        cur.execute("SELECT id,plan,paid_at FROM enrollments WHERE student_id=%s",(student,))
        enrollment=cur.fetchone()
        if not enrollment:
            return {"paid":False,"access":preview,"owner_preview":preview,
                    **({"plan":"elite"} if preview else {}),
                    "lessons":[{"day":n,"unlocked":preview,"completed":False} for n in range(1,46 if preview else 31)]}
        eid,plan,paid=enrollment
        cur.execute("SELECT lesson,passed_at FROM lesson_progress WHERE enrollment_id=%s",(eid,))
        passed=dict(cur.fetchall())
        now=datetime.now(timezone.utc)
        return {"paid":paid is not None,"access":preview or paid is not None,"owner_preview":preview,
                "plan":"elite" if preview else plan,
                "lessons":[{"day":n,"unlocked":preview or eligible(n,paid,passed,now,plan),"completed":n in passed} for n in range(1,46 if preview or plan in ('vip','elite') else 31)]}

def require_lesson(token,day):
    if type(day) is not int or not 1<=day<=45:
        raise ValueError("Invalid lesson")
    progress=student_progress(token)
    if day>len(progress["lessons"]) or not progress["lessons"][day-1]["unlocked"]:
        raise PermissionError("Lesson locked")
    return True

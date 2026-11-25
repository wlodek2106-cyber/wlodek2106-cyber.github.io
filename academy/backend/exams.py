from datetime import datetime, timezone
from psycopg.types.json import Jsonb
from database import transaction
from accounts import authenticate
from progression import eligible
from learning import owner_preview, ensure_preview_enrollment
from assessment import prepare_attempt, grade_attempt

def enrollment(cur, token, day):
    student=authenticate(token)
    if student is None or type(day) is not int or not 1<=day<=45:
        raise PermissionError("Access denied")
    preview=owner_preview(student)
    if preview:
        ensure_preview_enrollment(cur,student)
    cur.execute("SELECT id,paid_at,plan FROM enrollments WHERE student_id=%s FOR UPDATE",(student,))
    row=cur.fetchone()
    if not row:
        raise PermissionError("Enrollment required")
    eid,paid,plan=row
    cur.execute("SELECT lesson,passed_at FROM lesson_progress WHERE enrollment_id=%s",(eid,))
    passed=dict(cur.fetchall())
    if day in passed or (not preview and not eligible(day,paid,passed,datetime.now(timezone.utc),plan)):
        raise PermissionError("Lesson locked or completed")
    return eid

def start_exam(token,day,bank):
    with transaction() as cur:
        eid=enrollment(cur,token,day)
        public,key=prepare_attempt(bank)
        cur.execute("UPDATE assessment_sessions SET consumed_at=now() WHERE enrollment_id=%s AND lesson=%s AND consumed_at IS NULL",(eid,day))
        cur.execute("INSERT INTO assessment_sessions(id,enrollment_id,lesson,answer_key,expires_at) VALUES (%s,%s,%s,%s,now()+interval '1 hour')",(public["attempt_id"],eid,day,Jsonb(key)))
        return public

def submit_exam(token,day,attempt_id,answers):
    with transaction() as cur:
        eid=enrollment(cur,token,day)
        cur.execute("SELECT answer_key FROM assessment_sessions WHERE id=%s AND enrollment_id=%s AND lesson=%s AND consumed_at IS NULL AND expires_at>now() FOR UPDATE",(attempt_id,eid,day))
        row=cur.fetchone()
        if not row:
            raise PermissionError("Attempt unavailable")
        result=grade_attempt(answers,row[0])
        cur.execute("UPDATE assessment_sessions SET consumed_at=now() WHERE id=%s",(attempt_id,))
        cur.execute("INSERT INTO quiz_attempts(enrollment_id,lesson,score) VALUES (%s,%s,%s)",(eid,day,result["score"]))
        if result["passed"]:
            cur.execute("INSERT INTO lesson_progress(enrollment_id,lesson,score) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",(eid,day,result["score"]))
            cur.execute("SELECT passed_at+interval '1 day' FROM lesson_progress WHERE enrollment_id=%s AND lesson=%s",(eid,day))
            result["next_unlock_at"]=cur.fetchone()[0].isoformat() if day<45 and (day!=30 or cur.execute("SELECT plan FROM enrollments WHERE id=%s",(eid,)).fetchone()[0] in ("vip","elite")) else None
            if day in (30,45) and not owner_preview(authenticate(token)):
                from certificates import issue_completed
                result["certificate"]=issue_completed(cur,eid)
        return result
# Bank must be supplied by trusted server-side storage, never by the student.

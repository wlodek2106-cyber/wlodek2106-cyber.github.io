from accounts import authenticate
from database import transaction
from learning import require_lesson

def save(token,day,submission):
    require_lesson(token,day)
    student=authenticate(token)
    if not student: raise PermissionError("Authentication required")
    if not isinstance(submission,str) or not 1<=len(submission.strip())<=8000:
        raise ValueError("Submission must contain 1–8000 characters")
    with transaction() as cur:
        cur.execute("SELECT id FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL FOR UPDATE",(student,))
        row=cur.fetchone()
        if not row: raise PermissionError("Enrollment required")
        eid=row[0]
        cur.execute("SELECT count(*) FROM project_submissions WHERE enrollment_id=%s AND lesson=%s",(eid,day))
        if cur.fetchone()[0]>=10: raise ValueError("Maximum 10 submissions per lesson")
        cur.execute("INSERT INTO project_submissions(enrollment_id,lesson,submission) VALUES (%s,%s,%s) RETURNING id",(eid,day,submission.strip()))
        return {"id":cur.fetchone()[0],"status":"submitted"}

def list_projects(token):
    student=authenticate(token)
    if not student: raise PermissionError("Authentication required")
    with transaction() as cur:
        cur.execute("SELECT p.id,p.lesson,p.submission,p.submitted_at,p.score,p.feedback FROM project_submissions p JOIN enrollments e ON e.id=p.enrollment_id WHERE e.student_id=%s ORDER BY p.id DESC LIMIT 300",(student,))
        return {"items":[{"id":r[0],"lesson":r[1],"submission":r[2],"submitted_at":r[3].isoformat(),"score":r[4],"feedback":r[5]} for r in cur.fetchall()]}

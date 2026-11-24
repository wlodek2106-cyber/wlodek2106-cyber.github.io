"""Achievements derived from verified progress, not self-awarded counters."""
def calculate(lessons, scores, project_count):
    done=sum(x["completed"] for x in lessons)
    total=len(lessons)
    perfect=sum(s==100 for s in scores)
    targets=[("first_lesson",done,1),("five_lessons",done,5),("ten_lessons",done,10),
             ("half_course",done,(total+1)//2),("perfect_exam",perfect,1),
             ("five_perfect",perfect,5),("first_project",project_count,1),
             ("three_projects",project_count,3),("course_complete",done,total)]
    if total==45:
        targets.extend([("website_complete",done,35),("app_complete",done,40),("agent_complete",done,45)])
    return {"completed":done,"total":total,"project_count":project_count,
            "achievements":[{"id":k,"progress":min(v,t),"target":t,"earned":v>=t} for k,v,t in targets if t>0]}

def student_achievements(token):
    from accounts import authenticate
    from database import transaction
    from learning import student_progress
    student=authenticate(token)
    if student is None: raise PermissionError("Sign in required")
    p=student_progress(token)
    if not p["paid"]: raise PermissionError("Paid enrollment required")
    with transaction() as cur:
        cur.execute("""SELECT p.score FROM lesson_progress p JOIN enrollments e ON e.id=p.enrollment_id
            WHERE e.student_id=%s AND e.paid_at IS NOT NULL""",(student,))
        scores=[r[0] for r in cur.fetchall()]
        cur.execute("""SELECT count(*) FROM project_submissions p JOIN enrollments e ON e.id=p.enrollment_id
            WHERE e.student_id=%s AND e.paid_at IS NOT NULL""",(student,))
        count=cur.fetchone()[0]
    return calculate(p["lessons"],scores,count)

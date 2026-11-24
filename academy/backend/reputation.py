"""Order-linked reviews and consent-based applicant reputation. No payment verification."""
from student_business import clean,ident

def stats(cur,sid):
    cur.execute("""SELECT count(*) FROM academy_jobs j JOIN academy_job_applications a
        ON a.job_id=j.id AND a.id=j.selected_application WHERE a.student_id=%s AND j.status='completed'""",(sid,))
    completed=cur.fetchone()[0]
    cur.execute("""SELECT count(*),avg(r.rating) FROM academy_job_reviews r
        JOIN academy_jobs j ON j.id=r.job_id JOIN academy_job_applications a ON a.job_id=j.id AND a.id=j.selected_application
        WHERE a.student_id=%s AND j.status='completed' AND r.status='approved'""",(sid,))
    n,avg=cur.fetchone()
    cur.execute("""SELECT count(p.lesson),EXISTS(SELECT 1 FROM certificates c JOIN enrollments e2 ON e2.id=c.enrollment_id WHERE e2.student_id=%s AND e2.paid_at IS NOT NULL)
        FROM enrollments e LEFT JOIN lesson_progress p ON p.enrollment_id=e.id AND p.score>=80
        WHERE e.student_id=%s AND e.paid_at IS NOT NULL""",(sid,sid))
    lessons,cert=cur.fetchone()
    return {"completed_orders":completed,"review_count":n,"rating":round(float(avg),2) if avg is not None else None,"completed_lessons":lessons,"certificate_issued":bool(cert)}

def submit(cur,sid,b):
    jid=ident(b["id"]); rating=b["rating"]
    if type(rating) is not int or not 1<=rating<=5 or b.get("consent") is not True: raise ValueError("Invalid rating or consent")
    comment=clean(b.get("comment",""),1000)
    cur.execute("SELECT client_id,status,selected_application FROM academy_jobs WHERE id=%s FOR UPDATE",(jid,))
    row=cur.fetchone()
    if not row or row[0]!=sid or row[1]!="completed" or not row[2]: raise PermissionError("Completed client order required")
    cur.execute("""INSERT INTO academy_job_reviews(job_id,rating,comment) VALUES (%s,%s,%s)
        ON CONFLICT(job_id) DO NOTHING RETURNING job_id""",(jid,rating,comment))
    if not cur.fetchone(): raise ValueError("Review already submitted")
    return {"status":"pending"}

def own(cur,sid,b):
    from job_board import cursor
    cur.execute("""SELECT j.id,j.title,r.rating,r.comment,r.status FROM academy_jobs j
        JOIN academy_job_applications a ON a.job_id=j.id AND a.id=j.selected_application
        LEFT JOIN academy_job_reviews r ON r.job_id=j.id
        WHERE a.student_id=%s AND j.status='completed' AND j.id>%s ORDER BY j.id LIMIT 31""",(sid,cursor(b)))
    rows=cur.fetchall()
    items=[{"id":i,"title":t,"rating":n if s=="approved" else None,"comment":c if s=="approved" else None,"review_status":"approved" if s=="approved" else "none"} for i,t,n,c,s in rows[:30]]
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>30 else None,"stats":stats(cur,sid)}

def queue(cur,b):
    from job_board import cursor
    cur.execute("""SELECT r.job_id,j.title,r.rating,r.comment,r.status FROM academy_job_reviews r JOIN academy_jobs j ON j.id=r.job_id
        WHERE r.job_id>%s ORDER BY r.job_id LIMIT 31""",(cursor(b),))
    rows=cur.fetchall()
    items=[{"id":i,"title":t,"rating":n,"comment":c,"status":s} for i,t,n,c,s in rows[:30]]
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>30 else None}

def decide(cur,sid,b):
    action=b["action"]
    if action not in ("approved","rejected","hidden"): raise ValueError("Invalid review action")
    cur.execute("""UPDATE academy_job_reviews SET status=%s,reviewed_by=%s,reviewed_at=now()
        WHERE job_id=%s AND ((status='pending' AND %s IN ('approved','rejected')) OR (status='approved' AND %s='hidden')) RETURNING job_id""",(action,sid,ident(b["id"]),action,action))
    if not cur.fetchone(): raise ValueError("Review unavailable")
    if action=="approved":
        from notifications import emit,counterpart
        jid=ident(b["id"])
        emit(cur,counterpart(cur,jid,"client"),jid,"review_approved","applications")
    return {"status":action}

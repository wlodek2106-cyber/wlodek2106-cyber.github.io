"""One public review per paying student, anonymous by default; no fabricated content."""
from accounts import authenticate
from database import transaction

def validate(rating,body,consent):
    if type(rating) is not int or not 1<=rating<=5 or not isinstance(body,str) or not 10<=len(body.strip())<=1200 or consent is not True:
        raise ValueError("Rating 1–5, review 10–1200 characters and publication consent required")
    return rating,body.strip()

def publish(token,rating,body,consent):
    student=authenticate(token)
    if student is None:
        raise PermissionError("Sign in required")
    rating,body=validate(rating,body,consent)
    with transaction() as cur:
        cur.execute("SELECT id FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL FOR UPDATE",(student,))
        if not cur.fetchone():
            raise PermissionError("Paid student required")
        cur.execute("""INSERT INTO student_reviews(student_id,rating,body) VALUES (%s,%s,%s)
            ON CONFLICT(student_id) DO UPDATE SET rating=EXCLUDED.rating,body=EXCLUDED.body,updated_at=now()
            WHERE student_reviews.hidden_at IS NULL RETURNING student_id""",(student,rating,body))
        if not cur.fetchone():
            raise PermissionError("Review is moderated")
    return {"published":True}

def remove(token):
    student=authenticate(token)
    if student is None: raise PermissionError("Sign in required")
    with transaction() as cur:
        cur.execute("DELETE FROM student_reviews WHERE student_id=%s",(student,))
    return {"removed":True}

def public_reviews():
    with transaction() as cur:
        cur.execute("SELECT count(*),avg(rating) FROM student_reviews WHERE hidden_at IS NULL")
        count,avg=cur.fetchone()
        cur.execute("SELECT rating,body,updated_at FROM student_reviews WHERE hidden_at IS NULL ORDER BY updated_at DESC LIMIT 100")
        items=[{"rating":r,"body":b,"date":t.date().isoformat(),"author":"Verified paid student"} for r,b,t in cur.fetchall()]
    return {"count":count,"average":round(float(avg),2) if avg is not None else None,"items":items}

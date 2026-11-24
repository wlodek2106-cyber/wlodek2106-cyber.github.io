from database import transaction

def statistics(token):
    from partners import owner
    owner(token)
    with transaction() as cur:
        result={}
        for name,query in (
            ("students","SELECT count(*) FROM students"),
            ("paid_enrollments","SELECT count(*) FROM enrollments WHERE paid_at IS NOT NULL"),
            ("completed_lessons","SELECT count(*) FROM lesson_progress"),
            ("exam_attempts","SELECT count(*) FROM quiz_attempts"),
            ("certificates","SELECT count(*) FROM certificates"),
            ("reviews","SELECT count(*) FROM student_reviews WHERE hidden_at IS NULL"),
            ("projects","SELECT count(*) FROM project_submissions"),
            ("referrals","SELECT count(*) FROM referrals"),
            ("paid_referrals","SELECT count(*) FROM referrals r JOIN enrollments e ON e.student_id=r.student_id WHERE e.paid_at IS NOT NULL")):
            cur.execute(query)
            result[name]=cur.fetchone()[0]
        cur.execute("SELECT plan,count(*) FROM enrollments WHERE paid_at IS NOT NULL GROUP BY plan")
        result["plans"]=dict(cur.fetchall())
        cur.execute("SELECT asset,COALESCE(sum(amount_atomic),0),count(*) FROM payment_invoices WHERE paid_at IS NOT NULL GROUP BY asset")
        result["settled_payments"]=[{"asset":a,"atomic_amount":str(n),"count":c} for a,n,c in cur.fetchall()]
        cur.execute("SELECT avg(rating) FROM student_reviews WHERE hidden_at IS NULL")
        avg=cur.fetchone()[0]
        result["average_rating"]=round(float(avg),2) if avg is not None else None
        return result
# All administration requires explicitly provisioned owner IDs.

"""Private proposal planning for open jobs. No automatic application or payment."""
from decimal import Decimal, ROUND_CEILING
from career import quote

def estimate_job(job,body):
    base=quote(body["hours"],body["rate"],body["expenses"],body["buffer"])
    total=Decimal(base["total"])
    if total<=0:raise ValueError("Positive estimate required")
    # Optional planning scenario, not a charge or an assertion of enabled payments.
    fee=body.get("fee_scenario",False)
    if type(fee) is not bool:raise ValueError("Invalid fee scenario")
    gross=(total/Decimal("0.95")).quantize(Decimal("0.01"),rounding=ROUND_CEILING) if fee else total
    amount=int(gross*100)
    budget=job["budget_cents"]
    return {"job":{"id":job["id"],"title":job["title"],"category":job["category"],"brief":job["brief"],"budget_cents":budget},
            "estimate":base,"suggested_quote":str(gross),"quote_cents":amount,"budget_difference_cents":budget-amount,
            "fee_scenario_percent":5 if fee else 0,"draft_only":True}

def preview(cur,sid,body):
    from student_business import ident
    jid=ident(body["id"])
    cur.execute("SELECT id FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL",(sid,))
    if not cur.fetchone():raise PermissionError("Paid student required")
    cur.execute("""SELECT j.id,j.title,j.category,j.brief,j.budget_cents FROM academy_jobs j
        WHERE j.id=%s AND j.status='open' AND j.client_id<>%s
        AND NOT EXISTS (SELECT 1 FROM academy_job_applications a WHERE a.job_id=j.id AND a.student_id=%s)""",(jid,sid,sid))
    row=cur.fetchone()
    if not row:raise PermissionError("Job unavailable")
    return estimate_job(dict(zip(("id","title","category","brief","budget_cents"),row)),body)

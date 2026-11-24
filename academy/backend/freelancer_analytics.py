"""Private freelancer analytics. Application cohorts with current outcomes; no verified income."""
from datetime import datetime,timezone,timedelta
from marketplace import CATEGORIES

def period(days):
    if type(days) is not int or days not in (7,30,90): raise ValueError("Invalid reporting period")
    return days

def ratio(n,d):
    return round(100*n/d,2) if d else None

def bucket():
    return {"applications":0,"selected":0,"active":0,"awaiting_acceptance":0,"completed":0,"pending":0,"not_selected":0,"closed":0,"selected_cents":0,"completed_cents":0}

def add(b,status,selected,quote):
    b["applications"]+=1
    if selected:
        b["selected"]+=1
        b["selected_cents"]+=quote
        if status=="assigned": b["active"]+=1
        elif status=="delivered": b["awaiting_acceptance"]+=1
        elif status=="completed":
            b["completed"]+=1
            b["completed_cents"]+=quote
        else: b["closed"]+=1
    elif status=="open": b["pending"]+=1
    elif status in ("assigned","delivered","completed"): b["not_selected"]+=1
    else: b["closed"]+=1

def summarize(rows,days,today):
    period(days)
    start=today-timedelta(days=days-1)
    daily={start+timedelta(days=i):bucket() for i in range(days)}
    categories={k:bucket() for k in CATEGORIES}
    alltime=bucket(); cohort=bucket()
    for day,category,status,selected,quote in rows:
        add(alltime,status,selected,quote)
        if day in daily:
            add(cohort,status,selected,quote)
            add(daily[day],status,selected,quote)
            add(categories[category],status,selected,quote)
    for b in (alltime,cohort):
        b["selection_percent"]=ratio(b["selected"],b["applications"])
        b["completion_percent"]=ratio(b["completed"],b["selected"])
    return {"days":days,"start":start.isoformat(),"end":today.isoformat(),"all_time":alltime,"cohort":cohort,
        "daily":[{"date":day.isoformat(),**b} for day,b in daily.items()],
        "categories":[{"category":k,**b} for k,b in categories.items()],
        "basis":"application_date_utc_current_outcome","payment_verified":False}

def report(cur,sid,days):
    period(days)
    cur.execute("SELECT 1 FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL",(sid,))
    if not cur.fetchone(): raise PermissionError("Paid student required")
    cur.execute("""SELECT (a.created_at AT TIME ZONE 'UTC')::date,j.category,j.status,
        COALESCE(j.selected_application=a.id,false),a.quote_cents
        FROM academy_job_applications a JOIN academy_jobs j ON j.id=a.job_id
        WHERE a.student_id=%s ORDER BY a.id""",(sid,))
    rows=cur.fetchall()
    result=summarize(rows,days,datetime.now(timezone.utc).date())
    from reputation import stats
    result["reputation"]=stats(cur,sid)
    return result

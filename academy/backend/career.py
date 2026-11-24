"""Private career preparation. No publication, job guarantees or external messaging."""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

def quote(hours, rate, expenses, buffer):
    values=[]
    for v in (hours,rate,expenses,buffer):
        if type(v) not in (int,float,str) or len(str(v))>24:
            raise ValueError("Invalid estimate")
        try: n=Decimal(str(v))
        except InvalidOperation: raise ValueError("Invalid estimate")
        if not n.is_finite() or n<0: raise ValueError("Invalid estimate")
        values.append(n)
    h,r,e,b=values
    if h>1000 or r>10000 or e>100000 or b>100: raise ValueError("Estimate exceeds limits")
    money=lambda n: str(n.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))
    labor=h*r
    contingency=(labor+e)*b/100
    return {"labor":money(labor),"expenses":money(e),"contingency":money(contingency),"total":money(labor+e+contingency),"currency":"USD"}

def overview(token):
    from learning import student_progress
    from portfolio import list_projects
    p=student_progress(token)
    if not p["paid"]: raise PermissionError("Paid enrollment required")
    projects=list_projects(token)["items"]
    return {"plan":p["plan"],"completed":sum(x["completed"] for x in p["lessons"]),"total":len(p["lessons"]),
            "projects":[{"id":x["id"],"lesson":x["lesson"],"submission":x["submission"],"score":x["score"]} for x in projects],
            "private":True}

def estimate(token,body):
    from learning import student_progress
    if not student_progress(token)["paid"]: raise PermissionError("Paid enrollment required")
    return quote(body["hours"],body["rate"],body["expenses"],body["buffer"])

PROFILE_FIELDS=("name","headline","summary","skills","tools","languages")
def roadmap(profile,projects,status,clients,delivered,completed,total):
    fields=sum(bool(profile.get(k,"").strip()) for k in PROFILE_FIELDS)
    stages=[
        {"id":"profile","done":fields==len(PROFILE_FIELDS),"value":fields,"target":len(PROFILE_FIELDS)},
        {"id":"portfolio","done":projects>=3,"value":min(projects,3),"target":3},
        {"id":"listing","done":status=="approved","value":int(status=="approved"),"target":1},
        {"id":"clients","done":clients>=1,"value":min(clients,1),"target":1},
        {"id":"delivery","done":delivered>=1,"value":min(delivered,1),"target":1}
    ]
    return {"stages":stages,"completed_stages":sum(s["done"] for s in stages),"listing_status":status,
            "projects":projects,"clients":clients,"delivered":delivered,"lessons_completed":completed,"lessons_total":total,
            "next":next((s["id"] for s in stages if not s["done"]),None),"private":True,"engine":"rules_based"}

def accelerator_data(cur,sid,completed,total):
    from career_profile import load
    profile=load(cur,sid)
    cur.execute("""SELECT count(*) FROM project_submissions p JOIN enrollments e ON e.id=p.enrollment_id
        WHERE e.student_id=%s AND e.paid_at IS NOT NULL""",(sid,))
    projects=cur.fetchone()[0]
    cur.execute("SELECT status FROM marketplace_services WHERE student_id=%s",(sid,))
    row=cur.fetchone()
    status=row[0] if row else "none"
    cur.execute("SELECT count(*) FROM business_clients WHERE student_id=%s",(sid,))
    clients=cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM business_orders WHERE student_id=%s AND status='delivered'",(sid,))
    delivered=cur.fetchone()[0]
    return roadmap(profile,projects,status,clients,delivered,completed,total)

def accelerator(token):
    from career_profile import identity
    from learning import student_progress
    from database import transaction
    sid=identity(token)
    p=student_progress(token)
    with transaction() as cur:
        return accelerator_data(cur,sid,sum(x["completed"] for x in p["lessons"]),len(p["lessons"]))

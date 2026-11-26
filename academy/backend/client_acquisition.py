"""Private acquisition metrics and suggested next actions. No sending or lead scraping."""
from job_matching import TOPICS
def actions(profile_ready,listing,applications,selected,leads):
    if not profile_ready: return ["profile"]
    if listing!="approved": return ["listing"]
    if not applications: return ["proposal","portfolio"]
    if applications>=5 and selected==0: return ["improve","portfolio"]
    if leads: return ["followup","proposal"]
    return ["portfolio","proposal"]

def collect(cur,sid):
    from career_profile import load
    from career import PROFILE_FIELDS
    from freelancer_analytics import report
    profile=load(cur,sid)
    ready=all(bool(profile.get(k,"").strip()) for k in PROFILE_FIELDS)
    cur.execute("SELECT status FROM marketplace_services WHERE student_id=%s",(sid,))
    row=cur.fetchone()
    listing=row[0] if row else "none"
    cur.execute("SELECT count(*) FILTER(WHERE status='lead'),count(*) FILTER(WHERE status='in_progress'),count(*) FILTER(WHERE status='delivered') FROM business_orders WHERE student_id=%s",(sid,))
    leads,active,delivered=cur.fetchone()
    data=report(cur,sid,30)["cohort"]
    return {"applications":data["applications"],"selected":data["selected"],"completed":data["completed"],
            "leads":leads,"active":active,"delivered":delivered,"profile_ready":ready,"listing":listing,
            "actions":actions(ready,listing,data["applications"],data["selected"],leads)}

def snapshot(token):
    from accounts import authenticate
    from learning import student_progress
    from database import transaction
    sid=authenticate(token)
    if sid is None: raise PermissionError("Authentication required")
    progress=student_progress(token)
    if not progress["paid"]: return {"paid":False,"metrics":None,"automatic_execution":False}
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        metrics=collect(cur,sid)
    return {"paid":True,"metrics":metrics,"automatic_execution":False,"cohort_days":30,"crm_manual":True}

"""Private creator analytics: independent aggregates, never combine quotes with cash."""
from datetime import datetime,timezone,timedelta
from freelancer_analytics import period,report as freelancer_report
from student_business import totals,identity,transaction
from business_assistant import report as business_report

def recommendations(cohort,finance,marketing,actions):
    keys=[]
    if actions["action_count"]: keys.append("review_orders")
    if int(finance["cash_margin_cents"])<0: keys.append("review_costs")
    if not cohort["applications"]: keys.append("send_proposals")
    elif cohort["applications"]>=5 and cohort["selection_percent"]<20: keys.append("improve_proposals")
    if not sum(row["published"] for row in marketing): keys.append("publish_portfolio")
    return keys

def report(token,days=30):
    period(days)
    sid=identity(token)
    today=datetime.now(timezone.utc).date()
    start=today-timedelta(days=days-1)
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        jobs=freelancer_report(cur,sid,days)
        cur.execute("SELECT id,title,status,due,agreed_cents,received_cents,expense_cents FROM business_orders WHERE student_id=%s",(sid,))
        rows=cur.fetchall()
        finance=totals((status,a,r,e) for _,_,status,_,a,r,e in rows)
        triage=business_report([{"id":i,"title":t,"status":s,"due":d.isoformat() if d else "","agreed_cents":a,"received_cents":r,"expense_cents":e} for i,t,s,d,a,r,e in rows],today)
        cur.execute("""SELECT platform,count(*),count(*) FILTER (WHERE status='published')
            FROM marketing_posts WHERE student_id=%s AND day BETWEEN %s AND %s GROUP BY platform ORDER BY platform""",(sid,start,today))
        marketing=[{"platform":p,"planned":n,"published":published} for p,n,published in cur.fetchall()]
    return {"private":True,"days":days,"start":start.isoformat(),"end":today.isoformat(),
            "marketplace":jobs,"finance_all_time":finance,"marketing_calendar":marketing,
            "order_action_count":triage["action_count"],"recommendations":recommendations(jobs["cohort"],finance,marketing,triage),
            "finance_manual":True,"social_clicks_tracked":False}

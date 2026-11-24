"""Owner-only accounting view of recorded USDC sales; not a wallet balance or net profit."""
from datetime import datetime,timezone,timedelta
from payment_policy import PRICES

def validate_period(days):
    if type(days) is not int or days not in (7,30,90): raise ValueError("Invalid reporting period")
    return days

def summarize(gross,counts,commissions):
    buckets={k:0 for k in ("available","pending","approved","paid","rejected")}
    for status,amount in commissions:
        if status not in buckets or type(amount) is not int or amount<0: raise ValueError("Invalid commission row")
        buckets[status]+=amount
    reserved=sum(buckets[k] for k in ("available","pending","approved","rejected"))
    return {"gross_atomic":str(gross),"sales_count":counts,"commission_atomic":{k:str(v) for k,v in buckets.items()},
            "unpaid_reserve_atomic":str(reserved),"after_paid_atomic":str(gross-buckets["paid"]),
            "after_all_commissions_atomic":str(gross-buckets["paid"]-reserved)}

# Keep rejected requests in reserve until the underlying entitlement is resolved.
# All-time eligibility matches the direct partner program and excludes preapproval referrals.
ELIGIBLE="""SELECT i.id,i.plan,i.amount_atomic,i.paid_at,COALESCE(p.status,'available') AS status,
    COALESCE(p.amount_atomic,i.amount_atomic*30/100) AS commission
    FROM payment_invoices i
    JOIN enrollments e ON e.student_id=i.student_id AND e.payment_signature=i.signature AND e.paid_at IS NOT NULL
    JOIN referrals r ON r.student_id=i.student_id
    JOIN influencer_partners a ON a.student_id=r.referrer_id AND a.status='approved'
    LEFT JOIN influencer_payouts p ON p.invoice_id=i.id
    WHERE i.asset='USDC' AND i.paid_at IS NOT NULL AND r.created_at>=a.approved_at AND i.paid_at>=a.approved_at"""

def report(cur,days,now=None):
    validate_period(days)
    now=now or datetime.now(timezone.utc)
    start=now.replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=days-1)
    cur.execute("SELECT COALESCE(sum(amount_atomic),0),count(*) FROM payment_invoices WHERE asset='USDC' AND paid_at IS NOT NULL")
    gross,count=cur.fetchone()
    cur.execute("SELECT status,COALESCE(sum(commission),0) FROM ("+ELIGIBLE+") q GROUP BY status")
    alltime=summarize(int(gross),count,[(s,int(n)) for s,n in cur.fetchall()])
    cur.execute("""SELECT plan,count(*),COALESCE(sum(amount_atomic),0)
        FROM payment_invoices WHERE asset='USDC' AND paid_at>=%s AND paid_at<=%s GROUP BY plan""",(start,now))
    plans={p:{"count":0,"gross_atomic":"0"} for p in PRICES}
    for p,c,n in cur.fetchall(): plans[p]={"count":c,"gross_atomic":str(n)}
    cur.execute("""SELECT (paid_at AT TIME ZONE 'UTC')::date,count(*),sum(amount_atomic)
        FROM payment_invoices WHERE asset='USDC' AND paid_at>=%s AND paid_at<=%s GROUP BY 1 ORDER BY 1""",(start,now))
    byday={d:(c,n) for d,c,n in cur.fetchall()}
    series=[]
    for k in range(days):
        day=(start+timedelta(days=k)).date()
        c,n=byday.get(day,(0,0));series.append({"date":day.isoformat(),"count":c,"gross_atomic":str(n)})
    cur.execute("SELECT COALESCE(sum(amount_atomic),0),count(*) FROM influencer_payouts WHERE status='paid' AND paid_at>=%s AND paid_at<=%s",(start,now))
    paid,paid_count=cur.fetchone()
    cur.execute("SELECT status,count(*) FROM influencer_partners GROUP BY status")
    partners=dict(cur.fetchall())
    cur.execute("""SELECT p.id,p.amount_atomic,p.paid_at,p.payout_signature,p.partner_id
        FROM influencer_payouts p WHERE p.status='paid' ORDER BY p.paid_at DESC,p.id DESC LIMIT 50""")
    recent=[{"id":i,"amount_atomic":str(n),"date":d.isoformat(),"signature":s,"partner_id":u} for i,n,d,s,u in cur.fetchall()]
    return {"alltime":alltime,"period":{"days":days,"start":start.isoformat(),"end":now.isoformat(),"gross_atomic":str(sum(int(p["gross_atomic"]) for p in plans.values())),"sales_count":sum(p["count"] for p in plans.values()),"payout_atomic":str(paid),"payout_count":paid_count,"plans":plans,"series":series},"partners":partners,"recent_payouts":recent,"currency":"USDC","scope":"recorded_sales_only","timezone":"UTC"}

def founder_report(token,days):
    from partners import owner
    from database import transaction
    owner(token)
    validate_period(days)
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        return report(cur,days)

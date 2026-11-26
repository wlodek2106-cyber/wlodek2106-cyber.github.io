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

def percent(n,d):
    return round(100*n/d,2) if d else None

def daily_activity(start,days,rows):
    keys=("registrations","referred_registrations","paid_enrollments","exam_attempts","completed_lessons","project_submissions","certificates")
    data={}
    for date,key,count in rows:
        if key not in keys: raise ValueError("Invalid activity metric")
        data.setdefault(date,{})[key]=count
    return [{"date":(start+timedelta(days=i)).date().isoformat(),
             **{k:data.get((start+timedelta(days=i)).date(),{}).get(k,0) for k in keys}} for i in range(days)]

def trial_funnel(cur,start,now):
    # Registration cohort. First exam before payment is evidence of a free trial;
    # merely opening an unpaid enrollment is not counted as participation.
    cur.execute("""WITH cohort AS (
        SELECT s.id,e.id AS eid,e.paid_at,e.plan
        FROM students s LEFT JOIN enrollments e ON e.student_id=s.id
        WHERE s.created_at BETWEEN %s AND %s
    ), stages AS (
        SELECT c.*,
        EXISTS(SELECT 1 FROM quiz_attempts q WHERE q.enrollment_id=c.eid AND q.lesson=1
          AND q.attempted_at<=%s AND (c.paid_at IS NULL OR q.attempted_at<c.paid_at)) AS attempted,
        EXISTS(SELECT 1 FROM lesson_progress p WHERE p.enrollment_id=c.eid AND p.lesson=1
          AND p.passed_at<=%s AND (c.paid_at IS NULL OR p.passed_at<c.paid_at)) AS passed
        FROM cohort c
    )
    SELECT count(*),count(*) FILTER(WHERE attempted),count(*) FILTER(WHERE passed),
        count(*) FILTER(WHERE passed AND paid_at<=%s),
        count(*) FILTER(WHERE passed AND paid_at IS NULL),
        count(*) FILTER(WHERE passed AND paid_at<=%s AND plan='starter'),
        count(*) FILTER(WHERE passed AND paid_at<=%s AND plan='pro'),
        count(*) FILTER(WHERE passed AND paid_at<=%s AND plan='vip'),
        count(*) FILTER(WHERE passed AND paid_at<=%s AND plan='elite')
    FROM stages""",(start,now,now,now,now,now,now,now,now))
    registered,attempted,passed,paid,waiting,*counts=cur.fetchone()
    return {"registered":registered,"attempted":attempted,"passed":passed,"paid_after_pass":paid,
            "passed_unpaid":waiting,"attempt_rate":percent(attempted,registered),
            "pass_rate":percent(passed,attempted),"conversion_rate":percent(paid,passed),
            "plans":dict(zip(("starter","pro","vip","elite"),counts)),
            "basis":"registration_cohort_pre_payment_exam"}

def activity(cur,start,now,days):
    cur.execute("""SELECT count(*),count(*) FILTER(WHERE e.paid_at IS NOT NULL),
        count(*) FILTER(WHERE r.student_id IS NOT NULL),
        count(*) FILTER(WHERE r.student_id IS NOT NULL AND e.paid_at IS NOT NULL)
        FROM students s LEFT JOIN enrollments e ON e.student_id=s.id
        LEFT JOIN referrals r ON r.student_id=s.id""")
    registered,paid,referred,paid_referred=cur.fetchone()
    cur.execute("""SELECT count(*) FILTER(WHERE n>0),count(*) FILTER(WHERE n>=target)
        FROM (SELECT e.id,count(p.lesson) n,CASE WHEN e.plan IN ('vip','elite') THEN 45 ELSE 30 END target
        FROM enrollments e LEFT JOIN lesson_progress p ON p.enrollment_id=e.id
        WHERE e.paid_at IS NOT NULL GROUP BY e.id,e.plan) q""")
    started,finished=cur.fetchone()
    cur.execute("""SELECT count(*),count(*) FILTER(WHERE e.paid_at IS NOT NULL AND e.paid_at<=%s)
        FROM students s LEFT JOIN enrollments e ON e.student_id=s.id
        WHERE s.created_at BETWEEN %s AND %s""",(now,start,now))
    cohort,cohort_paid=cur.fetchone()
    cur.execute("""SELECT count(DISTINCT e.student_id) FROM quiz_attempts q JOIN enrollments e ON e.id=q.enrollment_id
        WHERE q.attempted_at BETWEEN %s AND %s AND e.paid_at IS NOT NULL""",(start,now))
    active=cur.fetchone()[0]
    cur.execute("""WITH events AS (
        SELECT created_at AS stamp,'registrations' AS metric FROM students WHERE created_at BETWEEN %s AND %s
        UNION ALL SELECT s.created_at,'referred_registrations' FROM students s JOIN referrals r ON r.student_id=s.id WHERE s.created_at BETWEEN %s AND %s
        UNION ALL SELECT paid_at,'paid_enrollments' FROM enrollments WHERE paid_at BETWEEN %s AND %s
        UNION ALL SELECT attempted_at,'exam_attempts' FROM quiz_attempts WHERE attempted_at BETWEEN %s AND %s
        UNION ALL SELECT passed_at,'completed_lessons' FROM lesson_progress WHERE passed_at BETWEEN %s AND %s
        UNION ALL SELECT submitted_at,'project_submissions' FROM project_submissions WHERE submitted_at BETWEEN %s AND %s
        UNION ALL SELECT issued_at,'certificates' FROM certificates WHERE issued_at BETWEEN %s AND %s
        ) SELECT (stamp AT TIME ZONE 'UTC')::date,metric,count(*) FROM events GROUP BY 1,2""",(start,now)*7)
    series=daily_activity(start,days,cur.fetchall())
    moderation={}
    for key,query in (("marketplace_pending","SELECT count(*) FROM marketplace_services WHERE status='pending'"),
                      ("community_pending","SELECT count(*) FROM community_posts WHERE status='pending'"),
                      ("partner_pending","SELECT count(*) FROM influencer_partners WHERE status='pending'"),
                      ("payment_support_open","SELECT count(*) FROM payment_support WHERE status='open'")):
        cur.execute(query);moderation[key]=cur.fetchone()[0]
    totals={k:sum(row[k] for row in series) for k in series[0] if k!="date"}
    return {"alltime":{"registered":registered,"paid":paid,"referred":referred,"paid_referred":paid_referred,
        "registration_to_paid_percent":percent(paid,registered),"referred_to_paid_percent":percent(paid_referred,referred),
        "started":started,"finished":finished,"completion_percent":percent(finished,paid)},
        "cohort":{"registered":cohort,"paid":cohort_paid,"conversion_percent":percent(cohort_paid,cohort)},
        "trial_funnel":trial_funnel(cur,start,now),"exam_active_students":active,"totals":totals,"series":series,"moderation":moderation}

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
    from campaign_growth import report as campaign_report
    return {"campaign_growth":campaign_report(cur,start,now),"alltime":alltime,"period":{"days":days,"start":start.isoformat(),"end":now.isoformat(),"gross_atomic":str(sum(int(p["gross_atomic"]) for p in plans.values())),"sales_count":sum(p["count"] for p in plans.values()),"payout_atomic":str(paid),"payout_count":paid_count,"plans":plans,"series":series},"partners":partners,"recent_payouts":recent,"activity":activity(cur,start,now,days),"currency":"USDC","scope":"recorded_sales_only","timezone":"UTC"}

def founder_report(token,days):
    from partners import owner
    from database import transaction
    owner(token)
    validate_period(days)
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        return report(cur,days)

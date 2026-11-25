"""Owner aggregate course acquisition, separate from hiring attribution.
Source is a registration URL label, not independent proof of referral or clicks.
"""
from acquisition import SOURCES

def summarize(rows):
    data={k:{"source":k,"registered":0,"paid":0,"gross_atomic":"0","conversion_percent":None} for k in (*SOURCES,"untracked")}
    for source,registered,paid,gross in rows:
        k=source if source in SOURCES else "untracked"
        r=data[k]
        r["registered"]+=registered
        r["paid"]+=paid
        r["gross_atomic"]=str(int(r["gross_atomic"])+int(gross))
    for r in data.values():
        if r["registered"]:
            r["conversion_percent"]=round(100*r["paid"]/r["registered"],2)
    return {"items":list(data.values()),"scope":"registration_cohort_as_of_report","self_reported":True,"clicks_tracked":False}

def report(cur,start,end):
    # Each student contributes once, and only a matching paid USDC invoice counts as recorded revenue.
    cur.execute("""SELECT s.campaign_source,count(*),
        count(*) FILTER (WHERE e.paid_at IS NOT NULL AND e.paid_at<=%s),
        COALESCE(sum(i.amount_atomic),0)
        FROM students s
        LEFT JOIN enrollments e ON e.student_id=s.id
        LEFT JOIN payment_invoices i ON i.student_id=s.id AND i.signature=e.payment_signature
            AND i.plan=e.plan AND i.asset='USDC' AND i.paid_at IS NOT NULL AND i.paid_at<=%s AND e.paid_at<=%s
        WHERE s.created_at BETWEEN %s AND %s GROUP BY s.campaign_source""",(end,end,end,start,end))
    return summarize(cur.fetchall())

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

def directory_query(cur,body):
    from learning import owner_preview
    after=body.get("after",0); search=body.get("search",""); kind=body.get("kind","all")
    if type(after) is not int or not 0<=after<=9223372036854775807: raise ValueError("Invalid cursor")
    if not isinstance(search,str) or len(search)>120 or kind not in ("all","paid","freelancers","partners","due"): raise ValueError("Invalid filter")
    sql="""WITH eligible AS (
      SELECT i.student_id AS buyer,a.student_id AS partner,i.id AS invoice,
        COALESCE(p.amount_atomic,i.amount_atomic*30/100) AS commission,COALESCE(p.status,'available') AS state
      FROM payment_invoices i JOIN enrollments e ON e.student_id=i.student_id
        AND e.payment_signature=i.signature AND e.paid_at IS NOT NULL
      JOIN referrals r ON r.student_id=i.student_id
      JOIN influencer_partners a ON a.student_id=r.referrer_id AND a.status='approved'
      LEFT JOIN influencer_payouts p ON p.invoice_id=i.id
      WHERE i.asset='USDC' AND i.paid_at IS NOT NULL AND r.created_at>=a.approved_at AND i.paid_at>=a.approved_at
    ), partner_totals AS (
      SELECT partner,count(*) AS sales,
        COALESCE(sum(commission) FILTER(WHERE state='available'),0) AS available,
        COALESCE(sum(commission) FILTER(WHERE state='pending'),0) AS pending,
        COALESCE(sum(commission) FILTER(WHERE state='approved'),0) AS approved,
        COALESCE(sum(commission) FILTER(WHERE state='rejected'),0) AS rejected,
        COALESCE(sum(commission) FILTER(WHERE state='paid'),0) AS paid FROM eligible GROUP BY partner
    ), jobs AS (
      SELECT a.student_id,count(*) AS assigned,count(*) FILTER(WHERE j.status='completed') AS completed,
        COALESCE(sum(a.quote_cents) FILTER(WHERE j.payment_mode='external' AND j.status IN ('delivered','completed')),0) AS external_quote,
        COALESCE(sum(p.quote_cents*9500) FILTER(WHERE p.paid_at IS NOT NULL),0) AS verified,
        COALESCE(sum(a.quote_cents*9500) FILTER(WHERE j.payment_mode='split' AND j.status='delivered' AND p.paid_at IS NULL),0) AS unsettled
      FROM academy_job_applications a JOIN academy_jobs j ON j.id=a.job_id AND j.selected_application=a.id
      LEFT JOIN academy_job_payments p ON p.job_id=j.id AND p.freelancer_id=a.student_id
      WHERE j.status IN ('assigned','delivered','completed') GROUP BY a.student_id
    )
    SELECT s.id,s.first_name,s.last_name,s.username,e.plan,i.amount_atomic,i.paid_at,u.username,
      ec.commission,ec.state,ap.status,m.status,
      (SELECT count(*) FROM academy_job_applications x WHERE x.student_id=s.id),
      COALESCE(j.assigned,0),COALESCE(j.completed,0),COALESCE(j.external_quote,0),COALESCE(j.verified,0),COALESCE(j.unsettled,0),
      COALESCE(pt.sales,0),COALESCE(pt.available,0),COALESCE(pt.pending,0),COALESCE(pt.approved,0),COALESCE(pt.rejected,0),COALESCE(pt.paid,0)
      FROM students s LEFT JOIN enrollments e ON e.student_id=s.id
      LEFT JOIN payment_invoices i ON i.student_id=s.id AND i.signature=e.payment_signature AND i.asset='USDC' AND i.paid_at IS NOT NULL AND e.paid_at IS NOT NULL
      LEFT JOIN referrals r ON r.student_id=s.id LEFT JOIN students u ON u.id=r.referrer_id
      LEFT JOIN eligible ec ON ec.buyer=s.id AND ec.invoice=i.id
      LEFT JOIN influencer_partners ap ON ap.student_id=s.id LEFT JOIN marketplace_services m ON m.student_id=s.id
      LEFT JOIN partner_totals pt ON pt.partner=s.id LEFT JOIN jobs j ON j.student_id=s.id
      WHERE s.id>%s AND (%s='' OR strpos(lower(concat_ws(' ',s.first_name,s.last_name,s.username)),lower(%s))>0)"""
    filters={"all":"","paid":" AND i.id IS NOT NULL","freelancers":" AND (m.id IS NOT NULL OR EXISTS(SELECT 1 FROM academy_job_applications a WHERE a.student_id=s.id))","partners":" AND ap.student_id IS NOT NULL","due":" AND (COALESCE(pt.available,0)+COALESCE(pt.pending,0)+COALESCE(pt.approved,0)+COALESCE(pt.rejected,0)>0 OR COALESCE(j.unsettled,0)>0)"}
    cur.execute(sql+filters[kind]+" ORDER BY s.id LIMIT 51",(after,search.strip(),search.strip()))
    rows=cur.fetchall(); items=[]
    for row in rows[:50]:
        sid,first,last,username,plan,amount,date,ref,commission,state,partner,listing,apps,assigned,completed,external,verified,unsettled,sales,available,pending,approved,rejected,paid=row
        items.append({"id":sid,"name":" ".join(x for x in (first,last) if x) or username or "Member","username":username,
            "badge":"owner" if owner_preview(sid) else "paid" if date else None,"plan":plan if date else None,
            "purchase_atomic":str(amount) if amount is not None else None,"purchase_at":date.isoformat() if date else None,
            "referrer":ref,"sale_commission_atomic":str(commission) if commission is not None else None,"sale_commission_status":state,
            "partner_status":partner,"listing_status":listing,"applications":apps,"assigned":assigned,"completed":completed,
            "external_quote_cents":str(external),"verified_atomic":str(verified),"unsettled_atomic":str(unsettled),"partner_sales":sales,
            "commission":{k:str(v) for k,v in (("available",available),("pending",pending),("approved",approved),("rejected",rejected),("paid",paid))},
            "reserve_atomic":str(available+pending+approved+rejected)})
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>50 else None}

def directory(token,body):
    from partners import owner
    owner(token)
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        return directory_query(cur,body)

"""Academy job board. Manual moderation and external contracts; no custody or payment processing."""
from accounts import authenticate
from database import transaction
from partners import owner
from student_business import clean,ident,cents
from marketplace import CATEGORIES

def cursor(b):
    n=b.get("after",0)
    if type(n) is not int or not 0<=n<=9223372036854775807: raise ValueError("Invalid cursor")
    return n

def positive(v):
    n=cents(v)
    if n<=0: raise ValueError("Positive USD amount required")
    return n

def create(cur,sid,b):
    if b.get("consent") is not True or b["category"] not in CATEGORIES: raise ValueError("Consent and valid category required")
    vals=(clean(b["title"],120,True),b["category"],clean(b["brief"],3000,True),positive(b["budget"]),clean(b["contact"],200,True))
    cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
    if not cur.fetchone(): raise PermissionError()
    cur.execute("SELECT count(*) FROM academy_jobs WHERE client_id=%s",(sid,))
    if cur.fetchone()[0]>=30: raise ValueError("Job limit reached")
    cur.execute("INSERT INTO academy_jobs(client_id,title,category,brief,budget_cents,contact) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",(sid,*vals))
    return {"id":cur.fetchone()[0],"status":"pending"}

FIELDS=("id","title","category","brief","budget_cents","status")
def page(cur,sid,mode,b):
    after=cursor(b)
    projection="j.id,j.title,j.category,j.brief,j.budget_cents,j.status"
    if mode=="feed":
        sql="SELECT "+projection+" FROM academy_jobs j WHERE j.status='open' AND j.id>%s ORDER BY j.id LIMIT 31"; args=(after,)
    elif mode=="mine":
        sql="SELECT "+projection+" FROM academy_jobs j WHERE j.client_id=%s AND j.id>%s ORDER BY j.id LIMIT 31"; args=(sid,after)
    elif mode=="admin":
        sql="SELECT "+projection+" FROM academy_jobs j WHERE j.id>%s ORDER BY j.id LIMIT 31"; args=(after,)
    else: raise ValueError()
    cur.execute(sql,args)
    rows=cur.fetchall()
    items=[dict(zip(FIELDS,r)) for r in rows[:30]]
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>30 else None}

def job_lock(cur,jid):
    cur.execute("SELECT client_id,status,selected_application FROM academy_jobs WHERE id=%s FOR UPDATE",(ident(jid),))
    row=cur.fetchone()
    if not row: raise PermissionError("Job unavailable")
    return row

def moderate(cur,sid,b):
    jid=ident(b["id"]); action=b["action"]
    _,status,_=job_lock(cur,jid)
    if not ((status=="pending" and action in ("open","rejected")) or (status=="open" and action=="cancelled")): raise ValueError("Invalid moderation transition")
    cur.execute("UPDATE academy_jobs SET status=%s,reviewed_by=%s,updated_at=now() WHERE id=%s",(action,sid,jid))
    return {"status":action}

def apply(cur,sid,b):
    jid=ident(b["id"])
    if b.get("consent") is not True: raise ValueError("Consent required")
    share=b.get("share_reputation",False)
    if type(share) is not bool: raise ValueError("Invalid consent")
    vals=(clean(b["alias"],80,True),clean(b["proposal"],2000,True),positive(b["quote"]),clean(b["contact"],200,True),share)
    cur.execute("SELECT id FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL FOR UPDATE",(sid,))
    if not cur.fetchone(): raise PermissionError("Paid student required")
    client,status,_=job_lock(cur,jid)
    if client==sid or status!="open": raise PermissionError("Job unavailable")
    cur.execute("SELECT count(*) FROM academy_job_applications WHERE student_id=%s",(sid,))
    if cur.fetchone()[0]>=100: raise ValueError("Application limit reached")
    cur.execute("SELECT count(*) FROM academy_job_applications WHERE job_id=%s",(jid,))
    if cur.fetchone()[0]>=50: raise ValueError("Job application limit reached")
    cur.execute("INSERT INTO academy_job_applications(job_id,student_id,alias,proposal,quote_cents,contact,share_reputation) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(job_id,student_id) DO NOTHING RETURNING id",(jid,sid,*vals))
    row=cur.fetchone()
    if not row: raise ValueError("Already applied")
    return {"id":row[0],"status":"submitted"}

def applicants(cur,sid,b):
    jid=ident(b["id"])
    cur.execute("SELECT client_id,selected_application,status FROM academy_jobs WHERE id=%s",(jid,))
    row=cur.fetchone()
    if not row or row[0]!=sid: raise PermissionError()
    cur.execute("SELECT id,alias,proposal,quote_cents,CASE WHEN id=%s AND %s IN ('assigned','delivered','completed') THEN contact ELSE NULL END,student_id,share_reputation FROM academy_job_applications WHERE job_id=%s ORDER BY id LIMIT 50",(row[1],row[2],jid))
    records=cur.fetchall()
    from reputation import stats
    items=[{"id":i,"alias":a,"proposal":p,"quote_cents":q,"contact":c,"selected":i==row[1],"reputation":stats(cur,student) if share else None} for i,a,p,q,c,student,share in records]
    cur.execute("SELECT status FROM academy_job_reviews WHERE job_id=%s",(jid,))
    review=cur.fetchone()
    return {"items":items,"review_status":review[0] if review else None}

def applications(cur,sid,b):
    cur.execute("""SELECT a.id,j.id,j.title,j.status,a.quote_cents,a.proposal,
        j.selected_application=a.id,CASE WHEN j.selected_application=a.id AND j.status IN ('assigned','delivered','completed') THEN j.contact ELSE NULL END
        FROM academy_job_applications a JOIN academy_jobs j ON j.id=a.job_id
        WHERE a.student_id=%s AND a.id>%s ORDER BY a.id LIMIT 31""",(sid,cursor(b)))
    rows=cur.fetchall()
    items=[{"id":i,"job_id":j,"title":t,"status":s,"quote_cents":q,"proposal":p,"selected":bool(sel),"contact":c} for i,j,t,s,q,p,sel,c in rows[:30]]
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>30 else None}

def transition(cur,sid,b):
    jid=ident(b["id"]);action=b["action"]
    client,status,selected=job_lock(cur,jid)
    if action=="select":
        if client!=sid or status!="open": raise PermissionError()
        aid=ident(b["application"])
        cur.execute("SELECT a.id FROM academy_job_applications a JOIN enrollments e ON e.student_id=a.student_id AND e.paid_at IS NOT NULL WHERE a.id=%s AND a.job_id=%s",(aid,jid))
        if not cur.fetchone(): raise ValueError("Application unavailable")
        cur.execute("UPDATE academy_jobs SET status='assigned',selected_application=%s,updated_at=now() WHERE id=%s",(aid,jid))
        return {"status":"assigned"}
    if action=="deliver":
        if status!="assigned" or not selected: raise PermissionError()
        cur.execute("SELECT 1 FROM academy_job_applications WHERE id=%s AND job_id=%s AND student_id=%s",(selected,jid,sid))
        if not cur.fetchone(): raise PermissionError()
        next_status="delivered"
    elif action=="complete" and client==sid and status=="delivered": next_status="completed"
    elif action=="cancel" and client==sid and status in ("pending","open"): next_status="cancelled"
    else: raise PermissionError("Transition unavailable")
    cur.execute("UPDATE academy_jobs SET status=%s,updated_at=now() WHERE id=%s",(next_status,jid))
    return {"status":next_status}

def recommend(cur,sid):
    from job_matching import rank
    cur.execute("SELECT id FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL",(sid,))
    row=cur.fetchone()
    if not row: raise PermissionError("Paid student required")
    cur.execute("SELECT lesson FROM lesson_progress WHERE enrollment_id=%s AND score>=80",(row[0],))
    passed=[r[0] for r in cur.fetchall()]
    cur.execute("SELECT category FROM marketplace_services WHERE student_id=%s AND status='approved'",(sid,))
    service=cur.fetchone()
    cur.execute("""SELECT j.id,j.title,j.category,j.brief,j.budget_cents,j.status FROM academy_jobs j
      WHERE j.status='open' AND j.client_id<>%s AND NOT EXISTS
      (SELECT 1 FROM academy_job_applications a WHERE a.job_id=j.id AND a.student_id=%s)
      ORDER BY j.id DESC LIMIT 300""",(sid,sid))
    candidates=[dict(zip(FIELDS,r)) for r in cur.fetchall()]
    return {"items":rank(candidates,passed,service[0] if service else None),"next_after":None,"candidate_limit":300,"engine":"rules_based"}

def dispatch(token,action,b):
    if action in ("admin","moderate","review-admin","review-decide"): sid=owner(token)
    else:
        sid=authenticate(token)
        if sid is None: raise PermissionError()
    with transaction() as cur:
        if action in ("feed","mine","admin"): return page(cur,sid,action,b)
        if action=="recommended": return recommend(cur,sid)
        if action=="create": return create(cur,sid,b)
        if action=="moderate": return moderate(cur,sid,b)
        if action=="apply": return apply(cur,sid,b)
        if action=="applicants": return applicants(cur,sid,b)
        if action=="applications": return applications(cur,sid,b)
        if action=="transition": return transition(cur,sid,b)
        if action in ("review","reputation","review-admin","review-decide"):
            from reputation import submit,own,queue,decide
            if action=="review": return submit(cur,sid,b)
            if action=="reputation": return own(cur,sid,b)
            if action=="review-admin": return queue(cur,b)
            if action=="review-decide": return decide(cur,sid,b)
    raise ValueError("Unknown action")

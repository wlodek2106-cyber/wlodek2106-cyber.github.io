"""Authenticated private support tickets. AI suggestions never modify accounts or payments."""
from student_business import clean,ident
CATEGORIES=("account","payment","learning","ai","marketplace","other")

def cursor_value(v):
    if v is None: return 9223372036854775807
    return ident(v)

def create(cur,sid,b):
    category=b.get("category")
    if not isinstance(category,str) or category not in CATEGORIES: raise ValueError("Invalid category")
    subject=clean(b.get("subject"),120,True);body=clean(b.get("body"),2000,True)
    if b.get("consent") is not True: raise ValueError("Consent required")
    cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
    if not cur.fetchone(): raise PermissionError("Account unavailable")
    cur.execute("SELECT count(*),count(*) FILTER(WHERE status<>'closed') FROM support_tickets WHERE student_id=%s",(sid,))
    total,active=cur.fetchone()
    if total>=200 or active>=5: raise ValueError("Ticket limit")
    from support_triage import classify
    topic,priority=classify(category,subject,body)
    cur.execute("INSERT INTO support_tickets(student_id,category,subject,admin_unread,topic,priority) VALUES (%s,%s,%s,true,%s,%s) RETURNING id",(sid,category,subject,topic,priority))
    tid=cur.fetchone()[0]
    cur.execute("INSERT INTO support_messages(ticket_id,role,body) VALUES (%s,'student',%s)",(tid,body))
    return {"id":tid,"status":"open"}

def counters(cur,sid,admin=False):
    cur.execute("""SELECT count(*) FILTER(WHERE status='open'),count(*) FILTER(WHERE status='answered'),
       count(*) FILTER(WHERE status='closed'),count(*) FILTER(WHERE CASE WHEN %s THEN admin_unread ELSE student_unread END)
       FROM support_tickets WHERE (%s OR student_id=%s)""",(admin,admin,sid))
    opened,answered,closed,unread=cur.fetchone()
    return {"open":opened,"answered":answered,"closed":closed,"unread":unread}

def filters(status,category):
    if status is not None and (not isinstance(status,str) or status not in ("open","answered","closed")):
        raise ValueError("Invalid status")
    if category is not None and (not isinstance(category,str) or category not in CATEGORIES):
        raise ValueError("Invalid category")
    return status,category

def listing(cur,sid,admin=False,before=None,status=None,category=None,priority=None):
    status,category=filters(status,category)
    from support_triage import PRIORITIES
    if priority is not None and (not isinstance(priority,str) or priority not in PRIORITIES): raise ValueError("Invalid priority")
    cur.execute("""SELECT id,category,subject,status,updated_at,
      CASE WHEN %s THEN admin_unread ELSE student_unread END,topic,priority,triage_manual
      FROM support_tickets WHERE (%s OR student_id=%s) AND id<%s
      AND (%s::text IS NULL OR status=%s) AND (%s::text IS NULL OR category=%s)
      AND (%s::text IS NULL OR priority=%s) ORDER BY id DESC LIMIT 51""",(admin,admin,sid,cursor_value(before),status,status,category,category,priority,priority))
    rows=cur.fetchall()
    items=[{"id":i,"category":c,"subject":s,"status":st,"updated_at":at.isoformat(),"unread":unread,**({"topic":topic,"priority":prio,"triage_manual":manual} if admin else {})} for i,c,s,st,at,unread,topic,prio,manual in rows[:50]]
    return {"items":items,"next_before":items[-1]["id"] if len(rows)>50 else None,"admin":admin,"counts":counters(cur,sid,admin)}

def access(cur,sid,tid,admin=False):
    cur.execute("SELECT student_id,subject,category,status FROM support_tickets WHERE id=%s FOR UPDATE",(ident(tid),))
    row=cur.fetchone()
    if not row or (not admin and row[0]!=sid): raise PermissionError("Ticket unavailable")
    return row

def thread(cur,sid,tid,admin=False):
    _,subject,category,state=access(cur,sid,tid,admin)
    cur.execute("UPDATE support_tickets SET admin_unread=false WHERE id=%s" if admin else "UPDATE support_tickets SET student_unread=false WHERE id=%s",(tid,))
    cur.execute("SELECT id,role,body,created_at FROM support_messages WHERE ticket_id=%s ORDER BY id",(tid,))
    rows=cur.fetchall()
    meta={}
    if admin:
        cur.execute("SELECT topic,priority,triage_manual FROM support_tickets WHERE id=%s",(tid,))
        topic,prio,manual=cur.fetchone()
        meta={"topic":topic,"priority":prio,"triage_manual":manual}
    return {"id":tid,"subject":subject,"category":category,"status":state,**meta,
            "messages":[{"id":i,"role":r,"body":b,"created_at":at.isoformat()} for i,r,b,at in rows]}

def reply(cur,sid,b,admin=False):
    tid=ident(b.get("id"));_,_,_,state=access(cur,sid,tid,admin)
    if state=="closed": raise ValueError("Ticket closed")
    body=clean(b.get("body"),2000,True)
    if b.get("consent") is not True: raise ValueError("Consent required")
    cur.execute("SELECT count(*) FROM support_messages WHERE ticket_id=%s",(tid,))
    if cur.fetchone()[0]>=30: raise ValueError("Message limit")
    role="admin" if admin else "student"
    state="answered" if admin else "open"
    cur.execute("INSERT INTO support_messages(ticket_id,role,body) VALUES (%s,%s,%s)",(tid,role,body))
    cur.execute("UPDATE support_tickets SET status=%s,updated_at=now(),student_unread=%s,admin_unread=%s WHERE id=%s",(state,admin,not admin,tid))
    return {"status":state}

def close(cur,sid,tid,admin=False):
    _,_,_,state=access(cur,sid,tid,admin)
    if state!="closed":
        cur.execute("UPDATE support_tickets SET status='closed',updated_at=now(),student_unread=%s,admin_unread=%s WHERE id=%s",(admin,not admin,tid))
    return {"status":"closed"}

ARTICLES=["login","passkey","payment","lesson","webgpu","higgsfield","marketplace","connection"]
def feedback(cur,sid,b):
    article=b.get("article");helpful=b.get("helpful")
    if not isinstance(article,str) or article not in ARTICLES or type(helpful) is not bool:
        raise ValueError("Invalid article feedback")
    cur.execute("""INSERT INTO support_article_feedback(student_id,article,helpful) VALUES (%s,%s,%s)
       ON CONFLICT(student_id,article) DO UPDATE SET helpful=EXCLUDED.helpful,updated_at=now()""",(sid,article,helpful))
    return {"saved":True}

def feedback_summary(cur):
    cur.execute("SELECT article,count(*) FILTER(WHERE helpful),count(*) FILTER(WHERE NOT helpful) FROM support_article_feedback GROUP BY article ORDER BY article")
    return {"items":[{"article":a,"helpful":h,"not_helpful":n} for a,h,n in cur.fetchall()]}

def dispatch(token,action,b):
    from accounts import authenticate
    from partners import owner
    from database import transaction
    sid=authenticate(token)
    if sid is None: raise PermissionError("Authentication required")
    try:
        owner(token);allowed=True
    except PermissionError: allowed=False
    admin=b.get("admin",False)
    if type(admin) is not bool or admin and not allowed: raise PermissionError("Owner required")
    with transaction() as cur:
        if action=="admin": return {"allowed":allowed}
        if action=="feedback": return feedback(cur,sid,b)
        if action=="feedback-summary":
            if not allowed: raise PermissionError("Owner required")
            return feedback_summary(cur)
        if action in ("triage","triage-summary"):
            if not allowed or not admin: raise PermissionError("Owner required")
            from support_triage import assign,summary
            return assign(cur,b.get("id"),b.get("topic"),b.get("priority")) if action=="triage" else summary(cur,b.get("days",7))
        if action=="list": return listing(cur,sid,admin,b.get("before"),b.get("status"),b.get("category"),b.get("priority") if admin else None)
        if action=="create": return create(cur,sid,b)
        if action=="thread": return thread(cur,sid,b.get("id"),admin)
        if action=="reply": return reply(cur,sid,b,admin)
        if action=="close": return close(cur,sid,b.get("id"),admin)
    raise ValueError("Invalid action")

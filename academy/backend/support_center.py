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
    cur.execute("INSERT INTO support_tickets(student_id,category,subject) VALUES (%s,%s,%s) RETURNING id",(sid,category,subject))
    tid=cur.fetchone()[0]
    cur.execute("INSERT INTO support_messages(ticket_id,role,body) VALUES (%s,'student',%s)",(tid,body))
    return {"id":tid,"status":"open"}

def listing(cur,sid,admin=False,before=None):
    cur.execute("""SELECT id,category,subject,status,updated_at FROM support_tickets
      WHERE (%s OR student_id=%s) AND id<%s ORDER BY id DESC LIMIT 51""",(admin,sid,cursor_value(before)))
    rows=cur.fetchall()
    items=[{"id":i,"category":c,"subject":s,"status":st,"updated_at":at.isoformat()} for i,c,s,st,at in rows[:50]]
    return {"items":items,"next_before":items[-1]["id"] if len(rows)>50 else None,"admin":admin}

def access(cur,sid,tid,admin=False):
    cur.execute("SELECT student_id,subject,category,status FROM support_tickets WHERE id=%s FOR UPDATE",(ident(tid),))
    row=cur.fetchone()
    if not row or (not admin and row[0]!=sid): raise PermissionError("Ticket unavailable")
    return row

def thread(cur,sid,tid,admin=False):
    _,subject,category,state=access(cur,sid,tid,admin)
    cur.execute("SELECT id,role,body,created_at FROM support_messages WHERE ticket_id=%s ORDER BY id",(tid,))
    return {"id":tid,"subject":subject,"category":category,"status":state,
            "messages":[{"id":i,"role":r,"body":b,"created_at":at.isoformat()} for i,r,b,at in cur.fetchall()]}

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
    cur.execute("UPDATE support_tickets SET status=%s,updated_at=now() WHERE id=%s",(state,tid))
    return {"status":state}

def close(cur,sid,tid,admin=False):
    access(cur,sid,tid,admin)
    cur.execute("UPDATE support_tickets SET status='closed',updated_at=now() WHERE id=%s",(tid,))
    return {"status":"closed"}

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
        if action=="list": return listing(cur,sid,admin,b.get("before"))
        if action=="create": return create(cur,sid,b)
        if action=="thread": return thread(cur,sid,b.get("id"),admin)
        if action=="reply": return reply(cur,sid,b,admin)
        if action=="close": return close(cur,sid,b.get("id"),admin)
    raise ValueError("Invalid action")

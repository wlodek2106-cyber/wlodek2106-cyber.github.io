"""Private project room. No escrow, file hosting or live chat infrastructure."""
from student_business import clean,ident
from job_board import job_lock,cursor

def access(cur,sid,jid):
    client,status,selected=job_lock(cur,jid)
    if status not in ("assigned","delivered","completed") or selected is None: raise PermissionError("Room unavailable")
    cur.execute("SELECT student_id,quote_cents FROM academy_job_applications WHERE id=%s AND job_id=%s",(selected,jid))
    row=cur.fetchone()
    if not row or sid not in (client,row[0]): raise PermissionError("Room unavailable")
    return ("client" if sid==client else "freelancer"),status,row[1]

def room(cur,sid,b):
    jid=ident(b["id"]);role,status,quote=access(cur,sid,jid)
    cur.execute("SELECT id,title,done FROM academy_job_milestones WHERE job_id=%s ORDER BY id",(jid,))
    milestones=[{"id":i,"title":t,"done":d} for i,t,d in cur.fetchall()]
    cur.execute("SELECT id,role,kind,body,created_at FROM academy_job_messages WHERE job_id=%s AND id>%s ORDER BY id LIMIT 51",(jid,cursor(b)))
    rows=cur.fetchall()
    items=[{"id":i,"role":r,"kind":k,"body":t,"created_at":at.isoformat()} for i,r,k,t,at in rows[:50]]
    return {"role":role,"status":status,"quote_cents":quote,"milestones":milestones,"items":items,"next_after":items[-1]["id"] if len(rows)>50 else None}

def append(cur,jid,role,kind,body):
    cur.execute("SELECT count(*) FROM academy_job_messages WHERE job_id=%s",(jid,))
    count=cur.fetchone()[0]
    # Reserve room for delivery/revision records when ordinary chat limit is reached.
    if count >= (500 if kind=="message" else 550): raise ValueError("Room message limit reached")
    cur.execute("INSERT INTO academy_job_messages(job_id,role,kind,body) VALUES (%s,%s,%s,%s) RETURNING id",(jid,role,kind,body))
    return cur.fetchone()[0]

def message(cur,sid,b):
    jid=ident(b["id"]);role,status,_=access(cur,sid,jid)
    if status=="completed": raise PermissionError("Completed room is read-only")
    return {"id":append(cur,jid,role,"message",clean(b["body"],1600,True))}

def milestone(cur,sid,b):
    jid=ident(b["id"]);role,status,_=access(cur,sid,jid)
    if status!="assigned": raise PermissionError("Project not in progress")
    if b["action"]=="add":
        if role!="client": raise PermissionError()
        cur.execute("SELECT count(*) FROM academy_job_milestones WHERE job_id=%s",(jid,))
        if cur.fetchone()[0]>=20: raise ValueError("Milestone limit reached")
        cur.execute("INSERT INTO academy_job_milestones(job_id,title) VALUES (%s,%s) RETURNING id",(jid,clean(b["title"],160,True)))
        return {"id":cur.fetchone()[0]}
    if b["action"]!="set" or type(b.get("done")) is not bool: raise ValueError("Invalid milestone action")
    if role!="freelancer" and b["done"]: raise PermissionError("Freelancer marks milestones done")
    cur.execute("UPDATE academy_job_milestones SET done=%s WHERE id=%s AND job_id=%s RETURNING id",(b["done"],ident(b["milestone"]),jid))
    if not cur.fetchone(): raise PermissionError("Milestone unavailable")
    return {"saved":True}

def handoff(cur,sid,b):
    jid=ident(b["id"]);role,status,_=access(cur,sid,jid)
    action=b["action"]
    if action=="deliver" and role=="freelancer" and status=="assigned": target="delivered"
    elif action=="revise" and role=="client" and status=="delivered": target="assigned"
    else: raise PermissionError("Transition unavailable")
    body=clean(b["body"],1600,True)
    append(cur,jid,role,action,body)
    cur.execute("UPDATE academy_jobs SET status=%s,updated_at=now() WHERE id=%s",(target,jid))
    return {"status":target}

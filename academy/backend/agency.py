"""Private team coordination; no payment, marketplace reassignment, or client record sharing."""
import hashlib,secrets,re
from student_business import clean,ident

def lock(cur,sid,aid,owner=False):
    aid=ident(aid)
    cur.execute("SELECT owner_id,name FROM creator_agencies WHERE id=%s FOR UPDATE",(aid,))
    row=cur.fetchone()
    if not row: raise PermissionError("Agency unavailable")
    is_owner=row[0]==sid
    if owner and not is_owner: raise PermissionError("Owner required")
    cur.execute("SELECT 1 FROM creator_agency_members WHERE agency_id=%s AND student_id=%s",(aid,sid))
    if not cur.fetchone(): raise PermissionError("Membership required")
    return is_owner,row[1]

def create(cur,sid,b):
    name=clean(b["name"],120,True); alias=clean(b["alias"],80,True)
    cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
    if not cur.fetchone(): raise PermissionError()
    cur.execute("SELECT 1 FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL",(sid,))
    if not cur.fetchone(): raise PermissionError("Paid student required to create agency")
    cur.execute("SELECT count(*) FROM creator_agencies WHERE owner_id=%s",(sid,))
    if cur.fetchone()[0]>=5: raise ValueError("Agency limit reached")
    cur.execute("INSERT INTO creator_agencies(owner_id,name) VALUES (%s,%s) RETURNING id",(sid,name))
    aid=cur.fetchone()[0]
    cur.execute("INSERT INTO creator_agency_members(agency_id,student_id,alias) VALUES (%s,%s,%s)",(aid,sid,alias))
    return {"id":aid}

def listing(cur,sid):
    cur.execute("""SELECT a.id,a.name,a.owner_id=m.student_id FROM creator_agencies a
        JOIN creator_agency_members m ON m.agency_id=a.id WHERE m.student_id=%s ORDER BY a.id LIMIT 50""",(sid,))
    return {"items":[{"id":i,"name":n,"owner":o} for i,n,o in cur.fetchall()]}

def detail(cur,sid,aid):
    owner,name=lock(cur,sid,aid)
    cur.execute("SELECT student_id,alias FROM creator_agency_members WHERE agency_id=%s ORDER BY student_id",(aid,))
    members=[{"id":i,"alias":a,"self":i==sid} for i,a in cur.fetchall()]
    cur.execute("SELECT id,title,assignee_id,status,project_id,due_date,workflow_key,workflow_step,depends_on FROM creator_agency_tasks WHERE agency_id=%s ORDER BY id DESC",(aid,))
    tasks=[{"id":i,"title":t,"assignee":a,"status":s,"project":pid,"due":d.isoformat() if d else None,"workflow":wk,"step":step,"depends_on":dep} for i,t,a,s,pid,d,wk,step,dep in cur.fetchall()]
    from agency_finance import summary
    return {"id":aid,"name":name,"owner":owner,"members":members,"tasks":tasks,"finance":summary(cur,sid,aid,owner)}

def digest(code):
    if not isinstance(code,str) or not re.fullmatch(r"[A-Za-z0-9_-]{43}",code): raise ValueError("Invalid invitation")
    return hashlib.sha256(code.encode()).hexdigest()

def invite(cur,sid,aid):
    lock(cur,sid,aid,True)
    code=secrets.token_urlsafe(32)
    cur.execute("""INSERT INTO creator_agency_invites(agency_id,digest,expires_at) VALUES (%s,%s,now()+interval '24 hours')
        ON CONFLICT(agency_id) DO UPDATE SET digest=EXCLUDED.digest,expires_at=EXCLUDED.expires_at""",(aid,digest(code)))
    return {"code":code,"expires_hours":24,"single_use":True}

def join(cur,sid,b):
    if b.get("consent") is not True: raise ValueError("Consent required")
    hashed=digest(b["code"]);alias=clean(b["alias"],80,True)
    cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
    if not cur.fetchone(): raise PermissionError()
    cur.execute("SELECT agency_id FROM creator_agency_invites WHERE digest=%s AND expires_at>now()",(hashed,))
    row=cur.fetchone()
    if not row: raise PermissionError("Invitation unavailable")
    aid=row[0]
    cur.execute("SELECT id FROM creator_agencies WHERE id=%s FOR UPDATE",(aid,))
    if not cur.fetchone(): raise PermissionError()
    cur.execute("SELECT 1 FROM creator_agency_invites WHERE agency_id=%s AND digest=%s AND expires_at>now()",(aid,hashed))
    if not cur.fetchone(): raise PermissionError("Invitation unavailable")
    cur.execute("SELECT count(*) FROM creator_agency_members WHERE student_id=%s",(sid,))
    if cur.fetchone()[0]>=50: raise ValueError("Membership limit")
    cur.execute("SELECT count(*) FROM creator_agency_members WHERE agency_id=%s",(aid,))
    if cur.fetchone()[0]>=20: raise ValueError("Team limit")
    cur.execute("INSERT INTO creator_agency_members(agency_id,student_id,alias) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING RETURNING student_id",(aid,sid,alias))
    if not cur.fetchone(): raise ValueError("Already a member")
    cur.execute("DELETE FROM creator_agency_invites WHERE agency_id=%s",(aid,))
    return {"id":aid}

def remove(cur,sid,b):
    aid=ident(b["id"]); target=ident(b["member"])
    is_owner,_=lock(cur,sid,aid)
    if not is_owner and target!=sid: raise PermissionError()
    cur.execute("SELECT owner_id FROM creator_agencies WHERE id=%s",(aid,))
    if cur.fetchone()[0]==target: raise ValueError("Owner cannot leave")
    cur.execute("UPDATE creator_agency_tasks SET assignee_id=NULL WHERE agency_id=%s AND assignee_id=%s",(aid,target))
    cur.execute("DELETE FROM creator_agency_members WHERE agency_id=%s AND student_id=%s RETURNING student_id",(aid,target))
    if not cur.fetchone(): raise ValueError("Member unavailable")
    return {"removed":True}

def task(cur,sid,b):
    aid=ident(b["id"]);lock(cur,sid,aid,True)
    title=clean(b["title"],160,True);assignee=b.get("assignee")
    if assignee is not None:
        assignee=ident(assignee)
        cur.execute("SELECT 1 FROM creator_agency_members WHERE agency_id=%s AND student_id=%s",(aid,assignee))
        if not cur.fetchone(): raise PermissionError("Invalid assignee")
    cur.execute("SELECT count(*) FROM creator_agency_tasks WHERE agency_id=%s",(aid,))
    if cur.fetchone()[0]>=200: raise ValueError("Task limit")
    from agency_finance import due
    deadline=due(b.get("due"));pid=b.get("project")
    if pid is not None:
        pid=ident(pid)
        cur.execute("SELECT 1 FROM creator_agency_projects WHERE agency_id=%s AND id=%s",(aid,pid))
        if not cur.fetchone(): raise PermissionError("Project unavailable")
    cur.execute("INSERT INTO creator_agency_tasks(agency_id,title,assignee_id,project_id,due_date) VALUES (%s,%s,%s,%s,%s) RETURNING id",(aid,title,assignee,pid,deadline))
    return {"id":cur.fetchone()[0]}

def status(cur,sid,b):
    aid=ident(b["id"]);owner,_=lock(cur,sid,aid);tid=ident(b["task"]);state=b["status"]
    if state not in ("todo","doing","done"): raise ValueError("Invalid status")
    cur.execute("SELECT assignee_id,status,workflow_key,workflow_step,depends_on FROM creator_agency_tasks WHERE agency_id=%s AND id=%s",(aid,tid))
    row=cur.fetchone()
    if not row or (not owner and row[0]!=sid): raise PermissionError()
    if state==row[1]: return {"status":state}
    if row[2]:
        from agency_workflow import plan
        if plan(row[2])[row[3]-1]["review"] and state=="done" and not owner:
            raise PermissionError("Owner approval required")
        if state in ("doing","done") and row[4] is not None:
            cur.execute("SELECT status FROM creator_agency_tasks WHERE id=%s AND agency_id=%s",(row[4],aid))
            prev=cur.fetchone()
            if not prev or prev[0]!="done": raise ValueError("Previous step incomplete")
        if row[1]=="done" and state!="done":
            cur.execute("SELECT 1 FROM creator_agency_tasks WHERE agency_id=%s AND depends_on=%s AND status!='todo'",(aid,tid))
            if cur.fetchone(): raise ValueError("Reset later steps first")
    cur.execute("UPDATE creator_agency_tasks SET status=%s WHERE agency_id=%s AND id=%s",(state,aid,tid))
    return {"status":state}

def dispatch(token,action,b):
    from accounts import authenticate
    from database import transaction
    sid=authenticate(token)
    if sid is None: raise PermissionError()
    with transaction() as cur:
        if action=="list": return listing(cur,sid)
        if action=="create": return create(cur,sid,b)
        if action=="detail": return detail(cur,sid,b["id"])
        if action=="invite": return invite(cur,sid,b["id"])
        if action=="join": return join(cur,sid,b)
        if action=="remove": return remove(cur,sid,b)
        if action=="task": return task(cur,sid,b)
        if action=="status": return status(cur,sid,b)
        if action in ("knowledge","knowledge-save"):
            from agency_knowledge import get,save
            return (get if action=="knowledge" else save)(cur,sid,b)
        if action in ("workflow","assign"):
            from agency_workflow import create as workflow_create,assign
            return (workflow_create if action=="workflow" else assign)(cur,sid,b)
        if action in ("project","reward"):
            from agency_finance import project,reward
            return (project if action=="project" else reward)(cur,sid,b)
        raise ValueError("Invalid action")

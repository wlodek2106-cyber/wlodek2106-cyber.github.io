"""Owner-only operational incident history. No automatic remediation."""
from student_business import clean,ident
from system_monitor import GROUPS
STATES=("detected","investigating","mitigated","resolved")
LEVELS=("normal","high","urgent")
TRANSITIONS={"detected":("investigating",),"investigating":("mitigated","resolved"),"mitigated":("investigating","resolved"),"resolved":("investigating",)}
def validate_transition(current,target,verified):
    if not isinstance(target,str) or target not in TRANSITIONS.get(current,()): raise ValueError("Invalid transition")
    if target=="resolved" and verified is not True: raise ValueError("Verification required")

def create(cur,b):
    module=b.get("module");level=b.get("severity")
    if not isinstance(module,str) or module not in GROUPS or not isinstance(level,str) or level not in LEVELS: raise ValueError("Invalid classification")
    title=clean(b.get("title"),120,True);note=clean(b.get("note"),2000,True)
    if b.get("consent") is not True: raise ValueError("Consent required")
    cur.execute("SELECT pg_advisory_xact_lock(77261501)")
    cur.execute("SELECT count(*) FROM system_incidents")
    if cur.fetchone()[0]>=1000: raise ValueError("Incident limit")
    cur.execute("INSERT INTO system_incidents(module,severity,title) VALUES (%s,%s,%s) RETURNING id",(module,level,title))
    iid=cur.fetchone()[0]
    cur.execute("INSERT INTO system_incident_events(incident_id,state,note,verified) VALUES (%s,'detected',%s,false)",(iid,note))
    return {"id":iid,"revision":1}

def listing(cur,b):
    before=b.get("before");state=b.get("state")
    if before is not None: ident(before)
    if state is not None and (not isinstance(state,str) or state not in STATES): raise ValueError("Invalid state")
    cur.execute("""SELECT id,module,severity,title,state,revision,updated_at FROM system_incidents
      WHERE (%s::bigint IS NULL OR id<%s) AND (%s::text IS NULL OR state=%s) ORDER BY id DESC LIMIT 31""",(before,before,state,state))
    rows=cur.fetchall()
    items=[{"id":i,"module":m,"severity":v,"title":t,"state":s,"revision":r,"updated_at":d.isoformat()} for i,m,v,t,s,r,d in rows[:30]]
    return {"items":items,"next_before":items[-1]["id"] if len(rows)>30 else None}

def detail(cur,iid):
    cur.execute("SELECT module,severity,title,state,revision FROM system_incidents WHERE id=%s FOR SHARE",(ident(iid),))
    row=cur.fetchone()
    if not row: raise ValueError("Incident unavailable")
    m,v,t,s,r=row
    cur.execute("SELECT state,note,verified,created_at FROM system_incident_events WHERE incident_id=%s ORDER BY id",(iid,))
    return {"id":iid,"module":m,"severity":v,"title":t,"state":s,"revision":r,"events":[{"state":k,"note":n,"verified":f,"at":d.isoformat()} for k,n,f,d in cur.fetchall()]}

def advance(cur,b):
    iid=ident(b.get("id"));revision=ident(b.get("revision"));note=clean(b.get("note"),2000,True)
    if b.get("consent") is not True: raise ValueError("Consent required")
    cur.execute("SELECT state,revision FROM system_incidents WHERE id=%s FOR UPDATE",(iid,))
    row=cur.fetchone()
    if not row or row[1]!=revision: raise ValueError("Stale incident")
    if revision>=100: raise ValueError("Event limit")
    target=b.get("state");verified=b.get("verified",False)
    if type(verified) is not bool: raise ValueError("Invalid verification")
    validate_transition(row[0],target,verified)
    cur.execute("UPDATE system_incidents SET state=%s,revision=revision+1,updated_at=now() WHERE id=%s",(target,iid))
    cur.execute("INSERT INTO system_incident_events(incident_id,state,note,verified) VALUES (%s,%s,%s,%s)",(iid,target,note,verified if target=="resolved" else False))
    return {"revision":revision+1}

def dispatch(token,action,b):
    from partners import owner
    from database import transaction
    owner(token)
    with transaction() as cur:
        if action=="list": return listing(cur,b)
        if action=="create": return create(cur,b)
        if action=="detail": return detail(cur,b.get("id"))
        if action=="advance": return advance(cur,b)
    raise ValueError("Invalid action")

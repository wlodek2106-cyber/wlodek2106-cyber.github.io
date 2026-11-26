"""Team-shared project notes. Only the owner can change them; all current members may read."""
from student_business import ident,clean

def get(cur,sid,b):
    from agency import lock
    aid,pid=ident(b["id"]),ident(b["project"])
    owner,_=lock(cur,sid,aid)
    cur.execute("SELECT 1 FROM creator_agency_projects WHERE agency_id=%s AND id=%s",(aid,pid))
    if not cur.fetchone(): raise PermissionError("Project unavailable")
    cur.execute("SELECT content,revision,updated_at FROM creator_agency_knowledge WHERE project_id=%s",(pid,))
    row=cur.fetchone()
    return {"content":row[0] if row else "", "revision":row[1] if row else 0,
            "updated_at":row[2].isoformat() if row else None,"owner":owner}

def save(cur,sid,b):
    from agency import lock
    aid,pid=ident(b["id"]),ident(b["project"]);lock(cur,sid,aid,True)
    prior=get(cur,sid,b)
    rev=b["revision"]
    if type(rev) is not int or rev!=prior["revision"]: raise ValueError("Refresh stale note")
    content=clean(b["content"],3000)
    if not content:
        cur.execute("DELETE FROM creator_agency_knowledge WHERE project_id=%s",(pid,))
        return {"deleted":True}
    if b.get("consent") is not True: raise ValueError("Sharing consent required")
    cur.execute("""INSERT INTO creator_agency_knowledge(project_id,content,revision) VALUES (%s,%s,1)
        ON CONFLICT(project_id) DO UPDATE SET content=EXCLUDED.content,revision=creator_agency_knowledge.revision+1,updated_at=now()""",(pid,content))
    return {"saved":True}

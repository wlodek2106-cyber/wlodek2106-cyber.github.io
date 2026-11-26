"""Read-only command center: own learning and authorized agency summaries."""
from datetime import datetime,timezone
from accounts import authenticate
from database import transaction
from learning import student_progress

def agency_snapshot(cur,sid):
    cur.execute("""SELECT a.id,a.name,a.owner_id=m.student_id,
      (SELECT count(*) FROM creator_agency_projects p WHERE p.agency_id=a.id),
      (SELECT count(*) FROM creator_agency_tasks t WHERE t.agency_id=a.id),
      (SELECT count(*) FROM creator_agency_tasks t WHERE t.agency_id=a.id AND t.status='done'),
      (SELECT count(*) FROM creator_agency_tasks t WHERE t.agency_id=a.id AND t.status<>'done' AND t.assignee_id=%s)
      FROM creator_agencies a JOIN creator_agency_members m ON m.agency_id=a.id
      WHERE m.student_id=%s ORDER BY a.id LIMIT 50""",(sid,sid))
    agencies=[{"id":i,"name":n,"owner":o,"projects":p,"tasks":t,"done":d,"assigned_open":x} for i,n,o,p,t,d,x in cur.fetchall()]
    cur.execute("""SELECT t.id,t.agency_id,t.title,t.status,t.due_date,
        t.depends_on IS NOT NULL AND NOT EXISTS
          (SELECT 1 FROM creator_agency_tasks p WHERE p.id=t.depends_on AND p.agency_id=t.agency_id AND p.status='done')
        FROM creator_agency_tasks t JOIN creator_agency_members m ON m.agency_id=t.agency_id
        WHERE m.student_id=%s AND t.assignee_id=%s AND t.status<>'done'
        ORDER BY t.due_date ASC NULLS LAST,t.id ASC LIMIT 20""",(sid,sid))
    tasks=[{"id":i,"agency":a,"title":t,"status":s,"due":d.isoformat() if d else None,"blocked":b} for i,a,t,s,d,b in cur.fetchall()]
    return {"agencies":agencies,"tasks":tasks}

def report(token):
    sid=authenticate(token)
    if sid is None: raise PermissionError("Authentication required")
    progress=student_progress(token)
    lessons=progress["lessons"]
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        data=agency_snapshot(cur,sid)
    return {"private":True,"as_of":datetime.now(timezone.utc).isoformat(),
        "learning":{"completed":sum(x["completed"] for x in lessons),"total":len(lessons),
        "available":sum(x["unlocked"] for x in lessons),
        "next":next((x["day"] for x in lessons if x["unlocked"] and not x["completed"]),None),
        "access":progress["access"],"trial":progress["trial"],"owner_preview":progress["owner_preview"]},
        **data}

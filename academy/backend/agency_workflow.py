"""Sequential agency plans; no external execution or spending."""
from student_business import ident
TEMPLATES={"video":[0,1,2,3,4,5],"advertising":[0,6,7,8,9,5],"design":[0,7,2,10,5],"agents":[0,11,12,13,14,5],"website":[0,11,7,15,13,5]}
TITLES=["Brief and acceptance criteria","Script and storyboard","Visual production","Animation and editing","Voice and audio","Human review and approval","Audience research","Creative concept","Advertising assets","Advertising copy","Export deliverables","Architecture","Prototype","Testing and fixes","Documentation and handoff","Build website"]
TOOLS=["","/creator-suite","/design-studio","/animation-studio","/voice-studio","","/creator-suite","/design-studio","/animation-studio","/creator-suite","/local-media","/automation-studio","/automation-studio","/automation-studio","/creator-suite","/website-builder"]
def plan(key):
    if not isinstance(key,str) or key not in TEMPLATES: raise ValueError("Invalid workflow")
    return [{"title":TITLES[k],"tool":TOOLS[k],"step":i+1,"review":k==5} for i,k in enumerate(TEMPLATES[key])]

def create(cur,sid,b):
    from agency import lock
    aid=ident(b["id"]);pid=ident(b["project"]);key=b["template"];steps=plan(key)
    lock(cur,sid,aid,True)
    cur.execute("SELECT 1 FROM creator_agency_projects WHERE agency_id=%s AND id=%s",(aid,pid))
    if not cur.fetchone(): raise PermissionError("Project unavailable")
    assignee=b.get("assignee")
    if assignee is not None:
        assignee=ident(assignee)
        cur.execute("SELECT 1 FROM creator_agency_members WHERE agency_id=%s AND student_id=%s",(aid,assignee))
        if not cur.fetchone(): raise PermissionError("Member unavailable")
    cur.execute("SELECT 1 FROM creator_agency_tasks WHERE agency_id=%s AND project_id=%s AND workflow_key=%s",(aid,pid,key))
    if cur.fetchone(): raise ValueError("Workflow exists")
    cur.execute("SELECT count(*) FROM creator_agency_tasks WHERE agency_id=%s",(aid,))
    if cur.fetchone()[0]+len(steps)>200: raise ValueError("Task limit")
    prev=None
    for step in steps:
        cur.execute("""INSERT INTO creator_agency_tasks(agency_id,title,assignee_id,project_id,workflow_key,workflow_step,depends_on)
            VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
            (aid,step["title"],sid if step["review"] else assignee,pid,key,step["step"],prev))
        prev=cur.fetchone()[0]
    return {"created":len(steps),"automatic_execution":False}

def assign(cur,sid,b):
    from agency import lock
    aid=ident(b["id"]);tid=ident(b["task"]);lock(cur,sid,aid,True)
    assignee=b.get("assignee")
    if assignee is not None:
        assignee=ident(assignee)
        cur.execute("SELECT 1 FROM creator_agency_members WHERE agency_id=%s AND student_id=%s",(aid,assignee))
        if not cur.fetchone(): raise PermissionError("Member unavailable")
    cur.execute("UPDATE creator_agency_tasks SET assignee_id=%s WHERE agency_id=%s AND id=%s RETURNING id",(assignee,aid,tid))
    if not cur.fetchone(): raise PermissionError("Task unavailable")
    return {"saved":True}

"""Agency project budgets and manual reward bookkeeping. No payment execution."""
from datetime import date,datetime,timezone
from student_business import clean,ident,cents

def due(v):
    if v in ("",None): return None
    if not isinstance(v,str) or len(v)!=10: raise ValueError("Invalid due date")
    d=date.fromisoformat(v)
    if not 2000<=d.year<=2100: raise ValueError("Invalid due date")
    return d

def project(cur,sid,b):
    from agency import lock
    aid=ident(b["id"]);lock(cur,sid,aid,True)
    title=clean(b["title"],160,True);deadline=due(b.get("due"))
    budget,received,expense=(cents(b[k]) for k in ("budget","received","expense"))
    if received>budget: raise ValueError("Receipts exceed budget")
    if b.get("project") is None:
        cur.execute("SELECT count(*) FROM creator_agency_projects WHERE agency_id=%s",(aid,))
        if cur.fetchone()[0]>=100: raise ValueError("Project limit")
        cur.execute("INSERT INTO creator_agency_projects(agency_id,title,due_date,budget_cents,received_cents,expense_cents) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",(aid,title,deadline,budget,received,expense))
    else:
        pid=ident(b["project"])
        cur.execute("UPDATE creator_agency_projects SET title=%s,due_date=%s,budget_cents=%s,received_cents=%s,expense_cents=%s WHERE id=%s AND agency_id=%s RETURNING id",(title,deadline,budget,received,expense,pid,aid))
    row=cur.fetchone()
    if not row: raise PermissionError("Project unavailable")
    return {"id":row[0]}

def reward(cur,sid,b):
    from agency import lock
    aid=ident(b["id"]);lock(cur,sid,aid,True)
    pid,member=ident(b["project"]),ident(b["member"])
    agreed,paid=cents(b["agreed"]),cents(b["paid"])
    if paid>agreed: raise ValueError("Paid exceeds agreed")
    cur.execute("SELECT 1 FROM creator_agency_projects WHERE id=%s AND agency_id=%s",(pid,aid))
    if not cur.fetchone(): raise PermissionError("Project unavailable")
    cur.execute("""SELECT 1 FROM creator_agency_members WHERE agency_id=%s AND student_id=%s
      UNION ALL SELECT 1 FROM creator_agency_rewards WHERE project_id=%s AND student_id=%s LIMIT 1""",(aid,member,pid,member))
    if not cur.fetchone(): raise PermissionError("Member unavailable")
    cur.execute("""INSERT INTO creator_agency_rewards(project_id,student_id,agreed_cents,paid_cents) VALUES (%s,%s,%s,%s)
        ON CONFLICT(project_id,student_id) DO UPDATE SET agreed_cents=EXCLUDED.agreed_cents,paid_cents=EXCLUDED.paid_cents""",(pid,member,agreed,paid))
    return {"saved":True,"manual":True}

def summary(cur,sid,aid,owner):
    today=datetime.now(timezone.utc).date()
    cur.execute("SELECT id,title,due_date,budget_cents,received_cents,expense_cents FROM creator_agency_projects WHERE agency_id=%s ORDER BY id DESC",(aid,))
    projects=[]
    for pid,title,d,b,r,e in cur.fetchall():
        projects.append({"id":pid,"title":title,"due":d.isoformat() if d else None,**({"budget_cents":b,"received_cents":r,"expense_cents":e} if owner else {})})
    cur.execute("""SELECT r.project_id,r.student_id,r.agreed_cents,r.paid_cents
        FROM creator_agency_rewards r JOIN creator_agency_projects p ON p.id=r.project_id
        WHERE p.agency_id=%s AND (%s OR r.student_id=%s) ORDER BY r.project_id,r.student_id""",(aid,owner,sid))
    rewards=[{"project":p,"member":m,"agreed_cents":a,"paid_cents":b} for p,m,a,b in cur.fetchall()]
    if owner:
        for p in projects:
            rows=[r for r in rewards if r["project"]==p["id"]]
            agreed=sum(r["agreed_cents"] for r in rows);paid=sum(r["paid_cents"] for r in rows)
            p.update(rewards_agreed_cents=agreed,rewards_paid_cents=paid,
                     projected_margin_cents=p["budget_cents"]-p["expense_cents"]-agreed,
                     cash_margin_cents=p["received_cents"]-p["expense_cents"]-paid)
    return {"projects":projects,"rewards":rewards,"as_of":today.isoformat(),"manual":True}

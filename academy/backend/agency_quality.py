"""Human-recorded quality evidence, not automatic file inspection or certification."""
from student_business import ident,clean
FIELDS=tuple(["scope","accuracy","technical","rights","privacy","delivery"])
STATES=("unchecked","pass","fail")
def validate(checks,evidence):
    if not isinstance(checks,dict) or set(checks)!=set(FIELDS) or any(not isinstance(v,str) or v not in STATES for v in checks.values()):
        raise ValueError("Invalid checks")
    evidence=clean(evidence,2000,True)
    return {"checks":dict(checks),"evidence":evidence,"ready":all(checks[k]=="pass" for k in FIELDS)}
def get(cur,sid,b):
    from agency import lock
    from agency_workflow import plan
    aid,tid=ident(b["id"]),ident(b["task"]);owner,_=lock(cur,sid,aid)
    cur.execute("SELECT workflow_key,workflow_step,status FROM creator_agency_tasks WHERE agency_id=%s AND id=%s",(aid,tid))
    row=cur.fetchone()
    if not row or not row[0] or not plan(row[0])[row[1]-1]["review"]: raise PermissionError("Review unavailable")
    cur.execute("SELECT checks,evidence,updated_at FROM creator_agency_quality WHERE task_id=%s",(tid,))
    note=cur.fetchone()
    return {"owner":owner,"status":row[2],"report":dict(validate(note[0],note[1]),updated_at=note[2].isoformat()) if note else None}
def save(cur,sid,b):
    from agency import lock
    from psycopg.types.json import Jsonb
    aid,tid=ident(b["id"]),ident(b["task"]);lock(cur,sid,aid,True)
    prior=get(cur,sid,b)
    if prior["status"]=="done": raise ValueError("Reopen before editing")
    if b.get("consent") is not True: raise ValueError("Human review acknowledgement required")
    report=validate(b["checks"],b["evidence"])
    cur.execute("""INSERT INTO creator_agency_quality(task_id,checks,evidence) VALUES (%s,%s,%s)
        ON CONFLICT(task_id) DO UPDATE SET checks=EXCLUDED.checks,evidence=EXCLUDED.evidence,updated_at=now()""",
        (tid,Jsonb(report["checks"]),report["evidence"]))
    return report
def require_ready(cur,tid):
    cur.execute("SELECT checks,evidence FROM creator_agency_quality WHERE task_id=%s",(tid,))
    row=cur.fetchone()
    if not row or not validate(*row)["ready"]: raise ValueError("Complete human quality review first")

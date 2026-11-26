"""Manual recovery evidence; no commands, credentials, deploys or payment actions."""
from student_business import ident,clean
CHECKS=("scope","cause","change_review","smoke_test","followup")

def validate(checks,evidence,consent):
    if not isinstance(checks,dict) or set(checks)!=set(CHECKS) or any(type(v) is not bool for v in checks.values()):
        raise ValueError("Invalid recovery checklist")
    if consent is not True: raise ValueError("Consent required")
    return clean(evidence,2000,True)

def read(cur,iid,revision):
    cur.execute("SELECT version,checks,evidence,updated_at FROM system_incident_recovery WHERE incident_id=%s AND incident_revision=%s",(iid,revision))
    row=cur.fetchone()
    if not row:return None
    v,c,e,at=row
    return {"version":v,"checks":c,"evidence":e,"at":at.isoformat(),"incident_revision":revision}

def save(cur,b):
    iid=ident(b.get("id"));rev=ident(b.get("revision"));v=b.get("version")
    if type(v) is not int or not 0<=v<100: raise ValueError("Invalid checklist version")
    checks=b.get("checks");evidence=validate(checks,b.get("evidence"),b.get("consent"))
    cur.execute("SELECT state,revision FROM system_incidents WHERE id=%s FOR UPDATE",(iid,))
    row=cur.fetchone()
    if not row or row[1]!=rev or row[0] not in ("investigating","mitigated"): raise ValueError("Incident is not ready or has changed")
    old=read(cur,iid,rev)
    if (old["version"] if old else 0)!=v: raise ValueError("Stale recovery checklist")
    from psycopg.types.json import Jsonb
    cur.execute("""INSERT INTO system_incident_recovery(incident_id,incident_revision,version,checks,evidence)
       VALUES (%s,%s,%s,%s,%s) ON CONFLICT(incident_id,incident_revision) DO UPDATE
       SET version=EXCLUDED.version,checks=EXCLUDED.checks,evidence=EXCLUDED.evidence,updated_at=now()""",
       (iid,rev,v+1,Jsonb(checks),evidence))
    return {"version":v+1}

def require_ready(cur,iid,revision):
    row=read(cur,iid,revision)
    if not row or set(row["checks"])!=set(CHECKS) or any(row["checks"][k] is not True for k in CHECKS):
        raise ValueError("Complete recovery checklist for current incident revision")

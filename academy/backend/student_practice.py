"""Private cross-device introductory practice draft. No exam or publication side effects."""
import json

def validate(body):
    if not isinstance(body,dict):raise ValueError("Invalid draft")
    fields=body.get("fields");checks=body.get("checks");revision=body.get("revision")
    if type(revision) is not int or not 0<=revision<2147483647:raise ValueError("Invalid revision")
    if not isinstance(fields,list) or len(fields)!=4 or any(not isinstance(x,str) or len(x)>1200 or "\x00" in x for x in fields):raise ValueError("Invalid fields")
    if not isinstance(checks,list) or len(checks)!=3 or any(type(x) is not bool for x in checks):raise ValueError("Invalid checks")
    device=body.get("device")
    if device not in ("phone","computer","gpu","cuda"):raise ValueError("Invalid device")
    data={"fields":fields,"checks":checks,"device":device}
    if len(json.dumps(data,ensure_ascii=False).encode("utf-8"))>22000:raise ValueError("Draft too large")
    return revision,data

def read(cur,sid):
    cur.execute("SELECT payload,revision,updated_at FROM student_practice_drafts WHERE student_id=%s",(sid,))
    row=cur.fetchone()
    if not row:return {"revision":0,"draft":None}
    return {"draft":row[0],"revision":row[1],"updated_at":row[2].isoformat()}

def save(cur,sid,body):
    revision,data=validate(body)
    if revision==0:
        cur.execute("""INSERT INTO student_practice_drafts(student_id,payload,revision) VALUES (%s,%s::jsonb,1)
            ON CONFLICT(student_id) DO NOTHING RETURNING revision""",(sid,json.dumps(data,ensure_ascii=False)))
    else:
        cur.execute("""UPDATE student_practice_drafts SET payload=%s::jsonb,revision=revision+1,updated_at=now()
            WHERE student_id=%s AND revision=%s RETURNING revision""",(json.dumps(data,ensure_ascii=False),sid,revision))
    row=cur.fetchone()
    if not row:return {"saved":False,"conflict":True}
    return {"saved":True,"revision":row[0]}

def dispatch(token,action,body):
    from accounts import authenticate
    from database import transaction
    sid=authenticate(token)
    if sid is None:raise PermissionError("Authentication required")
    with transaction() as cur:
        if action=="read":return read(cur,sid)
        if action=="save":return save(cur,sid,body)
    raise ValueError("Invalid action")

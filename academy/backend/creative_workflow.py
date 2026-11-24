"""Private production checklists, no model execution or asset uploads."""
import json
from pathlib import Path
from knowledge import student
from database import transaction
from student_business import clean,ident
TEMPLATES=json.loads(Path(__file__).with_name("workflow_templates.json").read_text())
def values(b):
    title=clean(b["title"],160,True)
    kind=b["kind"]
    if kind not in TEMPLATES: raise ValueError("Invalid workflow type")
    brief=clean(b["brief"],2000,True)
    completed=b.get("completed",[])
    ids={x["id"] for x in TEMPLATES[kind]}
    if not isinstance(completed,list) or any(not isinstance(x,str) or x not in ids for x in completed) or len(completed)!=len(set(completed)): raise ValueError("Invalid stages")
    notes=clean(b.get("notes",""),1000)
    return title,kind,brief,completed,notes
def save(cur,sid,b):
    v=values(b)
    if b.get("id") is None:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
        cur.execute("SELECT count(*) FROM creative_workflows WHERE student_id=%s",(sid,))
        if cur.fetchone()[0]>=100: raise ValueError("Workflow limit reached")
        cur.execute("INSERT INTO creative_workflows(student_id,title,kind,brief,completed,notes) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",(sid,*v))
    else:
        cur.execute("UPDATE creative_workflows SET title=%s,kind=%s,brief=%s,completed=%s,notes=%s,updated_at=now() WHERE student_id=%s AND id=%s RETURNING id",(*v,sid,ident(b["id"])))
    row=cur.fetchone()
    if not row: raise PermissionError("Workflow unavailable")
    return {"id":row[0]}
def listing(cur,sid,after=0):
    if type(after) is not int or not 0<=after<=9223372036854775807: raise ValueError("Invalid cursor")
    cur.execute("SELECT id,title,kind,brief,completed,notes,updated_at FROM creative_workflows WHERE student_id=%s AND id>%s ORDER BY id LIMIT 21",(sid,after))
    rows=cur.fetchall()
    items=[{"id":i,"title":t,"kind":k,"brief":b,"completed":c,"notes":n,"updated_at":u.isoformat()} for i,t,k,b,c,n,u in rows[:20]]
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>20 else None,"templates":TEMPLATES}
def remove(cur,sid,id):
    cur.execute("DELETE FROM creative_workflows WHERE student_id=%s AND id=%s RETURNING id",(sid,ident(id)))
    if not cur.fetchone(): raise PermissionError("Workflow unavailable")
    return {"deleted":True}
def dispatch(token,action,b):
    sid=student(token)
    with transaction() as cur:
        if action=="list": return listing(cur,sid,b.get("after",0))
        if action=="save": return save(cur,sid,b)
        if action=="delete": return remove(cur,sid,b["id"])
    raise ValueError("Invalid action")

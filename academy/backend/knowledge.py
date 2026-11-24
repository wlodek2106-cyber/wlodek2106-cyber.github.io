"""Private notebooks and bounded text search. No embeddings or remote AI."""
from accounts import authenticate
from database import transaction
from student_business import clean,ident
from learning import require_lesson
def student(token):
    sid=authenticate(token)
    if sid is None: raise PermissionError("Authentication required")
    return sid
def save(cur,sid,b):
    title=clean(b["title"],160,True)
    content=clean(b["content"],3000,True)
    if len(content.encode("utf-8"))>11000: raise ValueError("Note too large")
    tag=clean(b.get("tag",""),80)
    if b.get("id") is None:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
        cur.execute("SELECT count(*) FROM knowledge_notes WHERE student_id=%s",(sid,))
        if cur.fetchone()[0]>=200: raise ValueError("Note limit reached")
        cur.execute("INSERT INTO knowledge_notes(student_id,title,content,tag) VALUES (%s,%s,%s,%s) RETURNING id",(sid,title,content,tag))
    else:
        cur.execute("UPDATE knowledge_notes SET title=%s,content=%s,tag=%s,updated_at=now() WHERE id=%s AND student_id=%s RETURNING id",(title,content,tag,ident(b["id"]),sid))
    row=cur.fetchone()
    if not row: raise PermissionError("Note unavailable")
    return {"id":row[0]}
def remove(cur,sid,id):
    cur.execute("DELETE FROM knowledge_notes WHERE id=%s AND student_id=%s RETURNING id",(ident(id),sid))
    if not cur.fetchone(): raise PermissionError("Note unavailable")
    return {"deleted":True}
def list_notes(cur,sid,query="",after=0):
    query=clean(query,120)
    if type(after) is not int or not 0<=after<=9223372036854775807: raise ValueError("Invalid cursor")
    cur.execute("""SELECT id,title,content,tag,updated_at FROM knowledge_notes WHERE student_id=%s AND id>%s
    AND (%s='' OR strpos(lower(title||' '||content||' '||tag),lower(%s))>0) ORDER BY id LIMIT 21""",(sid,after,query,query))
    rows=cur.fetchall()
    items=[{"id":i,"title":t,"content":c,"tag":g,"updated_at":u.isoformat()} for i,t,c,g,u in rows[:20]]
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>20 else None}
def public_text(lesson):
    """Only allow-listed instructional fields; never serialize exam questions/keys."""
    out=[]
    for key in ("title","theory","sections","assignment","prompts"):
        value=lesson.get(key)
        if isinstance(value,str): out.append(value)
        elif isinstance(value,list): out.extend(v for v in value if isinstance(v,str))
    return "\n\n".join(out)
def dispatch_notes(token,action,b):
    sid=student(token)
    with transaction() as cur:
        if action=="list": return list_notes(cur,sid,b.get("query",""),b.get("after",0))
        if action=="save": return save(cur,sid,b)
        if action=="delete": return remove(cur,sid,b["id"])
    raise ValueError("Invalid action")

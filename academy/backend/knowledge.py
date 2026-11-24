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
    folder=clean(b.get("folder",""),80)
    favorite=b.get("favorite",False)
    if type(favorite) is not bool: raise ValueError("Invalid favorite")
    if b.get("id") is None:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
        cur.execute("SELECT count(*) FROM knowledge_notes WHERE student_id=%s",(sid,))
        if cur.fetchone()[0]>=200: raise ValueError("Note limit reached")
        cur.execute("INSERT INTO knowledge_notes(student_id,title,content,tag,folder,favorite) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",(sid,title,content,tag,folder,favorite))
    else:
        cur.execute("UPDATE knowledge_notes SET title=%s,content=%s,tag=%s,folder=%s,favorite=%s,updated_at=now() WHERE id=%s AND student_id=%s RETURNING id",(title,content,tag,folder,favorite,ident(b["id"]),sid))
    row=cur.fetchone()
    if not row: raise PermissionError("Note unavailable")
    return {"id":row[0]}
def remove(cur,sid,id):
    cur.execute("DELETE FROM knowledge_notes WHERE id=%s AND student_id=%s RETURNING id",(ident(id),sid))
    if not cur.fetchone(): raise PermissionError("Note unavailable")
    return {"deleted":True}
def note_item(row):
    i,t,c,g,u,f,v=row
    return {"id":i,"title":t,"content":c,"tag":g,"updated_at":u.isoformat(),"folder":f,"favorite":v}
def list_notes(cur,sid,query="",after=0,folder="",favorite=False,all_words=False):
    query=clean(query,120)
    folder=clean(folder,80)
    if type(favorite) is not bool or type(all_words) is not bool: raise ValueError("Invalid filters")
    if type(after) is not int or not 0<=after<=9223372036854775807: raise ValueError("Invalid cursor")
    terms=query.split() if all_words else ([query] if query else [])
    cur.execute("""SELECT id,title,content,tag,updated_at,folder,favorite FROM knowledge_notes WHERE student_id=%s AND id>%s
    AND (%s='' OR folder=%s) AND (NOT %s OR favorite)
    AND NOT EXISTS (SELECT 1 FROM unnest(%s::text[]) AS q(term)
       WHERE strpos(lower(title||' '||content||' '||tag||' '||folder),lower(q.term))=0)
    ORDER BY id LIMIT 21""",(sid,after,folder,folder,favorite,terms))
    rows=cur.fetchall()
    items=[note_item(r) for r in rows[:20]]
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>20 else None}
def folders(cur,sid):
    cur.execute("SELECT DISTINCT folder FROM knowledge_notes WHERE student_id=%s AND folder<>'' ORDER BY folder LIMIT 200",(sid,))
    return {"items":[r[0] for r in cur.fetchall()]}
def export_notes(cur,sid):
    cur.execute("SELECT id,title,content,tag,updated_at,folder,favorite FROM knowledge_notes WHERE student_id=%s ORDER BY id LIMIT 200",(sid,))
    return {"version":1,"items":[note_item(r) for r in cur.fetchall()]}
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
        if action=="list": return list_notes(cur,sid,b.get("query",""),b.get("after",0),b.get("folder",""),b.get("favorite",False),b.get("all_words",False))
        if action=="folders": return folders(cur,sid)
        if action=="export": return export_notes(cur,sid)
        if action=="save": return save(cur,sid,b)
        if action=="delete": return remove(cur,sid,b["id"])
    raise ValueError("Invalid action")

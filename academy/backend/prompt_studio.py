"""Private prompt library; templates are plain text, no inference or tool execution."""
import json
from pathlib import Path
from knowledge import student
from database import transaction
from student_business import clean,ident
CATEGORIES=("image","video","advertising","animation","audio","agent","other")
def values(b):
    title=clean(b["title"],160,True)
    prompt=clean(b["prompt"],3000,True)
    if len(prompt.encode("utf-8"))>11000: raise ValueError("Prompt too large")
    category=b["category"]
    favorite=b.get("favorite",False)
    if category not in CATEGORIES or type(favorite) is not bool: raise ValueError("Invalid category or favorite")
    return title,prompt,category,favorite
def save(cur,sid,b):
    v=values(b)
    if b.get("id") is None:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
        cur.execute("SELECT count(*) FROM student_prompts WHERE student_id=%s",(sid,))
        if cur.fetchone()[0]>=200: raise ValueError("Prompt limit reached")
        cur.execute("INSERT INTO student_prompts(student_id,title,prompt,category,favorite) VALUES (%s,%s,%s,%s,%s) RETURNING id",(sid,*v))
    else:
        cur.execute("UPDATE student_prompts SET title=%s,prompt=%s,category=%s,favorite=%s,updated_at=now() WHERE student_id=%s AND id=%s RETURNING id",(*v,sid,ident(b["id"])))
    row=cur.fetchone()
    if not row: raise PermissionError("Prompt unavailable")
    return {"id":row[0]}
def remove(cur,sid,id):
    cur.execute("DELETE FROM student_prompts WHERE student_id=%s AND id=%s RETURNING id",(sid,ident(id)))
    if not cur.fetchone(): raise PermissionError("Prompt unavailable")
    return {"deleted":True}
def listing(cur,sid,b):
    query=clean(b.get("query",""),120)
    category=b.get("category","")
    favorite=b.get("favorite",False)
    after=b.get("after",0)
    if category not in ("",*CATEGORIES) or type(favorite) is not bool or type(after) is not int or not 0<=after<=9223372036854775807: raise ValueError("Invalid filter")
    cur.execute("""SELECT id,title,prompt,category,favorite,updated_at FROM student_prompts
    WHERE student_id=%s AND id>%s AND (%s='' OR category=%s) AND (NOT %s OR favorite)
    AND (%s='' OR strpos(lower(title||' '||prompt),lower(%s))>0) ORDER BY id LIMIT 21""",(sid,after,category,category,favorite,query,query))
    rows=cur.fetchall()
    items=[{"id":i,"title":t,"prompt":p,"category":c,"favorite":f,"updated_at":u.isoformat()} for i,t,p,c,f,u in rows[:20]]
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>20 else None}
def dispatch(token,action,b):
    sid=student(token)
    if action=="templates": return {"items":json.loads(Path(__file__).with_name("prompt_templates.json").read_text()),"language":"en"}
    with transaction() as cur:
        if action=="list": return listing(cur,sid,b)
        if action=="save": return save(cur,sid,b)
        if action=="delete": return remove(cur,sid,b["id"])
    raise ValueError("Invalid action")

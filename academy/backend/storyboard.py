"""Private storyboard plans, not a rendering engine."""
from knowledge import student
from database import transaction
from student_business import clean,ident
FORMATS=("16:9","9:16","1:1","4:3")
def integer(v,low,high):
    if type(v) is not int or not low<=v<=high: raise ValueError("Invalid number")
    return v
def project_values(b):
    title=clean(b["title"],160,True)
    story=clean(b["story"],1500,True)
    style=clean(b["style"],300)
    characters=clean(b.get("characters",""),2000)
    fmt=b["format"]
    if fmt not in FORMATS: raise ValueError("Invalid format")
    return title,story,style,characters,fmt
def scene_values(b):
    return (integer(b["position"],1,999),integer(b["seconds"],1,120),
            clean(b["title"],120,True),clean(b["action"],1000,True),
            clean(b.get("camera",""),500),clean(b.get("audio",""),500),clean(b.get("continuity",""),500))
def project_lock(cur,sid,pid):
    cur.execute("SELECT id FROM storyboard_projects WHERE id=%s AND student_id=%s FOR UPDATE",(ident(pid),sid))
    if not cur.fetchone(): raise PermissionError("Storyboard unavailable")
def save_project(cur,sid,b):
    v=project_values(b)
    if b.get("id") is None:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
        cur.execute("SELECT count(*) FROM storyboard_projects WHERE student_id=%s",(sid,))
        if cur.fetchone()[0]>=50: raise ValueError("Storyboard limit reached")
        cur.execute("INSERT INTO storyboard_projects(student_id,title,story,style,characters,format) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",(sid,*v))
    else:
        cur.execute("UPDATE storyboard_projects SET title=%s,story=%s,style=%s,characters=%s,format=%s,updated_at=now() WHERE student_id=%s AND id=%s RETURNING id",(*v,sid,ident(b["id"])))
    row=cur.fetchone()
    if not row: raise PermissionError("Storyboard unavailable")
    return {"id":row[0]}
def save_scene(cur,sid,b):
    pid=ident(b["project"]);v=scene_values(b)
    project_lock(cur,sid,pid)
    if b.get("id") is None:
        cur.execute("SELECT count(*) FROM storyboard_scenes WHERE project_id=%s",(pid,))
        if cur.fetchone()[0]>=60: raise ValueError("Scene limit reached")
        cur.execute("INSERT INTO storyboard_scenes(project_id,position,seconds,title,action,camera,audio,continuity) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",(pid,*v))
    else:
        cur.execute("UPDATE storyboard_scenes SET position=%s,seconds=%s,title=%s,action=%s,camera=%s,audio=%s,continuity=%s WHERE project_id=%s AND id=%s RETURNING id",(*v,pid,ident(b["id"])))
    row=cur.fetchone()
    if not row: raise PermissionError("Scene unavailable")
    return {"id":row[0]}
def timeline(rows):
    elapsed=0;items=[]
    for i,p,s,t,a,c,m,k in rows:
        items.append({"id":i,"position":p,"seconds":s,"title":t,"action":a,"camera":c,"audio":m,"continuity":k,"start":elapsed,"end":elapsed+s})
        elapsed+=s
    return items,elapsed
def get(cur,sid,pid):
    project_lock(cur,sid,pid)
    cur.execute("SELECT id,title,story,style,characters,format FROM storyboard_projects WHERE id=%s AND student_id=%s",(pid,sid))
    row=cur.fetchone()
    p=dict(zip(("id","title","story","style","characters","format"),row))
    cur.execute("SELECT id,position,seconds,title,action,camera,audio,continuity FROM storyboard_scenes WHERE project_id=%s ORDER BY position,id",(pid,))
    p["scenes"],p["total_seconds"]=timeline(cur.fetchall())
    return p
def listing(cur,sid):
    cur.execute("""SELECT p.id,p.title,p.format,count(s.id),coalesce(sum(s.seconds),0) FROM storyboard_projects p
      LEFT JOIN storyboard_scenes s ON s.project_id=p.id WHERE p.student_id=%s GROUP BY p.id ORDER BY p.id DESC""",(sid,))
    return {"items":[dict(zip(("id","title","format","scene_count","total_seconds"),r)) for r in cur.fetchall()]}
def remove(cur,sid,b):
    pid=ident(b["project"]);project_lock(cur,sid,pid)
    if b.get("scene") is None: cur.execute("DELETE FROM storyboard_projects WHERE id=%s AND student_id=%s RETURNING id",(pid,sid))
    else: cur.execute("DELETE FROM storyboard_scenes WHERE id=%s AND project_id=%s RETURNING id",(ident(b["scene"]),pid))
    if not cur.fetchone(): raise PermissionError("Record unavailable")
    return {"deleted":True}
def dispatch(token,action,b):
    sid=student(token)
    with transaction() as cur:
        if action=="list": return listing(cur,sid)
        if action=="get": return get(cur,sid,ident(b["project"]))
        if action=="project": return save_project(cur,sid,b)
        if action=="scene": return save_scene(cur,sid,b)
        if action=="delete": return remove(cur,sid,b)
        raise ValueError("Invalid action")

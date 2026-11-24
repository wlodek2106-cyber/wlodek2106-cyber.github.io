"""Private daily planner; date-only scheduling and read-only order deadlines."""
from datetime import date,timedelta
import re
from student_business import identity,transaction,clean,ident
CATEGORIES=("study","client","personal")
def parse_day(v):
    if not isinstance(v,str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}",v): raise ValueError("Invalid date")
    d=date.fromisoformat(v)
    if not 2000<=d.year<=2100: raise ValueError("Date outside supported range")
    return d
def values(b):
    title=clean(b["title"],160,True)
    day=parse_day(b["day"])
    category=b["category"]
    if category not in CATEGORIES: raise ValueError("Invalid category")
    priority=b["priority"]
    if type(priority) is not int or priority not in (1,2,3): raise ValueError("Invalid priority")
    minutes=b["minutes"]
    if type(minutes) is not int or not 0<=minutes<=1440: raise ValueError("Invalid minutes")
    done=b.get("done",False)
    if type(done) is not bool: raise ValueError("Invalid completion")
    return title,day,category,priority,minutes,done
def save(cur,sid,b):
    v=values(b)
    if b.get("id") is None:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
        cur.execute("SELECT count(*) FROM student_tasks WHERE student_id=%s",(sid,))
        if cur.fetchone()[0]>=2000: raise ValueError("Task limit reached")
        cur.execute("INSERT INTO student_tasks(student_id,title,day,category,priority,minutes,done) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",(sid,*v))
    else:
        cur.execute("UPDATE student_tasks SET title=%s,day=%s,category=%s,priority=%s,minutes=%s,done=%s WHERE student_id=%s AND id=%s RETURNING id",(*v,sid,ident(b["id"])))
    row=cur.fetchone()
    if not row: raise PermissionError("Task unavailable")
    return {"id":row[0]}
def remove(cur,sid,id):
    cur.execute("DELETE FROM student_tasks WHERE student_id=%s AND id=%s RETURNING id",(sid,ident(id)))
    if not cur.fetchone(): raise PermissionError("Task unavailable")
    return {"deleted":True}
def overview(cur,sid,start):
    start=parse_day(start)
    end=start+timedelta(days=6)
    cur.execute("SELECT id,title,day,category,priority,minutes,done FROM student_tasks WHERE student_id=%s AND day BETWEEN %s AND %s ORDER BY day,done,priority,id",(sid,start,end))
    tasks=[{"id":i,"title":t,"day":d.isoformat(),"category":c,"priority":p,"minutes":m,"done":x} for i,t,d,c,p,m,x in cur.fetchall()]
    cur.execute("SELECT id,title,due,status FROM business_orders WHERE student_id=%s AND due BETWEEN %s AND %s AND status IN ('lead','in_progress') ORDER BY due,id",(sid,start,end))
    deadlines=[{"id":i,"title":t,"day":d.isoformat(),"status":s} for i,t,d,s in cur.fetchall()]
    cur.execute("SELECT id,title,day,category,priority,minutes,done FROM student_tasks WHERE student_id=%s AND day<%s AND NOT done ORDER BY day,priority,id LIMIT 100",(sid,start))
    earlier=[{"id":i,"title":t,"day":d.isoformat(),"category":c,"priority":p,"minutes":m,"done":x} for i,t,d,c,p,m,x in cur.fetchall()]
    return {"start":start.isoformat(),"end":end.isoformat(),"tasks":tasks,"deadlines":deadlines,"earlier_open":earlier,"total":len(tasks),"completed":sum(t["done"] for t in tasks),"planned_minutes":sum(t["minutes"] for t in tasks),"completed_planned_minutes":sum(t["minutes"] for t in tasks if t["done"])}
def dispatch(token,action,b):
    sid=identity(token)
    with transaction() as cur:
        if action=="overview": return overview(cur,sid,b["start"])
        if action=="save": return save(cur,sid,b)
        if action=="delete": return remove(cur,sid,b["id"])
        raise ValueError("Invalid action")

"""Authenticated, opt-in, manually moderated student discussion board."""
from database import transaction
from knowledge import student
from partners import owner
from student_business import clean,ident
CATEGORIES=("question","project","collaboration","experience")
FIELDS=("id","parent_id","alias","category","title","body","status")
PROJECTION="id,parent_id,alias,category,title,body,status"
def page(cur,sid,b,mode="feed"):
    after=b.get("after",0)
    if type(after) is not int or not 0<=after<=9223372036854775807: raise ValueError("Invalid cursor")
    if mode=="feed":
        parent=b.get("parent")
        if parent is None:
            clause="parent_id IS NULL AND status='approved'";args=[]
        else:
            parent=ident(parent)
            cur.execute("SELECT 1 FROM community_posts WHERE id=%s AND parent_id IS NULL AND status='approved'",(parent,))
            if not cur.fetchone(): raise PermissionError("Thread unavailable")
            clause="parent_id=%s AND status='approved'";args=[parent]
    elif mode=="mine": clause="student_id=%s";args=[sid]
    elif mode=="admin": clause="status IN ('pending','approved')";args=[]
    else: raise ValueError("Invalid mode")
    cur.execute("SELECT "+PROJECTION+" FROM community_posts WHERE "+clause+" AND id>%s ORDER BY id LIMIT 31",(*args,after))
    rows=cur.fetchall()
    items=[dict(zip(FIELDS,r)) for r in rows[:30]]
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>30 else None}
def create(cur,sid,b):
    if b.get("consent") is not True: raise ValueError("Publication consent required")
    alias=clean(b["alias"],60,True)
    body=clean(b["body"],1600,True)
    parent=b.get("parent")
    cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
    cur.execute("SELECT count(*) FROM community_posts WHERE student_id=%s",(sid,))
    if cur.fetchone()[0]>=300: raise ValueError("Post limit reached")
    cur.execute("SELECT count(*) FROM community_posts WHERE student_id=%s AND created_at>now()-interval '24 hours'",(sid,))
    if cur.fetchone()[0]>=10: raise ValueError("Daily posting limit reached")
    if parent is None:
        category=b["category"]
        if category not in CATEGORIES: raise ValueError("Invalid category")
        title=clean(b["title"],140,True)
    else:
        parent=ident(parent)
        cur.execute("SELECT category FROM community_posts WHERE id=%s AND parent_id IS NULL AND status='approved' FOR SHARE",(parent,))
        row=cur.fetchone()
        if not row: raise PermissionError("Thread unavailable")
        category=row[0];title=""
    cur.execute("INSERT INTO community_posts(student_id,parent_id,alias,category,title,body) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",(sid,parent,alias,category,title,body))
    return {"id":cur.fetchone()[0],"status":"pending"}
def withdraw(cur,sid,b):
    cur.execute("UPDATE community_posts SET status='withdrawn' WHERE student_id=%s AND id=%s AND status IN ('pending','approved','rejected') RETURNING id",(sid,ident(b["id"])))
    if not cur.fetchone(): raise PermissionError("Post unavailable")
    return {"status":"withdrawn"}
def decide(cur,sid,b):
    action=b["action"]
    if action not in ("approved","rejected","hidden"): raise ValueError("Invalid decision")
    cur.execute("""UPDATE community_posts SET status=%s,reviewed_by=%s,reviewed_at=now() WHERE id=%s
      AND (status='pending' OR (status='approved' AND %s='hidden')) RETURNING id""",(action,sid,ident(b["id"]),action))
    if not cur.fetchone(): raise ValueError("Post no longer reviewable")
    return {"status":action}
def dispatch(token,action,b):
    sid=owner(token) if action in ("admin","decide") else student(token)
    with transaction() as cur:
        if action in ("feed","mine","admin"): return page(cur,sid,b,action)
        if action=="create": return create(cur,sid,b)
        if action=="withdraw": return withdraw(cur,sid,b)
        if action=="decide": return decide(cur,sid,b)
    raise ValueError("Invalid action")

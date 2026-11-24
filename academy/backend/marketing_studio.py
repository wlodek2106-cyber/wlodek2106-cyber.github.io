"""Private manual content calendar; no publishing, ad spend or external APIs."""
from datetime import date,timedelta
from knowledge import student
from database import transaction
from student_business import clean,ident
PLATFORMS=("instagram","tiktok","youtube","x","other")
STATES=("draft","ready","published","cancelled")
def day(v):
    if not isinstance(v,str) or len(v)!=10: raise ValueError("Invalid date")
    d=date.fromisoformat(v)
    if not 2000<=d.year<=2100: raise ValueError("Invalid year")
    return d
def campaign_values(b):
    return clean(b["title"],160,True),clean(b.get("goal",""),1000),clean(b.get("audience",""),500)
def post_values(b):
    p=b["platform"];s=b["status"]
    if p not in PLATFORMS or s not in STATES: raise ValueError("Invalid platform or status")
    return ident(b["campaign_id"]),day(b["day"]),p,s,clean(b["title"],160,True),clean(b.get("caption",""),2000),clean(b.get("hashtags",""),500),clean(b.get("asset_notes",""),500)
def save_campaign(cur,sid,b):
    v=campaign_values(b)
    if b.get("id") is None:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
        cur.execute("SELECT count(*) FROM marketing_campaigns WHERE student_id=%s",(sid,))
        if cur.fetchone()[0]>=30: raise ValueError("Campaign limit reached")
        cur.execute("INSERT INTO marketing_campaigns(student_id,title,goal,audience) VALUES (%s,%s,%s,%s) RETURNING id",(sid,*v))
    else:
        cur.execute("UPDATE marketing_campaigns SET title=%s,goal=%s,audience=%s WHERE id=%s AND student_id=%s RETURNING id",(*v,ident(b["id"]),sid))
    row=cur.fetchone()
    if not row: raise PermissionError("Campaign unavailable")
    return {"id":row[0]}
def save_post(cur,sid,b):
    v=post_values(b)
    cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
    cur.execute("SELECT id FROM marketing_campaigns WHERE id=%s AND student_id=%s FOR UPDATE",(v[0],sid))
    if not cur.fetchone(): raise PermissionError("Campaign unavailable")
    if b.get("id") is None:
        cur.execute("SELECT count(*) FROM marketing_posts WHERE student_id=%s",(sid,))
        if cur.fetchone()[0]>=300: raise ValueError("Post limit reached")
        cur.execute("INSERT INTO marketing_posts(student_id,campaign_id,day,platform,status,title,caption,hashtags,asset_notes) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",(sid,*v))
    else:
        cur.execute("UPDATE marketing_posts SET campaign_id=%s,day=%s,platform=%s,status=%s,title=%s,caption=%s,hashtags=%s,asset_notes=%s WHERE id=%s AND student_id=%s RETURNING id",(*v,ident(b["id"]),sid))
    row=cur.fetchone()
    if not row: raise PermissionError("Post unavailable")
    return {"id":row[0]}
def listing(cur,sid,start):
    d=day(start);end=d+timedelta(days=30)
    cur.execute("SELECT id,title,goal,audience FROM marketing_campaigns WHERE student_id=%s ORDER BY id",(sid,))
    campaigns=[dict(zip(("id","title","goal","audience"),r)) for r in cur.fetchall()]
    cur.execute("SELECT id,campaign_id,day,platform,status,title,caption,hashtags,asset_notes FROM marketing_posts WHERE student_id=%s AND day BETWEEN %s AND %s ORDER BY day,id",(sid,d,end))
    items=[dict(zip(("id","campaign_id","day","platform","status","title","caption","hashtags","asset_notes"),(r[0],r[1],r[2].isoformat(),*r[3:]))) for r in cur.fetchall()]
    return {"campaigns":campaigns,"items":items,"start":d.isoformat(),"end":end.isoformat()}
def remove(cur,sid,b):
    if b["kind"]=="post":
        cur.execute("DELETE FROM marketing_posts WHERE id=%s AND student_id=%s RETURNING id",(ident(b["id"]),sid))
    elif b["kind"]=="campaign":
        cur.execute("SELECT id FROM marketing_campaigns WHERE id=%s AND student_id=%s FOR UPDATE",(ident(b["id"]),sid))
        if not cur.fetchone(): raise PermissionError("Campaign unavailable")
        cur.execute("SELECT 1 FROM marketing_posts WHERE campaign_id=%s AND student_id=%s LIMIT 1",(ident(b["id"]),sid))
        if cur.fetchone(): raise ValueError("Delete or move campaign posts first")
        cur.execute("DELETE FROM marketing_campaigns WHERE id=%s AND student_id=%s RETURNING id",(ident(b["id"]),sid))
    else: raise ValueError("Invalid kind")
    if not cur.fetchone(): raise PermissionError("Record unavailable")
    return {"deleted":True}
def dispatch(token,action,b):
    sid=student(token)
    with transaction() as cur:
        if action=="list": return listing(cur,sid,b["start"])
        if action=="campaign": return save_campaign(cur,sid,b)
        if action=="post": return save_post(cur,sid,b)
        if action=="delete": return remove(cur,sid,b)
    raise ValueError("Invalid action")

"""Opt-in moderated student services directory. No orders, funds or private portfolio disclosure."""
from urllib.parse import urlsplit
from database import transaction
from knowledge import student
from partners import owner
from student_business import clean,ident
CATEGORIES=("design","video","audio","web","automation","marketing","other")
def values(b):
    if b.get("consent") is not True: raise ValueError("Public consent required")
    category=b["category"]
    if category not in CATEGORIES: raise ValueError("Invalid category")
    name=clean(b["name"],80,True)
    title=clean(b["title"],120,True)
    description=clean(b["description"],1000,True)
    price=clean(b.get("price",""),80)
    link=clean(b["link"],400,True)
    u=urlsplit(link)
    if u.scheme!="https" or not u.hostname or u.username or u.password or any(c.isspace() or ord(c)<32 for c in link) or "\\" in link: raise ValueError("HTTPS link required")
    return name,title,category,description,price,link
FIELDS=("id","name","title","category","description","price","link","status","revision")
PROJECTION="id,name,title,category,description,price,link,status,revision"
def save(cur,sid,b):
    v=values(b)
    cur.execute("SELECT id FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL FOR UPDATE",(sid,))
    if not cur.fetchone(): raise PermissionError("Paid student required")
    cur.execute("""INSERT INTO marketplace_services(student_id,name,title,category,description,price,link)
       VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(student_id) DO UPDATE SET
       name=EXCLUDED.name,title=EXCLUDED.title,category=EXCLUDED.category,description=EXCLUDED.description,
       price=EXCLUDED.price,link=EXCLUDED.link,status='pending',revision=marketplace_services.revision+1,updated_at=now(),
       reviewed_by=NULL,reviewed_at=NULL
       WHERE marketplace_services.status!='blocked' RETURNING id,revision""",(sid,*v))
    row=cur.fetchone()
    if not row: raise PermissionError("Listing blocked")
    return {"id":row[0],"revision":row[1],"status":"pending"}
def mine(cur,sid):
    cur.execute("SELECT "+PROJECTION+" FROM marketplace_services WHERE student_id=%s",(sid,))
    r=cur.fetchone()
    return {"item":dict(zip(FIELDS,r)) if r else None}
def withdraw(cur,sid):
    cur.execute("UPDATE marketplace_services SET status='withdrawn',revision=revision+1,updated_at=now() WHERE student_id=%s AND status!='blocked'",(sid,))
    return {"withdrawn":True}
def listing(cur,public=True,after=0):
    if type(after) is not int or not 0<=after<=9223372036854775807: raise ValueError("Invalid cursor")
    clause="status='approved' AND " if public else ""
    cur.execute("SELECT "+PROJECTION+" FROM marketplace_services WHERE "+clause+"id>%s ORDER BY id LIMIT 51",(after,))
    rows=cur.fetchall()
    items=[dict(zip(FIELDS,r)) for r in rows[:50]]
    if public and items:
        cur.execute("""SELECT m.id,EXISTS(SELECT 1 FROM enrollments e JOIN payment_invoices i
            ON i.student_id=e.student_id AND i.signature=e.payment_signature AND i.paid_at IS NOT NULL AND i.asset='USDC'
            WHERE e.student_id=m.student_id AND e.paid_at IS NOT NULL)
            FROM marketplace_services m WHERE m.id=ANY(%s)""",([x["id"] for x in items],))
        paid=dict(cur.fetchall())
        for item in items: item["paid_badge"]=bool(paid.get(item["id"]))
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>50 else None}
def public_detail(cur,listing_id):
    """Only approved public listing fields; never expose private account data."""
    listing_id=ident(listing_id)
    cur.execute("SELECT "+PROJECTION+" FROM marketplace_services WHERE id=%s AND status='approved'",(listing_id,))
    row=cur.fetchone()
    if not row:
        return {"item":None}
    item=dict(zip(FIELDS,row))
    cur.execute("""SELECT EXISTS(SELECT 1 FROM enrollments e JOIN payment_invoices i
        ON i.student_id=e.student_id AND i.signature=e.payment_signature AND i.paid_at IS NOT NULL AND i.asset='USDC'
        WHERE e.student_id=m.student_id AND e.paid_at IS NOT NULL)
        FROM marketplace_services m WHERE m.id=%s""",(listing_id,))
    badge=cur.fetchone()
    item["paid_badge"]=bool(badge and badge[0])
    return {"item":item}

def decide(cur,admin,b):
    action=b["action"]
    if action not in ("approved","rejected","blocked"): raise ValueError("Invalid decision")
    rev=ident(b["revision"])
    cur.execute("""UPDATE marketplace_services SET status=%s,revision=revision+1,reviewed_by=%s,reviewed_at=now()
        WHERE id=%s AND revision=%s AND (status='pending' OR (%s='blocked' AND status='approved')) RETURNING id""",
        (action,admin,ident(b["id"]),rev,action))
    if not cur.fetchone(): raise ValueError("Listing changed or not reviewable")
    return {"status":action}
def dispatch(token,action,b):
    if action=="public-detail":
        with transaction() as cur: return public_detail(cur,b["id"])
    if action=="public":
        with transaction() as cur: return listing(cur,True,b.get("after",0))
    if action in ("admin","decide"):
        sid=owner(token)
        with transaction() as cur:
            return listing(cur,False,b.get("after",0)) if action=="admin" else decide(cur,sid,b)
    sid=student(token)
    with transaction() as cur:
        if action=="mine": return mine(cur,sid)
        if action=="save": return save(cur,sid,b)
        if action=="withdraw": return withdraw(cur,sid)
    raise ValueError("Invalid action")

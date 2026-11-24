"""Private in-app notifications; no external delivery or sensitive message previews."""
from student_business import ident
KINDS=("job_open","job_rejected","job_cancelled","application","selected","message","delivered","revision","completed","review_approved")
TARGETS=("mine","applications","room")

def emit(cur,recipient,jid,kind,target):
    if kind not in KINDS or target not in TARGETS: raise ValueError("Invalid notification")
    cur.execute("INSERT INTO academy_notifications(student_id,job_id,kind,target) VALUES (%s,%s,%s,%s)",(recipient,jid,kind,target))
    # Retention is bounded on writes per recipient; old notices are not the project history.
    cur.execute("""DELETE FROM academy_notifications WHERE student_id=%s AND
        (created_at<now()-interval '90 days' OR id IN
        (SELECT id FROM academy_notifications WHERE student_id=%s ORDER BY id DESC OFFSET 500))""",(recipient,recipient))

def counterpart(cur,jid,role):
    cur.execute("""SELECT j.client_id,a.student_id FROM academy_jobs j
       JOIN academy_job_applications a ON a.job_id=j.id AND a.id=j.selected_application WHERE j.id=%s""",(jid,))
    row=cur.fetchone()
    if not row: raise PermissionError("Project unavailable")
    return row[1] if role=="client" else row[0]

def count(cur,sid):
    cur.execute("SELECT count(*) FROM academy_notifications WHERE student_id=%s AND read_at IS NULL AND created_at>=now()-interval '90 days'",(sid,))
    return {"unread":cur.fetchone()[0]}

def listing(cur,sid,b):
    before=b.get("before",None)
    if before is not None: ident(before)
    cur.execute("""SELECT n.id,n.job_id,j.title,n.kind,n.target,n.created_at,n.read_at IS NOT NULL
        FROM academy_notifications n JOIN academy_jobs j ON j.id=n.job_id
        WHERE n.student_id=%s AND n.created_at>=now()-interval '90 days'
          AND (%s::bigint IS NULL OR n.id<%s) ORDER BY n.id DESC LIMIT 31""",(sid,before,before))
    rows=cur.fetchall()
    items=[{"id":i,"job_id":j,"title":t,"kind":k,"target":v,"created_at":c.isoformat(),"read":r} for i,j,t,k,v,c,r in rows[:30]]
    return {"items":items,"next_before":items[-1]["id"] if len(rows)>30 else None,**count(cur,sid)}

def mark(cur,sid,b):
    ids=b["ids"]
    if not isinstance(ids,list) or not 1<=len(ids)<=30: raise ValueError("Invalid notification selection")
    ids=[ident(i) for i in ids]
    cur.execute("UPDATE academy_notifications SET read_at=COALESCE(read_at,now()) WHERE student_id=%s AND id=ANY(%s::bigint[])",(sid,ids))
    return count(cur,sid)

def dispatch(token,action,b):
    from accounts import authenticate
    from database import transaction
    sid=authenticate(token)
    if sid is None: raise PermissionError("Sign in required")
    with transaction() as cur:
        if action=="count": return count(cur,sid)
        if action=="list": return listing(cur,sid,b)
        if action=="read": return mark(cur,sid,b)
    raise ValueError("Invalid action")

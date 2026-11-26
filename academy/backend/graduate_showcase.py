"""Opt-in unlisted graduate portfolio. Never publish private project submissions."""
import re,secrets
from urllib.parse import urlsplit
CODE=re.compile(r"[A-Za-z0-9_-]{32}")
def clean_text(value,limit,minimum=0):
    if not isinstance(value,str) or not minimum<=len(value.strip())<=limit or any(ord(c)<32 and c not in "\n\t" for c in value):
        raise ValueError("Invalid text")
    return value.strip()
def validate(profile):
    if not isinstance(profile,dict) or set(profile)!={"headline","bio","projects","show_name"} or type(profile["show_name"]) is not bool:
        raise ValueError("Invalid showcase")
    projects=profile["projects"]
    if not isinstance(projects,list) or not 1<=len(projects)<=5:raise ValueError("Provide 1–5 public projects")
    rows=[]
    for project in projects:
        if not isinstance(project,dict) or set(project)!={"title","description","url"}:raise ValueError("Invalid project")
        url=clean_text(project["url"],500)
        u=urlsplit(url)
        if url and (u.scheme!="https" or not u.hostname or u.username or u.password or any(ch.isspace() for ch in url) or "\\" in url):
            raise ValueError("Use a public HTTPS link")
        rows.append({"title":clean_text(project["title"],120,1),"description":clean_text(project["description"],500,1),"url":url})
    return {"headline":clean_text(profile["headline"],120,1),"bio":clean_text(profile["bio"],1000,1),"projects":rows,"show_name":profile["show_name"]}
def identity(token):
    from accounts import authenticate
    sid=authenticate(token)
    if sid is None:raise PermissionError("Authentication required")
    return sid
def credential(cur,sid):
    cur.execute("""SELECT e.plan,c.recipient_name,c.issued_at,ec.recipient_name,ec.issued_at
        FROM enrollments e LEFT JOIN certificates c ON c.enrollment_id=e.id
        LEFT JOIN elite_certificates ec ON ec.enrollment_id=e.id
        WHERE e.student_id=%s AND e.paid_at IS NOT NULL AND (c.enrollment_id IS NOT NULL OR ec.enrollment_id IS NOT NULL)""",(sid,))
    row=cur.fetchone()
    if not row:return None
    plan,name,issued,elite_name,elite_issued=row
    if elite_issued:return {"level":"ELITE","lessons":45,"approved_projects":5,"name":elite_name,"issued_at":elite_issued.date().isoformat()}
    return {"level":plan.upper()+" · Core","lessons":45 if plan in ("elite","vip") else 30,"name":name,"issued_at":issued.date().isoformat()}
def mine(token):
    from database import transaction
    sid=identity(token)
    with transaction() as cur:
        cert=credential(cur,sid)
        cur.execute("SELECT share_code,profile FROM graduate_showcases WHERE student_id=%s",(sid,))
        row=cur.fetchone()
    return {"eligible":bool(cert),"published":bool(row),"code":row[0] if row else None,"profile":row[1] if row else None}
def publish(token,profile,consent):
    from database import transaction
    from psycopg.types.json import Jsonb
    sid=identity(token)
    if consent is not True:raise ValueError("Explicit publication consent required")
    data=validate(profile)
    with transaction() as cur:
        if not credential(cur,sid):raise PermissionError("Graduate certificate required")
        cur.execute("""INSERT INTO graduate_showcases(student_id,share_code,profile) VALUES (%s,%s,%s)
          ON CONFLICT(student_id) DO UPDATE SET profile=EXCLUDED.profile,published_at=now() RETURNING share_code""",(sid,secrets.token_urlsafe(24),Jsonb(data)))
        return {"code":cur.fetchone()[0],"published":True}
def withdraw(token):
    from database import transaction
    sid=identity(token)
    with transaction() as cur:cur.execute("DELETE FROM graduate_showcases WHERE student_id=%s",(sid,))
    return {"published":False}
def public(code):
    from database import transaction
    if not isinstance(code,str) or not CODE.fullmatch(code):return {"found":False}
    with transaction() as cur:
        cur.execute("SELECT student_id,profile FROM graduate_showcases WHERE share_code=%s",(code,))
        row=cur.fetchone()
        if not row:return {"found":False}
        cert=credential(cur,row[0])
        if not cert:return {"found":False}
    data=validate(row[1])
    name=cert.pop("name")
    show=data.pop("show_name")
    return {"found":True,"profile":data,"credential":cert,**({"recipient_name":name} if show else {})}

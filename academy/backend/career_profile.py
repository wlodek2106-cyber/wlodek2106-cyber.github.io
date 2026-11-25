"""Private career profile and opt-in export; no automatic publishing."""
FIELDS={"name":100,"headline":160,"summary":1500,"skills":800,"tools":800,"experience":2000,"education":1000,"contact":200,"languages":200}
EMPTY={k:"" for k in FIELDS}
def validate(data):
    if not isinstance(data,dict) or set(data)!=set(FIELDS):
        raise ValueError("Invalid career profile")
    if any(not isinstance(data[k],str) or len(data[k])>n or "\x00" in data[k] for k,n in FIELDS.items()):
        raise ValueError("Invalid profile fields")
    return {k:data[k].strip() for k in FIELDS}
def identity(token):
    from accounts import authenticate
    from learning import student_progress
    sid=authenticate(token)
    if sid is None or not student_progress(token)["access"]:
        raise PermissionError("Paid enrollment required")
    return sid
def load(cur,sid):
    cur.execute("SELECT profile FROM career_profiles WHERE student_id=%s",(sid,))
    row=cur.fetchone()
    return row[0] if row else dict(EMPTY)
def save(cur,sid,data):
    from psycopg.types.json import Jsonb
    clean=validate(data)
    cur.execute("""INSERT INTO career_profiles(student_id,profile) VALUES (%s,%s)
      ON CONFLICT(student_id) DO UPDATE SET profile=EXCLUDED.profile,updated_at=now()""",(sid,Jsonb(clean)))
    return {"saved":True}
def get_profile(token):
    from database import transaction
    sid=identity(token)
    with transaction() as cur: return {"profile":load(cur,sid),"private":True}
def save_profile(token,data):
    from database import transaction
    sid=identity(token)
    with transaction() as cur: return save(cur,sid,data)
def delete_profile(token):
    from database import transaction
    sid=identity(token)
    with transaction() as cur:
        cur.execute("DELETE FROM career_profiles WHERE student_id=%s",(sid,))
    return {"deleted":True}

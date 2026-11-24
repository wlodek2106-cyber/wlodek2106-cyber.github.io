"""New paid course content stored in the database, not in public Git.
Existing public curriculum remains a legacy fallback unless strict mode is enabled."""
import os,re
LANGS=("en","ru","uk","pl")
KINDS=("lesson","exam")

def validate_slot(kind,day,lang):
    if kind not in KINDS or type(day) is not int or not 1<=day<=45 or lang not in LANGS:
        raise ValueError("Invalid content slot")
    return kind,day,lang

def validate(kind,day,lang,data):
    validate_slot(kind,day,lang)
    def string(v,limit):
        return isinstance(v,str) and 1<=len(v.strip())<=limit
    if kind=="lesson":
        if not isinstance(data,dict) or set(data)!={"title","theory","assignment","prompts"}: raise ValueError("Invalid lesson structure")
        if not all(string(data[k],limit) for k,limit in (("title",200),("theory",8000),("assignment",3000))): raise ValueError("Invalid lesson text")
        if not isinstance(data["prompts"],list) or len(data["prompts"])>20 or not all(string(x,1500) for x in data["prompts"]): raise ValueError("Invalid prompts")
    else:
        if not isinstance(data,list) or not 10<=len(data)<=40: raise ValueError("10–40 questions required")
        ids=set();questions=set()
        for q in data:
            if not isinstance(q,dict) or set(q)!={"id","question","options","correct"}: raise ValueError("Invalid question structure")
            if not string(q["id"],40) or not re.fullmatch(r"[A-Za-z0-9_-]+",q["id"]) or q["id"] in ids: raise ValueError("Duplicate or invalid ID")
            if not string(q["question"],1000) or q["question"].strip().casefold() in questions: raise ValueError("Duplicate or invalid question")
            o=q["options"]
            if not isinstance(o,list) or not 3<=len(o)<=6 or not all(string(x,400) for x in o) or len({x.strip().casefold() for x in o})!=len(o) or q["correct"] not in o: raise ValueError("Invalid options")
            ids.add(q["id"]);questions.add(q["question"].strip().casefold())
    return data

def load(cur,kind,day,lang):
    lang=lang if lang in LANGS else "en"
    validate_slot(kind,day,lang)
    cur.execute("""SELECT language,content FROM private_curriculum WHERE kind=%s AND lesson=%s AND language IN (%s,'en')
       ORDER BY CASE WHEN language=%s THEN 0 ELSE 1 END LIMIT 1""",(kind,day,lang,lang))
    row=cur.fetchone()
    if row: return {"language":row[0],"content":row[1]}
    if os.getenv("ACADEMY_PRIVATE_"+("EXAMS" if kind=="exam" else "LESSONS")+"_REQUIRED")=="true":
        raise RuntimeError("Private curriculum not yet available")
    return None

def get(kind,day,lang):
    from database import transaction
    with transaction() as cur: return load(cur,kind,day,lang)

def save(cur,owner,kind,day,lang,data):
    from psycopg.types.json import Jsonb
    validate(kind,day,lang,data)
    cur.execute("""INSERT INTO private_curriculum(kind,lesson,language,content,updated_by) VALUES (%s,%s,%s,%s,%s)
        ON CONFLICT(kind,lesson,language) DO UPDATE SET content=EXCLUDED.content,updated_by=EXCLUDED.updated_by,updated_at=now(),revision=private_curriculum.revision+1
        RETURNING revision""",(kind,day,lang,Jsonb(data),owner))
    revision=cur.fetchone()[0]
    cur.execute("INSERT INTO private_curriculum_audit(kind,lesson,language,revision,updated_by) VALUES (%s,%s,%s,%s,%s)",(kind,day,lang,revision,owner))
    return {"saved":True,"revision":revision}

def inventory(cur):
    cur.execute("SELECT kind,lesson,language,revision,updated_at FROM private_curriculum ORDER BY kind,lesson,language")
    items=[{"kind":k,"day":d,"lang":l,"revision":v,"updated_at":t.isoformat()} for k,d,l,v,t in cur.fetchall()]
    return {"items":items,"english_coverage":{k:sum(x["kind"]==k and x["lang"]=="en" for x in items) for k in KINDS},
            "strict":{"exam":os.getenv("ACADEMY_PRIVATE_EXAMS_REQUIRED")=="true","lesson":os.getenv("ACADEMY_PRIVATE_LESSONS_REQUIRED")=="true"}}

def admin_inventory(token):
    from partners import owner
    from database import transaction
    owner(token)
    with transaction() as cur: return inventory(cur)

def admin_save(token,body):
    from partners import owner
    from database import transaction
    sid=owner(token)
    with transaction() as cur: return save(cur,sid,body["kind"],body["day"],body["lang"],body["content"])

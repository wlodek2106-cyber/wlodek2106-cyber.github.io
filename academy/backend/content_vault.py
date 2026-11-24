"""New paid course content stored in the database, not in public Git.
Existing public curriculum remains a legacy fallback unless strict mode is enabled."""
import os,re,json,unicodedata
from pathlib import Path
from functools import lru_cache
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

def normalize_question(text):
    # Compare punctuation/case/spacing variants, not semantic equivalence.
    return "".join(c for c in unicodedata.normalize("NFKC",text).casefold() if c.isalnum())

@lru_cache(maxsize=1)
def legacy_questions():
    from lesson01 import LESSON
    read=lambda name:json.loads(Path(__file__).with_name(name).read_text())
    texts=[q[0] for q in LESSON["questions"]]
    for bank in read("quiz01_translations.json").values():
        texts.extend(q[0] for q in bank)
    texts.extend(q["question"] for q in read("quiz02.json"))
    for name in ("quiz03_30.json","vip_lessons.json"):
        for lesson in read(name):
            texts.extend(q["question"] for q in lesson["questions"])
    return frozenset(normalize_question(t) for t in texts)

def legacy_overlap(bank):
    known=legacy_questions()
    return sum(normalize_question(q["question"]) in known for q in bank)

def require_original_exam(bank):
    if legacy_overlap(bank): raise ValueError("Public legacy question detected")
    fingerprints=[normalize_question(q["question"]) for q in bank]
    if not all(fingerprints) or len(set(fingerprints))!=len(fingerprints):
        raise ValueError("Duplicate normalized questions")

def coverage(items):
    result={}
    for lang in LANGS:
        result[lang]={}
        for kind in KINDS:
            valid={x["day"] for x in items if x["kind"]==kind and x["lang"]==lang and x.get("legacy_overlap",0)==0}
            missing=[d for d in range(1,46) if d not in valid]
            result[lang][kind]={"count":len(valid),"missing":missing}
    return result

def load(cur,kind,day,lang):
    lang=lang if lang in LANGS else "en"
    validate_slot(kind,day,lang)
    cur.execute("""SELECT language,content FROM private_curriculum WHERE kind=%s AND lesson=%s AND language IN (%s,'en')
       ORDER BY CASE WHEN language=%s THEN 0 ELSE 1 END LIMIT 1""",(kind,day,lang,lang))
    row=cur.fetchone()
    if row:
        if kind=="exam" and os.getenv("ACADEMY_PRIVATE_EXAMS_REQUIRED")=="true":
            require_original_exam(row[1])
        return {"language":row[0],"content":row[1]}
    if os.getenv("ACADEMY_PRIVATE_"+("EXAMS" if kind=="exam" else "LESSONS")+"_REQUIRED")=="true":
        raise RuntimeError("Private curriculum not yet available")
    return None

def get(kind,day,lang):
    from database import transaction
    with transaction() as cur: return load(cur,kind,day,lang)

def save(cur,owner,kind,day,lang,data):
    from psycopg.types.json import Jsonb
    validate(kind,day,lang,data)
    if kind=="exam": require_original_exam(data)
    cur.execute("""INSERT INTO private_curriculum(kind,lesson,language,content,updated_by) VALUES (%s,%s,%s,%s,%s)
        ON CONFLICT(kind,lesson,language) DO UPDATE SET content=EXCLUDED.content,updated_by=EXCLUDED.updated_by,updated_at=now(),revision=private_curriculum.revision+1
        RETURNING revision""",(kind,day,lang,Jsonb(data),owner))
    revision=cur.fetchone()[0]
    cur.execute("INSERT INTO private_curriculum_audit(kind,lesson,language,revision,updated_by) VALUES (%s,%s,%s,%s,%s)",(kind,day,lang,revision,owner))
    return {"saved":True,"revision":revision}

def inventory(cur):
    cur.execute("SELECT kind,lesson,language,revision,updated_at,CASE WHEN kind='exam' THEN content ELSE NULL END FROM private_curriculum ORDER BY kind,lesson,language")
    items=[{"kind":k,"day":d,"lang":l,"revision":v,"updated_at":t.isoformat(),"legacy_overlap":legacy_overlap(c) if k=="exam" else 0} for k,d,l,v,t,c in cur.fetchall()]
    by_language=coverage(items)
    return {"items":items,"english_coverage":{k:sum(x["kind"]==k and x["lang"]=="en" for x in items) for k in KINDS},
            "coverage":by_language,"strict_ready":{k:by_language["en"][k]["count"]==45 and not any(x["kind"]==k and x["legacy_overlap"] for x in items) for k in KINDS},
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

"""Bounded process-local HTTP counters. No raw paths, identities, request bodies or persistence."""
from collections import Counter
from threading import Lock
from time import monotonic
from datetime import datetime,timezone
from urllib.parse import urlsplit

TABLES={
 "account":("students","student_sessions","student_mfa","student_passkeys"),
 "learning":("enrollments","lesson_progress","quiz_attempts","project_submissions"),
 "payments":("payment_invoices","payment_support"),
 "marketplace":("academy_jobs","academy_job_applications","marketplace_services"),
 "agency":("creator_agencies","creator_agency_tasks","creator_agency_projects"),
 "support":("support_tickets","support_messages","support_article_feedback"),
}
GROUPS=tuple(TABLES)+("creator","system","other")
def group(path):
    try: p=urlsplit(path).path
    except (ValueError,TypeError): return "other"
    if p in ("/login","/register","/logout") or p.startswith(("/account/","/passkeys/")): return "account"
    if p.startswith(("/checkout/","/admin/payment-support")): return "payments"
    if p=="/progress" or p.startswith(("/elite/certificate/","/learning/","/lesson/","/lessons/","/exam/","/exams/","/quiz/","/teacher/","/practice/","/review-journal/","/certificate")): return "learning"
    if p.startswith(("/marketplace","/jobs/","/hire","/client-portal","/notifications/")): return "marketplace"
    if p=="/agency" or p.startswith("/agency/"): return "agency"
    if p=="/support" or p.startswith("/support/"): return "support"
    if p.startswith(("/creator/","/career/","/business/","/higgsfield/","/free-ai","/ai-workspace")): return "creator"
    if p in ("/health","/ready") or p.startswith("/admin/"): return "system"
    return "other"

class Metrics:
    def __init__(self,clock=monotonic):
        self.clock=clock;self.started=clock();self.lock=Lock();self.buckets={}
    def prune(self,minute):
        for k in tuple(self.buckets):
            if k<minute-59 or k>minute: del self.buckets[k]
    def record(self,key,status):
        if key not in GROUPS or type(status) is not int or not 100<=status<=599:return
        kind="limited" if status==429 else "server" if status>=500 else "client" if status>=400 else "ok" if status>=200 else "other"
        minute=int(self.clock()//60)
        with self.lock:
            self.prune(minute);self.buckets.setdefault(minute,Counter())[(key,kind)]+=1
    def snapshot(self,minutes):
        if type(minutes) is not int or minutes not in (15,60):raise ValueError("Invalid window")
        now=self.clock();minute=int(now//60)
        with self.lock:
            self.prune(minute);total=Counter()
            for k,b in self.buckets.items():
                if k>=minute-minutes+1:total.update(b)
        rows=[]
        for key in GROUPS:
            counts={k:total[key,k] for k in ("ok","client","limited","server","other")}
            rows.append({"module":key,"requests":sum(counts.values()),**counts})
        return {"minutes":minutes,"process_age_seconds":max(0,int(now-self.started)),"rows":rows,"persistent":False}
metrics=Metrics()

def table_status(cur):
    rows=[]
    for key,names in TABLES.items():
        cur.execute("SELECT count(*) FROM unnest(%s::text[]) AS n(name) WHERE to_regclass('academy.'||n.name) IS NOT NULL",(list(names),))
        found=cur.fetchone()[0]
        rows.append({"module":key,"found":found,"expected":len(names),"present":found==len(names)})
    return rows

def recommendations(tables,traffic,integrity):
    actions=[]
    if any(not x["present"] for x in tables):actions.append("schema")
    if not integrity:actions.append("integrity")
    if any(x["server"] for x in traffic["rows"]):actions.append("errors")
    if any(x["limited"] for x in traffic["rows"]):actions.append("limits")
    return actions

def report(token,minutes):
    from partners import owner
    from database import transaction
    from security_center import inspect
    owner(token)
    traffic=metrics.snapshot(minutes)
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        cur.execute("SET LOCAL statement_timeout='5s'")
        tables=table_status(cur)
        # Existing integrity queries require all their tables; do not mislabel missing schema as a pass.
        integrity=inspect(cur) if all(x["present"] for x in tables) else None
    ok=bool(integrity and integrity["database_checks_pass"])
    return {"as_of":datetime.now(timezone.utc).isoformat(),"tables":tables,"traffic":traffic,
            "integrity":None if integrity is None else integrity["checks"],"recommendations":recommendations(tables,traffic,ok),
            "external_probes":False,"backup_verified":False,"read_only":True}

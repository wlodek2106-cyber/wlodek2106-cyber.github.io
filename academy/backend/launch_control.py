"""Owner-only launch snapshot; no configuration writes, payments or release approval."""
import os
from datetime import datetime,timezone
from payment_policy import PRICES,course_amount
LANGUAGES=("en","ru","uk","pl")
def packages(inventory):
    rows=[]
    for plan,price in PRICES.items():
        days=45 if plan in ("vip","elite") else 30
        languages={}
        for lang in LANGUAGES:
            languages[lang]={kind:days-sum(1 for d in inventory["coverage"][lang][kind]["missing"] if 1<=d<=days) for kind in ("lesson","exam")}
        rows.append({"plan":plan,"days":days,"price_usdc":price,"discount_atomic":str(course_amount(plan,True)),
            "languages":languages,"private_slots":sum(sum(v.values()) for v in languages.values()),"target":days*8})
    return rows

def collect(cur):
    from security_center import inspect
    from content_vault import inventory
    from launch_readiness import summarize
    from system_monitor import table_status
    tables=table_status(cur)
    cur.execute("SELECT count(*) FROM system_incidents WHERE state<>'resolved'")
    incidents=cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM system_incidents WHERE state<>'resolved' AND severity='urgent'")
    urgent=cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM support_tickets WHERE status='open'")
    support=cur.fetchone()[0]
    diag=inspect(cur)
    inv=inventory(cur)
    launch=summarize(diag,inv)
    checkout=os.getenv("ACADEMY_CHECKOUT_READY")=="true" and os.getenv("ACADEMY_PAYMENTS_ENABLED")=="true"
    return {"as_of":datetime.now(timezone.utc).isoformat(),"packages":packages(inv),
        "tables":tables,"integrity_pass":diag["database_checks_pass"],
        "integrity":diag["checks"],"launch":launch,"checkout_configured":checkout,
        "incidents":incidents,"urgent_incidents":urgent,"open_support":support,
        "live_payment_tested":False,"commercial_approved":False,"read_only":True}

def report(token):
    from partners import owner
    from database import transaction
    owner(token)
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        cur.execute("SET LOCAL statement_timeout='5s'")
        return collect(cur)

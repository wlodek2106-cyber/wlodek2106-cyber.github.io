"""Rule-based private order triage, with optional manual local AI handoff."""
from datetime import date,datetime,timezone
from decimal import Decimal,ROUND_HALF_UP
def report(orders,today):
    if type(today) is not date: raise ValueError("Invalid report date")
    result=[]
    for o in orders:
        status=o["status"]
        if status=="cancelled": continue
        a,r,e=(o[k] for k in ("agreed_cents","received_cents","expense_cents"))
        delta=(date.fromisoformat(o["due"])-today).days if o["due"] else None
        flags=[]
        if status=="in_progress" and delta is not None and delta<0: flags.append("overdue")
        elif status=="in_progress" and delta is not None and delta<=3: flags.append("due_soon")
        if status=="delivered" and a>r: flags.append("collect_payment")
        if e>a: flags.append("cost_overrun")
        if status=="in_progress" and delta is None: flags.append("set_deadline")
        if status=="lead": flags.append("follow_up")
        if not flags: continue
        priority=min({"overdue":0,"cost_overrun":1,"due_soon":2,"collect_payment":3,"set_deadline":4,"follow_up":5}[f] for f in flags)
        result.append({"id":o["id"],"title":o["title"],"status":status,"days_remaining":delta,"flags":flags,"priority":priority,"outstanding_cents":a-r})
    result.sort(key=lambda x:(x["priority"],x["days_remaining"] if x["days_remaining"] is not None else 1000000,x["id"]))
    active=[o for o in orders if o["status"] in ("in_progress","delivered")]
    value=sum(o["agreed_cents"] for o in active)
    cost=sum(o["expense_cents"] for o in active)
    pct=str((Decimal(value-cost)*100/Decimal(value)).quantize(Decimal("0.1"),rounding=ROUND_HALF_UP)) if value else None
    return {"as_of":today.isoformat(),"engine":"rules_based","currency":"USD","actions":result[:100],"action_count":len(result),"contract_value_cents":str(value),"recorded_cost_cents":str(cost),"projected_margin_cents":str(value-cost),"projected_margin_percent":pct,"manual_records":True}
def assistant(token):
    from student_business import identity,transaction
    sid=identity(token)
    with transaction() as cur:
        cur.execute("SELECT id,title,status,due,agreed_cents,received_cents,expense_cents FROM business_orders WHERE student_id=%s",(sid,))
        rows=[{"id":i,"title":t,"status":s,"due":d.isoformat() if d else "","agreed_cents":a,"received_cents":r,"expense_cents":e} for i,t,s,d,a,r,e in cur.fetchall()]
    return report(rows,datetime.now(timezone.utc).date())

def studio_summary(clients_count,orders,today):
    """Minimal read-only snapshot; never return client contacts or private notes."""
    from student_business import totals,STATES
    counts={state:sum(o["status"]==state for o in orders) for state in STATES}
    financial=totals((o["status"],o["agreed_cents"],o["received_cents"],o["expense_cents"]) for o in orders)
    priorities=report(orders,today)
    return {"clients":clients_count,"orders":len(orders),"counts":counts,"totals":financial,
            "actions":[{k:a[k] for k in ("id","title","flags","days_remaining","outstanding_cents")} for a in priorities["actions"][:12]],
            "action_count":priorities["action_count"],"currency":"USD","manual":True,"private":True,"as_of":today.isoformat()}

def studio(token):
    from student_business import identity,transaction
    sid=identity(token)
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        cur.execute("SELECT count(*) FROM business_clients WHERE student_id=%s",(sid,))
        clients=cur.fetchone()[0]
        cur.execute("SELECT id,title,status,due,agreed_cents,received_cents,expense_cents FROM business_orders WHERE student_id=%s",(sid,))
        rows=[{"id":i,"title":t,"status":s,"due":d.isoformat() if d else "","agreed_cents":a,"received_cents":r,"expense_cents":e} for i,t,s,d,a,r,e in cur.fetchall()]
    return studio_summary(clients,rows,datetime.now(timezone.utc).date())

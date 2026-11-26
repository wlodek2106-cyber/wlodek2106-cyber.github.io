"""Private read-only account diagnostics, using existing progression rules."""
from datetime import datetime,timezone,timedelta
from progression import lesson_available

def learning_state(plan,paid,passed,preview,now):
    total=45 if preview or plan in ("vip","elite") else 30
    available=[d for d in range(1,total+1) if lesson_available(d,paid,passed,now,plan,preview)]
    completed={d for d in passed if 1<=d<=total}
    next_day=next((d for d in range(1,total+1) if d not in completed),None)
    reason="finished";earliest=None
    if next_day is not None:
        if next_day in available: reason="available"
        elif not paid: reason="payment_required"
        elif any(d not in passed or passed[d]>now for d in range(1,next_day)): reason="previous_required"
        else:
            earliest=max(paid+timedelta(days=next_day-1),passed[next_day-1]+timedelta(days=1)) if next_day>1 else paid
            reason="scheduled" if earliest>now else "check_support"
    return {"plan":"elite" if preview else plan if paid else None,"access":"preview" if preview else "paid" if paid else "trial",
            "total":total,"completed":len(completed),"unlocked":len(available),"next":next_day,
            "reason":reason,"earliest":earliest.isoformat() if reason=="scheduled" else None}

def collect(cur,sid,preview=False,now=None):
    now=now or datetime.now(timezone.utc)
    cur.execute("SELECT id,plan,paid_at FROM enrollments WHERE student_id=%s",(sid,))
    row=cur.fetchone()
    eid,plan,paid=row if row else (None,None,None)
    passed={}
    if eid is not None:
        cur.execute("SELECT lesson,passed_at FROM lesson_progress WHERE enrollment_id=%s",(eid,))
        passed=dict(cur.fetchall())
    learning=learning_state(plan,paid,passed,preview,now)
    cur.execute("""SELECT plan,CASE WHEN paid_at IS NOT NULL THEN 'paid' WHEN expires_at<=%s THEN 'expired' ELSE 'active' END
      FROM payment_invoices WHERE student_id=%s ORDER BY created_at DESC,id DESC LIMIT 1""",(now,sid))
    invoice=cur.fetchone()
    cur.execute("SELECT count(*) FROM payment_support t JOIN payment_invoices i ON i.id=t.invoice_id WHERE i.student_id=%s AND t.status='open'",(sid,))
    pending_support=cur.fetchone()[0]
    cur.execute("SELECT secret IS NOT NULL,cardinality(recovery_digests) FROM student_mfa WHERE student_id=%s",(sid,))
    security=cur.fetchone()
    cur.execute("SELECT count(*) FROM student_passkeys WHERE student_id=%s",(sid,))
    keys=cur.fetchone()[0]
    return {"learning":learning,"invoice":{"plan":invoice[0],"status":invoice[1]} if invoice else {"plan":None,"status":"none"},
            "payment_support_open":pending_support,"security":{"mfa_enabled":bool(security and security[0]),
            "recovery_remaining":int(security[1] or 0) if security and security[0] else 0,"passkeys":keys},
            "as_of":now.isoformat(),"read_only":True,"chain_verified_now":False}

def report(token):
    from accounts import authenticate
    from learning import owner_preview
    from database import transaction
    sid=authenticate(token)
    if sid is None: raise PermissionError("Authentication required")
    preview=owner_preview(sid)
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        return collect(cur,sid,preview)

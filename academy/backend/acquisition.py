"""First registration acquisition attribution, aggregate reporting only."""
SOURCES=("direct","telegram","instagram","youtube","linkedin","facebook","tiktok","x","partner","other")
def normalize(value):
    return value if isinstance(value,str) and value in SOURCES else None

def summarize(registrations,orders,applications):
    rows={k:{"source":k,"registrations":0,"clients":0,"jobs":0,"pending":0,"open":0,"assigned":0,"delivered":0,"completed":0,"rejected":0,"cancelled":0,"applications":0} for k in (*SOURCES,"untracked")}
    for source,n in registrations: rows[source or "untracked"]["registrations"]=n
    for source,n,clients,pending,opened,assigned,delivered,completed,rejected,cancelled in orders:
        rows[source or "untracked"].update(clients=clients,jobs=n,pending=pending,open=opened,assigned=assigned,delivered=delivered,completed=completed,rejected=rejected,cancelled=cancelled)
    for source,n in applications: rows[source or "untracked"]["applications"]=n
    for r in rows.values():
        r["client_conversion_percent"]=round(100*r["clients"]/r["registrations"],2) if r["registrations"] else None
    return {"items":list(rows.values()),"scope":"all_time_registration_attribution","self_reported":True}

def report(cur):
    cur.execute("SELECT hire_source,count(*) FROM students GROUP BY hire_source")
    reg=cur.fetchall()
    cur.execute("""SELECT s.hire_source,count(*),count(DISTINCT j.client_id),
        count(*) FILTER(WHERE j.status='pending'),count(*) FILTER(WHERE j.status='open'),
        count(*) FILTER(WHERE j.status='assigned'),count(*) FILTER(WHERE j.status='delivered'),
        count(*) FILTER(WHERE j.status='completed'),count(*) FILTER(WHERE j.status='rejected'),
        count(*) FILTER(WHERE j.status='cancelled')
        FROM academy_jobs j JOIN students s ON s.id=j.client_id GROUP BY s.hire_source""")
    orders=cur.fetchall()
    cur.execute("""SELECT s.hire_source,count(*) FROM academy_job_applications a
       JOIN academy_jobs j ON j.id=a.job_id JOIN students s ON s.id=j.client_id GROUP BY s.hire_source""")
    return summarize(reg,orders,cur.fetchall())

def admin_report(token):
    from partners import owner
    from database import transaction
    owner(token)
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        return report(cur)

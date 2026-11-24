"""Owner-only registration tree, paginated by direct parent; no financial multi-level rewards."""
PAGE_SIZE=50
def validate(parent,after,search):
    if parent is not None and (type(parent) is not int or not 1<=parent<=9223372036854775807):
        raise ValueError("Invalid parent")
    if type(after) is not int or not 0<=after<=9223372036854775807:
        raise ValueError("Invalid cursor")
    if not isinstance(search,str) or len(search)>120:
        raise ValueError("Invalid search")
    return parent,after,search.strip()

def query(cur,parent=None,after=0,search=""):
    parent,after,search=validate(parent,after,search)
    if parent is not None:
        cur.execute("SELECT id,first_name,last_name,email FROM students WHERE id=%s",(parent,))
        row=cur.fetchone()
        if not row: raise ValueError("Account not found")
        current={"id":row[0],"name":" ".join(x for x in row[1:3] if x),"email":row[3]}
        cur.execute("SELECT referrer_id FROM referrals WHERE student_id=%s",(parent,))
        row=cur.fetchone()
        current["parent_id"]=row[0] if row else None
    else: current=None
    if search:
        # Literal substring, not a wildcard expression or executable SQL.
        where="(strpos(lower(s.email),lower(%s))>0 OR strpos(lower(concat_ws(' ',s.first_name,s.last_name)),lower(%s))>0 OR s.id::text=%s)"
        params=[search,search,search]
    elif parent is None:
        where="r.referrer_id IS NULL";params=[]
    else:
        where="r.referrer_id=%s";params=[parent]
    cur.execute("""SELECT count(*),count(*) FILTER(WHERE e.paid_at IS NOT NULL)
        FROM students s LEFT JOIN enrollments e ON e.student_id=s.id""")
    total,paid=cur.fetchone()
    cur.execute("""SELECT count(*) FROM referrals""")
    referred=cur.fetchone()[0]
    cur.execute("""SELECT s.id,s.first_name,s.last_name,s.email,s.created_at,r.referrer_id,
          u.first_name,u.last_name,u.email,e.plan,e.paid_at,a.status,
          (SELECT count(*) FROM referrals c WHERE c.referrer_id=s.id),
          (SELECT count(*) FROM referrals c JOIN enrollments ce ON ce.student_id=c.student_id AND ce.paid_at IS NOT NULL WHERE c.referrer_id=s.id),
          (SELECT count(*) FROM payment_invoices i WHERE i.student_id=s.id AND i.paid_at IS NOT NULL),
          (SELECT COALESCE(sum(i.amount_atomic),0) FROM payment_invoices i WHERE i.student_id=s.id AND i.asset='USDC' AND i.paid_at IS NOT NULL)
        FROM students s LEFT JOIN referrals r ON r.student_id=s.id
        LEFT JOIN students u ON u.id=r.referrer_id
        LEFT JOIN enrollments e ON e.student_id=s.id
        LEFT JOIN influencer_partners a ON a.student_id=s.id
        WHERE s.id>%s AND """+where+" ORDER BY s.id LIMIT %s",[after,*params,PAGE_SIZE+1])
    rows=cur.fetchall()
    items=[]
    for sid,first,last,email,created,pid,pfirst,plast,pemail,plan,paid_at,partner,children,paid_children,settled,atomic in rows[:PAGE_SIZE]:
        items.append({"id":sid,"name":" ".join(x for x in (first,last) if x),"email":email,
            "registered_at":created.isoformat(),"parent_id":pid,"parent_name":" ".join(x for x in (pfirst,plast) if x),"parent_email":pemail,
            "plan":plan,"paid":paid_at is not None,"partner_status":partner,"direct_count":children,"direct_paid":paid_children,
            "settled_invoices":settled,"usdc_atomic":str(atomic)})
    return {"items":items,"current":current,"next_after":items[-1]["id"] if len(rows)>PAGE_SIZE else None,
            "total":total,"paid":paid,"referred":referred,"direct":total-referred,"search":search}

def network(token,body):
    from partners import owner
    from database import transaction
    owner(token)
    if not isinstance(body,dict): raise ValueError("Invalid request")
    parent,after,search=validate(body.get("parent"),body.get("after",0),body.get("search",""))
    with transaction() as cur:
        return query(cur,parent,after,search)

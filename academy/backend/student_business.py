"""Private student CRM and manual USD bookkeeping, not payment processing."""
from decimal import Decimal,InvalidOperation
import re
from datetime import date
STATES=("lead","in_progress","delivered","cancelled")
def identity(token):
    from career_profile import identity
    return identity(token)
def transaction():
    from database import transaction as tx
    return tx()
def clean(v,n,required=False):
    if not isinstance(v,str) or len(v)>n or "\x00" in v or (required and not v.strip()): raise ValueError("Invalid text")
    return v.strip()
def ident(v):
    if type(v) is not int or not 1<=v<=9223372036854775807: raise ValueError("Invalid ID")
    return v
def cents(v):
    if not isinstance(v,str) or not re.fullmatch(r"[0-9]{1,8}(?:\.[0-9]{1,2})?",v): raise ValueError("Enter USD with up to two decimals")
    n=Decimal(v)
    if n>1000000: raise ValueError("Amount exceeds limit")
    return int(n*100)
def order_values(b):
    client=ident(b["client_id"])
    title=clean(b["title"],200,True)
    status=b["status"]
    if status not in STATES: raise ValueError("Invalid status")
    due=b.get("due","")
    if due:
        if not isinstance(due,str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}",due): raise ValueError("Invalid date")
        due=date.fromisoformat(due)
    else: due=None
    agreed,received,expense=(cents(b[k]) for k in ("agreed","received","expense"))
    if received>agreed: raise ValueError("Received amount exceeds order value")
    return (client,title,status,due,agreed,received,expense,clean(b.get("notes",""),2000))
def totals(rows):
    agreed=received=expense=outstanding=0
    for status,a,r,e in rows:
        received+=r;expense+=e
        if status!="cancelled": agreed+=a;outstanding+=a-r
    return {"agreed_cents":str(agreed),"received_cents":str(received),"expense_cents":str(expense),"outstanding_cents":str(outstanding),"cash_margin_cents":str(received-expense)}
def save_client(cur,sid,b):
    name=clean(b["name"],120,True);contact=clean(b.get("contact",""),200);notes=clean(b.get("notes",""),1000)
    if b.get("id") is None:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
        cur.execute("SELECT count(*) FROM business_clients WHERE student_id=%s",(sid,))
        if cur.fetchone()[0]>=500: raise ValueError("Client limit reached")
        cur.execute("INSERT INTO business_clients(student_id,name,contact,notes) VALUES (%s,%s,%s,%s) RETURNING id",(sid,name,contact,notes))
    else:
        cur.execute("UPDATE business_clients SET name=%s,contact=%s,notes=%s WHERE student_id=%s AND id=%s RETURNING id",(name,contact,notes,sid,ident(b["id"])))
    row=cur.fetchone()
    if not row: raise PermissionError("Client unavailable")
    return {"id":row[0]}
def save_order(cur,sid,b):
    values=order_values(b)
    cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
    cur.execute("SELECT id FROM business_clients WHERE student_id=%s AND id=%s FOR KEY SHARE",(sid,values[0]))
    if not cur.fetchone(): raise PermissionError("Client unavailable")
    if b.get("id") is None:
        cur.execute("SELECT count(*) FROM business_orders WHERE student_id=%s",(sid,))
        if cur.fetchone()[0]>=1000: raise ValueError("Order limit reached")
        cur.execute("""INSERT INTO business_orders(student_id,client_id,title,status,due,agreed_cents,received_cents,expense_cents,notes)
          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",(sid,*values))
    else:
        cur.execute("""UPDATE business_orders SET client_id=%s,title=%s,status=%s,due=%s,agreed_cents=%s,received_cents=%s,expense_cents=%s,notes=%s
          WHERE student_id=%s AND id=%s RETURNING id""",(*values,sid,ident(b["id"])))
    row=cur.fetchone()
    if not row: raise PermissionError("Order unavailable")
    return {"id":row[0]}
def overview(cur,sid):
    cur.execute("SELECT id,name,contact,notes FROM business_clients WHERE student_id=%s ORDER BY id DESC",(sid,))
    clients=[dict(zip(("id","name","contact","notes"),r)) for r in cur.fetchall()]
    cur.execute("""SELECT id,client_id,title,status,due,agreed_cents,received_cents,expense_cents,notes FROM business_orders WHERE student_id=%s ORDER BY id DESC""",(sid,))
    rows=cur.fetchall()
    orders=[{"id":i,"client_id":c,"title":t,"status":s,"due":d.isoformat() if d else "","agreed_cents":a,"received_cents":r,"expense_cents":e,"notes":n} for i,c,t,s,d,a,r,e,n in rows]
    return {"clients":clients,"orders":orders,"totals":totals((r[3],r[5],r[6],r[7]) for r in rows),"currency":"USD","manual":True}
def delete(cur,sid,kind,id):
    id=ident(id)
    if kind=="client":
        cur.execute("SELECT id FROM business_clients WHERE student_id=%s AND id=%s FOR UPDATE",(sid,id))
        if not cur.fetchone(): raise PermissionError("Client unavailable")
        cur.execute("SELECT 1 FROM business_orders WHERE student_id=%s AND client_id=%s LIMIT 1",(sid,id))
        if cur.fetchone(): raise ValueError("Delete or reassign client orders first")
        cur.execute("DELETE FROM business_clients WHERE student_id=%s AND id=%s RETURNING id",(sid,id))
    elif kind=="order":
        cur.execute("DELETE FROM business_orders WHERE student_id=%s AND id=%s RETURNING id",(sid,id))
    else: raise ValueError("Invalid record type")
    if not cur.fetchone(): raise PermissionError("Record unavailable")
    return {"deleted":True}
def dispatch(token,action,b):
    sid=identity(token)
    with transaction() as cur:
        if action=="overview": return overview(cur,sid)
        if action=="client": return save_client(cur,sid,b)
        if action=="order": return save_order(cur,sid,b)
        if action=="delete": return delete(cur,sid,b["kind"],b["id"])
        raise ValueError("Invalid action")

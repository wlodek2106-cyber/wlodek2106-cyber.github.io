"""Private career preparation. No publication, job guarantees or external messaging."""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

def quote(hours, rate, expenses, buffer):
    values=[]
    for v in (hours,rate,expenses,buffer):
        if type(v) not in (int,float,str) or len(str(v))>24:
            raise ValueError("Invalid estimate")
        try: n=Decimal(str(v))
        except InvalidOperation: raise ValueError("Invalid estimate")
        if not n.is_finite() or n<0: raise ValueError("Invalid estimate")
        values.append(n)
    h,r,e,b=values
    if h>1000 or r>10000 or e>100000 or b>100: raise ValueError("Estimate exceeds limits")
    money=lambda n: str(n.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))
    labor=h*r
    contingency=(labor+e)*b/100
    return {"labor":money(labor),"expenses":money(e),"contingency":money(contingency),"total":money(labor+e+contingency),"currency":"USD"}

def overview(token):
    from learning import student_progress
    from portfolio import list_projects
    p=student_progress(token)
    if not p["paid"]: raise PermissionError("Paid enrollment required")
    projects=list_projects(token)["items"]
    return {"plan":p["plan"],"completed":sum(x["completed"] for x in p["lessons"]),"total":len(p["lessons"]),
            "projects":[{"id":x["id"],"lesson":x["lesson"],"submission":x["submission"],"score":x["score"]} for x in projects],
            "private":True}

def estimate(token,body):
    from learning import student_progress
    if not student_progress(token)["paid"]: raise PermissionError("Paid enrollment required")
    return quote(body["hours"],body["rate"],body["expenses"],body["buffer"])

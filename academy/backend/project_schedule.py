"""Shared project schedule summaries. Calendar dates are interpreted in UTC."""
from datetime import date,datetime,timezone,timedelta

def due_date(value,today=None):
    if value is None or value=="":return None
    if not isinstance(value,str) or len(value)!=10:raise ValueError("Invalid deadline")
    try:d=date.fromisoformat(value)
    except ValueError:raise ValueError("Invalid deadline")
    if d.isoformat()!=value:raise ValueError("Invalid deadline")
    today=today or datetime.now(timezone.utc).date()
    if not today<=d<=today+timedelta(days=730):raise ValueError("Deadline must be within the next two years")
    return d

def summarize(milestones,today=None):
    today=today or datetime.now(timezone.utc).date()
    items=[]
    for item in milestones:
        due=item.get("due_date")
        delta=(date.fromisoformat(due)-today).days if due else None
        state="done" if item["done"] else "unscheduled" if delta is None else "overdue" if delta<0 else "due_today" if delta==0 else "upcoming"
        items.append({**item,"schedule_state":state,"days_remaining":delta})
    done=sum(x["done"] for x in items)
    return {"items":items,"total":len(items),"done":done,
            "percent":round(100*done/len(items)) if items else None,
            "overdue":sum(x["schedule_state"]=="overdue" for x in items),
            "due_today":sum(x["schedule_state"]=="due_today" for x in items),
            "unscheduled":sum(x["schedule_state"]=="unscheduled" for x in items),
            "date_basis":"UTC","advisory_only":True}

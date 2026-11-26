"""Rule-based triage; reports are not verified incidents."""
from student_business import ident
TOPICS=("security","signin","payment","lesson","model","provider","order","connection","other")
PRIORITIES=("normal","high","urgent")
DEFAULT={"account":"signin","payment":"payment","learning":"lesson","ai":"model","marketplace":"order","other":"other"}
def classify(category,subject,body):
    text=(subject+" "+body).casefold()
    if any(x in text for x in ("account hacked","unauthorized access","взлом","украли аккаунт","несанкционирован","зламали","włam","przejęto konto")): return "security","urgent"
    if "higgsfield" in text: return "provider","normal"
    if any(x in text for x in ("503","502","504","service unavailable","server error","сервер недоступен","помилка сервера","błąd serwera")): return "connection","high"
    return DEFAULT[category],"high" if category=="payment" else "normal"
def assign(cur,tid,topic,priority):
    if not isinstance(topic,str) or topic not in TOPICS or not isinstance(priority,str) or priority not in PRIORITIES: raise ValueError("Invalid classification")
    cur.execute("UPDATE support_tickets SET topic=%s,priority=%s,triage_manual=true WHERE id=%s RETURNING id",(topic,priority,ident(tid)))
    if not cur.fetchone(): raise ValueError("Ticket unavailable")
    return {"saved":True}
def summary(cur,days):
    if type(days) is not int or days not in (7,30): raise ValueError("Invalid period")
    cur.execute("""SELECT topic,count(*),count(*) FILTER(WHERE status='open'),count(DISTINCT student_id)
       FROM support_tickets WHERE created_at>=now()-(%s * interval '1 day') GROUP BY topic ORDER BY count(*) DESC,topic""",(days,))
    topics=[{"topic":k,"tickets":n,"open":o,"accounts":a,"pattern":a>=3} for k,n,o,a in cur.fetchall()]
    cur.execute("SELECT priority,count(*) FROM support_tickets WHERE status='open' GROUP BY priority")
    counts=dict(cur.fetchall())
    cur.execute("SELECT count(*) FROM support_tickets WHERE status='open' AND updated_at<now()-interval '24 hours'")
    return {"topics":topics,"priorities":{k:counts.get(k,0) for k in PRIORITIES},"waiting":cur.fetchone()[0],"days":days}

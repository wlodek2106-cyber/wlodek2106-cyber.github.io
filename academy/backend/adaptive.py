"""Free, transparent study recommendations based on the learner's own quiz results."""
from datetime import datetime, timezone

def recommend(lessons, attempts):
    visible={x["day"]:x for x in lessons if x["unlocked"] or x["completed"]}
    grouped={}
    for day,score in attempts:
        if day in visible:
            grouped.setdefault(day,[]).append(score)
    review=[]
    for day,scores in grouped.items():
        latest=scores[0]
        if latest<90 or (len(scores)>1 and min(scores)<80):
            review.append({"day":day,"last_score":latest,"attempts":len(scores),"priority":"high" if latest<80 else "medium"})
    review.sort(key=lambda x:(x["priority"]!="high",x["last_score"],-x["day"]))
    next_lesson=next((x for x in lessons if not x["completed"]),None)
    return {"completed":sum(x["completed"] for x in lessons),"total":len(lessons),
            "attempted_lessons":len(grouped),"mean_latest":round(sum(s[0] for s in grouped.values())/len(grouped),1) if grouped else None,
            "review":review[:5],"next":next_lesson,"engine":"rules_based","evidence":"quiz_scores_only"}

def weekly_plan(lessons,attempts,minutes=30):
    """Seven suggested sessions, based only on the current entitlement snapshot."""
    if type(minutes) is not int or minutes not in (15,30,60):
        raise ValueError("Choose 15, 30 or 60 minutes")
    summary=recommend(lessons,attempts)
    unlocked={x["day"] for x in lessons if x["unlocked"]}
    focus=[r["day"] for r in summary["review"] if r["day"] in unlocked]
    next_lesson=summary["next"]
    current=next_lesson["day"] if next_lesson and next_lesson["unlocked"] else None
    completed=[x["day"] for x in reversed(lessons) if x["completed"] and x["unlocked"]]
    queue=list(dict.fromkeys(focus+completed))
    sessions=[]
    for i in range(7):
        if i==0 and current is not None:
            kind,day="learn",current
        elif i in (2,5) and (queue or current is not None):
            kind,day="practice",queue[i%len(queue)] if queue else current
        elif queue:
            kind,day="review",queue[(i-1)%len(queue)]
        elif current is not None:
            kind,day="review",current
        else:
            kind,day="reflect",None
        if i==6:
            kind,day="reflect",None
        first=minutes//3
        sessions.append({"session":i+1,"kind":kind,"lesson":day,"minutes":minutes,
                         "blocks":[first,first,minutes-2*first]})
    return {"sessions":sessions,"daily_minutes":minutes,"total_minutes":minutes*7,
            "engine":"rules_based","access":"current_snapshot","recommendations":summary}
def student_plan(token,minutes=None):
    from learning import student_progress
    from accounts import authenticate
    from database import transaction
    student=authenticate(token)
    if student is None: raise PermissionError("Sign in required")
    p=student_progress(token)
    if not p["paid"]: raise PermissionError("Paid enrollment required")
    with transaction() as cur:
        cur.execute("""SELECT a.lesson,a.score FROM quiz_attempts a
        JOIN enrollments e ON e.id=a.enrollment_id
        WHERE e.student_id=%s AND e.paid_at IS NOT NULL
        ORDER BY a.attempted_at DESC,a.id DESC LIMIT 500""",(student,))
        attempts=cur.fetchall()
    return recommend(p["lessons"],attempts) if minutes is None else weekly_plan(p["lessons"],attempts,minutes)

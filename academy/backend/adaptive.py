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

def student_plan(token):
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
    return recommend(p["lessons"],attempts)

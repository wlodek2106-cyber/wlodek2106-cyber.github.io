"""Private review journal based on actual quiz scores and learner-entered reflections."""
from datetime import datetime,timezone,timedelta

def build_journal(lessons,attempts,notes,now=None):
    now=now or datetime.now(timezone.utc)
    visible={l["day"] for l in lessons if l["unlocked"]}
    groups={}
    for day,score,when in attempts:
        if day in visible:groups.setdefault(day,[]).append((score,when))
    result=[]
    for day in sorted(visible):
        scores=groups.get(day,[])
        note=notes.get(day)
        if not scores and not note:continue
        latest=scores[0][0] if scores else None
        first=scores[-1][0] if scores else None
        last_exam=scores[0][1] if scores else None
        reviewed=note["reviewed_at"] if note else None
        base=max(x for x in (last_exam,reviewed) if x is not None)
        interval=1 if latest is None or latest<80 else 3 if latest<90 else 7
        due=base+timedelta(days=interval)
        result.append({"day":day,"attempts":len(scores),"latest":latest,"first_in_window":first,
                       "best_in_window":max(x[0] for x in scores) if scores else None,
                       "change":latest-first if scores else None,"due_at":due.isoformat(),
                       "due":due<=now,"interval_days":interval,
                       "reflection":note["reflection"] if note else "",
                       "reviewed_at":reviewed.isoformat() if reviewed else None})
    result.sort(key=lambda r:(not r["due"],r["due_at"],r["day"]))
    return {"items":result,"due_count":sum(x["due"] for x in result),"attempt_window":500,
            "engine":"rules_based","evidence":"quiz_scores_and_self_reflection"}

def validate(day,reflection):
    if type(day) is not int or not 1<=day<=45:raise ValueError("Invalid lesson")
    if not isinstance(reflection,str) or not 5<=len(reflection.strip())<=1200 or "\x00" in reflection:
        raise ValueError("Enter 5–1200 characters of reflection")
    return day,reflection.strip()

def dispatch(token,action,body):
    from accounts import authenticate
    from learning import student_progress
    from database import transaction
    sid=authenticate(token)
    if sid is None:raise PermissionError("Authentication required")
    progress=student_progress(token)
    visible={x["day"] for x in progress["lessons"] if x["unlocked"]}
    with transaction() as cur:
        if action=="review":
            day,reflection=validate(body.get("day"),body.get("reflection"))
            if day not in visible:raise PermissionError("Lesson locked")
            cur.execute("""INSERT INTO student_review_notes(student_id,lesson,reflection) VALUES (%s,%s,%s)
                ON CONFLICT(student_id,lesson) DO UPDATE SET reflection=EXCLUDED.reflection,reviewed_at=now()""",(sid,day,reflection))
            return {"saved":True}
        if action=="delete":
            day=body.get("day")
            if type(day) is not int or not 1<=day<=45:raise ValueError("Invalid lesson")
            cur.execute("DELETE FROM student_review_notes WHERE student_id=%s AND lesson=%s",(sid,day))
            return {"deleted":True}
        if action=="list":
            cur.execute("""SELECT a.lesson,a.score,a.attempted_at FROM quiz_attempts a
                JOIN enrollments e ON e.id=a.enrollment_id WHERE e.student_id=%s
                ORDER BY a.attempted_at DESC,a.id DESC LIMIT 500""",(sid,))
            attempts=cur.fetchall()
            cur.execute("SELECT lesson,reflection,reviewed_at FROM student_review_notes WHERE student_id=%s",(sid,))
            notes={d:{"reflection":r,"reviewed_at":t} for d,r,t in cur.fetchall()}
            return build_journal(progress["lessons"],attempts,notes)
    raise ValueError("Invalid action")

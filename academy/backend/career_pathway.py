"""Private evidence-based career plan. No claims of professional qualification or job guarantees."""
from job_matching import TOPICS

CATEGORIES=tuple(k for k,v in TOPICS.items() if v)

def pathway(lessons,projects,category):
    if not isinstance(category,str) or category not in CATEGORIES: raise ValueError("Invalid specialization")
    all_days={x["day"] for x in lessons}
    visible={x["day"] for x in lessons if x["unlocked"]}
    completed={x["day"] for x in lessons if x["unlocked"] and x["completed"]}
    relevant=set(TOPICS[category])
    included=relevant & all_days
    submitted={p["lesson"] for p in projects if p["lesson"] in visible and p["lesson"] in included}
    approved={p["lesson"] for p in projects if p["lesson"] in submitted and p.get("passed") is True}
    passed=included & completed
    practice=sorted((included & visible)-submitted)
    improve=sorted(submitted-approved)
    next_day=next(iter(sorted(visible-completed)),None)
    next_relevant=next(iter(sorted((included & visible)-completed)),None)
    if practice: action,day="practice",practice[0]
    elif improve: action,day="review_project",improve[0]
    elif next_relevant is not None: action,day="learn",next_relevant
    elif included-passed or not included:
        action,day=("continue_course",next_day) if next_day is not None else ("wait_or_plan",None)
    else: action,day="portfolio",None
    return {"category":category,"in_plan":len(included),"outside_plan":len(relevant-included),
            "unlocked":len(included & visible),"completed":len(passed),"submitted":len(submitted),
            "review_passed":len(approved),"next":{"action":action,"day":day},
            "evidence":"distinct_lesson_days","qualification_verified":False}

def collect(cur,sid):
    cur.execute("""SELECT p.lesson,p.score,p.rubric_scores FROM project_submissions p
        JOIN enrollments e ON e.id=p.enrollment_id WHERE e.student_id=%s ORDER BY p.id""",(sid,))
    return [{"lesson":day,"passed":score is not None and score>=80 and isinstance(rubric,dict) and
             type(rubric.get("rights")) is int and rubric["rights"]>=12} for day,score,rubric in cur.fetchall()]

def report(token,category,lang):
    from accounts import authenticate
    from database import transaction
    from learning import student_progress
    from practice_lab import student_brief,LABELS
    from career import accelerator_data
    sid=authenticate(token)
    if sid is None: raise PermissionError("Authentication required")
    if not isinstance(lang,str) or lang not in LABELS: raise ValueError("Invalid language")
    progress=student_progress(token)
    lessons=progress["lessons"]
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        result=pathway(lessons,collect(cur,sid),category)
        roadmap=accelerator_data(cur,sid,sum(x["completed"] for x in lessons),len(lessons)) if progress["access"] else None
    day=result["next"]["day"]
    result["brief"]=student_brief(token,day,lang) if day is not None and result["next"]["action"] in ("practice","review_project") else None
    result["roadmap"]=roadmap
    result["private"]=True
    result["paid"]=progress["paid"]
    return result

"""Owner-reviewed practical projects. Existing completion and ELITE credentials are unchanged."""
import json
CRITERIA=("goal","quality","workflow","verification","rights")
def evaluate(scores,feedback):
    if not isinstance(scores,dict) or set(scores)!=set(CRITERIA) or any(type(v) is not int or not 0<=v<=20 for v in scores.values()):
        raise ValueError("Five integer scores of 0–20 are required")
    if not isinstance(feedback,str) or not 10<=len(feedback.strip())<=2000 or "\x00" in feedback:
        raise ValueError("Provide 10–2000 characters of feedback")
    total=sum(scores.values())
    return {"score":total,"criteria":{k:scores[k] for k in CRITERIA},"feedback":feedback.strip(),"passed":total>=80 and scores["rights"]>=12}

def ident(value):
    if type(value) is not int or not 1<=value<=9223372036854775807:raise ValueError("Invalid project")
    return value

def pending(cur,after=0):
    if type(after) is not int or not 0<=after<=9223372036854775807:raise ValueError("Invalid cursor")
    cur.execute("""SELECT p.id,p.lesson,p.submission,p.submitted_at,e.student_id,e.plan,e.paid_at IS NOT NULL
        FROM project_submissions p JOIN enrollments e ON e.id=p.enrollment_id
        WHERE p.score IS NULL AND p.id>%s ORDER BY p.id LIMIT 21""",(after,))
    rows=cur.fetchall()
    items=[{"id":i,"lesson":l,"submission":s,"submitted_at":t.isoformat(),"student_id":sid,"plan":plan,"paid":paid} for i,l,s,t,sid,plan,paid in rows[:20]]
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>20 else None}

def grade(cur,body):
    pid=ident(body.get("id"))
    if body.get("inspected") is not True:raise ValueError("Confirm actual evidence was inspected")
    result=evaluate(body.get("scores"),body.get("feedback"))
    cur.execute("""UPDATE project_submissions SET score=%s,feedback=%s,rubric_scores=%s::jsonb,reviewed_at=now()
        WHERE id=%s AND score IS NULL RETURNING id""",(result["score"],result["feedback"],json.dumps(result["criteria"]),pid))
    if not cur.fetchone():raise PermissionError("Project unavailable or already reviewed")
    return {"id":pid,**result}

def dispatch(token,action,body):
    from partners import owner
    from database import transaction
    owner(token)
    with transaction() as cur:
        if action=="pending":return pending(cur,body.get("after",0))
        if action=="grade":return grade(cur,body)
    raise ValueError("Invalid action")

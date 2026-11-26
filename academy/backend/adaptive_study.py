"""Rule-based study agenda; never unlock or grade lessons."""
def agenda(progress,journal,minutes):
    if type(minutes) is not int or minutes not in (15,30,60): raise ValueError("Invalid study duration")
    visible={x["day"]:x for x in progress["lessons"] if x["unlocked"]}
    scores={x["day"]:x for x in journal["items"] if x["day"] in visible}
    rows=sorted(scores.values(),key=lambda r:(not r["due"],r["latest"] is None,r["latest"] if r["latest"] is not None else 101,r["day"]))
    next_day=next((d for d,x in sorted(visible.items()) if not x["completed"]),None)
    focus=next((r for r in rows if r["due"] or (r["latest"] is not None and r["latest"]<80)),None)
    day=focus["day"] if focus else next_day
    if day is None and rows: day=rows[0]["day"]
    if day is None and visible: day=max(visible)
    if day is None: return {"minutes":minutes,"items":[],"focus":None,"engine":"rules_based"}
    score=scores.get(day,{}).get("latest")
    level="foundation" if score is None or score<80 else "reinforce" if score<90 else "challenge"
    review=focus is not None or visible[day]["completed"]
    durations={15:(4,8,3),30:(8,16,6),60:(15,35,10)}[minutes]
    items=[{"day":day,"kind":kind,"minutes":n} for kind,n in zip(("review" if review else "learn","practice","reflect"),durations)]
    return {"minutes":minutes,"items":items,"focus":{"day":day,"latest":score,"level":level,"due":bool(scores.get(day,{}).get("due"))},"engine":"rules_based"}

def plan(token,minutes,lang):
    from learning import student_progress
    from review_journal import dispatch
    from practice_lab import student_brief,LABELS
    from teacher_profile import snapshot
    if not isinstance(lang,str) or lang not in LABELS: raise ValueError("Invalid language")
    progress=student_progress(token)
    journal=dispatch(token,"list",{})
    result=agenda(progress,journal,minutes)
    result["snapshot"]=snapshot(progress,journal)
    result["brief"]=student_brief(token,result["focus"]["day"],lang) if result["focus"] else None
    result["private"]=True
    result["official_grading"]=False
    return result

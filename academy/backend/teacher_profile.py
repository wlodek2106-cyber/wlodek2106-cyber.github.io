"""Minimal learner-controlled snapshot, with no identity, notes, exam keys or private submissions."""
def snapshot(progress,journal):
    visible={x["day"]:x for x in progress["lessons"] if x["unlocked"]}
    next_day=next((d for d,l in sorted(visible.items()) if not l["completed"]),None)
    rows=[]
    for item in journal["items"]:
        day=item["day"]
        if day not in visible:continue
        rows.append({"day":day,"latest":item["latest"],"attempts":item["attempts"],"due":item["due"]})
    rows.sort(key=lambda x:(not x["due"],x["latest"] is None,x["latest"] if x["latest"] is not None else 101,x["day"]))
    return {"version":1,"kind":"zer0life_teacher_snapshot","completed":sum(l["completed"] for l in visible.values()),"available":len(visible),"next_day":next_day,"review":rows[:8],"evidence":"quiz_summary_only"}

def export(token):
    from learning import student_progress
    from review_journal import dispatch
    p=student_progress(token)
    j=dispatch(token,"list",{})
    return snapshot(p,j)

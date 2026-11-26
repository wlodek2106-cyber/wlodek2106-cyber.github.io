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

# These are practice suggestions based on score summaries, never a diagnosis of specific mistakes.
PRACTICE_LEVELS={
    "en":{"foundation":"Explain the key concept without notes, then create a simple example and compare it with the lesson.","reinforce":"Repeat the task with a different input; compare both outputs against two acceptance criteria.","challenge":"Create a variant for a new client brief; document a failure case, verification and revisions."},
    "ru":{"foundation":"Объясни ключевое понятие без подсказок, создай простой пример и сравни его с уроком.","reinforce":"Повтори задание с другими исходными данными; сравни оба результата по двум критериям приёмки.","challenge":"Создай вариант для нового клиентского брифа; опиши неудачный случай, проверку и правки."},
    "uk":{"foundation":"Поясни ключове поняття без підказок, створи простий приклад і порівняй його з уроком.","reinforce":"Повтори завдання з іншими вхідними даними; порівняй результати за двома критеріями приймання.","challenge":"Створи варіант для нового клієнтського брифу; опиши невдалий випадок, перевірку та правки."},
    "pl":{"foundation":"Wyjaśnij kluczowe pojęcie bez notatek, stwórz prosty przykład i porównaj z lekcją.","reinforce":"Powtórz zadanie z innymi danymi; porównaj oba wyniki według dwóch kryteriów akceptacji.","challenge":"Przygotuj wariant dla nowego briefu klienta; opisz niepowodzenie, weryfikację i poprawki."}
}

def practice_focus(focus,lang):
    if lang not in PRACTICE_LEVELS: raise ValueError("Invalid language")
    if focus is None:return None
    return {"day":focus["day"],"level":focus["level"],"task":PRACTICE_LEVELS[lang][focus["level"]],
            "evidence":"quiz_summary_only","official_grading":False}

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
    result["practice_focus"]=practice_focus(result["focus"],lang)
    result["private"]=True
    result["official_grading"]=False
    return result

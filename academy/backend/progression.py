"""Server-side policy; caller must authenticate and persist verified quiz results."""
from datetime import datetime, timedelta, timezone

LESSONS = 30
PASS_PERCENT = 80

def eligible(lesson, paid_at, passed_at, now=None):
    now = now or datetime.now(timezone.utc)
    if not paid_at or not isinstance(lesson, int) or not 1 <= lesson <= LESSONS:
        return False
    if now < paid_at + timedelta(days=lesson-1):
        return False
    for previous in range(1, lesson):
        stamp = passed_at.get(previous)
        if stamp is None or stamp > now:
            return False
    if lesson > 1 and now < passed_at[lesson-1] + timedelta(days=1):
        return False
    return True

def quiz_passed(answers, correct):
    if not correct or set(answers) != set(correct):
        return False
    return sum(answers[k] == v for k,v in correct.items()) * 100 >= PASS_PERCENT * len(correct)

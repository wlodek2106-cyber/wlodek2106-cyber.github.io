from secrets import SystemRandom
from uuid import uuid4
from progression import quiz_passed

def prepare_attempt(bank):
    if len(bank) < 10 or len({q["id"] for q in bank}) != len(bank):
        raise ValueError("Ten distinct questions required")
    rng = SystemRandom()
    public, key = [], {}
    for q in rng.sample(bank,10):
        options = list(q["options"])
        if len(set(options)) != len(options) or q["correct"] not in options:
            raise ValueError("Invalid question")
        rng.shuffle(options)
        public.append({"id":q["id"],"question":q["question"],"options":options})
        key[q["id"]] = options.index(q["correct"])
    return {"attempt_id":str(uuid4()),"questions":public},key

def grade_attempt(answers,key):
    if len(key)!=10 or set(answers)!=set(key) or any(type(v) is not int for v in answers.values()):
        raise ValueError("Invalid submission")
    score = sum(answers[k]==v for k,v in key.items())*10
    return {"score":score,"passed":quiz_passed(answers,key)}

RUBRIC = {"brief_alignment":25,"technical_quality":25,"originality":20,"verification_and_rights":20,"presentation":10}

def grade_project(points):
    if set(points)!=set(RUBRIC) or any(type(v) is not int or not 0<=v<=RUBRIC[k] for k,v in points.items()):
        raise ValueError("Invalid rubric scores")
    return sum(points.values())

# Attempt keys must be stored privately, bound to authenticated enrollment,
# lesson and expiry, and consumed atomically on submission. Never publish keys.

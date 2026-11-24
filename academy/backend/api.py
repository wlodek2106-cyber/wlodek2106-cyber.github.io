import os
from accounts import register,login,logout
from learning import student_progress,require_lesson
from database import ready
from lesson01 import public_lesson
import json
from pathlib import Path

def dispatch(method,path,body,token):
    if path=="/ready":
        return 200,{"database":ready(),"payments":False}
    if not ready():
        return 503,{"error":"Database unavailable"}
    if path=="/register" and method=="POST":
        if os.getenv("ACADEMY_REGISTRATION_ENABLED")!="true":
            return 403,{"error":"Registration closed"}
        return 201,{"id":register(body["email"],body["password"])}
    if path=="/login" and method=="POST":
        return 200,{"token":login(body["email"],body["password"])}
    if path=="/logout" and method=="POST":
        if not token: raise PermissionError("Authentication required")
        logout(token)
        return 200,{"ok":True}
    if path=="/progress" and method=="GET":
        return 200,student_progress(token)
    if path=="/tutor" and method=="POST":
        from tutor import guidance
        return 200,guidance(token,body["day"],body["mode"])
    if path=="/admin/statistics" and method=="GET":
        if os.getenv("ACADEMY_ADMIN_ENABLED")!="true":
            raise PermissionError("Administration disabled")
        from admin import statistics
        return 200,statistics(token)
    if path=="/certificates/issue" and method=="POST":
        from certificates import issue_certificate
        return 200,issue_certificate(token)
    if path=="/certificates/verify" and method=="POST":
        from certificates import verify_certificate
        code=body["code"]
        if not isinstance(code,str) or len(code)>128:
            raise ValueError("Invalid code")
        return 200,verify_certificate(code)
    if path=="/exams/start" and method=="POST":
        from exams import start_exam
        day=body["day"]
        require_lesson(token,day)
        if day==1:
            from lesson01 import LESSON
            bank=[{"id":str(i),"question":q[0],"options":q[1],"correct":q[1][q[2]]} for i,q in enumerate(LESSON["questions"])]
        elif day==2:
            bank=json.loads(Path(__file__).with_name("quiz02.json").read_text())
        else:
            banks=json.loads(Path(__file__).with_name("quiz03_30.json").read_text())
            bank=next(item["questions"] for item in banks if item["day"]==day)
        return 200,start_exam(token,day,bank)
    if path=="/exams/submit" and method=="POST":
        from exams import submit_exam
        return 200,submit_exam(token,body["day"],body["attempt_id"],body["answers"])
    if path.startswith("/lessons/") and method=="GET":
        day=int(path.rsplit("/",1)[1])
        require_lesson(token,day)
        if day==1:
            return 200,public_lesson()
        filename="lessons02_06.json" if day<=6 else "lessons07_30.json"
        lessons=json.loads(Path(__file__).with_name(filename).read_text())
        return 200,next(item for item in lessons if item["day"]==day)
    return 404,{"error":"Not found"}
# HTTP adapter must validate request bodies, enforce rate limits and handle errors.

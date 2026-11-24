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

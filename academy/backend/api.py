import os
from accounts import register,login,logout
from learning import student_progress,require_lesson
from database import ready
from lesson01 import public_lesson
import json
from pathlib import Path

def dispatch(method,path,body,token):
    if path=="/ready":
        database_ok=ready()
        payments=database_ok and os.getenv("ACADEMY_CHECKOUT_READY")=="true" and os.getenv("ACADEMY_PAYMENTS_ENABLED")=="true"
        return 200,{"database":database_ok,"payments":payments,"assets":["USDC"] if payments else [],"settlement_live_tested":False}
    if not ready():
        return 503,{"error":"Database unavailable"}
    if path=="/reviews/public" and method=="GET":
        from reviews import public_reviews
        return 200,public_reviews()
    if path=="/reviews/publish" and method=="POST":
        from reviews import publish
        return 200,publish(token,body["rating"],body["review"],body.get("consent"))
    if path=="/reviews/remove" and method=="POST":
        from reviews import remove
        return 200,remove(token)
    if path=="/tutor/models" and method=="GET":
        from accounts import authenticate
        from ai_models import status
        if authenticate(token) is None: raise PermissionError("Sign in required")
        return 200,{"roles":status()}
    if path=="/register" and method=="POST":
        if os.getenv("ACADEMY_REGISTRATION_ENABLED")!="true":
            return 403,{"error":"Registration closed"}
        if not all(isinstance(body.get(k),str) and body[k].strip() for k in ("first_name","last_name")):
            raise ValueError("First and last name required")
        return 201,{"id":register(body["email"],body["password"],body["first_name"],body["last_name"],body.get("referral"))}
    if path=="/login" and method=="POST":
        return 200,{"token":login(body["email"],body["password"])}
    if path=="/account/me" and method=="GET":
        from accounts import authenticate
        student=authenticate(token)
        if student is None: raise PermissionError("Sign in required")
        return 200,{"id":student}
    if path=="/logout" and method=="POST":
        if not token: raise PermissionError("Authentication required")
        logout(token)
        return 200,{"ok":True}
    if path=="/pro/library" and method=="GET":
        p=student_progress(token)
        if not p.get("paid") or p.get("plan") not in ("pro","vip"):
            raise PermissionError("Pro or VIP required")
        return 200,{"items":json.loads(Path(__file__).with_name("pro_library.json").read_text()),"language":"en"}
    if path=="/portfolio" and method=="GET":
        from portfolio import list_projects
        return 200,list_projects(token)
    if path=="/portfolio" and method=="POST":
        from portfolio import save
        return 201,save(token,body["day"],body["submission"])
    if path.startswith("/agent-lab/") and method=="GET":
        day=int(path.rsplit("/",1)[1])
        if not 41<=day<=45:
            raise ValueError("Invalid lab")
        require_lesson(token,day)
        return 200,next(x for x in json.loads(Path(__file__).with_name("agent_lab.json").read_text()) if x["day"]==day)
    if path=="/achievements" and method=="GET":
        from achievements import student_achievements
        return 200,student_achievements(token)
    if path=="/agent-playground" and method=="POST":
        require_lesson(token,41)
        from playground import simulate
        return 200,simulate(body["case"],body["tools"],body["approval"],body["max_steps"])
    if path=="/partners" and method=="GET":
        from partners import dashboard
        return 200,dashboard(token)
    if path=="/partners/marketing" and method=="POST":
        from marketing import kit
        return 200,kit(token,body.get("lang","en"))
    if path=="/partners/apply" and method=="POST":
        from partners import apply
        return 201,apply(token,body["profile"],body["wallet"],body.get("consent"))
    if path=="/partners/request" and method=="POST":
        from partners import request
        return 201,request(token,body["invoice"])
    if path=="/admin/partners" and method=="GET":
        from partners import queue
        return 200,queue(token)
    if path=="/admin/partners/decide" and method=="POST":
        from partners import decide
        return 200,decide(token,body["kind"],body["id"],body["action"],body.get("signature"))
    if path=="/referrals" and method=="GET":
        from referrals import overview
        return 200,overview(token)
    if path=="/career/overview" and method=="GET":
        from career import overview
        return 200,overview(token)
    if path=="/career/estimate" and method=="POST":
        from career import estimate
        return 200,estimate(token,body)
    if path=="/adaptive/plan" and method=="GET":
        from adaptive import student_plan
        return 200,student_plan(token)
    if path=="/progress" and method=="GET":
        return 200,student_progress(token)
    if path=="/checkout/history" and method=="POST":
        from checkout import history
        return 200,history(token,body.get("offset",0))
    if path=="/checkout/prices" and method=="GET":
        from checkout import prices
        return 200,prices(token)
    if path=="/checkout/discover" and method=="POST":
        from payment_discovery import discover
        return 200,discover(token,body["invoice"])
    if path=="/checkout/confirm" and method=="POST":
        from settlement import settle
        return 200,settle(token,body["invoice"],body["signature"])
    if path=="/checkout/qr" and method=="GET":
        if os.getenv("ACADEMY_CHECKOUT_READY")!="true" or os.getenv("ACADEMY_PAYMENTS_ENABLED")!="true":
            raise PermissionError("Payments closed")
        from checkout import active_invoice
        import qrcode
        from qrcode.image.svg import SvgPathImage
        from io import BytesIO
        import base64
        invoice=active_invoice(token)["invoice"]
        if not invoice:
            raise ValueError("No active invoice")
        buf=BytesIO()
        qrcode.make(invoice["url"],image_factory=SvgPathImage).save(buf)
        return 200,{"svg_base64":base64.b64encode(buf.getvalue()).decode("ascii")}
    if path=="/checkout/active" and method=="GET":
        if os.getenv("ACADEMY_CHECKOUT_READY")!="true" or os.getenv("ACADEMY_PAYMENTS_ENABLED")!="true":
            return 200,{"invoice":None}
        from checkout import active_invoice
        return 200,active_invoice(token)
    if path=="/checkout/create" and method=="POST":
        if os.getenv("ACADEMY_CHECKOUT_READY")!="true":
            return 503,{"error":"Checkout not available"}
        from checkout import create_invoice
        return 201,create_invoice(token,body["plan"])
    if path=="/tutor/ask" and method=="POST":
        from tutor import ask,save_answer
        lang=body.get("lang","en")
        result=ask(token,body["day"],body["mode"],lang,body["question"],body.get("role"),body.get("consent"))
        return 200,save_answer(token,body["day"],body["mode"],lang,body["question"],result)
    if path=="/tutor/history" and method=="GET":
        from tutor import history
        return 200,history(token)
    if path=="/tutor/history/clear" and method=="POST":
        from tutor import clear_history
        return 200,clear_history(token)
    if path=="/tutor" and method=="POST":
        from tutor import guidance
        return 200,guidance(token,body["day"],body["mode"],body.get("lang","en"))
    if path=="/admin/founder" and method=="POST":
        from founder import founder_report
        return 200,founder_report(token,body.get("days",30))
    if path=="/admin/network-access" and method=="GET":
        from partners import owner
        try: owner(token)
        except PermissionError: return 200,{"allowed":False}
        return 200,{"allowed":True}
    if path=="/admin/network" and method=="POST":
        from network_admin import network
        return 200,network(token,body)
    if path=="/admin/statistics" and method=="GET":
        if os.getenv("ACADEMY_ADMIN_ENABLED")!="true":
            raise PermissionError("Administration disabled")
        from admin import statistics
        return 200,statistics(token)
    if path=="/certificates/pdf" and method=="GET":
        from certificates import issue_certificate,certificate_pdf
        import base64
        return 200,{"pdf_base64":base64.b64encode(certificate_pdf(issue_certificate(token))).decode("ascii")}
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
            localized=json.loads(Path(__file__).with_name("quiz01_translations.json").read_text()).get(body.get("lang","en"))
            questions=LESSON["questions"] if not localized else [(v[0],v[1:],LESSON["questions"][i][2]) for i,v in enumerate(localized)]
            bank=[{"id":str(i),"question":q[0],"options":q[1],"correct":q[1][q[2]]} for i,q in enumerate(questions)]
        elif day>30:
            bank=next(x["questions"] for x in json.loads(Path(__file__).with_name("vip_lessons.json").read_text()) if x["day"]==day)
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
        parts=path.split("/")
        day=int(parts[2])
        lang=parts[3] if len(parts)==4 else "en"
        require_lesson(token,day)
        if day==1:
            lesson=public_lesson()
            localized=json.loads(Path(__file__).with_name("lesson01_translations.json").read_text())
            lesson.update(localized.get(lang,{}))
            lesson["content_language"]=lang if lang in localized else "en"
            return 200,lesson
        if day>30:
            lesson=next(x for x in json.loads(Path(__file__).with_name("vip_lessons.json").read_text()) if x["day"]==day)
            localized=json.loads(Path(__file__).with_name("vip_translations.json").read_text())
            if lang in localized:
                lesson.update(next(x for x in localized[lang] if x["day"]==day))
            return 200,{**{k:v for k,v in lesson.items() if k!="questions"},"content_language":lang if lang in localized else "en","prompts_language":"en"}
        filename="lessons02_06.json" if day<=6 else "lessons07_30.json"
        lessons=json.loads(Path(__file__).with_name(filename).read_text())
        lesson=next(item for item in lessons if item["day"]==day)
        if day<=30 and lang in ("ru","uk","pl"):
            translations=json.loads(Path(__file__).with_name("lessons02_06_translations.json" if day<=6 else "lessons07_15_translations.json" if day<=15 else "lessons16_30_translations.json").read_text())
            lesson.update(next(item for item in translations[lang] if item["day"]==day))
            return 200,{**lesson,"content_language":lang,"prompts_language":lang if day<=6 else "en"}
        return 200,{**lesson,"content_language":"en"}
    return 404,{"error":"Not found"}
# HTTP adapter must validate request bodies, enforce rate limits and handle errors.

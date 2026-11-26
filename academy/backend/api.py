import os
from accounts import register,login,logout
from learning import student_progress,require_lesson
from database import ready
from lesson01 import public_lesson
from vip_creator_labs import supplement as _vip_supplement
from creator_2027 import TRACKS, enrich

def vip_creator_supplement(lesson,day,lang):
    return enrich(_vip_supplement(lesson,day,lang),day,lang)
import json
from pathlib import Path

def dispatch(method,path,body,token):
    if path=="/ready":
        database_ok=ready()
        payments=database_ok and os.getenv("ACADEMY_CHECKOUT_READY")=="true" and os.getenv("ACADEMY_PAYMENTS_ENABLED")=="true"
        from marketplace_release import enabled as marketplace_enabled
        return 200,{"database":database_ok,"payments":payments,"assets":["USDC"] if payments else [],
                    "course_checkout_configured":payments,
                    "marketplace_payments":database_ok and marketplace_enabled(),
                    "settlement_live_tested":False,"commercial_approved":False}
    if not ready():
        return 503,{"error":"Database unavailable"}
    if path in ("/notifications/count","/notifications/list","/notifications/read") and method=="POST":
        from notifications import dispatch as notification_dispatch
        return 200,notification_dispatch(token,path.rsplit("/",1)[1],body)
    # Guard new payment issuance at the HTTP dispatch boundary as well as the payment module.
    # Existing reconciliation and settlement routes remain available for already-issued invoices.
    if ((path.startswith("/marketplace-pay/request/") and method in ("GET","POST")) or
        (path in ("/marketplace-pay/qr","/marketplace-pay/wallet","/marketplace-pay/create") and method=="POST")):
        from marketplace_release import enabled
        if not enabled():
            raise PermissionError("Marketplace payments closed")
    if path.startswith("/marketplace-pay/request/") and method in ("GET","POST"):
        from marketplace_payments import request_transaction
        return 200,request_transaction(path.rsplit("/",1)[1],method,body)
    if path in ("/marketplace-pay/qr","/marketplace-pay/preview","/marketplace-pay/wallet","/marketplace-pay/create","/marketplace-pay/settle","/marketplace-pay/treasury","/marketplace-pay/treasury-preflight","/marketplace-pay/reconcile","/marketplace-pay/admin-reconcile","/marketplace-pay/cancel-unissued") and method=="POST":
        from marketplace_payments import dispatch as pay_dispatch
        return 200,pay_dispatch(token,path.rsplit("/",1)[1],body)
    if path=="/admin/acquisition" and method=="GET":
        from acquisition import admin_report
        return 200,admin_report(token)
    if path in tuple("/jobs/"+x for x in ("feed","mine","admin","create","moderate","apply","applicants","applications","transition","recommended","analytics","review","reputation","review-admin","review-decide","room","room-message","room-milestone","room-handoff")) and method=="POST":
        from job_board import dispatch as job_dispatch
        return 200,job_dispatch(token,path.rsplit("/",1)[1],body)
    if path in ("/community/feed","/community/mine","/community/create","/community/withdraw","/community/admin","/community/decide") and method=="POST":
        from community import dispatch as community_dispatch
        return 200,community_dispatch(token,path.rsplit("/",1)[1],body)
    if path in ("/marketplace/public","/marketplace/mine","/marketplace/save","/marketplace/withdraw","/marketplace/admin","/marketplace/decide") and method=="POST":
        from marketplace import dispatch as market_dispatch
        return 200,market_dispatch(token,path.rsplit("/",1)[1],body)
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
            return 403,{"error":"Registration closed","code":"registration_closed"}
        from registration_validation import validate
        values,error=validate(body)
        if error:
            return 400,{"error":"Registration details invalid","code":error}
        try:
            return 201,{"id":register(values["email"],values["password"],values["first_name"],values["last_name"],body.get("referral"),body.get("hire_source"),body.get("campaign_source"))}
        except ValueError:
            # Do not reveal whether an address is registered or expose internal exceptions.
            return 400,{"error":"Registration unavailable; try signing in if you already have an account.","code":"registration_unavailable"}
    if path=="/login" and method=="POST":
        return 200,{"token":login(body["email"],body["password"],body.get("code"))}
    if path=="/account/passkeys" and method=="GET":
        from passkeys import status
        return 200,status(token)
    if path in ("/account/passkeys/begin","/account/passkeys/finish","/account/passkeys/disable","/passkeys/login/begin","/passkeys/login/finish") and method=="POST":
        import passkeys
        if path=="/passkeys/login/begin": return 200,passkeys.login_begin()
        if path=="/passkeys/login/finish": return 200,passkeys.login_finish(body)
        action=path.rsplit("/",1)[1]
        handler={"begin":passkeys.register_begin,"finish":passkeys.register_finish,"disable":passkeys.disable}[action]
        return 200,handler(token,body)
    if path=="/account/me" and method=="GET":
        from accounts import profile
        return 200,profile(token)
    if path=="/admin/directory" and method=="POST":
        from admin import directory
        return 200,directory(token,body)
    if path=="/admin/directory/detail" and method=="POST":
        from admin import directory_detail
        return 200,directory_detail(token,body)
    if path in ("/marketing/list","/marketing/campaign","/marketing/post","/marketing/delete") and method=="POST":
        from marketing_studio import dispatch as marketing_dispatch
        return 200,marketing_dispatch(token,path.rsplit("/",1)[1],body)
    if path in ("/storyboard/list","/storyboard/get","/storyboard/project","/storyboard/scene","/storyboard/delete") and method=="POST":
        from storyboard import dispatch as storyboard_dispatch
        return 200,storyboard_dispatch(token,path.rsplit("/",1)[1],body)
    if path in ("/creative-workflows/list","/creative-workflows/save","/creative-workflows/delete") and method=="POST":
        from creative_workflow import dispatch as workflow_dispatch
        return 200,workflow_dispatch(token,path.rsplit("/",1)[1],body)
    if path in ("/prompts/list","/prompts/save","/prompts/delete","/prompts/templates") and method=="POST":
        from prompt_studio import dispatch as prompt_dispatch
        return 200,prompt_dispatch(token,path.rsplit("/",1)[1],body)
    if path in ("/knowledge/list","/knowledge/save","/knowledge/delete","/knowledge/folders","/knowledge/export") and method=="POST":
        from knowledge import dispatch_notes
        return 200,dispatch_notes(token,path.rsplit("/",1)[1],body)
    if path=="/knowledge/course-search" and method=="POST":
        from knowledge import public_text
        from student_business import clean
        q=clean(body["query"],120,True).casefold()
        lang=body.get("lang","en")
        if lang not in ("en","ru","uk","pl"): raise ValueError("Invalid language")
        p=student_progress(token)
        # Same entitlement and strict-content checks as the existing lesson endpoint.
        # Search at most 5 unlocked lessons per request to bound free-tier load.
        day=body.get("after",0)
        if type(day) is not int or not 0<=day<=45: raise ValueError("Invalid cursor")
        days=[x["day"] for x in p["lessons"] if x["unlocked"] and x["day"]>day]
        results=[]
        for n in days[:5]:
            status,lesson=dispatch("GET","/lessons/"+str(n)+"/"+lang,{},token)
            if status!=200: continue
            content=public_text(lesson)
            if q in content.casefold():
                results.append({"day":n,"title":lesson["title"],"language":lesson.get("content_language","en")})
        return 200,{"items":results,"next_after":days[4] if len(days)>5 else None}
    if path=="/privacy/export" and method=="POST":
        from privacy_center import export
        return 200,export(token,body["password"],body.get("code"))
    if path=="/privacy/request" and method=="POST":
        from privacy_center import create
        return 201,create(token,body["password"],body.get("code"),body["kind"],body.get("details",""))
    if path=="/privacy/list" and method=="POST":
        from privacy_center import list_user
        return 200,list_user(token,body.get("after",0))
    if path=="/admin/privacy" and method=="POST":
        from privacy_center import list_admin
        return 200,list_admin(token,body.get("after",0))
    if path=="/admin/privacy/close" and method=="POST":
        from privacy_center import close
        return 200,close(token,body["request"],body["response"])
    if path=="/account/mfa" and method=="GET":
        from accounts import mfa_status
        return 200,mfa_status(token)
    if path=="/account/mfa/begin" and method=="POST":
        from accounts import mfa_begin
        return 200,mfa_begin(token,body["password"])
    if path=="/account/mfa/confirm" and method=="POST":
        from accounts import mfa_confirm
        return 200,mfa_confirm(token,body["password"],body["code"])
    if path=="/account/mfa/disable" and method=="POST":
        from accounts import mfa_disable
        return 200,mfa_disable(token,body["password"],body["code"])
    if path=="/account/password" and method=="POST":
        from accounts import change_password
        return 200,change_password(token,body["current_password"],body["new_password"],body.get("code"))
    if path=="/logout" and method=="POST":
        if not token: raise PermissionError("Authentication required")
        logout(token)
        return 200,{"ok":True}
    if path=="/pro/library" and method=="GET":
        p=student_progress(token)
        if not p.get("access") or p.get("plan") not in ("pro","vip","elite"):
            raise PermissionError("Pro or VIP required")
        return 200,{"items":json.loads(Path(__file__).with_name("pro_library.json").read_text()),"language":"en"}
    if path=="/portfolio/review" and method=="POST":
        from project_reviewer import student_review
        return 200,student_review(token,body["project"],body["fields"],body.get("lang","en"))
    if path=="/practice/brief" and method=="POST":
        from practice_lab import student_brief
        return 200,student_brief(token,body["day"],body.get("lang","en"))
    if path=="/showcase/public" and method=="POST":
        from graduate_showcase import public
        return 200,public(body.get("code"))
    if path=="/showcase/mine" and method=="GET":
        from graduate_showcase import mine
        return 200,mine(token)
    if path=="/showcase/publish" and method=="POST":
        from graduate_showcase import publish
        return 200,publish(token,body.get("profile"),body.get("consent"))
    if path=="/showcase/withdraw" and method=="POST":
        from graduate_showcase import withdraw
        return 200,withdraw(token)
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
    if path in ("/productivity/overview","/productivity/save","/productivity/delete") and method=="POST":
        from productivity import dispatch as productivity
        return 200,productivity(token,path.rsplit("/",1)[1],body)
    if path=="/business/assistant" and method=="GET":
        from business_assistant import assistant
        return 200,assistant(token)
    if path=="/business/proposal/pdf" and method=="POST":
        from invoice_studio import generate
        return 200,generate(token,body)
    if path=="/business" and method=="GET":
        from student_business import dispatch as business
        return 200,business(token,"overview",{})
    if path in ("/business/client","/business/order","/business/delete","/business/import-job") and method=="POST":
        from student_business import dispatch as business
        return 200,business(token,path.rsplit("/",1)[1],body)
    if path=="/career/profile" and method=="GET":
        from career_profile import get_profile
        return 200,get_profile(token)
    if path=="/career/profile" and method=="POST":
        from career_profile import save_profile
        return 200,save_profile(token,body["profile"])
    if path=="/career/profile/delete" and method=="POST":
        from career_profile import delete_profile
        return 200,delete_profile(token)
    if path=="/career/accelerator" and method=="GET":
        from career import accelerator
        return 200,accelerator(token)
    if path=="/career/overview" and method=="GET":
        from career import overview
        return 200,overview(token)
    if path=="/career/estimate" and method=="POST":
        from career import estimate
        return 200,estimate(token,body)
    if path=="/adaptive/week" and method=="POST":
        from adaptive import student_plan
        return 200,student_plan(token,body["minutes"])
    if path=="/adaptive/plan" and method=="GET":
        from adaptive import student_plan
        return 200,student_plan(token)
    if path=="/admin/elite/reviews" and method=="POST":
        from elite_program import review_queue
        return 200,review_queue(token,body.get("status","pending"),body.get("offset",0))
    if path=="/admin/elite/review" and method=="POST":
        from elite_program import review_project
        return 200,review_project(token,body.get("student_id"),body.get("project"),body.get("revision"),body.get("scores"),body.get("feedback"))
    if path=="/elite/ad-production/plan" and method=="POST":
        from ad_production import student_plan
        return 200,student_plan(token,body["brief"],body.get("lang","en"))
    if path=="/elite/ad-production/subtitles" and method=="POST":
        from ad_production import student_subtitles
        return 200,student_subtitles(token,body["duration"],body["captions"])
    if path=="/elite/ad-production/narration" and method=="GET":
        from elite_program import access,unlocked
        if not unlocked(access(token)):
            raise PermissionError("Complete core lessons first")
        import base64
        return 200,{"source_base64":base64.b64encode(Path(__file__).with_name("local-narration-studio.py").read_bytes()).decode("ascii")}
    if path=="/elite/ad-production/assembler" and method=="GET":
        from elite_program import access,unlocked
        if not unlocked(access(token)):
            raise PermissionError("Complete the 45 core lessons first")
        import base64
        return 200,{"source_base64":base64.b64encode(Path(__file__).with_name("commercial-video-assembler.py").read_bytes()).decode("ascii")}
    if path=="/elite/open-generative/bridge" and method=="GET":
        from elite_program import access,unlocked
        if not unlocked(access(token)):
            raise PermissionError("Complete the 45 core lessons first")
        import base64
        return 200,{"source_base64":base64.b64encode(Path(__file__).with_name("open-generative-bridge.py").read_bytes()).decode("ascii")}
    if path=="/elite/projects" and method=="GET":
        from elite_program import catalog
        return 200,catalog(token,"en")
    if path=="/elite/projects" and method=="POST":
        from elite_program import catalog
        return 200,catalog(token,body.get("lang","en"))
    if path=="/elite/projects/save" and method=="POST":
        from elite_program import save
        return 200,save(token,body.get("project"),body.get("evidence"))
    if path=="/creator-2027" and method=="GET":
        progress=student_progress(token)
        if not progress.get("access") or progress.get("plan") not in ("vip","elite"):
            raise PermissionError("VIP access required")
        return 200,{"tracks":[{"id":t["id"],"title":t["title"],"day":t["day"],"unlocked":progress["lessons"][t["day"]-1]["unlocked"]} for t in TRACKS]}
    if path=="/progress" and method=="GET":
        return 200,student_progress(token)
    if path=="/checkout/support" and method=="POST":
        from payment_support import submit
        return 201,submit(token,body["invoice"],body["signature"])
    if path=="/checkout/support/list" and method=="POST":
        from payment_support import student_items
        return 200,student_items(token,body.get("after",0))
    if path=="/admin/payment-support" and method=="POST":
        from payment_support import admin_items
        return 200,admin_items(token,body.get("after",0))
    if path=="/admin/payment-support/check" and method=="POST":
        from payment_support import check
        return 200,check(token,body["ticket"])
    if path=="/admin/payment-support/resolve" and method=="POST":
        from payment_support import resolve
        return 200,resolve(token,body["ticket"],body["note"])
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
    if path=="/admin/content/validate" and method=="POST":
        from content_vault import admin_validate
        return 200,admin_validate(token,body)
    if path=="/admin/content" and method=="GET":
        from content_vault import admin_inventory
        return 200,admin_inventory(token)
    if path=="/admin/content" and method=="POST":
        from content_vault import admin_save
        return 200,admin_save(token,body)
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
    if path=="/admin/security" and method=="GET":
        from security_center import report
        return 200,report(token)
    if path=="/admin/statistics" and method=="GET":
        if os.getenv("ACADEMY_ADMIN_ENABLED")!="true":
            raise PermissionError("Administration disabled")
        from admin import statistics
        return 200,statistics(token)
    if path=="/elite/certificate/issue" and method=="POST":
        from certificates import issue_elite_certificate
        return 200,issue_elite_certificate(token)
    if path=="/elite/certificate/pdf" and method=="GET":
        from certificates import issue_elite_certificate,certificate_pdf
        import base64
        return 200,{"pdf_base64":base64.b64encode(certificate_pdf(issue_elite_certificate(token))).decode("ascii")}
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
        from content_vault import get
        private=get("exam",day,body.get("lang","en"))
        if private:
            attempt=start_exam(token,day,private["content"])
            return 200,{**attempt,"content_language":private["language"]}
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
        from content_vault import get
        private=get("lesson",day,lang)
        if private:
            return 200,vip_creator_supplement({"day":day,**private["content"],"content_language":private["language"],"prompts_language":private["language"]},day,lang)
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
            return 200,vip_creator_supplement({**{k:v for k,v in lesson.items() if k!="questions"},"content_language":lang if lang in localized else "en","prompts_language":"en"},day,lang)
        filename="lessons02_06.json" if day<=6 else "lessons07_30.json"
        lessons=json.loads(Path(__file__).with_name(filename).read_text())
        lesson=next(item for item in lessons if item["day"]==day)
        if day<=30 and lang in ("ru","uk","pl"):
            translations=json.loads(Path(__file__).with_name("lessons02_06_translations.json" if day<=6 else "lessons07_15_translations.json" if day<=15 else "lessons16_30_translations.json").read_text())
            lesson.update(next(item for item in translations[lang] if item["day"]==day))
            return 200,{**{k:v for k,v in lesson.items() if k!="questions"},"content_language":lang,"prompts_language":lang if day<=6 else "en"}
        return 200,{**{k:v for k,v in lesson.items() if k!="questions"},"content_language":"en"}
    return 404,{"error":"Not found"}
# HTTP adapter must validate request bodies, enforce rate limits and handle errors.

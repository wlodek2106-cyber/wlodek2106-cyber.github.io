"""Rollback-only end-to-end DB exercise. Blockchain is mocked; no actual funds or messages."""
import os,unittest,uuid
from contextlib import contextmanager,ExitStack
from unittest.mock import patch
from database import transaction
import accounts,checkout,settlement,learning,exams,certificates,partners,reviews,portfolio,admin,network_admin,founder
from lesson01 import LESSON

@unittest.skipUnless(os.getenv("ACADEMY_DATABASE_URL"),"Database not configured")
class LaunchIntegration(unittest.TestCase):
    def test_sale_learning_partner_and_access(self):
        class Rollback(Exception): pass
        suffix=uuid.uuid4().hex
        password="Test-only-"+suffix
        try:
            with transaction() as cur,ExitStack() as stack:
                @contextmanager
                def shared(): yield cur
                for module in (accounts,checkout,settlement,learning,exams,certificates,partners,reviews,portfolio,admin):
                    stack.enter_context(patch.object(module,"transaction",shared))
                stack.enter_context(patch.dict(os.environ,{"ACADEMY_ADMIN_ENABLED":"true","ACADEMY_PAYMENTS_ENABLED":"true","ACADEMY_CHECKOUT_READY":"true"}))
                owner_id=accounts.register("owner-"+suffix+"@example.invalid",password,"Test","Owner")
                partner_id=accounts.register("partner-"+suffix+"@example.invalid",password,"Test","Partner",hire_source="telegram")
                owner=accounts.login("owner-"+suffix+"@example.invalid",password)
                partner=accounts.login("partner-"+suffix+"@example.invalid",password)
                stack.enter_context(patch.dict(os.environ,{"ACADEMY_PARTNER_ADMIN_IDS":str(owner_id)}))
                self.assertEqual(partners.owner(owner),owner_id)
                for denied in (None,partner):
                    with self.assertRaises(PermissionError): partners.owner(denied)
                    with self.assertRaises(PermissionError): admin.statistics(denied)
                self.assertEqual(partners.apply(partner,"https://example.invalid/profile","1"*32,True)["status"],"pending")
                with self.assertRaises(PermissionError): partners.decide(partner,"application",partner_id,"approve")
                partners.decide(owner,"application",partner_id,"approve")
                code=uuid.uuid4().hex[:24]
                cur.execute("INSERT INTO referral_codes(student_id,code) VALUES (%s,%s)",(partner_id,code))
                buyer_id=accounts.register("buyer-"+suffix+"@example.invalid",password,"Тест","Студент",code,campaign_source="instagram")
                buyer=accounts.login("buyer-"+suffix+"@example.invalid",password)
                self.assertFalse(learning.student_progress(buyer)["paid"])
                with self.assertRaises(PermissionError): reviews.publish(buyer,5,"Test review only",True)
                self.assertEqual(checkout.prices(partner)["discount_percent"],0)
                self.assertTrue(learning.student_progress(buyer)["trial"])
                self.assertFalse(learning.student_progress(buyer)["access"])
                self.assertTrue(learning.require_lesson(buyer,1))
                with self.assertRaises(PermissionError): learning.require_lesson(buyer,2)
                portfolio.save(buyer,1,"First free practice submission")
                with self.assertRaises(PermissionError): portfolio.save(buyer,2,"Not allowed")
                bank=[{"id":str(i),"question":q[0],"options":q[1],"correct":q[1][q[2]]} for i,q in enumerate(LESSON["questions"])]
                attempt=exams.start_exam(buyer,1,bank)
                self.assertTrue(all("correct" not in q for q in attempt["questions"]))
                answers={q["id"]:q["options"].index(bank[int(q["id"])]["correct"]) for q in attempt["questions"]}
                result=exams.submit_exam(buyer,1,attempt["attempt_id"],answers)
                self.assertEqual(result["score"],100)
                with self.assertRaises(PermissionError): exams.submit_exam(buyer,1,attempt["attempt_id"],answers)
                self.assertTrue(result["trial"])
                self.assertIsNone(result["next_unlock_at"])
                self.assertFalse(learning.student_progress(buyer)["paid"])
                with self.assertRaises(PermissionError): exams.start_exam(buyer,2,bank)
                with self.assertRaises(PermissionError): certificates.issue_certificate(buyer)
                invoice=checkout.create_invoice(buyer,"starter")
                with patch.object(settlement,"verify_usdc",return_value=False):
                    with self.assertRaises(ValueError): settlement.settle(buyer,invoice["id"],"test-"+suffix)
                self.assertFalse(learning.student_progress(buyer)["paid"])
                from payment_support import submit_record,items,resolve_record
                ticket=submit_record(cur,buyer_id,invoice["id"],"1"*64)
                self.assertEqual(submit_record(cur,buyer_id,invoice["id"],"1"*64),ticket)
                self.assertEqual(items(cur,partner_id)["items"],[])
                with self.assertRaises(PermissionError): submit_record(cur,partner_id,invoice["id"],"1"*64)
                self.assertTrue(resolve_record(cur,owner_id,ticket["id"],"Test review only")["closed"])
                self.assertEqual(items(cur,buyer_id)["items"][0]["status"],"closed")
                with patch.object(settlement,"verify_usdc",return_value=True):
                    self.assertTrue(settlement.settle(buyer,invoice["id"],"test-"+suffix)["paid"])
                    self.assertTrue(settlement.settle(buyer,invoice["id"],"test-"+suffix)["paid"])
                self.assertTrue(learning.student_progress(buyer)["paid"])
                self.assertEqual(checkout.prices(partner)["discount_percent"],5)
                self.assertEqual(checkout.prices(partner)["prices"]["starter"],189050000)
                self.assertEqual(checkout.prices(buyer)["discount_percent"],0)
                self.assertTrue(learning.student_progress(buyer)["lessons"][0]["unlocked"])
                with self.assertRaises(PermissionError): learning.require_lesson(buyer,2)
                self.assertTrue(learning.student_progress(buyer)["lessons"][0]["completed"])
                from adaptive_study import plan as study_plan
                study=study_plan(buyer,30,"ru")
                self.assertEqual(study["focus"]["day"],1)
                self.assertEqual(study["brief"]["language"],"ru")
                self.assertEqual(sum(x["minutes"] for x in study["items"]),30)
                self.assertFalse(study["official_grading"])
                self.assertNotIn("email",study["snapshot"])
                with self.assertRaises(PermissionError): study_plan("invalid-token",30,"en")
                with self.assertRaises(PermissionError): exams.start_exam(buyer,1,bank)
                with self.assertRaises(PermissionError): certificates.issue_certificate(buyer)
                import agency
                aid=agency.create(cur,buyer_id,{"name":"Test team","alias":"Creator"})["id"]
                with self.assertRaises(PermissionError): agency.detail(cur,partner_id,aid)
                with self.assertRaises(PermissionError): agency.create(cur,partner_id,{"name":"No access","alias":"Client"})
                invitation=agency.invite(cur,buyer_id,aid)
                agency.join(cur,partner_id,{"code":invitation["code"],"alias":"Partner","consent":True})
                with self.assertRaises(PermissionError): agency.join(cur,owner_id,{"code":invitation["code"],"alias":"Other","consent":True})
                self.assertFalse(agency.detail(cur,partner_id,aid)["owner"])
                with self.assertRaises(PermissionError): agency.invite(cur,partner_id,aid)
                tid=agency.task(cur,buyer_id,{"id":aid,"title":"Test task","assignee":partner_id})["id"]
                with self.assertRaises(PermissionError): agency.task(cur,partner_id,{"id":aid,"title":"Denied"})
                self.assertEqual(agency.status(cur,partner_id,{"id":aid,"task":tid,"status":"done"})["status"],"done")
                from agency_finance import project as agency_project,reward as agency_reward
                values={"id":aid,"title":"Budget test","budget":"100","received":"50","expense":"10","due":"2027-01-01"}
                with self.assertRaises(PermissionError): agency_project(cur,partner_id,values)
                pid=agency_project(cur,buyer_id,values)["id"]
                with self.assertRaises(ValueError): agency_reward(cur,buyer_id,{"id":aid,"project":pid,"member":partner_id,"agreed":"20","paid":"21"})
                agency_reward(cur,buyer_id,{"id":aid,"project":pid,"member":partner_id,"agreed":"20","paid":"5"})
                finances=agency.detail(cur,buyer_id,aid)["finance"]
                self.assertEqual(finances["projects"][0]["projected_margin_cents"],7000)
                self.assertEqual(finances["projects"][0]["cash_margin_cents"],3500)
                member_finance=agency.detail(cur,partner_id,aid)["finance"]
                self.assertNotIn("budget_cents",member_finance["projects"][0])
                self.assertEqual(member_finance["rewards"][0]["paid_cents"],500)
                agency.remove(cur,buyer_id,{"id":aid,"member":partner_id})
                self.assertEqual(agency.detail(cur,buyer_id,aid)["finance"]["rewards"][0]["agreed_cents"],2000)
                with self.assertRaises(PermissionError): agency.detail(cur,partner_id,aid)
                self.assertIsNone(agency.detail(cur,buyer_id,aid)["tasks"][0]["assignee"])
                from agency_knowledge import get as knowledge_get,save as knowledge_save
                kb={"id":aid,"project":pid}
                self.assertEqual(knowledge_get(cur,buyer_id,kb)["revision"],0)
                with self.assertRaises(PermissionError): knowledge_get(cur,partner_id,kb)
                with self.assertRaises(ValueError): knowledge_save(cur,buyer_id,{**kb,"revision":0,"content":"Brand rules"})
                knowledge_save(cur,buyer_id,{**kb,"revision":0,"content":"Brand rules","consent":True})
                with self.assertRaises(ValueError): knowledge_save(cur,buyer_id,{**kb,"revision":0,"content":"Stale","consent":True})
                self.assertEqual(knowledge_get(cur,buyer_id,kb)["content"],"Brand rules")
                from agency_workflow import create as workflow_create,assign as workflow_assign
                agency.join(cur,partner_id,{"code":agency.invite(cur,buyer_id,aid)["code"],"alias":"Partner","consent":True})
                self.assertEqual(knowledge_get(cur,partner_id,kb)["content"],"Brand rules")
                with self.assertRaises(PermissionError): knowledge_save(cur,partner_id,{**kb,"revision":1,"content":"Forbidden","consent":True})
                knowledge_save(cur,buyer_id,{**kb,"revision":1,"content":""})
                empty=knowledge_get(cur,partner_id,kb)
                self.assertEqual(empty["content"],"")
                self.assertEqual(empty["revision"],2)
                with self.assertRaises(ValueError): knowledge_save(cur,buyer_id,{**kb,"revision":0,"content":"Stale initial draft","consent":True})
                knowledge_save(cur,buyer_id,{**kb,"revision":2,"content":"New brand rules","consent":True})
                self.assertEqual(knowledge_get(cur,partner_id,kb)["revision"],3)
                with self.assertRaises(ValueError): knowledge_save(cur,buyer_id,{**kb,"revision":1,"content":"Stale pre-delete draft","consent":True})
                args={"id":aid,"project":pid,"template":"design","assignee":partner_id}
                with self.assertRaises(PermissionError): workflow_create(cur,partner_id,args)
                self.assertEqual(workflow_create(cur,buyer_id,args)["created"],5)
                with self.assertRaises(ValueError): workflow_create(cur,buyer_id,args)
                flow=sorted([x for x in agency.detail(cur,buyer_id,aid)["tasks"] if x["workflow"]=="design"],key=lambda x:x["step"])
                with self.assertRaises(ValueError): agency.status(cur,partner_id,{"id":aid,"task":flow[1]["id"],"status":"done"})
                for x in flow[:-1]: agency.status(cur,partner_id,{"id":aid,"task":x["id"],"status":"done"})
                workflow_assign(cur,buyer_id,{"id":aid,"task":flow[-1]["id"],"assignee":partner_id})
                with self.assertRaises(PermissionError): agency.status(cur,partner_id,{"id":aid,"task":flow[-1]["id"],"status":"done"})
                from command_center import agency_snapshot
                own_snapshot=agency_snapshot(cur,buyer_id)
                member_snapshot=agency_snapshot(cur,partner_id)
                self.assertTrue(any(x["id"]==aid and x["owner"] for x in own_snapshot["agencies"]))
                self.assertTrue(any(x["id"]==aid and not x["owner"] for x in member_snapshot["agencies"]))
                self.assertTrue(any(x["id"]==flow[-1]["id"] for x in member_snapshot["tasks"]))
                self.assertFalse(any(x["id"]==aid for x in agency_snapshot(cur,owner_id)["agencies"]))
                from agency_quality import save as quality_save,get as quality_get,FIELDS
                review={"id":aid,"task":flow[-1]["id"]}
                with self.assertRaises(ValueError): agency.status(cur,buyer_id,{**review,"status":"done"})
                checks={k:"pass" for k in FIELDS}
                with self.assertRaises(PermissionError): quality_save(cur,partner_id,{**review,"checks":checks,"evidence":"Synthetic evidence","consent":True})
                quality_save(cur,buyer_id,{**review,"checks":{**checks,"rights":"unchecked"},"evidence":"Synthetic evidence","consent":True})
                with self.assertRaises(ValueError): agency.status(cur,buyer_id,{**review,"status":"done"})
                quality_save(cur,buyer_id,{**review,"checks":checks,"evidence":"Synthetic evidence","consent":True})
                self.assertTrue(quality_get(cur,partner_id,review)["report"]["ready"])
                agency.status(cur,buyer_id,{**review,"status":"done"})
                with self.assertRaises(ValueError): quality_save(cur,buyer_id,{**review,"checks":checks,"evidence":"Another report","consent":True})
                with self.assertRaises(ValueError): agency.status(cur,buyer_id,{"id":aid,"task":flow[0]["id"],"status":"todo"})
                agency.remove(cur,buyer_id,{"id":aid,"member":partner_id})
                self.assertTrue(reviews.publish(buyer,5,"Test review only",True)["published"])
                self.assertTrue(reviews.remove(buyer)["removed"])
                from marketplace import save as market_save,mine as market_mine,listing as market_list,decide as market_decide,withdraw as market_withdraw,public_detail as market_detail
                service={"name":"Test creator","title":"Test design","category":"design","description":"Test service","price":"100 USD","link":"https://example.invalid/portfolio","consent":True}
                with self.assertRaises(ValueError): market_save(cur,buyer_id,{**service,"consent":False})
                listing=market_save(cur,buyer_id,service)
                self.assertIsNone(market_mine(cur,partner_id)["item"])
                self.assertFalse(any(x["id"]==listing["id"] for x in market_list(cur,True,listing["id"]-1)["items"]))
                self.assertIsNone(market_detail(cur,listing["id"])["item"])
                market_decide(cur,owner_id,{"id":listing["id"],"revision":listing["revision"],"action":"approved"})
                public_item=next(x for x in market_list(cur,True,listing["id"]-1)["items"] if x["id"]==listing["id"])
                self.assertNotIn("student_id",public_item)
                self.assertIs(public_item["paid_badge"],True)
                self.assertEqual(market_detail(cur,listing["id"])["item"],public_item)
                updated=market_save(cur,buyer_id,service)
                with self.assertRaises(ValueError): market_decide(cur,owner_id,{"id":listing["id"],"revision":listing["revision"],"action":"approved"})
                self.assertEqual(market_mine(cur,buyer_id)["item"]["status"],"pending")
                self.assertTrue(market_withdraw(cur,buyer_id)["withdrawn"])
                self.assertIsNone(market_detail(cur,listing["id"])["item"])
                from job_board import create as job_create,page as job_page,moderate as job_moderate,apply as job_apply,applicants as job_applicants,applications as job_applications,transition as job_transition
                job={"title":"Test project","category":"design","brief":"Test brief","budget":"150","contact":"client@example.invalid","consent":True}
                with patch.dict(os.environ,{"ACADEMY_MARKETPLACE_PAYMENTS_ENABLED":"false"}):
                    jid=job_create(cur,partner_id,job)["id"]
                self.assertFalse(any(x["id"]==jid for x in job_page(cur,buyer_id,"feed",{"after":jid-1})["items"]))
                job_moderate(cur,owner_id,{"id":jid,"action":"open"})
                self.assertNotIn("contact",job_page(cur,buyer_id,"feed",{"after":jid-1})["items"][0])
                bid={"id":jid,"alias":"Test student","proposal":"Test proposal","quote":"140","contact":"worker@example.invalid","consent":True}
                with self.assertRaises(PermissionError): job_apply(cur,owner_id,bid)
                from job_board import recommend
                with self.assertRaises(PermissionError): recommend(cur,owner_id)
                self.assertIn("items",recommend(cur,buyer_id))
                aid=job_apply(cur,buyer_id,bid)["id"]
                self.assertFalse(any(x["id"]==jid for x in recommend(cur,buyer_id)["items"]))
                with self.assertRaises(ValueError): job_apply(cur,buyer_id,bid)
                with self.assertRaises(PermissionError): job_applicants(cur,buyer_id,{"id":jid})
                self.assertIsNone(job_applicants(cur,partner_id,{"id":jid})["items"][0]["contact"])
                self.assertIsNone(job_applications(cur,buyer_id,{})["items"][0]["contact"])
                with self.assertRaises(PermissionError): job_transition(cur,buyer_id,{"id":jid,"action":"select","application":aid})
                self.assertEqual(job_transition(cur,partner_id,{"id":jid,"action":"select","application":aid})["status"],"assigned")
                self.assertEqual(job_applicants(cur,partner_id,{"id":jid})["items"][0]["contact"],"worker@example.invalid")
                self.assertEqual(job_applications(cur,buyer_id,{})["items"][0]["contact"],"client@example.invalid")
                with self.assertRaises(PermissionError): job_transition(cur,partner_id,{"id":jid,"action":"deliver"})
                from project_room import room,message,milestone,handoff
                with self.assertRaises(PermissionError): room(cur,owner_id,{"id":jid})
                self.assertEqual(room(cur,partner_id,{"id":jid})["role"],"client")
                self.assertEqual(room(cur,buyer_id,{"id":jid})["role"],"freelancer")
                with self.assertRaises(PermissionError): milestone(cur,buyer_id,{"id":jid,"action":"add","title":"Test"})
                mid=milestone(cur,partner_id,{"id":jid,"action":"add","title":"Test milestone"})["id"]
                milestone(cur,buyer_id,{"id":jid,"action":"set","milestone":mid,"done":True})
                self.assertTrue(room(cur,partner_id,{"id":jid})["milestones"][0]["done"])
                message(cur,buyer_id,{"id":jid,"body":"Synthetic message"})
                self.assertEqual(room(cur,partner_id,{"id":jid})["items"][0]["body"],"Synthetic message")
                self.assertEqual(handoff(cur,buyer_id,{"id":jid,"action":"deliver","body":"Test result"})["status"],"delivered")
                self.assertEqual(handoff(cur,partner_id,{"id":jid,"action":"revise","body":"Test revision"})["status"],"assigned")
                milestone(cur,partner_id,{"id":jid,"action":"set","milestone":mid,"done":False})
                self.assertEqual(handoff(cur,buyer_id,{"id":jid,"action":"deliver","body":"Test revised result"})["status"],"delivered")
                from reputation import submit as review_submit,stats as rep_stats,decide as review_decide,own as review_own
                with self.assertRaises(PermissionError): review_submit(cur,partner_id,{"id":jid,"rating":5,"consent":True})
                from marketplace_payments import preview as payment_preview,treasury_report
                p=payment_preview(cur,buyer_id,{"id":jid})
                self.assertEqual((p["mode"],p["fee_atomic"],p["freelancer_atomic"]),("external",7000000,133000000))
                with self.assertRaises(PermissionError): payment_preview(cur,owner_id,{"id":jid})
                self.assertIn("fee_atomic",treasury_report(cur))
                # Real dispatch authorization, with the disposable transaction shared.
                import api, marketplace_payments
                from marketplace_release import readiness
                with patch.object(api,"ready",return_value=True),patch.object(marketplace_payments,"transaction",shared),patch.dict(os.environ,{"ACADEMY_MARKETPLACE_PAYMENTS_ENABLED":"true"}):
                    self.assertTrue(readiness()["requested"])
                    self.assertFalse(readiness()["enabled"])
                    for route,method in (("/marketplace-pay/request/test","GET"),("/marketplace-pay/request/test","POST"),("/marketplace-pay/qr","POST"),("/marketplace-pay/wallet","POST"),("/marketplace-pay/create","POST")):
                        for token in (None,buyer,owner):
                            with self.assertRaises(PermissionError):
                                api.dispatch(method,route,{},token)
                    for token in (None,buyer,partner):
                        with self.assertRaises(PermissionError):
                            api.dispatch("POST","/marketplace-pay/treasury",{},token)
                        with self.assertRaises(PermissionError):
                            api.dispatch("POST","/marketplace-pay/treasury-preflight",{},token)
                    code,report=api.dispatch("POST","/marketplace-pay/treasury",{},owner)
                    self.assertEqual(code,200)
                    self.assertFalse(report["enabled"])
                    self.assertFalse(report["release"]["live_payment_tested"])
                self.assertEqual(job_transition(cur,partner_id,{"id":jid,"action":"complete"})["status"],"completed")
                with self.assertRaises(PermissionError): message(cur,buyer_id,{"id":jid,"body":"Closed"})
                self.assertEqual(len(room(cur,partner_id,{"id":jid})["items"]),4)
                review={"id":jid,"rating":4,"comment":"Synthetic feedback","consent":True}
                with self.assertRaises(PermissionError): review_submit(cur,buyer_id,review)
                self.assertEqual(review_submit(cur,partner_id,review)["status"],"pending")
                with self.assertRaises(ValueError): review_submit(cur,partner_id,review)
                self.assertIsNone(rep_stats(cur,buyer_id)["rating"])
                self.assertIsNone(job_applicants(cur,partner_id,{"id":jid})["items"][0]["reputation"])
                review_decide(cur,owner_id,{"id":jid,"action":"approved"})
                self.assertEqual(rep_stats(cur,buyer_id)["rating"],4.0)
                self.assertEqual(rep_stats(cur,buyer_id)["experience_level"],"new")
                self.assertIsNone(job_applicants(cur,partner_id,{"id":jid})["items"][0]["reputation"])
                from freelancer_analytics import report as freelancer_report
                analytics=freelancer_report(cur,buyer_id,7)
                self.assertEqual(analytics["all_time"]["applications"],1)
                self.assertEqual(analytics["all_time"]["completed"],1)
                self.assertEqual(analytics["all_time"]["completed_cents"],14000)
                self.assertFalse(analytics["payment_verified"])
                with self.assertRaises(PermissionError): freelancer_report(cur,partner_id,7)
                self.assertEqual(review_own(cur,buyer_id,{})["items"][0]["comment"],"Synthetic feedback")
                self.assertEqual(review_own(cur,partner_id,{})["items"],[])
                from notifications import listing as notices,mark as notice_read,count as notice_count
                client_notices=notices(cur,partner_id,{})["items"]
                worker_notices=notices(cur,buyer_id,{})["items"]
                self.assertTrue({"job_open","application","message","delivered"}<=set(n["kind"] for n in client_notices))
                self.assertTrue({"selected","revision","completed","review_approved"}<=set(n["kind"] for n in worker_notices))
                self.assertFalse(any("body" in n or "contact" in n for n in client_notices+worker_notices))
                self.assertEqual(notice_count(cur,owner_id)["unread"],0)
                before=notice_count(cur,buyer_id)["unread"]
                notice_read(cur,partner_id,{"ids":[worker_notices[0]["id"]]})
                self.assertEqual(notice_count(cur,buyer_id)["unread"],before)
                notice_read(cur,buyer_id,{"ids":[worker_notices[0]["id"]]})
                self.assertEqual(notice_count(cur,buyer_id)["unread"],before-1)
                review_decide(cur,owner_id,{"id":jid,"action":"hidden"})
                self.assertIsNone(rep_stats(cur,buyer_id)["rating"])
                from acquisition import report as acquisition_report
                source=next(r for r in acquisition_report(cur)["items"] if r["source"]=="telegram")
                self.assertGreaterEqual(source["registrations"],1)
                self.assertGreaterEqual(source["completed"],1)
                self.assertGreaterEqual(source["applications"],1)
                from community import create as community_create,page as community_page,decide as community_decide,withdraw as community_withdraw
                topic={"alias":"Test creator","title":"Test question","category":"question","body":"Test discussion","consent":True}
                with self.assertRaises(ValueError): community_create(cur,buyer_id,{**topic,"consent":False})
                post=community_create(cur,buyer_id,topic)["id"]
                self.assertFalse(any(x["id"]==post for x in community_page(cur,partner_id,{"after":post-1})["items"]))
                community_decide(cur,owner_id,{"id":post,"action":"approved"})
                visible=community_page(cur,partner_id,{"after":post-1})["items"][0]
                self.assertEqual(visible["id"],post)
                self.assertNotIn("student_id",visible)
                reply=community_create(cur,partner_id,{**topic,"parent":post})["id"]
                self.assertEqual(community_page(cur,buyer_id,{"parent":post})["items"],[])
                community_decide(cur,owner_id,{"id":reply,"action":"approved"})
                self.assertEqual(community_page(cur,buyer_id,{"parent":post})["items"][0]["id"],reply)
                with self.assertRaises(PermissionError): community_withdraw(cur,partner_id,{"id":post})
                community_withdraw(cur,buyer_id,{"id":post})
                with self.assertRaises(PermissionError): community_page(cur,partner_id,{"parent":post})
                self.assertEqual(portfolio.save(buyer,1,"Test project")["status"],"submitted")
                # Backfill progress inside the rollback transaction to exercise graduation.
                cur.execute("SELECT id FROM enrollments WHERE student_id=%s",(buyer_id,))
                eid=cur.fetchone()[0]
                cur.execute("INSERT INTO lesson_progress(enrollment_id,lesson,score) SELECT %s,n,80 FROM generate_series(2,30) n",(eid,))
                certificate=certificates.issue_certificate(buyer)
                self.assertEqual(certificate["lessons"],30)
                self.assertEqual(certificates.issue_certificate(buyer)["code"],certificate["code"])
                self.assertTrue(certificates.verify_certificate(certificate["code"])["valid"])
                self.assertTrue(certificates.certificate_pdf(certificate).startswith(b"%PDF"))
                for denied in (None,partner,buyer):
                    with self.assertRaises(PermissionError): admin.directory_detail(denied,{"id":partner_id,"kind":"sales"})
                before=admin.directory_detail(owner,{"id":partner_id,"kind":"sales"})["items"]
                self.assertEqual(len(before),1)
                self.assertEqual(before[0]["commission_atomic"],"59700000")
                self.assertEqual(before[0]["status"],"available")
                self.assertEqual(admin.directory_detail(owner,{"id":partner_id,"kind":"sales","after":before[0]["invoice"]})["items"],[])
                jobs=admin.directory_detail(owner,{"id":buyer_id,"kind":"jobs"})["items"]
                external=next(x for x in jobs if x["id"]==jid)
                self.assertEqual(external["mode"],"external")
                self.assertIsNone(external["verified_atomic"])
                self.assertIsNone(external["unsettled_atomic"])
                req=partners.request(partner,invoice["id"])
                with self.assertRaises(ValueError): partners.request(partner,invoice["id"])
                with self.assertRaises(PermissionError): partners.request(buyer,invoice["id"])
                partners.decide(owner,"payout",req["id"],"approve")
                with patch("payout_verify.verify",return_value=False):
                    with self.assertRaises(ValueError): partners.decide(owner,"payout",req["id"],"mark_paid","1"*64)
                with patch("payout_verify.verify",return_value=True):
                    partners.decide(owner,"payout",req["id"],"mark_paid","1"*63+"2")
                    with self.assertRaises(ValueError): partners.decide(owner,"payout",req["id"],"mark_paid","1"*63+"2")
                cur.execute("SELECT status,amount_atomic FROM influencer_payouts WHERE id=%s",(req["id"],))
                self.assertEqual(cur.fetchone(),("paid",59700000))
                after_payment=admin.directory_detail(owner,{"id":partner_id,"kind":"sales"})["items"][0]
                self.assertEqual(after_payment["status"],"paid")
                self.assertEqual(after_payment["payout_signature"],"1"*63+"2")
                self.assertEqual(network_admin.query(cur,parent=partner_id)["items"][0]["id"],buyer_id)
                with patch("database.transaction",shared):
                    for denied in (None,partner,buyer):
                        with self.assertRaises(PermissionError):
                            network_admin.network(denied,{"parent":partner_id})
                    tree=network_admin.network(owner,{"parent":partner_id})
                    self.assertEqual(tree["items"][0]["id"],buyer_id)
                    self.assertEqual(tree["items"][0]["parent_id"],partner_id)
                    self.assertTrue(tree["items"][0]["paid"])
                    self.assertEqual(tree["items"][0]["usdc_atomic"],"199000000")
                report=founder.report(cur,7)
                self.assertIn("after_all_commissions_atomic",report["alltime"])
                funnel=report["activity"]["trial_funnel"]
                self.assertGreaterEqual(funnel["registered"],3)
                self.assertLessEqual(funnel["paid_after_pass"],funnel["passed"])
                self.assertEqual(sum(funnel["plans"].values()),funnel["paid_after_pass"])
                ig=next(x for x in report["campaign_growth"]["items"] if x["source"]=="instagram")
                self.assertGreaterEqual(ig["registered"],1)
                self.assertGreaterEqual(ig["paid"],1)
                self.assertGreaterEqual(int(ig["gross_atomic"]),199000000)
                cur.execute("SELECT hire_source,campaign_source FROM students WHERE id=%s",(buyer_id,))
                self.assertEqual(cur.fetchone(),(None,"instagram"))
                self.assertEqual(len(report["activity"]["series"]),7)
                self.assertGreaterEqual(report["activity"]["alltime"]["registered"],2)
                self.assertGreaterEqual(report["activity"]["alltime"]["paid"],1)
                self.assertGreaterEqual(report["activity"]["alltime"]["paid_referred"],1)
                self.assertIn("students",admin.statistics(owner))
                from security_center import inspect as security_inspect,report as security_report
                from system_monitor import table_status,report as monitor_report
                self.assertTrue(all(x["present"] for x in table_status(cur)))
                with self.assertRaises(PermissionError): monitor_report(partner,15)
                from incident_manager import create as incident_create,detail as incident_detail,advance as incident_advance,dispatch as incident_dispatch
                with self.assertRaises(PermissionError): incident_dispatch(partner,"list",{})
                inc=incident_create(cur,{"module":"support","severity":"high","title":"Synthetic test incident","note":"Synthetic observation","consent":True})
                args={"id":inc["id"],"revision":1,"state":"investigating","note":"Synthetic investigation","consent":True}
                self.assertEqual(incident_advance(cur,args)["revision"],2)
                with self.assertRaises(ValueError): incident_advance(cur,args)
                with self.assertRaises(ValueError): incident_advance(cur,{**args,"revision":2,"state":"resolved"})
                incident_advance(cur,{**args,"revision":2,"state":"resolved","verified":True})
                self.assertTrue(incident_detail(cur,inc["id"])["events"][-1]["verified"])
                self.assertEqual(incident_detail(cur,inc["id"])["state"],"resolved")
                diagnostics=security_inspect(cur)
                self.assertIn("database_checks_pass",diagnostics)
                for key in ("agency_owner_without_membership","agency_task_project_mismatch","agency_task_dependency_mismatch","agency_active_task_without_completed_predecessor"):
                    self.assertIn(key,diagnostics["checks"])
                self.assertEqual(security_inspect(cur)["backup_status"],"not_verified")
                with self.assertRaises(PermissionError): security_report(partner)
                from student_business import save_client,save_order,overview as business_overview,delete as business_delete
                cid=save_client(cur,buyer_id,{"name":"Test client"})["id"]
                order={"client_id":cid,"title":"Test order","status":"in_progress","agreed":"100.00","received":"40.00","expense":"10.00"}
                oid=save_order(cur,buyer_id,order)["id"]
                self.assertEqual(business_overview(cur,buyer_id)["totals"]["cash_margin_cents"],"3000")
                from productivity import save as task_save,overview as task_overview,remove as task_remove
                task={"title":"Practice","day":"2026-11-24","category":"study","priority":1,"minutes":30,"done":False}
                tid=task_save(cur,buyer_id,task)["id"]
                self.assertEqual(task_overview(cur,buyer_id,"2026-11-24")["total"],1)
                self.assertEqual(task_overview(cur,partner_id,"2026-11-24")["total"],0)
                with self.assertRaises(PermissionError): task_save(cur,partner_id,{**task,"id":tid})
                task_save(cur,buyer_id,{**task,"id":tid,"done":True})
                self.assertEqual(task_overview(cur,buyer_id,"2026-11-24")["completed"],1)
                self.assertTrue(task_remove(cur,buyer_id,tid)["deleted"])
                from invoice_studio import record,render
                proposal={"order":oid,"lang":"ru","provider":"Тест <&>","scope":"Создать проект","terms":"Две правки"}
                doc=record(cur,buyer_id,proposal)
                self.assertEqual(doc["remaining"],6000)
                self.assertTrue(render(doc).startswith(b"%PDF"))
                with self.assertRaises(PermissionError): record(cur,partner_id,proposal)
                self.assertEqual(business_overview(cur,partner_id)["orders"],[])
                with self.assertRaises(PermissionError): save_order(cur,partner_id,order)
                with self.assertRaises(ValueError): business_delete(cur,buyer_id,"client",cid)
                self.assertTrue(business_delete(cur,buyer_id,"order",oid)["deleted"])
                self.assertTrue(business_delete(cur,buyer_id,"client",cid)["deleted"])
                from client_acquisition import collect as acquisition_collect,snapshot as acquisition_snapshot
                self.assertEqual(acquisition_collect(cur,buyer_id)["leads"],0)
                self.assertIsNone(acquisition_snapshot(partner)["metrics"])
                with self.assertRaises(PermissionError): acquisition_snapshot("invalid-token")
                from student_business import import_job
                with self.assertRaises(PermissionError): import_job(cur,partner_id,{"job_id":jid,"client_name":"No access"})
                imported=import_job(cur,buyer_id,{"job_id":jid,"client_name":"Marketplace test client"})
                self.assertTrue(imported["created"])
                result=business_overview(cur,buyer_id)
                item=result["orders"][0]
                self.assertEqual((item["source_job_id"],item["agreed_cents"],item["received_cents"],item["expense_cents"],item["status"]),(jid,14000,0,0,"delivered"))
                save_order(cur,buyer_id,{"id":item["id"],"client_id":item["client_id"],"title":item["title"],"status":"delivered","agreed":"140","received":"50","expense":"20"})
                self.assertEqual(import_job(cur,buyer_id,{"job_id":jid,"client_name":"Not duplicated"}),{"id":item["id"],"created":False})
                self.assertEqual(business_overview(cur,buyer_id)["totals"]["cash_margin_cents"],"3000")
                self.assertEqual(len(business_overview(cur,buyer_id)["clients"]),1)
                from knowledge import save as note_save,list_notes,remove as note_remove,public_text
                note=note_save(cur,buyer_id,{"title":"Test note","content":"Local AI notes","tag":"AI"})
                self.assertEqual(list_notes(cur,buyer_id,"local")["items"][0]["id"],note["id"])
                from knowledge import folders as note_folders,export_notes
                note_save(cur,buyer_id,{"id":note["id"],"title":"Test note","content":"Local AI notes","tag":"AI","folder":"Study","favorite":True})
                self.assertEqual(note_folders(cur,buyer_id)["items"],["Study"])
                self.assertEqual(list_notes(cur,buyer_id,"notes Local",folder="Study",favorite=True,all_words=True)["items"][0]["id"],note["id"])
                self.assertEqual(list_notes(cur,buyer_id,"missing Local",all_words=True)["items"],[])
                self.assertEqual(list_notes(cur,buyer_id,folder="Other")["items"],[])
                self.assertEqual(export_notes(cur,buyer_id)["items"][0]["favorite"],True)
                self.assertEqual(export_notes(cur,partner_id)["items"],[])
                with self.assertRaises(ValueError): note_save(cur,buyer_id,{"title":"Invalid","content":"Test","favorite":"true"})
                self.assertEqual(list_notes(cur,partner_id)["items"],[])
                with self.assertRaises(PermissionError): note_remove(cur,partner_id,note["id"])
                self.assertNotIn("secret",public_text({"title":"Lesson","questions":["secret"]}))
                from prompt_studio import save as prompt_save,listing as prompt_list,remove as prompt_remove
                prompt=prompt_save(cur,buyer_id,{"title":"Test prompt","prompt":"Local image","category":"image","favorite":True})
                self.assertEqual(prompt_list(cur,buyer_id,{"favorite":True,"category":"image","query":"local"})["items"][0]["id"],prompt["id"])
                self.assertEqual(prompt_list(cur,partner_id,{})["items"],[])
                with self.assertRaises(PermissionError): prompt_remove(cur,partner_id,prompt["id"])
                from creative_workflow import save as workflow_save,listing as workflow_list,remove as workflow_remove
                flow=workflow_save(cur,buyer_id,{"title":"Test flow","kind":"video","brief":"Local clip","completed":["brief"]})
                self.assertEqual(workflow_list(cur,buyer_id)["items"][0]["completed"],["brief"])
                workflow_save(cur,buyer_id,{"id":flow["id"],"title":"Test flow","kind":"video","brief":"Local clip","completed":["brief"],"due":"2027-01-15","tasks":[{"title":"Edit","done":True}],"materials":"local-file.txt"})
                project=workflow_list(cur,buyer_id)["items"][0]
                self.assertEqual(project["due"],"2027-01-15")
                self.assertEqual(project["tasks"],[{"title":"Edit","done":True}])
                self.assertEqual(project["materials"],"local-file.txt")
                with self.assertRaises(ValueError): workflow_save(cur,buyer_id,{"title":"Invalid","kind":"product","brief":"Test","tasks":[{"title":"Bad","done":"yes"}]})
                with self.assertRaises(PermissionError): workflow_save(cur,partner_id,{"id":flow["id"],"title":"Other","kind":"video","brief":"Test"})
                product=workflow_save(cur,buyer_id,{"title":"Product","kind":"product","brief":"Prototype"})
                self.assertTrue(workflow_remove(cur,buyer_id,product["id"])["deleted"])
                self.assertEqual(workflow_list(cur,partner_id)["items"],[])
                with self.assertRaises(PermissionError): workflow_remove(cur,partner_id,flow["id"])
                with self.assertRaises(ValueError): workflow_save(cur,buyer_id,{"title":"Invalid","kind":"video","brief":"Test","completed":["unknown"]})
                from storyboard import save_project,save_scene,get as storyboard_get,remove as storyboard_remove
                film=save_project(cur,buyer_id,{"title":"Test film","story":"A short film","style":"3D","characters":"Original character","format":"16:9"})["id"]
                scene={"project":film,"title":"First","position":1,"seconds":15,"action":"Walk"}
                first=save_scene(cur,buyer_id,scene)["id"]
                save_scene(cur,buyer_id,{**scene,"title":"Second","position":2,"seconds":10})
                self.assertEqual(storyboard_get(cur,buyer_id,film)["total_seconds"],25)
                self.assertEqual(storyboard_get(cur,buyer_id,film)["scenes"][1]["start"],15)
                with self.assertRaises(PermissionError): storyboard_get(cur,partner_id,film)
                with self.assertRaises(ValueError): save_scene(cur,buyer_id,{**scene,"seconds":0})
                from marketing_studio import save_campaign,save_post,listing as marketing_list,remove as marketing_remove
                campaign=save_campaign(cur,buyer_id,{"title":"Test campaign","goal":"Local content"})["id"]
                post={"campaign_id":campaign,"day":"2027-01-01","platform":"instagram","status":"draft","title":"Test post"}
                mid=save_post(cur,buyer_id,post)["id"]
                self.assertEqual(marketing_list(cur,buyer_id,"2027-01-01")["items"][0]["id"],mid)
                self.assertEqual(marketing_list(cur,partner_id,"2027-01-01")["items"],[])
                with self.assertRaises(PermissionError): save_post(cur,partner_id,post)
                with self.assertRaises(ValueError): marketing_remove(cur,buyer_id,{"kind":"campaign","id":campaign})
                from privacy_center import export_data,create_record,list_records,close_record
                req= create_record(cur,buyer_id,"erasure","Test request")
                self.assertTrue(create_record(cur,buyer_id,"erasure","Duplicate")["existing"])
                self.assertEqual(list_records(cur,partner_id)["items"],[])
                exported=export_data(cur,buyer_id)["datasets"]
                self.assertEqual(exported["account"][0]["id"],buyer_id)
                self.assertEqual(exported["marketplace"][0]["status"],"withdrawn")
                self.assertEqual(exported["community"][0]["status"],"withdrawn")
                self.assertNotIn("password_hash",exported["account"][0])
                self.assertEqual(exported["knowledge_notes"][0]["title"],"Test note")
                self.assertEqual(exported["knowledge_notes"][0]["folder"],"Study")
                self.assertEqual(exported["student_prompts"][0]["title"],"Test prompt")
                self.assertEqual(exported["creative_workflows"][0]["title"],"Test flow")
                self.assertEqual(exported["creative_workflows"][0]["tasks"],[{"title":"Edit","done":True}])
                self.assertEqual(exported["storyboard_projects"][0]["title"],"Test film")
                self.assertEqual(exported["marketing_posts"][0]["title"],"Test post")
                self.assertTrue(marketing_remove(cur,buyer_id,{"kind":"post","id":mid})["deleted"])
                self.assertTrue(marketing_remove(cur,buyer_id,{"kind":"campaign","id":campaign})["deleted"])
                self.assertEqual(len(exported["storyboard_scenes"]),2)
                self.assertTrue(storyboard_remove(cur,buyer_id,{"project":film,"scene":first})["deleted"])
                self.assertTrue(storyboard_remove(cur,buyer_id,{"project":film})["deleted"])
                self.assertTrue(workflow_remove(cur,buyer_id,flow["id"])["deleted"])
                self.assertTrue(prompt_remove(cur,buyer_id,prompt["id"])["deleted"])
                self.assertTrue(note_remove(cur,buyer_id,note["id"])["deleted"])
                self.assertTrue(all("token_digest" not in x for x in exported["sessions"]))
                self.assertTrue(close_record(cur,owner_id,req["id"],"Test response only")["closed"])
                self.assertEqual(list_records(cur,buyer_id)["items"][0]["status"],"closed")
                self.assertTrue(learning.student_progress(buyer)["paid"])
                from career_profile import save as save_profile,load as load_profile,EMPTY
                profile={**EMPTY,"name":"Test Student","headline":"AI creator"}
                self.assertTrue(save_profile(cur,buyer_id,profile)["saved"])
                self.assertEqual(load_profile(cur,buyer_id),profile)
                self.assertEqual(load_profile(cur,partner_id),EMPTY)
                from support_diagnostics import collect as support_diagnosis,report as diagnosis_report
                own_diag=support_diagnosis(cur,buyer_id)
                other_diag=support_diagnosis(cur,partner_id)
                self.assertEqual(own_diag["learning"]["access"],"paid")
                self.assertEqual(other_diag["learning"]["access"],"trial")
                self.assertEqual(own_diag["invoice"]["status"],"paid")
                self.assertEqual(other_diag["invoice"]["status"],"none")
                self.assertFalse(own_diag["chain_verified_now"])
                self.assertNotIn("signature",own_diag["invoice"])
                self.assertNotIn("email",own_diag)
                with self.assertRaises(PermissionError): diagnosis_report("invalid-token")
                from support_center import create as support_create,listing as support_list,thread as support_thread,reply as support_reply,close as support_close
                ticket={"category":"ai","subject":"Synthetic support","body":"Test issue","consent":True}
                with self.assertRaises(ValueError): support_create(cur,buyer_id,{**ticket,"consent":False})
                stid=support_create(cur,buyer_id,ticket)["id"]
                self.assertEqual(support_list(cur,buyer_id)["items"][0]["id"],stid)
                self.assertFalse(support_list(cur,buyer_id)["items"][0]["unread"])
                from support_triage import assign as triage_assign
                self.assertEqual(support_list(cur,buyer_id)["items"][0].get("priority"),None)
                triage_assign(cur,stid,"provider","high")
                self.assertEqual(support_thread(cur,owner_id,stid,True)["priority"],"high")
                self.assertNotIn("priority",support_thread(cur,buyer_id,stid))
                cur.execute("UPDATE support_tickets SET admin_unread=true WHERE id=%s",(stid,))
                cur.execute("SELECT admin_unread FROM support_tickets WHERE id=%s",(stid,))
                self.assertTrue(cur.fetchone()[0])
                self.assertEqual(support_list(cur,buyer_id,status="closed")["items"],[])
                with self.assertRaises(ValueError): support_list(cur,buyer_id,status="invalid")
                self.assertEqual(support_list(cur,partner_id)["items"],[])
                with self.assertRaises(PermissionError): support_thread(cur,partner_id,stid)
                with self.assertRaises(PermissionError): support_reply(cur,partner_id,{"id":stid,"body":"Denied","consent":True})
                self.assertEqual(support_reply(cur,owner_id,{"id":stid,"body":"Test response","consent":True},True)["status"],"answered")
                self.assertTrue(support_list(cur,buyer_id)["items"][0]["unread"])
                self.assertEqual(support_list(cur,buyer_id)["counts"]["unread"],1)
                self.assertEqual(support_thread(cur,buyer_id,stid)["messages"][-1]["role"],"admin")
                self.assertEqual(support_list(cur,buyer_id)["counts"]["unread"],0)
                self.assertEqual(support_reply(cur,buyer_id,{"id":stid,"body":"Follow up","consent":True})["status"],"open")
                self.assertEqual(support_close(cur,buyer_id,stid)["status"],"closed")
                with self.assertRaises(ValueError): support_reply(cur,buyer_id,{"id":stid,"body":"Closed","consent":True})
                from support_center import feedback as article_feedback,feedback_summary
                with self.assertRaises(ValueError): article_feedback(cur,buyer_id,{"article":"invalid","helpful":True})
                with self.assertRaises(ValueError): article_feedback(cur,buyer_id,{"article":"payment","helpful":1})
                self.assertTrue(article_feedback(cur,buyer_id,{"article":"payment","helpful":True})["saved"])
                article_feedback(cur,buyer_id,{"article":"payment","helpful":False})
                cur.execute("SELECT helpful FROM support_article_feedback WHERE student_id=%s AND article='payment'",(buyer_id,))
                self.assertEqual(cur.fetchall(),[(False,)])
                self.assertTrue(any(x["article"]=="payment" and x["not_helpful"]>=1 for x in feedback_summary(cur)["items"]))
                from career_pathway import collect as career_collect,pathway as career_pathway
                self.assertTrue(any(x["lesson"]==1 for x in career_collect(cur,buyer_id)))
                self.assertEqual(career_collect(cur,partner_id),[])
                self.assertFalse(career_pathway(learning.student_progress(buyer)["lessons"],career_collect(cur,buyer_id),"design")["qualification_verified"])
                from career import accelerator_data
                mine=accelerator_data(cur,buyer_id,30,30)
                self.assertGreaterEqual(mine["projects"],1)
                self.assertEqual(mine["listing_status"],"withdrawn")
                self.assertEqual(accelerator_data(cur,partner_id,0,30)["projects"],0)
                from content_vault import save,load,inventory,preflight
                # Startup tests must never modify the real owner curriculum, even transiently.
                # PostgreSQL temp copies include constraints and identity definitions, but not foreign keys.
                cur.execute("CREATE TEMP TABLE private_curriculum (LIKE academy.private_curriculum INCLUDING ALL) ON COMMIT DROP")
                cur.execute("CREATE TEMP TABLE private_curriculum_audit (LIKE academy.private_curriculum_audit INCLUDING ALL) ON COMMIT DROP")
                cur.execute("SET LOCAL search_path TO pg_temp, academy, pg_catalog")
                cur.execute("SELECT count(*) FROM private_curriculum")
                self.assertEqual(cur.fetchone()[0],0)
                private={"title":"Private test","theory":"New material","assignment":"Test task","prompts":[]}
                self.assertTrue(preflight("lesson",1,"en",private)["valid"])
                self.assertFalse(preflight("lesson",1,"en",{**private,"theory":"bad\x00text"})["valid"])
                cur.execute("SELECT count(*) FROM private_curriculum")
                self.assertEqual(cur.fetchone()[0],0)
                self.assertEqual(save(cur,owner_id,"lesson",1,"en",private)["revision"],1)
                self.assertEqual(load(cur,"lesson",1,"pl")["content"],private)
                self.assertEqual(save(cur,owner_id,"lesson",1,"en",private)["revision"],2)
                self.assertTrue(save(cur,owner_id,"lesson",1,"en",{**private,"title":"Do not overwrite"},True)["skipped"])
                self.assertEqual(load(cur,"lesson",1,"en")["content"],private)
                self.assertEqual(save(cur,owner_id,"lesson",2,"en",private,True)["revision"],1)
                self.assertIn("english_coverage",inventory(cur))
                self.assertFalse(preflight("exam",1,"en",bank)["valid"])
                with self.assertRaises(ValueError): save(cur,owner_id,"exam",1,"en",bank)
                private_bank=[{"id":"new"+str(i),"question":"Synthetic private test scenario "+str(i),"options":["A","B","C"],"correct":"A"} for i in range(10)]
                self.assertEqual(save(cur,owner_id,"exam",1,"en",private_bank)["revision"],1)
                self.assertEqual(load(cur,"exam",1,"en")["content"],private_bank)
                self.assertGreaterEqual(inventory(cur)["coverage"]["en"]["exam"]["count"],1)
                # Isolated split checkout lifecycle, after all earlier marketplace assertions.
                # No network calls, signing, real funds or changes retained in production.
                import marketplace_payments as mp
                from marketplace_split import ALPHABET,decode58,TOKEN
                from marketplace_tx import unsigned
                from payment_policy import TREASURY,USDC_MINT
                import base64
                def enc(raw):
                    n=int.from_bytes(raw,"big");out=""
                    while n:
                        n,i=divmod(n,58);out=ALPHABET[i]+out
                    return "1"*(len(raw)-len(raw.lstrip(bytes([0]))))+out
                payer,recipient,src,d1,d2=[enc(bytes([i])*32) for i in range(11,16)]
                sig=enc(bytes([21])*64)
                other_sig=enc(bytes([22])*64)
                cur.execute("CREATE TEMP TABLE academy_job_payments (LIKE academy.academy_job_payments INCLUDING ALL) ON COMMIT DROP")
                cur.execute("CREATE TEMP TABLE academy_job_payment_wallets (LIKE academy.academy_job_payment_wallets INCLUDING ALL) ON COMMIT DROP")
                baseline=mp.treasury_report(cur)
                with patch.dict(os.environ,{"ACADEMY_MARKETPLACE_PAYMENTS_ENABLED":"true"}),patch.object(mp,"transaction",shared),patch.object(mp,"enabled",side_effect=lambda:os.getenv("ACADEMY_MARKETPLACE_PAYMENTS_ENABLED")=="true"):
                    split_job=job_create(cur,partner_id,{**job,"title":"Synthetic split checkout"})["id"]
                    job_moderate(cur,owner_id,{"id":split_job,"action":"open"})
                    split_aid=job_apply(cur,buyer_id,{**bid,"id":split_job,"quote":"1000"})["id"]
                    job_transition(cur,partner_id,{"id":split_job,"action":"select","application":split_aid})
                    with self.assertRaises(PermissionError): mp.wallet(cur,partner_id,{"id":split_job,"wallet":recipient,"confirm":True})
                    mp.wallet(cur,buyer_id,{"id":split_job,"wallet":recipient,"confirm":True})
                    args={"id":split_job,"payer":payer,"recipient":recipient,"confirm":True}
                    with self.assertRaises(PermissionError): mp.create(cur,partner_id,args)
                    handoff(cur,buyer_id,{"id":split_job,"action":"deliver","body":"Synthetic delivery"})
                    with self.assertRaises(PermissionError): job_transition(cur,partner_id,{"id":split_job,"action":"complete"})
                    with self.assertRaises(PermissionError): mp.create(cur,buyer_id,args)
                    p=mp.create(cur,partner_id,args)
                    first_ref=p["invoice"]["reference"]
                    with self.assertRaises(PermissionError): mp.cancel_unissued(cur,buyer_id,{"id":split_job,"confirm":True})
                    self.assertTrue(mp.cancel_unissued(cur,partner_id,{"id":split_job,"confirm":True})["cancelled"])
                    with self.assertRaises(PermissionError): mp.request_transaction(first_ref,"GET",{})
                    p=mp.create(cur,partner_id,args)
                    ref=p["invoice"]["reference"]
                    self.assertNotEqual(ref,first_ref)
                    self.assertEqual((p["gross_atomic"],p["fee_atomic"],p["freelancer_atomic"]),(1000000000,50000000,950000000))
                    self.assertEqual(mp.create(cur,partner_id,args)["invoice"]["reference"],ref)
                    self.assertIsNone(mp.preview(cur,buyer_id,{"id":split_job})["invoice"]["reference"])
                    with self.assertRaises(ValueError): mp.wallet(cur,buyer_id,{"id":split_job,"wallet":payer,"confirm":True})
                    with self.assertRaises(PermissionError): handoff(cur,partner_id,{"id":split_job,"action":"revise","body":"Locked"})
                    self.assertTrue(mp.qr(partner,{"id":split_job})["url"].endswith(ref))
                    with self.assertRaises(PermissionError): mp.qr(buyer,{"id":split_job})
                    self.assertIn("label",mp.request_transaction(ref,"GET",{}))
                    with self.assertRaises(PermissionError): mp.request_transaction(ref,"POST",{"account":recipient})
                    expected=unsigned(payer,src,d1,d2,ref,100000)
                    with patch("marketplace_tx.build",return_value=expected):
                        result=mp.request_transaction(ref,"POST",{"account":payer})
                        self.assertEqual(result["transaction"],expected)
                        with self.assertRaises(PermissionError): mp.request_transaction(ref,"POST",{"account":payer})
                    with self.assertRaises(ValueError): mp.cancel_unissued(cur,partner_id,{"id":split_job,"confirm":True})
                    cur.execute("SELECT issued_at FROM academy_job_payments WHERE job_id=%s",(split_job,))
                    issued=cur.fetchone()[0]
                    keys=[payer,src,d1,d2,USDC_MINT,ref,TOKEN]
                    def ix(dst,amt):
                        return {"programIdIndex":6,"accounts":[1,4,dst,0,5],"data":enc(bytes([12])+amt.to_bytes(8,"little")+bytes([6]))}
                    def bal(i,owner,n):
                        return {"accountIndex":i,"owner":owner,"mint":USDC_MINT,"uiTokenAmount":{"amount":str(n),"decimals":6}}
                    tx={"blockTime":int(issued.timestamp())+1,"transaction":{"signatures":[sig],"message":{"accountKeys":keys,"header":{"numRequiredSignatures":1,"numReadonlySignedAccounts":0,"numReadonlyUnsignedAccounts":3},"instructions":[ix(2,950000000),ix(3,50000000)]}},"meta":{"err":None,"preTokenBalances":[bal(1,payer,1000000000),bal(2,recipient,0),bal(3,TREASURY,0)],"postTokenBalances":[bal(1,payer,0),bal(2,recipient,950000000),bal(3,TREASURY,50000000)]}}
                    def fake_rpc(method,params):
                        if method=="getSignaturesForAddress":
                            return [{"signature":sig,"confirmationStatus":"finalized","err":None}]
                        return tx
                    with patch.object(mp,"reconcile_rpc",fake_rpc):
                        self.assertEqual(mp.reconcile(partner,{"id":split_job})["matches"],[sig])
                        self.assertEqual(mp.reconcile(owner,{"id":split_job},True)["status"],"candidate")
                        with self.assertRaises(PermissionError): mp.reconcile(owner,{"id":split_job})
                    import copy
                    invalid=copy.deepcopy(tx)
                    invalid["meta"]["postTokenBalances"][2]["uiTokenAmount"]["amount"]="49999999"
                    def verify_fixture(s,p,r,ref,c,at):
                        return mp.matches(invalid,s,p,r,ref,c,at)
                    with patch.object(mp,"verify_chain",verify_fixture):
                        with self.assertRaises(ValueError): mp.settle(partner,{"id":split_job,"signature":sig})
                    self.assertFalse(mp.preview(cur,partner_id,{"id":split_job})["invoice"]["paid_at"])
                    # Closing new issuance must not prevent recording an already issued payment.
                    with patch.dict(os.environ,{"ACADEMY_MARKETPLACE_PAYMENTS_ENABLED":"false"}),patch.object(mp,"verify_chain",lambda s,p,r,f,c,t:mp.matches(tx,s,p,r,f,c,t)):
                        with self.assertRaises(PermissionError): mp.settle(buyer,{"id":split_job,"signature":sig})
                        self.assertTrue(mp.settle(partner,{"id":split_job,"signature":sig})["paid"])
                        self.assertTrue(mp.settle(partner,{"id":split_job,"signature":sig})["paid"])
                        with self.assertRaises(ValueError): mp.settle(partner,{"id":split_job,"signature":other_sig})
                    self.assertEqual(job_transition(cur,partner_id,{"id":split_job,"action":"complete"})["status"],"completed")
                    after=mp.treasury_report(cur)
                    self.assertEqual(after["paid_count"]-baseline["paid_count"],1)
                    self.assertEqual(int(after["gross_atomic"])-int(baseline["gross_atomic"]),1000000000)
                    self.assertEqual(int(after["fee_atomic"])-int(baseline["fee_atomic"]),50000000)
                # ELITE review regression: all rows and synthetic enrollment roll back.
                import elite_program as elite
                from certificates import issue_elite_certificate,verify_certificate,certificate_pdf
                with patch("database.transaction",shared):
                    with self.assertRaises(PermissionError):issue_elite_certificate(buyer)
                    with self.assertRaises(PermissionError):elite.review_queue(buyer)
                    with self.assertRaises(PermissionError):elite.save(buyer,"film","A synthetic project report for the test.")
                    cur.execute("UPDATE enrollments SET plan='elite' WHERE student_id=%s",(buyer_id,))
                    with self.assertRaises(PermissionError):elite.save(buyer,"film","A synthetic project report for the test.")
                    cur.execute("INSERT INTO lesson_progress(enrollment_id,lesson,score) SELECT e.id,n,100 FROM enrollments e CROSS JOIN generate_series(1,45) n WHERE e.student_id=%s ON CONFLICT DO NOTHING",(buyer_id,))
                    self.assertTrue(elite.save(buyer,"film","A synthetic project report for the test.")["saved"])
                    queue=elite.review_queue(owner)
                    # Verify the exact fixture in the private table even when queue is paginated.
                    cur.execute("SELECT revision FROM elite_projects WHERE student_id=%s AND project='film'",(buyer_id,))
                    rev=cur.fetchone()[0]
                    self.assertEqual(elite.review_project(owner,buyer_id,"film",rev,dict(elite.RUBRIC,brief=0),"Please improve the synthetic brief.")["status"],"revision")
                    elite.save(buyer,"film","A revised synthetic project report for the test.")
                    with self.assertRaises(ValueError):elite.review_project(owner,buyer_id,"film",rev,elite.RUBRIC,"Stale synthetic revision.")
                    self.assertEqual(elite.review_project(owner,buyer_id,"film",rev+1,elite.RUBRIC,"Synthetic report checked.")["status"],"approved")
                    project=next(t for t in elite.catalog(buyer,"ru")["projects"] if t["id"]=="film")
                    self.assertEqual(project["submission"]["score"],100)
                    self.assertEqual(project["submission"]["status"],"approved")
                    with self.assertRaises(PermissionError):issue_elite_certificate(buyer)
                    for key,_,_,_ in elite.PROJECTS:
                        if key=="film":continue
                        elite.save(buyer,key,"Synthetic evidence for credential test only.")
                        elite.review_project(owner,buyer_id,key,1,elite.RUBRIC,"Synthetic evidence reviewed.")
                    credential=issue_elite_certificate(buyer)
                    self.assertEqual(credential["projects"],5)
                    self.assertEqual(credential["average_score"],100)
                    self.assertEqual(issue_elite_certificate(buyer)["code"],credential["code"])
                    self.assertEqual(verify_certificate(credential["code"])["credential"],"elite")
                    self.assertNotIn("recipient_name",verify_certificate(credential["code"]))
                    self.assertTrue(certificate_pdf(credential).startswith(b"%PDF-"))
                    import graduate_showcase as showcase
                    profile={"headline":"Synthetic graduate","bio":"Test portfolio only","show_name":False,"projects":[{"title":"Demo","description":"Public demo","url":"https://example.invalid/demo"}]}
                    with self.assertRaises(PermissionError):showcase.publish(partner,profile,True)
                    with self.assertRaises(ValueError):showcase.publish(buyer,profile,False)
                    published=showcase.publish(buyer,profile,True)
                    public=showcase.public(published["code"])
                    self.assertTrue(public["found"])
                    self.assertEqual(public["credential"]["level"],"ELITE")
                    self.assertNotIn("recipient_name",public)
                    self.assertNotIn("student_id",public)
                    self.assertNotIn("evidence",public["profile"])
                    self.assertEqual(showcase.mine(buyer)["code"],published["code"])
                    self.assertEqual(showcase.publish(buyer,dict(profile,show_name=True),True)["code"],published["code"])
                    self.assertIn("recipient_name",showcase.public(published["code"]))
                    showcase.withdraw(buyer)
                    self.assertFalse(showcase.public(published["code"])["found"])
                    with self.assertRaises(ValueError):elite.save(buyer,"film","Attempt to replace an approved test report.")
                raise Rollback()
        except Rollback:
            pass

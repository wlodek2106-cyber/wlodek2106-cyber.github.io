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
                partner_id=accounts.register("partner-"+suffix+"@example.invalid",password,"Test","Partner")
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
                buyer_id=accounts.register("buyer-"+suffix+"@example.invalid",password,"Тест","Студент",code)
                buyer=accounts.login("buyer-"+suffix+"@example.invalid",password)
                self.assertFalse(learning.student_progress(buyer)["paid"])
                with self.assertRaises(PermissionError): reviews.publish(buyer,5,"Test review only",True)
                invoice=checkout.create_invoice(buyer,"starter")
                with patch.object(settlement,"verify_usdc",return_value=False):
                    with self.assertRaises(ValueError): settlement.settle(buyer,invoice["id"],"test-"+suffix)
                self.assertFalse(learning.student_progress(buyer)["paid"])
                with patch.object(settlement,"verify_usdc",return_value=True):
                    self.assertTrue(settlement.settle(buyer,invoice["id"],"test-"+suffix)["paid"])
                    self.assertTrue(settlement.settle(buyer,invoice["id"],"test-"+suffix)["paid"])
                self.assertTrue(learning.student_progress(buyer)["paid"])
                self.assertTrue(learning.student_progress(buyer)["lessons"][0]["unlocked"])
                with self.assertRaises(PermissionError): learning.require_lesson(buyer,2)
                bank=[{"id":str(i),"question":q[0],"options":q[1],"correct":q[1][q[2]]} for i,q in enumerate(LESSON["questions"])]
                attempt=exams.start_exam(buyer,1,bank)
                self.assertTrue(all("correct" not in q for q in attempt["questions"]))
                answers={q["id"]:q["options"].index(bank[int(q["id"])]["correct"]) for q in attempt["questions"]}
                result=exams.submit_exam(buyer,1,attempt["attempt_id"],answers)
                self.assertEqual(result["score"],100)
                with self.assertRaises(PermissionError): exams.submit_exam(buyer,1,attempt["attempt_id"],answers)
                with self.assertRaises(PermissionError): certificates.issue_certificate(buyer)
                self.assertTrue(reviews.publish(buyer,5,"Test review only",True)["published"])
                self.assertTrue(reviews.remove(buyer)["removed"])
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
                self.assertEqual(network_admin.query(cur,parent=partner_id)["items"][0]["id"],buyer_id)
                self.assertIn("after_all_commissions_atomic",founder.report(cur,7)["alltime"])
                self.assertIn("students",admin.statistics(owner))
                from student_business import save_client,save_order,overview as business_overview,delete as business_delete
                cid=save_client(cur,buyer_id,{"name":"Test client"})["id"]
                order={"client_id":cid,"title":"Test order","status":"in_progress","agreed":"100.00","received":"40.00","expense":"10.00"}
                oid=save_order(cur,buyer_id,order)["id"]
                self.assertEqual(business_overview(cur,buyer_id)["totals"]["cash_margin_cents"],"3000")
                self.assertEqual(business_overview(cur,partner_id)["orders"],[])
                with self.assertRaises(PermissionError): save_order(cur,partner_id,order)
                with self.assertRaises(ValueError): business_delete(cur,buyer_id,"client",cid)
                self.assertTrue(business_delete(cur,buyer_id,"order",oid)["deleted"])
                self.assertTrue(business_delete(cur,buyer_id,"client",cid)["deleted"])
                from career_profile import save as save_profile,load as load_profile,EMPTY
                profile={**EMPTY,"name":"Test Student","headline":"AI creator"}
                self.assertTrue(save_profile(cur,buyer_id,profile)["saved"])
                self.assertEqual(load_profile(cur,buyer_id),profile)
                self.assertEqual(load_profile(cur,partner_id),EMPTY)
                from content_vault import save,load,inventory
                private={"title":"Private test","theory":"New material","assignment":"Test task","prompts":[]}
                self.assertEqual(save(cur,owner_id,"lesson",1,"en",private)["revision"],1)
                self.assertEqual(load(cur,"lesson",1,"pl")["content"],private)
                self.assertEqual(save(cur,owner_id,"lesson",1,"en",private)["revision"],2)
                self.assertIn("english_coverage",inventory(cur))
                self.assertEqual(save(cur,owner_id,"exam",1,"en",bank)["revision"],1)
                self.assertEqual(load(cur,"exam",1,"en")["content"],bank)
                raise Rollback()
        except Rollback:
            pass

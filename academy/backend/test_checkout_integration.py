import os
import unittest
import uuid
from contextlib import contextmanager
from unittest.mock import patch
import accounts
import checkout
from database import transaction

@unittest.skipUnless(os.getenv("ACADEMY_DATABASE_URL"),"Database not configured")
class CheckoutIntegration(unittest.TestCase):
    def test_invoice_recovery(self):
        class Rollback(Exception): pass
        try:
            with transaction() as cur:
                @contextmanager
                def shared():
                    yield cur
                with patch.object(accounts,"transaction",shared), patch.object(checkout,"transaction",shared), patch.dict(os.environ,{"ACADEMY_PAYMENTS_ENABLED":"true"}):
                    email=f"checkout-{uuid.uuid4().hex}@example.invalid"
                    password="Test-only-"+uuid.uuid4().hex
                    student=accounts.register(email,password)
                    token=accounts.login(email,password)
                    invoice=checkout.create_invoice(token,"starter")
                    self.assertEqual(invoice["amount_atomic"],199000000)
                    self.assertTrue(invoice["url"].startswith("solana:"))
                    self.assertEqual(checkout.active_invoice(token)["invoice"],invoice)
                    with self.assertRaises(ValueError):
                        checkout.create_invoice(token,"vip")
                    cur.execute("DELETE FROM payment_invoices WHERE student_id=%s",(student,))
                    code=uuid.uuid4().hex[:24]
                    cur.execute("INSERT INTO referral_codes(student_id,code) VALUES (%s,%s)",(student,code))
                    invited=accounts.register("invite-"+email,password,referral=code)
                    self.assertEqual(checkout.prices(token)["discount_percent"],0)
                    cur.execute("INSERT INTO enrollments(student_id,plan,paid_at,payment_signature) VALUES (%s,%s,now(),%s)",(invited,"starter","test-"+uuid.uuid4().hex))
                    self.assertEqual(checkout.prices(token)["discount_percent"],5)
                    discounted=checkout.create_invoice(token,"starter")
                    self.assertEqual(discounted["amount_atomic"],189050000)
                    self.assertIn("amount=189.05",discounted["url"])
                    self.assertEqual(checkout.active_invoice(token)["invoice"],discounted)
                raise Rollback()
        except Rollback:
            pass

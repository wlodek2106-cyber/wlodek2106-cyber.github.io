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
                    accounts.register(email,password)
                    token=accounts.login(email,password)
                    invoice=checkout.create_invoice(token,"starter")
                    self.assertEqual(invoice["amount_atomic"],199000000)
                    self.assertTrue(invoice["url"].startswith("solana:"))
                    self.assertEqual(checkout.active_invoice(token)["invoice"],invoice)
                    with self.assertRaises(ValueError):
                        checkout.create_invoice(token,"vip")
                raise Rollback()
        except Rollback:
            pass

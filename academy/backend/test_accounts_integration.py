import os
import unittest
import uuid
from unittest.mock import patch
from contextlib import contextmanager
import accounts
from database import transaction

@unittest.skipUnless(os.getenv("ACADEMY_DATABASE_URL"),"Database not configured")
class AccountIntegration(unittest.TestCase):
    def test_registration_login_logout(self):
        class Rollback(Exception): pass
        email=f"test-{uuid.uuid4().hex}@example.invalid"
        password="Test-only-"+uuid.uuid4().hex
        try:
            with transaction() as cur:
                @contextmanager
                def shared():
                    yield cur
                with patch.object(accounts,"transaction",shared):
                    student=accounts.register(email,password)
                    with self.assertRaises(ValueError):
                        accounts.register(email,password)
                    with self.assertRaises(ValueError):
                        accounts.login(email,"wrong-password")
                    token=accounts.login(email,password)
                    self.assertEqual(accounts.authenticate(token),student)
                    accounts.logout(token)
                    self.assertIsNone(accounts.authenticate(token))
                raise Rollback()
        except Rollback:
            pass

if __name__=="__main__":
    unittest.main()

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
                    from referrals import attribute,normalize
                    code=uuid.uuid4().hex[:24]
                    cur.execute("INSERT INTO referral_codes(student_id,code) VALUES (%s,%s)",(student,code))
                    invited=accounts.register("invite-"+email,password,referral=code)
                    cur.execute("SELECT referrer_id FROM referrals WHERE student_id=%s",(invited,))
                    self.assertEqual(cur.fetchone()[0],student)
                    from network_admin import query
                    branch=query(cur,parent=student)
                    self.assertEqual([x["id"] for x in branch["items"]],[invited])
                    self.assertEqual(branch["items"][0]["parent_id"],student)
                    self.assertEqual(query(cur,search="invite-"+email)["items"][0]["id"],invited)
                    attribute(cur,student,code)
                    cur.execute("SELECT count(*) FROM referrals WHERE student_id=%s",(student,))
                    self.assertEqual(cur.fetchone()[0],0)
                    with self.assertRaises(ValueError): normalize("invalid")
                    with self.assertRaises(ValueError):
                        accounts.register(email,password)
                    with self.assertRaises(ValueError):
                        accounts.login(email,"wrong-password")
                    token=accounts.login(email,password)
                    self.assertEqual(accounts.authenticate(token),student)
                    other=accounts.login(email,password)
                    with self.assertRaises(PermissionError): accounts.change_password(token,"incorrect-password",password+"new")
                    self.assertEqual(accounts.authenticate(token),student)
                    self.assertTrue(accounts.change_password(token,password,password+"new")["changed"])
                    self.assertIsNone(accounts.authenticate(token))
                    self.assertIsNone(accounts.authenticate(other))
                    with self.assertRaises(ValueError): accounts.login(email,password)
                    fresh=accounts.login(email,password+"new")
                    self.assertEqual(accounts.authenticate(fresh),student)
                    accounts.logout(fresh)
                    self.assertIsNone(accounts.authenticate(fresh))
                raise Rollback()
        except Rollback:
            pass

if __name__=="__main__":
    unittest.main()

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
                    from registration_validation import validate
                    valid={"email":email,"password":password,"first_name":"  Test  ","last_name":"Student"}
                    for key,value in (("first_name"," "),("last_name",None),("email","invalid"),("password","short"),("referral","bad")):
                        self.assertEqual(validate(dict(valid,**{key:value}))[1],key)
                    values,error=validate(valid)
                    self.assertIsNone(error)
                    self.assertEqual(values["first_name"],"Test")
                    student=accounts.register(**values)
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
                    from mfa import code_at
                    from time import time
                    setup=accounts.mfa_begin(fresh,password+"new")
                    counter=int(time())//30
                    with patch("mfa.time.time",return_value=counter*30):
                        enabled=accounts.mfa_confirm(fresh,password+"new",code_at(setup["secret"],counter))
                        self.assertIsNone(accounts.authenticate(fresh))
                        with self.assertRaises(PermissionError): accounts.login(email,password+"new")
                        with self.assertRaises(PermissionError): accounts.login(email,password+"new",code_at(setup["secret"],counter))
                        recovered=accounts.login(email,password+"new",enabled["recovery_codes"][0])
                        self.assertEqual(accounts.mfa_status(recovered)["recovery_remaining"],7)
                        with self.assertRaises(PermissionError): accounts.login(email,password+"new",enabled["recovery_codes"][0])
                        self.assertFalse(accounts.mfa_disable(recovered,password+"new",enabled["recovery_codes"][1])["enabled"])
                        self.assertIsNone(accounts.authenticate(recovered))
                    fresh=accounts.login(email,password+"new")
                    accounts.logout(fresh)
                    self.assertIsNone(accounts.authenticate(fresh))
                raise Rollback()
        except Rollback:
            pass

if __name__=="__main__":
    unittest.main()

import unittest,base64,json
from unittest.mock import patch
from passkeys import (RP_ID,ORIGIN,user_handle,checked_uuid,decode,credential,
                      generate_authentication_options,options_to_json,
                      UserVerificationRequirement,login_finish)

def enc(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

class PasskeyTests(unittest.TestCase):
    def test_user_handle(self):
        self.assertNotEqual(user_handle(24),user_handle(25))
        self.assertEqual(len(user_handle(24)),8)
    def test_invalid_id(self):
        with self.assertRaises(ValueError): checked_uuid("invalid")
        with self.assertRaises(ValueError): decode("a/b")
    def test_required_verification(self):
        data=json.loads(options_to_json(generate_authentication_options(rp_id=RP_ID,user_verification=UserVerificationRequirement.REQUIRED)))
        self.assertEqual(data["rpId"],RP_ID)
        self.assertEqual(data["userVerification"],"required")
        self.assertEqual(ORIGIN,"https://zer0life-academy.onrender.com")
    def test_credential_id_mismatch(self):
        with self.assertRaises(ValueError): credential({"credential":{"id":"YQ","rawId":"Yg","type":"public-key","response":{}}})
    def test_cross_origin(self):
        value={"id":"YQ","rawId":"YQ","type":"public-key","response":{"clientDataJSON":enc(b'{"crossOrigin":true}')}}
        with self.assertRaises(PermissionError): credential({"credential":value})
    def test_invalid_challenge_fails_before_db_lookup(self):
        with patch("passkeys.take_challenge",side_effect=PermissionError("Expired")):
            with patch("passkeys.transaction") as tx:
                with self.assertRaises(PermissionError): login_finish({})
                tx.assert_not_called()

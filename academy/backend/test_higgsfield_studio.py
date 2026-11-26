import unittest
from unittest.mock import patch
import higgsfield_studio as h

class HiggsfieldStudioTests(unittest.TestCase):
    def setUp(self):
        h.SESSIONS.clear()
        h.RATE.clear()
    def tearDown(self):
        h.SESSIONS.clear()
        h.RATE.clear()
    def call(self, action, body, owner="student"):
        h.RATE.clear()
        with patch.object(h, "session_id", return_value=owner):
            return h.dispatch("token", action, body)
    def test_configuration(self):
        p=h.generation_payload({"prompt":" test ","confirm_charge":True,"duration":15,"resolution":"4k","aspect_ratio":"9:16","generate_audio":False})
        self.assertEqual(p,{"prompt":"test","duration":15,"resolution":"4k","aspect_ratio":"9:16","generate_audio":False})
        for key,val in [("duration",True),("duration",16),("resolution","8k"),("aspect_ratio",[]),("generate_audio","false"),("confirm_charge",False)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                h.generation_payload({"prompt":"test","confirm_charge":True,key:val})
    def test_resume_and_isolation(self):
        key="example:secret123"
        self.assertEqual(self.call("connect",{"key":key,"consent":True})[0],200)
        with patch.object(h,"upstream",return_value={"request_id":"job_123"}) as provider:
            self.assertEqual(self.call("submit",{"prompt":"test","confirm_charge":True})[1]["request_id"],"job_123")
            self.assertEqual(self.call("submit",{"prompt":"test","confirm_charge":True})[0],409)
            self.assertEqual(provider.call_count,1)
        self.call("disconnect",{})
        self.assertIsNone(h.SESSIONS["student"]["key"])
        self.assertEqual(self.call("connect",{"key":"another:secret123","consent":True})[0],409)
        self.assertEqual(self.call("connect",{"key":key,"consent":True})[1]["request_id"],"job_123")
        self.assertEqual(self.call("status",{},owner="other")[0],409)
    def test_unknown(self):
        key="example:secret123"
        self.call("connect",{"key":key,"consent":True})
        with patch.object(h,"upstream",return_value={"error_code":"outcome_unknown"}):
            self.call("submit",{"prompt":"test","confirm_charge":True})
        self.call("disconnect",{})
        self.assertTrue(self.call("connect",{"key":key,"consent":True})[1]["unknown"])
        self.assertEqual(self.call("submit",{"prompt":"test","confirm_charge":True})[0],409)
        with self.assertRaises(ValueError):
            self.call("reviewed",{"checked_provider_history":False})
        self.assertEqual(self.call("reviewed",{"checked_provider_history":True})[0],200)

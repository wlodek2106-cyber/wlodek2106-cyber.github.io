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

    def test_model_presets_and_untrusted_path(self):
        for name, config in h.MODEL_PRESETS.items():
            with self.subTest(model=name):
                path, payload, kind = h.selected_request({"model":name,"prompt":" test ","confirm_charge":True,"path":"https://evil.invalid","resolution":"8k"})
                self.assertEqual(path, config["path"])
                self.assertEqual(payload, {"prompt":"test", **config["settings"]})
                self.assertEqual(kind, config["kind"])
        for invalid in ["https://evil.invalid", "unavailable", [], None]:
            with self.subTest(model=invalid), self.assertRaises(ValueError):
                h.selected_request({"model":invalid,"prompt":"test","confirm_charge":True})
        with self.assertRaises(ValueError):
            h.selected_request({"model":"seedream_v5_pro","prompt":"test","confirm_charge":False})

    def test_image_result_and_no_leak(self):
        self.call("connect",{"key":"example:secret123","consent":True})
        with patch.object(h,"upstream",return_value={"request_id":"image_123"}) as provider:
            self.call("submit",{"model":"seedream_v5_pro","prompt":"test","confirm_charge":True})
            self.assertEqual(provider.call_args.args[1],"/bytedance/seedream/v5.0/pro/text-to-image")
        with patch.object(h,"upstream",return_value={"status":"completed","images":[{"url":"https://example.com/a.png"},{"url":"javascript:bad"},{"url":"https://user:password@example.com/b.png"}]}):
            self.assertEqual(self.call("status",{})[1],{"status":"completed","request_id":"image_123","image_urls":["https://example.com/a.png"]})

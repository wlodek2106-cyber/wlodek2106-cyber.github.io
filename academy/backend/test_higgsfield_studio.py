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

    def test_reference_modes_and_consent(self):
        for name, config in h.REFERENCE_PRESETS.items():
            body={"model":name,"prompt":"animate","confirm_charge":True,"confirm_reference_rights":True,"references":["https://example.com/image.png"]}
            path,payload,kind=h.selected_request(body)
            self.assertEqual(path,config["path"])
            self.assertEqual(kind,config["kind"])
            self.assertEqual(payload.get("image_url") or payload.get("image_urls"),"https://example.com/image.png" if config["reference"]=="single" else ["https://example.com/image.png"])
            with self.assertRaises(ValueError):
                h.selected_request({**body,"confirm_reference_rights":False})
            with self.assertRaises(ValueError):
                h.selected_request({**body,"references":["https://example.com/a.png"]*(config["limit"]+1)})
        for url in ["http://example.com/a.png","https://localhost/a.png","https://127.0.0.1/a.png","https://service.internal/a.png","https://user:secret@example.com/a.png","https://example.com:8888/a.png","file:///tmp/a.png","https://example.com/a.png#fragment"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                h.reference_url(url)

    def test_signed_upload(self):
        payload=h.upload_request({"content_type":"image/png","size":1024,"confirm_upload_rights":True})
        self.assertEqual(payload,{"content_type":"image/png"})
        response={"upload_url":"https://example.s3.us-east-1.amazonaws.com/image.png?X-Amz-Signature=example","public_url":"https://cdn.example.com/image.png","upload_headers":{"Content-Type":"image/png","x-amz-tagging":"project=example"}}
        self.assertEqual(h.signed_upload_fields(response,"image/png"),response)
        for patch_values in [{"size":0},{"size":10485761},{"size":True},{"content_type":"image/svg+xml"},{"confirm_upload_rights":False}]:
            with self.assertRaises(ValueError):
                h.upload_request({"content_type":"image/png","size":1024,"confirm_upload_rights":True,**patch_values})
        for patch_values in [{"upload_url":"https://example.com/upload?x=1"},{"upload_url":"https://example.s3.amazonaws.com.evil.com/a?x=1"},{"upload_headers":{"Authorization":"secret"}},{"upload_headers":{"Content-Type":"image/jpeg"}},{"public_url":"https://localhost/image.png"}]:
            with self.assertRaises(ValueError):
                h.signed_upload_fields({**response,**patch_values},"image/png")
        self.call("connect",{"key":"example:secret123","consent":True})
        with patch.object(h,"upstream",return_value=response) as provider:
            self.assertEqual(self.call("upload",{"content_type":"image/png","size":1024,"confirm_upload_rights":True})[1],response)
            self.assertEqual(provider.call_args.args[1],"/files/generate-upload-url")

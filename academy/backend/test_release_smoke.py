"""Release smoke checks on an isolated local HTTP server. No DB or external APIs."""
import http.client
import json
import os
import threading
import unittest
from unittest.mock import patch
from server import Handler,BoundedHTTPServer

PRIVATE={
    "/support":"/support.js",
    "/command-center":"/command-center.js",
    "/agency":"/agency.js",
    "/creator-analytics":"/creator-analytics.js",
    "/client-portal":"/client-portal.js",
    "/graduate-showcase":"/graduate-showcase.js",
}
PUBLIC={
    "/creator-suite":"/creator-suite.js",
    "/marketplace":"/marketplace.js",
    "/hire":"/hire.js",
    "/free-ai":"/free-ai.js",
    "/production-cost":"/production-cost.js",
    "/ai-workspace":"/ai-workspace.js",
    "/local-media":"/local-media.js",
    "/voice-studio":"/voice-studio.js",
    "/design-studio":"/design-studio.js",
    "/animation-studio":"/animation-studio.js",
    "/music-studio":"/music-studio.js",
    "/website-builder":"/website-builder.js",
    "/automation-studio":"/automation-studio.js",
}

class ReleaseSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=BoundedHTTPServer(("127.0.0.1",0),Handler)
        cls.worker=threading.Thread(target=cls.http.serve_forever,daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.worker.join(timeout=5)

    def request(self,path,method="GET",body=None,headers=None):
        conn=http.client.HTTPConnection("127.0.0.1",self.http.server_port,timeout=5)
        try:
            conn.request(method,path,body,headers or {})
            r=conn.getresponse()
            return r.status,{k.lower():v for k,v in r.getheaders()},r.read()
        finally:
            conn.close()

    def test_private_pages_and_assets(self):
        for path,script in PRIVATE.items():
            with self.subTest(page=path):
                code,headers,body=self.request(path+"?lang=ru")
                self.assertEqual(code,200)
                self.assertIn(script.encode(),body)
                self.assertIn("noindex",headers["x-robots-tag"])
                self.assertIn("connect-src 'self'",headers["content-security-policy"])
                self.assertIn("frame-ancestors 'none'",headers["content-security-policy"])
                self.assertEqual(headers["cache-control"],"no-store")
                code,headers,body=self.request(script)
                self.assertEqual(code,200)
                self.assertIn("javascript",headers["content-type"])
                self.assertGreater(len(body),100)
                self.assertTrue(headers.get("etag"))
                code,_,body=self.request(script,headers={"If-None-Match":headers["etag"]})
                self.assertEqual((code,body),(304,b""))
        code,_,body=self.request("/module-auth.js")
        self.assertEqual(code,200)
        self.assertIn(b"/passkeys/login/begin",body)
        self.assertNotIn(b"localStorage",body)

    def test_public_pages_and_assets(self):
        for path,script in PUBLIC.items():
            with self.subTest(page=path):
                code,headers,body=self.request(path)
                self.assertEqual(code,200)
                self.assertEqual(headers["cache-control"],"no-store")
                self.assertIn(script.encode(),body)
                code,headers,body=self.request(script)
                self.assertEqual(code,200)
                self.assertIn("javascript",headers["content-type"])
                self.assertGreater(len(body),100)
        code,headers,body=self.request("/dashboard")
        self.assertEqual(code,200)
        self.assertIn(b"academySidebar",body)
        self.assertIn("frame-ancestors 'none'",headers["content-security-policy"])

    def test_dashboard_shell_assets(self):
        from server import dashboard_shell,dashboard_csp
        original=b'<html><style>body{}</style><nav id="academyNav"></nav><script>let original=1;</script></html>'
        changed=dashboard_shell(original)
        self.assertIn(b'<script>let original=1;</script>',changed)
        self.assertIn(b'id="academyNav"',changed)
        self.assertEqual(dashboard_csp(original),dashboard_csp(changed))
        self.assertEqual(dashboard_shell(b'invalid'),b'invalid')
        code,headers,body=self.request("/dashboard")
        self.assertEqual(code,200)
        self.assertIn(b'/academy-shell.css',body)
        self.assertIn(b'/academy-shell.js',body)
        for asset,mime in (("/academy-shell.css","text/css"),("/academy-shell.js","javascript")):
            code,headers,body=self.request(asset)
            self.assertEqual(code,200)
            self.assertIn(mime,headers["content-type"])
            self.assertGreater(len(body),1000)
    def test_aurora_assets(self):
        from server import aurora_shell,dashboard_csp
        original=b'<html><style>body{}</style><script>let original=1;</script></html>'
        self.assertEqual(dashboard_csp(original),dashboard_csp(aurora_shell(original)))
        for path in ("/dashboard","/free-ai","/creator-suite","/support","/agency","/production-cost"):
            code,headers,body=self.request(path)
            self.assertEqual(code,200)
            self.assertIn(b'/academy-aurora.css',body)
            self.assertIn(b'/academy-aurora.js',body)
            if "content-security-policy" in headers:
                self.assertIn("style-src 'self'",headers["content-security-policy"])
        for asset,mime in (("/academy-aurora.css","text/css"),("/academy-aurora.js","javascript")):
            code,headers,body=self.request(asset)
            self.assertEqual(code,200)
            self.assertIn(mime,headers["content-type"])
            self.assertGreater(len(body),1000)
    def test_mobile_accessibility_markup(self):
        for path in ("/support","/command-center","/agency","/client-portal","/creator-analytics","/graduate-showcase","/free-ai","/production-cost"):
            with self.subTest(page=path):
                code,_,body=self.request(path)
                self.assertEqual(code,200)
                for marker in (b"viewport-fit=cover",b"academy-mobile-accessibility-v1",b"prefers-reduced-motion",b"safe-area-inset-bottom"):
                    self.assertIn(marker,body)
                if path in ("/support","/command-center","/agency","/client-portal","/creator-analytics"):
                    self.assertIn(b'autocomplete="username" autocapitalize="none"',body)
                    self.assertIn(b'aria-live="polite" aria-atomic="true"',body)
                    self.assertIn(b'id="private" hidden tabindex="-1"',body)
    def test_offline_database_fails_closed(self):
        with patch.dict(os.environ,{"ACADEMY_DATABASE_URL":""}):
            code,_,body=self.request("/health")
            self.assertEqual(code,200)
            self.assertEqual(json.loads(body)["status"],"ok")
            for path in ("/support/diagnose","/admin/system-monitor","/admin/incidents/list","/admin/launch-control","/checkout/create"):
                with self.subTest(route=path):
                    code,headers,body=self.request(path,"POST",b"{}",{"Content-Type":"application/json"})
                    self.assertEqual(code,503)
                    self.assertEqual(headers["cache-control"],"no-store")
                    self.assertFalse(json.loads(body)["payments"])

"""HTTP adapter checks against an isolated local server; no DB, no real payments."""
import unittest,threading,os,sys,types,json
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from server import Handler,BoundedHTTPServer,dashboard_csp,auth_retry_after
class HttpBoundary(unittest.TestCase):
    def test_auth_limits(self):
        from collections import OrderedDict
        with patch('server._limits',OrderedDict()),patch('server.time.monotonic',return_value=100):
            for _ in range(8): self.assertEqual(auth_retry_after('/login','a@example.invalid'),0)
            self.assertGreater(auth_retry_after('/login','a@example.invalid'),0)
            for n in range(52): self.assertEqual(auth_retry_after('/login',f'{n}@example.invalid'),0)
            self.assertGreater(auth_retry_after('/login','new@example.invalid'),0)
            self.assertEqual(auth_retry_after('/register','a@example.invalid'),0)
            with patch('server.time.monotonic',return_value=161):
                self.assertEqual(auth_retry_after('/login','a@example.invalid'),0)

    def test_http_boundary(self):
        def fake_dispatch(method,path,body,token):
            if path=="/private":
                if token!="test-only": raise PermissionError()
                return 200,{"ok":True}
            return 404,{"error":"Not found"}
        server=BoundedHTTPServer(("127.0.0.1",0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        url="http://127.0.0.1:"+str(server.server_port)
        def req(path,body=None,headers=None):
            try: return urlopen(Request(url+path,data=body,headers=headers or {}),timeout=5)
            except HTTPError as e: return e
        try:
            with patch.dict(os.environ,{"ACADEMY_DATABASE_URL":"test-only-not-a-real-db"}),patch.dict(sys.modules,{"api":types.SimpleNamespace(dispatch=fake_dispatch)}):
                with req("/health") as r:
                    self.assertEqual(r.status,200)
                    self.assertEqual(r.headers["Cache-Control"],"no-store")
                    self.assertEqual(r.headers["X-Frame-Options"],"DENY")
                with req("/dashboard") as r:
                    self.assertEqual(r.status,200)
                    body=r.read()
                    self.assertIn(b"academySidebar",body)
                    self.assertEqual(r.headers["Content-Security-Policy"],dashboard_csp(body))
                    self.assertNotIn("'unsafe-inline'",r.headers["Content-Security-Policy"].split("script-src ",1)[1].split(";",1)[0])
                    self.assertIn("camera=()",r.headers["Permissions-Policy"])
                with req("/ai-workspace.js") as r:
                    tag=r.headers["ETag"]
                    self.assertTrue(tag)
                with req("/ai-workspace.js",headers={"If-None-Match":tag}) as r:
                    self.assertEqual(r.status,304)
                    self.assertEqual(r.read(),b"")
                with req("/legal") as r:
                    self.assertEqual(r.status,200)
                    content=r.read()
                    for lang in (b'lang="en"',b'lang="ru"',b'lang="uk"',b'lang="pl"'):
                        self.assertIn(lang,content)
                    self.assertIn(b"PRE-LAUNCH DRAFT",content)
                with req("/creator-suite") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"creator-suite.js",r.read())
                with req("/production-cost") as r:
                    self.assertIn("connect-src 'none'",r.headers["Content-Security-Policy"])
                    self.assertIn(b'production-cost.js',r.read())
                with req("/production-cost.js") as r:
                    self.assertIn(b'function price',r.read())
                with req("/creator-suite.js") as r:
                    self.assertEqual(r.status,200)
                    body=r.read()
                    for project in (b"AppFlowy",b"OpenProject",b"OpenWhispr",b"CapSoftware",b"VoiceStudio",b"Chatwoot",b"Open-Generative-AI",b"open-seo"):
                        self.assertIn(project,body)
                    self.assertIn(b"getDisplayMedia",body)
                with req("/local-media") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"connect-src 'none'",r.read())
                with req("/local-media.js") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"decodeAudioData",r.read())
                with req("/voice-studio") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"connect-src 'none'",r.read())
                with req("/voice-studio.js") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"localService===true",r.read())
                with req("/design-studio") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"connect-src 'none'",r.read())
                with req("/design-studio.js") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"toBlob",r.read())
                with req("/animation-studio") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"connect-src 'none'",r.read())
                with req("/animation-studio.js") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"captureStream",r.read())
                with req("/music-studio") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"connect-src 'none'",r.read())
                with req("/music-studio.js") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"function wav",r.read())
                with req("/website-builder") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b'sandbox=""',r.read())
                with req("/website-builder.js") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"function buildSite",r.read())
                with req("/automation-studio") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"connect-src 'none'",r.read())
                with req("/automation-studio.js") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"function runWorkflow",r.read())
                with req("/ai-workspace") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"connect-src 'none'",r.read())
                with req("/ai-workspace.js") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"function selectTools",r.read())
                with req("/hire") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"hire.js",r.read())
                with req("/hire.js") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"intent=post",r.read())
                with req("/marketplace") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"marketplace.js",r.read())
                with req("/marketplace-preview") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn("connect-src 'none'",r.headers["Content-Security-Policy"])
                    self.assertIn("form-action 'none'",r.headers["Content-Security-Policy"])
                    self.assertIn("frame-ancestors 'none'",r.headers["Content-Security-Policy"])
                    self.assertIn("payment=()",r.headers["Permissions-Policy"])
                    self.assertEqual(r.headers["Cache-Control"],"no-store")
                    content=r.read()
                    self.assertIn(b"connect-src 'none'",content)
                    self.assertIn(b'id="pay" disabled',content)
                    self.assertIn(b"marketplace-preview.js",content)
                with req("/marketplace-preview.js") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"function quotePreview",r.read())
                with req("/marketplace.js") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"/marketplace/public",r.read())
                for path,body,headers,status in [("/private",None,{},403),("/private",None,{"Authorization":"Bearer test-only"},200),("/private",b"[]",{},400),("/private",b"{" ,{},400),("/private",b"x"*16385,{},400),("/private",None,{"Authorization":"Bearer "+"x"*129},403),("/unknown",None,{},404)]:
                    with req(path,body,headers) as r:
                        self.assertEqual(r.status,status)
                        self.assertEqual(r.headers["Cache-Control"],"no-store")
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)

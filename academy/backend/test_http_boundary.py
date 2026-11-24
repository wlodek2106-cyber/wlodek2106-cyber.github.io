"""HTTP adapter checks against an isolated local server; no DB, no real payments."""
import unittest,threading,os,sys,types,json
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from server import Handler,ThreadingHTTPServer
class HttpBoundary(unittest.TestCase):
    def test_http_boundary(self):
        def fake_dispatch(method,path,body,token):
            if path=="/private":
                if token!="test-only": raise PermissionError()
                return 200,{"ok":True}
            return 404,{"error":"Not found"}
        server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
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
                    self.assertIn(b"academySidebar",r.read())
                with req("/legal") as r:
                    self.assertEqual(r.status,200)
                    content=r.read()
                    for lang in (b'lang="en"',b'lang="ru"',b'lang="uk"',b'lang="pl"'):
                        self.assertIn(lang,content)
                    self.assertIn(b"PRE-LAUNCH DRAFT",content)
                with req("/creator-suite") as r:
                    self.assertEqual(r.status,200)
                    self.assertIn(b"creator-suite.js",r.read())
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
                for path,body,headers,status in [("/private",None,{},403),("/private",None,{"Authorization":"Bearer test-only"},200),("/private",b"[]",{},400),("/private",b"{" ,{},400),("/private",b"x"*16385,{},400),("/unknown",None,{},404)]:
                    with req(path,body,headers) as r:
                        self.assertEqual(r.status,status)
                        self.assertEqual(r.headers["Cache-Control"],"no-store")
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)

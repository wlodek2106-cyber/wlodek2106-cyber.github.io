from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os
import time, threading
from collections import OrderedDict
_limits=OrderedDict()
_limit_lock=threading.Lock()
def allow_auth(key):
    now=time.monotonic()
    with _limit_lock:
        start,count=_limits.get(key,(now,0))
        if now-start>=60: start,count=now,0
        if count>=8: return False
        _limits[key]=(start,count+1)
        _limits.move_to_end(key)
        while len(_limits)>10000: _limits.popitem(last=False)
        return True
from pathlib import Path
from urllib.parse import urlsplit
class Handler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Referrer-Policy","no-referrer")
        self.send_header("X-Frame-Options","DENY")
        super().end_headers()
    def respond(self,status,data):
        body=json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def handle_api(self):
        path=urlsplit(self.path).path
        assets={"/creator-suite.js":("creator-suite.js","application/javascript; charset=utf-8"),"/free-ai.js":("free-ai.js","application/javascript; charset=utf-8"),"/manifest.webmanifest":("manifest.webmanifest","application/manifest+json"),"/academy-icon.svg":("academy-icon.svg","image/svg+xml"),"/academy-sw.js":("academy-sw.js","application/javascript")}
        if self.command=="GET" and path in assets:
            name,mime=assets[path]
            body=Path(__file__).with_name(name).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type",mime)
            self.send_header("Cache-Control","no-cache")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path in ("/","/dashboard","/downloads","/reviews","/free-ai","/legal","/creator-suite") and self.command=="GET":
            body=Path(__file__).with_name("creator-suite.html" if path=="/creator-suite" else "legal.html" if path=="/legal" else "free-ai.html" if path=="/free-ai" else "reviews.html" if path=="/reviews" else "downloads.html" if path=="/downloads" else "dashboard.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Cache-Control","no-store")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path=="/health":
            return self.respond(200,{"status":"ok","service":"academy"})
        if not os.getenv("ACADEMY_DATABASE_URL"):
            return self.respond(503,{"ready":False,"payments":False,"error":"Database unavailable"})
        try:
            from api import dispatch
            body={}
            if self.command=="POST":
                n=int(self.headers.get("Content-Length","0"))
                if not 0<n<=16384:
                    return self.respond(400,{"error":"Invalid body length"})
                body=json.loads(self.rfile.read(n))
                if not isinstance(body,dict):
                    raise ValueError()
            auth=self.headers.get("Authorization","")
            token=auth[7:] if auth.startswith("Bearer ") else None
            if self.command=="POST" and path in ("/login","/register"):
                email=str(body.get("email","")).strip().lower()[:254]
                if not allow_auth((path,email)) or not allow_auth((path,"global")):
                    return self.respond(429,{"error":"Too many attempts; retry later"})
            if self.command=="POST" and path in ("/account/password","/account/mfa/begin","/account/mfa/confirm","/account/mfa/disable","/privacy/export","/privacy/request"):
                from hashlib import sha256
                if not token or not allow_auth((path,sha256(token.encode()).hexdigest())) or not allow_auth((path,"global")):
                    return self.respond(429,{"error":"Too many attempts; retry later"})
            status,data=dispatch(self.command,path,body,token)
            return self.respond(status,data)
        except PermissionError:
            return self.respond(403,{"error":"Access denied"})
        except (ValueError,KeyError,TypeError,AttributeError):
            return self.respond(400,{"error":"Invalid request"})
        except Exception:
            return self.respond(503,{"error":"Service unavailable"})
    def do_HEAD(self):
        self.send_response(200 if urlsplit(self.path).path in ("/","/health","/dashboard","/downloads","/reviews","/free-ai","/legal","/creator-suite") else 404)
        self.end_headers()
    do_GET=handle_api
    do_POST=handle_api
if __name__=="__main__":
    if os.getenv("ACADEMY_DATABASE_URL"):
        import subprocess, sys
        subprocess.check_call([sys.executable,"-m","pip","install","-r",str(Path(__file__).with_name("requirements.txt"))])
        from migrate import migrate
        migrate()
        import unittest
        from test_accounts_integration import AccountIntegration
        from test_payment_policy import PaymentPolicyTests
        payment_result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PaymentPolicyTests))
        if not payment_result.wasSuccessful() or payment_result.testsRun<6:
            raise RuntimeError('Payment policy check failed')
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AccountIntegration))
        if not result.wasSuccessful() or result.testsRun!=1 or result.skipped:
            raise RuntimeError("Account integration check failed")
        from test_checkout_integration import CheckoutIntegration
        checkout_result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CheckoutIntegration))
        if not checkout_result.wasSuccessful() or checkout_result.testsRun!=1 or checkout_result.skipped:
            raise RuntimeError("Checkout integration check failed")
        from test_launch_integration import LaunchIntegration
        launch_result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LaunchIntegration))
        if not launch_result.wasSuccessful() or launch_result.testsRun<1 or launch_result.skipped:
            raise RuntimeError("Launch integration check failed")
    from certificate_mail import configured,run
    if configured():
        threading.Thread(target=run,daemon=True,name="certificate-email").start()
    ThreadingHTTPServer(("0.0.0.0",int(os.environ.get("PORT","10000"))),Handler).serve_forever()

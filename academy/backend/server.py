from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os, re, hashlib, base64
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
def auth_retry_after(path,email):
    """Separate account limits from a bounded service-wide budget.
    Check both counters atomically without consuming attempts when blocked.
    """
    now=time.monotonic()
    digest=hashlib.sha256(email.encode()).hexdigest()
    buckets=[(("auth-account",path,digest),8),(("auth-service",path),60)]
    with _limit_lock:
        pending=[]
        retry=0
        for key,limit in buckets:
            start,count=_limits.get(key,(now,0))
            if now-start>=60: start,count=now,0
            if count>=limit: retry=max(retry,max(1,int(60-(now-start))+1))
            pending.append((key,start,count))
        if retry: return retry
        for key,start,count in pending:
            _limits[key]=(start,count+1)
            _limits.move_to_end(key)
        while len(_limits)>10000: _limits.popitem(last=False)
    return 0
from pathlib import Path
from urllib.parse import urlsplit
def dashboard_csp(body):
    text=body.decode("utf-8").replace("\r\n","\n").replace("\r","\n")
    scripts=re.findall(r"<script>(.*?)</script>",text,re.S)
    hashes=["'sha256-"+base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()+"'" for s in scripts]
    return "default-src 'none'; script-src 'self' "+" ".join(hashes)+"; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src blob:; connect-src 'self' https://*.amazonaws.com; manifest-src 'self'; worker-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'; object-src 'none'"

class BoundedHTTPServer(ThreadingHTTPServer):
    # One small service, bounded thread and database connection pressure.
    daemon_threads=True
    def __init__(self,*args,**kwargs):
        self.slots=threading.BoundedSemaphore(16)
        super().__init__(*args,**kwargs)
    def service_actions(self):
        # BaseServer invokes this on its regular serve_forever polling loop.
        # No background worker, external service or additional paid resources.
        from higgsfield_studio import prune_expired
        prune_expired()
        super().service_actions()
    def process_request(self,request,client_address):
        if not self.slots.acquire(blocking=False):
            try:
                request.settimeout(1)
                request.sendall(b"HTTP/1.1 503 Service Unavailable\r\nConnection: close\r\nCache-Control: no-store\r\nRetry-After: 2\r\nContent-Length: 0\r\n\r\n")
            except OSError:
                pass
            self.shutdown_request(request)
            return
        try:
            super().process_request(request,client_address)
        except BaseException:
            self.slots.release()
            raise
    def process_request_thread(self,request,client_address):
        try:
            super().process_request_thread(request,client_address)
        finally:
            self.slots.release()

class Handler(BaseHTTPRequestHandler):
    timeout=15
    def log_request(self,code="-",size="-"):
        # Do not put query strings, referral codes or supplied path data in logs.
        self.log_message("request %s %s",self.command,code)
    def end_headers(self):
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Referrer-Policy","no-referrer")
        self.send_header("X-Frame-Options","DENY")
        self.send_header("Permissions-Policy","geolocation=(), camera=(), microphone=(), payment=(), usb=()")
        super().end_headers()
    def respond(self,status,data):
        body=json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        if status==429 and type(data.get("retry_after")) is int:
            self.send_header("Retry-After",str(data["retry_after"]))
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def handle_api(self):
        path=urlsplit(self.path).path
        assets={"/client-portal.js":("client-portal.js","application/javascript; charset=utf-8"),"/production-cost.js":("production-cost.js","application/javascript; charset=utf-8"),"/graduate-showcase.js":("graduate-showcase.js","application/javascript; charset=utf-8"),"/local-ai-engine.py":("local-ai-engine.py","application/octet-stream"),"/veyra-lab.js":("veyra-lab.js","application/javascript; charset=utf-8"),"/openmvs-lab.js":("openmvs-lab.js","application/javascript; charset=utf-8"),"/openmvs-runner.py":("openmvs-runner.py","application/octet-stream"),"/openmotion-lab.js":("openmotion-lab.js","application/javascript; charset=utf-8"),"/marketplace-preview.js":("marketplace-preview.js","application/javascript; charset=utf-8"),"/hire.js":("hire.js","application/javascript; charset=utf-8"),"/marketplace.js":("marketplace.js","application/javascript; charset=utf-8"),"/ai-workspace.js":("ai-workspace.js","application/javascript; charset=utf-8"),"/automation-studio.js":("automation-studio.js","application/javascript; charset=utf-8"),"/website-builder.js":("website-builder.js","application/javascript; charset=utf-8"),"/music-studio.js":("music-studio.js","application/javascript; charset=utf-8"),"/animation-studio.js":("animation-studio.js","application/javascript; charset=utf-8"),"/design-studio.js":("design-studio.js","application/javascript; charset=utf-8"),"/voice-studio.js":("voice-studio.js","application/javascript; charset=utf-8"),"/local-media.js":("local-media.js","application/javascript; charset=utf-8"),"/creator-suite.js":("creator-suite.js","application/javascript; charset=utf-8"),"/free-ai.js":("free-ai.js","application/javascript; charset=utf-8"),"/manifest.webmanifest":("manifest.webmanifest","application/manifest+json"),"/academy-icon.svg":("academy-icon.svg","image/svg+xml"),"/academy-sw.js":("academy-sw.js","application/javascript")}
        if self.command=="GET" and path in assets:
            name,mime=assets[path]
            body=Path(__file__).with_name(name).read_bytes()
            etag='"'+hashlib.sha256(body).hexdigest()+'"'
            if self.headers.get("If-None-Match")==etag:
                self.send_response(304)
                self.send_header("ETag",etag)
                self.send_header("Cache-Control","no-cache")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("ETag",etag)
            self.send_header("Content-Type",mime)
            if path=="/local-ai-engine.py": self.send_header("Content-Disposition",'attachment; filename="zer0life_local_ai.py"')
            if path=="/openmvs-runner.py": self.send_header("Content-Disposition",'attachment; filename="zer0life_openmvs.py"')
            self.send_header("Cache-Control","no-cache")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path in ("/","/graduate-showcase","/veyra-lab","/openmvs-lab","/openmotion-lab","/dashboard","/downloads","/reviews","/free-ai","/legal","/creator-suite","/local-media","/voice-studio","/design-studio","/animation-studio","/music-studio","/website-builder","/automation-studio","/ai-workspace","/marketplace","/hire","/marketplace-preview","/production-cost","/client-portal") and self.command=="GET":
            body=Path(__file__).with_name("client-portal.html" if path=="/client-portal" else "production-cost.html" if path=="/production-cost" else "graduate-showcase.html" if path=="/graduate-showcase" else "veyra-lab.html" if path=="/veyra-lab" else "openmvs-lab.html" if path=="/openmvs-lab" else "openmotion-lab.html" if path=="/openmotion-lab" else "marketplace-preview.html" if path=="/marketplace-preview" else "hire.html" if path=="/hire" else "marketplace.html" if path=="/marketplace" else "ai-workspace.html" if path=="/ai-workspace" else "automation-studio.html" if path=="/automation-studio" else "website-builder.html" if path=="/website-builder" else "music-studio.html" if path=="/music-studio" else "animation-studio.html" if path=="/animation-studio" else "design-studio.html" if path=="/design-studio" else "voice-studio.html" if path=="/voice-studio" else "local-media.html" if path=="/local-media" else "creator-suite.html" if path=="/creator-suite" else "legal.html" if path=="/legal" else "free-ai.html" if path=="/free-ai" else "reviews.html" if path=="/reviews" else "downloads.html" if path=="/downloads" else "dashboard.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            if path in ("/","/dashboard"):
                self.send_header("Content-Security-Policy",dashboard_csp(body))
            elif path in ("/graduate-showcase","/client-portal"):
                self.send_header("Content-Security-Policy","default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
                self.send_header("X-Robots-Tag","noindex, nofollow")
            elif path in ("/marketplace-preview","/production-cost"):
                self.send_header("Content-Security-Policy","default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'; object-src 'none'")
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
                if self.headers.get("Transfer-Encoding") or len(self.headers.get_all("Content-Length",[]))!=1:
                    return self.respond(400,{"error":"Invalid body framing"})
                n=int(self.headers.get("Content-Length","0"))
                if not 0<n<=16384:
                    return self.respond(400,{"error":"Invalid body length"})
                raw=self.rfile.read(n)
                if len(raw)!=n:
                    return self.respond(400,{"error":"Incomplete body"})
                body=json.loads(raw)
                if not isinstance(body,dict):
                    raise ValueError()
            auth=self.headers.get("Authorization","")
            token=auth[7:] if auth.startswith("Bearer ") else None
            if token is not None and len(token)>128:
                return self.respond(403,{"error":"Access denied"})
            if self.command=="POST" and path in ("/login","/register"):
                email=str(body.get("email","")).strip().lower()[:254]
                if path=="/login": email=email.removeprefix("@")
                retry=auth_retry_after(path,email)
                if retry:
                    return self.respond(429,{"error":"Too many attempts; retry later","code":"rate_limit","retry_after":retry})
            if self.command=="POST" and path in ("/passkeys/login/begin","/passkeys/login/finish","/account/passkeys/begin","/account/passkeys/finish","/account/passkeys/disable"):
                if self.headers.get("Origin")!="https://zer0life-academy.onrender.com":
                    return self.respond(403,{"error":"Access denied"})
                retry=auth_retry_after(path,"passkeys" if path.startswith("/passkeys/") else hashlib.sha256((token or "").encode()).hexdigest())
                if retry: return self.respond(429,{"error":"Too many attempts; retry later","retry_after":retry})
            if self.command=="POST" and path in ("/account/password","/account/mfa/begin","/account/mfa/confirm","/account/mfa/disable","/privacy/export","/privacy/request","/account/passkeys/begin","/account/passkeys/finish","/account/passkeys/disable"):
                from hashlib import sha256
                if not token or not allow_auth((path,sha256(token.encode()).hexdigest())) or not allow_auth((path,"global")):
                    return self.respond(429,{"error":"Too many attempts; retry later"})
            if path.startswith("/marketplace-pay/request/") or path in ("/marketplace-pay/settle","/marketplace-pay/reconcile","/marketplace-pay/admin-reconcile","/marketplace-pay/treasury-preflight"):
                if not allow_auth(("marketplace-payment", "global")):
                    return self.respond(429,{"error":"Too many requests; retry later"})
            status,data=dispatch(self.command,path,body,token)
            return self.respond(status,data)
        except PermissionError:
            return self.respond(403,{"error":"Access denied"})
        except (ValueError,KeyError,TypeError,AttributeError):
            return self.respond(400,{"error":"Invalid request"})
        except Exception:
            return self.respond(503,{"error":"Service unavailable"})
    def do_HEAD(self):
        self.send_response(200 if urlsplit(self.path).path in ("/","/health","/graduate-showcase","/veyra-lab","/openmvs-lab","/openmotion-lab","/dashboard","/downloads","/reviews","/free-ai","/legal","/creator-suite","/local-media","/voice-studio","/design-studio","/animation-studio","/music-studio","/website-builder","/automation-studio","/ai-workspace","/marketplace","/hire","/marketplace-preview","/production-cost","/client-portal") else 404)
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
        from test_passkeys import PasskeyTests
        passkey_result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PasskeyTests))
        if not passkey_result.wasSuccessful() or passkey_result.testsRun<5:
            raise RuntimeError("Passkey security checks failed")
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
    BoundedHTTPServer(("0.0.0.0",int(os.environ.get("PORT","10000"))),Handler).serve_forever()

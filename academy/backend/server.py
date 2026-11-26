from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os, re, hashlib, base64
import time, threading
from collections import OrderedDict
from functools import lru_cache
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
from urllib.parse import urlsplit, parse_qs
def dashboard_shell(body):
    if b'</style>' not in body or not body.rstrip().endswith(b'</html>'):
        return body
    body=body.replace(b'</style>',b'</style><link rel="stylesheet" href="/academy-shell.css">',1)
    head,_,tail=body.rpartition(b'</html>')
    return head+b'<script src="/academy-shell.js"></script></html>'+tail

AURORA_PAGES={"/","/dashboard","/free-ai","/creator-suite","/ai-workspace","/support","/command-center","/agency","/creator-analytics","/client-portal","/production-cost","/marketplace","/hire","/animation-studio","/music-studio","/website-builder","/automation-studio","/design-studio","/voice-studio","/local-media","/graduate-showcase"}

def aurora_shell(body):
    if b'</style>' not in body or not body.rstrip().endswith(b'</html>'):
        return body
    body=body.replace(b'</style>',b'</style><link rel="stylesheet" href="/academy-aurora.css">',1)
    head,_,tail=body.rpartition(b'</html>')
    return head+b'<script src="/academy-aurora.js"></script></html>'+tail

# The public static dashboard is identical for all visitors; cache only two content variants.
# The entire immutable HTML is the cache key, so edited scripts always get new hashes.
@lru_cache(maxsize=2)
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
        self.startup_ready=True
        super().__init__(*args,**kwargs)
    def service_actions(self):
        # BaseServer invokes this on its regular serve_forever polling loop.
        # No background worker, external service or additional paid resources.
        if self.startup_ready:
            from higgsfield_studio import prune_expired
            prune_expired()
        super().service_actions()
    def process_request(self,request,client_address):
        if not self.slots.acquire(blocking=False):
            from system_monitor import metrics
            metrics.record("system",503)
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
    def send_response(self,code,message=None):
        from system_monitor import metrics,group
        if self.command in ("GET","POST"):
            metrics.record(group(self.path),code)
        super().send_response(code,message)
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
    def startup_response(self,path):
        if self.command=="GET" and path in ("/","/dashboard"):
            body=('<!doctype html><html lang="en"><meta charset="utf-8">'
                  '<meta name="viewport" content="width=device-width,initial-scale=1">'
                  '<meta http-equiv="refresh" content="8"><title>Zer0Life Academy</title>'
                  '<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#151121;color:#f0e7ff;font:16px system-ui}main{max-width:460px;padding:28px}h1{font-size:26px}p{line-height:1.6}a{color:#ccb2ff}small{color:#c2b2dd}</style>'
                  '<main><small>ZER0LIFE / ACADEMY</small><h1>Starting Academy</h1>'
                  '<p>Сервер запускается и проверяет безопасность. Страница обновится автоматически.</p>'
                  '<p>The server is starting and checking readiness. This page refreshes automatically.</p>'
                  '<a href="/dashboard?view=classic">Classic mode / Без 3D</a></main></html>').encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Cache-Control","no-store")
            self.send_header("Content-Security-Policy","default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(503)
        body=b'{"error":"Academy is starting","code":"starting","ready":false,"payments":false}'
        self.send_header("Content-Type","application/json")
        self.send_header("Cache-Control","no-store")
        self.send_header("Retry-After","8")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def handle_api(self):
        try: path=urlsplit(self.path).path
        except ValueError: return self.respond(400,{"error":"Invalid path"})
        if not self.server.startup_ready:
            return self.startup_response(path)
        assets={"/academy-aurora.css":("academy-aurora.css","text/css; charset=utf-8"),"/academy-aurora.js":("academy-aurora.js","application/javascript; charset=utf-8"),"/academy-shell.css":("academy-shell.css","text/css; charset=utf-8"),"/academy-shell.js":("academy-shell.js","application/javascript; charset=utf-8"),"/support.js":("support.js","application/javascript; charset=utf-8"),"/module-auth.js":("module-auth.js","application/javascript; charset=utf-8"),"/command-center.js":("command-center.js","application/javascript; charset=utf-8"),"/agency.js":("agency.js","application/javascript; charset=utf-8"),"/creator-analytics.js":("creator-analytics.js","application/javascript; charset=utf-8"),"/client-portal.js":("client-portal.js","application/javascript; charset=utf-8"),"/production-cost.js":("production-cost.js","application/javascript; charset=utf-8"),"/graduate-showcase.js":("graduate-showcase.js","application/javascript; charset=utf-8"),"/local-ai-engine.py":("local-ai-engine.py","application/octet-stream"),"/veyra-lab.js":("veyra-lab.js","application/javascript; charset=utf-8"),"/openmvs-lab.js":("openmvs-lab.js","application/javascript; charset=utf-8"),"/openmvs-runner.py":("openmvs-runner.py","application/octet-stream"),"/openmotion-lab.js":("openmotion-lab.js","application/javascript; charset=utf-8"),"/marketplace-preview.js":("marketplace-preview.js","application/javascript; charset=utf-8"),"/hire.js":("hire.js","application/javascript; charset=utf-8"),"/marketplace.js":("marketplace.js","application/javascript; charset=utf-8"),"/ai-workspace.js":("ai-workspace.js","application/javascript; charset=utf-8"),"/automation-studio.js":("automation-studio.js","application/javascript; charset=utf-8"),"/website-builder.js":("website-builder.js","application/javascript; charset=utf-8"),"/music-studio.js":("music-studio.js","application/javascript; charset=utf-8"),"/animation-studio.js":("animation-studio.js","application/javascript; charset=utf-8"),"/design-studio.js":("design-studio.js","application/javascript; charset=utf-8"),"/voice-studio.js":("voice-studio.js","application/javascript; charset=utf-8"),"/local-media.js":("local-media.js","application/javascript; charset=utf-8"),"/creator-suite.js":("creator-suite.js","application/javascript; charset=utf-8"),"/free-ai.js":("free-ai.js","application/javascript; charset=utf-8"),"/manifest.webmanifest":("manifest.webmanifest","application/manifest+json"),"/academy-icon.svg":("academy-icon.svg","image/svg+xml"),"/academy-sw.js":("academy-sw.js","application/javascript")}
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
        if path in ("/","/graduate-showcase","/veyra-lab","/openmvs-lab","/openmotion-lab","/dashboard","/downloads","/reviews","/free-ai","/legal","/creator-suite","/local-media","/voice-studio","/design-studio","/animation-studio","/music-studio","/website-builder","/automation-studio","/ai-workspace","/marketplace","/hire","/marketplace-preview","/production-cost","/client-portal","/creator-analytics","/agency","/command-center","/support") and self.command=="GET":
            body=Path(__file__).with_name("support.html" if path=="/support" else "command-center.html" if path=="/command-center" else "agency.html" if path=="/agency" else "creator-analytics.html" if path=="/creator-analytics" else "client-portal.html" if path=="/client-portal" else "production-cost.html" if path=="/production-cost" else "graduate-showcase.html" if path=="/graduate-showcase" else "veyra-lab.html" if path=="/veyra-lab" else "openmvs-lab.html" if path=="/openmvs-lab" else "openmotion-lab.html" if path=="/openmotion-lab" else "marketplace-preview.html" if path=="/marketplace-preview" else "hire.html" if path=="/hire" else "marketplace.html" if path=="/marketplace" else "ai-workspace.html" if path=="/ai-workspace" else "automation-studio.html" if path=="/automation-studio" else "website-builder.html" if path=="/website-builder" else "music-studio.html" if path=="/music-studio" else "animation-studio.html" if path=="/animation-studio" else "design-studio.html" if path=="/design-studio" else "voice-studio.html" if path=="/voice-studio" else "local-media.html" if path=="/local-media" else "creator-suite.html" if path=="/creator-suite" else "legal.html" if path=="/legal" else "free-ai.html" if path=="/free-ai" else "reviews.html" if path=="/reviews" else "downloads.html" if path=="/downloads" else "dashboard.html").read_bytes()
            classic=parse_qs(urlsplit(self.path).query).get("view")==["classic"]
            if path in ("/","/dashboard"):
                body=dashboard_shell(body)
                # Static recovery link stays usable even if optional UI JavaScript fails.
                recovery=(b'<p><a href="/dashboard">Aurora 3D / Modern interface</a></p>' if classic else
                          b'<p><a href="/dashboard?view=classic">Classic mode / Lite / Bez animacji</a></p>')
                body=body.replace(b'<section id="auth">',b'<section id="auth">'+recovery,1)
            if path in AURORA_PAGES and not classic: body=aurora_shell(body)
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            if path in ("/","/dashboard"):
                self.send_header("Content-Security-Policy",dashboard_csp(body))
            elif path in ("/graduate-showcase","/client-portal","/creator-analytics","/agency","/command-center","/support"):
                self.send_header("Content-Security-Policy","default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
                self.send_header("X-Robots-Tag","noindex, nofollow")
            elif path in ("/marketplace-preview","/production-cost"):
                self.send_header("Content-Security-Policy","default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'; object-src 'none'")
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
        try: path=urlsplit(self.path).path
        except ValueError:
            self.send_response(400)
            self.end_headers()
            return
        if not self.server.startup_ready and path=="/health":
            self.send_response(503)
            self.send_header("Retry-After","8")
            self.end_headers()
            return
        self.send_response(200 if path in ("/","/health","/graduate-showcase","/veyra-lab","/openmvs-lab","/openmotion-lab","/dashboard","/downloads","/reviews","/free-ai","/legal","/creator-suite","/local-media","/voice-studio","/design-studio","/animation-studio","/music-studio","/website-builder","/automation-studio","/ai-workspace","/marketplace","/hire","/marketplace-preview","/production-cost","/client-portal","/creator-analytics","/agency","/command-center","/support") else 404)
        self.end_headers()
    do_GET=handle_api
    do_POST=handle_api
def release_db_verified():
    commit=os.getenv("RENDER_GIT_COMMIT")
    proof=Path(__file__).with_name(".academy-db-release-check")
    return bool(commit and proof.is_file() and proof.read_text().strip()==commit)

def run_release_db_checks():
    import unittest
    from test_accounts_integration import AccountIntegration
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

def initialize():
    if os.getenv("ACADEMY_DATABASE_URL"):
        import subprocess, sys
        if not (os.getenv("RENDER")=="true" or os.getenv("RENDER_SERVICE_NAME")=="zer0life-academy"):
            subprocess.check_call([sys.executable,"-m","pip","install","-r",str(Path(__file__).with_name("requirements.txt"))])
        from migrate import migrate
        migrate()
        import unittest
        from test_passkeys import PasskeyTests
        passkey_result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PasskeyTests))
        if not passkey_result.wasSuccessful() or passkey_result.testsRun<5:
            raise RuntimeError("Passkey security checks failed")
        from test_payment_policy import PaymentPolicyTests
        payment_result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PaymentPolicyTests))
        if not payment_result.wasSuccessful() or payment_result.testsRun<6:
            raise RuntimeError('Payment policy check failed')
        # A successful build-stage DB regression is valid only for this exact release.
        # If Render did not expose the DB during build, keep the full startup gate.
        if not release_db_verified():
            run_release_db_checks()
        else:
            print("Database release checks verified during build",flush=True)
        from database import ready
        if not ready():
            raise RuntimeError("Database readiness check failed")
    from certificate_mail import configured,run
    if configured():
        threading.Thread(target=run,daemon=True,name="certificate-email").start()
if __name__=="__main__":
    with BoundedHTTPServer(("0.0.0.0",int(os.environ.get("PORT","10000"))),Handler) as http:
        http.startup_ready=False
        worker=threading.Thread(target=http.serve_forever,daemon=True,name="academy-http")
        worker.start()
        print("Academy HTTP bound; startup checks in progress",flush=True)
        try:
            initialize()
            http.startup_ready=True
            print("Academy startup checks complete; API ready",flush=True)
            worker.join()
        finally:
            http.shutdown()
            worker.join(timeout=5)

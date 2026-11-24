from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os
from pathlib import Path
from urllib.parse import urlsplit
class Handler(BaseHTTPRequestHandler):
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
        if path=="/dashboard" and self.command=="GET":
            body=Path(__file__).with_name("dashboard.html").read_bytes()
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
            status,data=dispatch(self.command,path,body,token)
            return self.respond(status,data)
        except PermissionError:
            return self.respond(403,{"error":"Access denied"})
        except (ValueError,KeyError,TypeError,AttributeError):
            return self.respond(400,{"error":"Invalid request"})
        except Exception:
            return self.respond(503,{"error":"Service unavailable"})
    do_GET=handle_api
    do_POST=handle_api
if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",int(os.environ.get("PORT","10000"))),Handler).serve_forever()

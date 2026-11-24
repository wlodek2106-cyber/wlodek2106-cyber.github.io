from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            status, data = 200, {"status":"ok","service":"academy"}
        elif self.path == "/ready":
            status, data = 503, {"ready":False,"payments":False,"reason":"Persistent database and authentication not configured"}
        else:
            status, data = 404, {"error":"not found"}
        body=json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)
if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",int(os.environ.get("PORT","10000"))),Handler).serve_forever()

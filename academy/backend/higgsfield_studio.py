"""Graduate-only, per-session Higgsfield BYOK beta. No Academy provider key."""
import hashlib, json, re, threading, time
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

BASE = "https://api.higgsfield.ai"
MODEL = "/bytedance/seedance-2.0/text-to-video"
TTL = 1800
LOCK = threading.Lock()
SESSIONS = {}
RATE = {}
ID = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")
TERMINAL = {"completed", "failed", "nsfw", "canceled"}

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def upstream(key, path, payload=None):
    # Only fixed provider endpoints; never use provider-supplied status URLs.
    headers = {"Authorization": "Key " + key, "Accept": "application/json"}
    raw = None if payload is None else json.dumps(payload).encode()
    if raw is not None:
        headers["Content-Type"] = "application/json"
    try:
        req = Request(BASE + path, data=raw, headers=headers)
        with build_opener(NoRedirect()).open(req, timeout=10) as response:
            data = json.loads(response.read(262145))
            if not isinstance(data, dict):
                raise ValueError()
            return data
    except HTTPError as e:
        # Never expose the upstream response, request headers or credentials.
        if e.code in (401, 403):
            return {"error_code": "key_rejected"}
        if e.code == 402:
            return {"error_code": "balance_required"}
        if e.code == 429:
            return {"error_code": "provider_rate_limit"}
        if 400 <= e.code < 500:
            return {"error_code": "provider_rejected"}
        return {"error_code": "outcome_unknown"}
    except (URLError, OSError, ValueError, TimeoutError):
        return {"error_code": "outcome_unknown"}

def valid_key(key):
    return isinstance(key, str) and 12 <= len(key) <= 1024 and all(33 <= ord(c) <= 126 for c in key) and not key.startswith("Key ")

def safe_url(value):
    if not isinstance(value, str) or len(value) > 4096:
        return None
    try:
        u = urlsplit(value)
        return value if u.scheme == "https" and u.hostname and not u.username and not u.password and not any(c.isspace() for c in value) and "\\" not in value else None
    except ValueError:
        return None

def session_id(token):
    from graduate_showcase import identity, credential
    from database import transaction
    sid = identity(token)
    with transaction() as cur:
        if not credential(cur, sid):
            raise PermissionError("Graduate certificate required")
    return str(sid) + ":" + hashlib.sha256(token.encode()).hexdigest()

def dispatch(token, action, body):
    owner = session_id(token)
    now = time.monotonic()
    with LOCK:
        for k in list(SESSIONS):
            if SESSIONS[k]["expires"] <= now and not SESSIONS[k]["busy"]:
                del SESSIONS[k]
        for k in list(RATE):
            if RATE[k] <= now:
                del RATE[k]
        if len(RATE) >= 5000 or RATE.get(owner, 0) > now:
            return 429, {"error": "Wait before retrying"}
        RATE[owner] = now + 2
        session = SESSIONS.get(owner)
        if action == "connect":
            key = body.get("key")
            if not valid_key(key) or body.get("consent") is not True:
                raise ValueError()
            if session and (session["busy"] or session["job"] or session["unknown"]):
                return 409, {"error": "Finish or disconnect the existing session first"}
            if len(SESSIONS) >= 100 and session is None:
                return 503, {"error": "Studio temporarily full"}
            SESSIONS[owner] = {"key": key, "expires": now + TTL, "busy": False, "job": None, "unknown": False}
            return 200, {"session": "ready_unverified", "expires_in": TTL}
        if action == "disconnect":
            if session and session["busy"]:
                return 409, {"error": "Request in progress"}
            SESSIONS.pop(owner, None)
            return 200, {"session": "disconnected"}
        if not session or session["expires"] <= now:
            return 409, {"error": "Reconnect your API key"}
        if session["busy"]:
            return 409, {"error": "Request in progress"}
        if action == "submit":
            prompt = body.get("prompt")
            if body.get("confirm_charge") is not True or not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 4000:
                raise ValueError()
            if session["job"] or session["unknown"]:
                return 409, {"error": "Resolve the previous request first"}
            path = MODEL
            payload = {"prompt": prompt.strip(), "resolution": "720p", "generate_audio": True, "duration": 5, "aspect_ratio": "16:9"}
        elif action in ("status", "cancel"):
            job = session["job"]
            if not job or not ID.fullmatch(job):
                return 409, {"error": "No active request"}
            path = "/requests/" + job + "/" + action
            payload = {} if action == "cancel" else None
        else:
            raise ValueError()
        session["busy"] = True
        key = session["key"]
    try:
        result = upstream(key, path, payload)
        with LOCK:
            if "error_code" in result:
                if action == "submit" and result["error_code"] == "outcome_unknown":
                    session["unknown"] = True
                return 200, {"error_code": result["error_code"]}
            if action == "submit":
                job = result.get("request_id")
                if not isinstance(job, str) or not ID.fullmatch(job):
                    session["unknown"] = True
                    return 200, {"error_code": "outcome_unknown"}
                session["job"] = job
                return 200, {"request_id": job, "status": "submitted"}
            status = result.get("status")
            if status not in TERMINAL | {"queued", "in_progress", "processing", "running", "pending"}:
                status = "pending"
            output = {"status": status, "request_id": session["job"]}
            if status == "completed":
                video = result.get("video")
                url = safe_url(video.get("url")) if isinstance(video, dict) else None
                if url:
                    output["video_url"] = url
                else:
                    return 200, {"status": "pending", "request_id": session["job"], "error_code": "result_unavailable"}
            if status in TERMINAL:
                session["job"] = None
            return 200, output
    finally:
        with LOCK:
            session["busy"] = False

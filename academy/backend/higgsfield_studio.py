"""Graduate-only, per-session Higgsfield BYOK beta. No Academy provider key."""
import hashlib, json, re, threading, time
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

BASE = "https://api.higgsfield.ai"
MODEL = "/bytedance/seedance-2.0/text-to-video"
MODEL_PRESETS = {"seedream_v5_pro": {"path": "/bytedance/seedream/v5.0/pro/text-to-image", "kind": "image", "settings": {"resolution": "2k", "aspect_ratio": "1:1"}}, "kling_image_4_0": {"path": "/kling-image/v4.0/text-to-image", "kind": "image", "settings": {"resolution": "2k", "aspect_ratio": "16:9"}}, "recraft_v4_1": {"path": "/recraft/v4.1/text-to-image", "kind": "image", "settings": {"resolution": "1k", "aspect_ratio": "1:1", "output_format": "jpg"}}, "qwen_image_3": {"path": "/alibaba/qwen-image-3/text-to-image", "kind": "image", "settings": {"resolution": "1k", "aspect_ratio": "1:1", "prompt_extend": True, "enable_thinking": True, "prompt_extend_mode": "direct"}}, "soul_2": {"path": "/higgsfield-ai/soul/v2/standard", "kind": "image", "settings": {"seed": None, "batch_size": 1, "resolution": "720p", "aspect_ratio": "4:3", "enhance_prompt": True}}, "kling_video_4_0": {"path": "/kling-video/v4.0/text-to-video", "kind": "video", "settings": {"duration": 10, "resolution": "1080p", "aspect_ratio": "16:9"}}, "wan_3_0": {"path": "/alibaba/wan-3.0/text-to-video", "kind": "video", "settings": {"duration": 5, "resolution": "1080p", "aspect_ratio": "adaptive", "generate_audio": True, "enable_thinking": False}}, "wan_3_0_prime": {"path": "/alibaba/wan-3.0-prime/text-to-video", "kind": "video", "settings": {"duration": 5, "resolution": "1080p", "aspect_ratio": "adaptive", "generate_audio": True, "enable_thinking": False}}}
TTL = 1800
LOCK = threading.Lock()
SESSIONS = {}
RATE = {}
ID = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")
TERMINAL = {"completed", "failed", "nsfw", "canceled", "cancelled"}
RESOLUTIONS = {"480p", "720p", "1080p", "4k"}
RATIOS = {"16:9", "4:3", "1:1", "3:4", "9:16", "21:9"}
GUARD_TTL = 86400

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

def generation_payload(body):
    prompt = body.get("prompt")
    duration = body.get("duration", 5)
    resolution = body.get("resolution", "720p")
    ratio = body.get("aspect_ratio", "16:9")
    audio = body.get("generate_audio", True)
    if body.get("confirm_charge") is not True or not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 4000:
        raise ValueError("Invalid prompt or consent")
    if type(duration) is not int or not 4 <= duration <= 15:
        raise ValueError("Invalid duration")
    if not isinstance(resolution, str) or resolution not in RESOLUTIONS or not isinstance(ratio, str) or ratio not in RATIOS or type(audio) is not bool:
        raise ValueError("Invalid generation settings")
    return {"prompt": prompt.strip(), "duration": duration, "resolution": resolution, "aspect_ratio": ratio, "generate_audio": audio}

def selected_request(body):
    model = body.get("model", "seedance_2_0")
    if not isinstance(model, str):
        raise ValueError("Invalid model")
    if model == "seedance_2_0":
        return MODEL, generation_payload(body), "video"
    config = MODEL_PRESETS.get(model)
    if not config:
        raise ValueError("Unsupported API model")
    prompt = body.get("prompt")
    if body.get("confirm_charge") is not True or not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 4000:
        raise ValueError("Invalid prompt or consent")
    # Fixed, documented initial settings. Never accept a caller-supplied endpoint or arbitrary provider fields.
    return config["path"], {"prompt": prompt.strip(), **config["settings"]}, config["kind"]

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
            item = SESSIONS[k]
            if item["expires"] <= now and not item["busy"]:
                item["key"] = None
                if not (item["job"] or item["unknown"]) or item["guard_until"] <= now:
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
            fingerprint = hashlib.sha256(key.encode()).hexdigest()
            if session and session["busy"]:
                return 409, {"error": "Request in progress"}
            if session and (session["job"] or session["unknown"]):
                if session["fingerprint"] != fingerprint:
                    return 409, {"error": "Use the original key to resolve the previous request"}
                session["key"] = key
                session["expires"] = now + TTL
                return 200, {"session": "ready_unverified", "expires_in": TTL, "request_id": session["job"], "unknown": session["unknown"]}
            if len(SESSIONS) >= 100 and session is None:
                return 503, {"error": "Studio temporarily full"}
            SESSIONS[owner] = {"key": key, "fingerprint": fingerprint, "expires": now + TTL, "guard_until": now + GUARD_TTL, "busy": False, "job": None, "unknown": False}
            return 200, {"session": "ready_unverified", "expires_in": TTL}
        if action == "disconnect":
            if session and session["busy"]:
                return 409, {"error": "Request in progress"}
            if session and (session["job"] or session["unknown"]):
                # Keep the pending-job guard without keeping the API secret.
                session["key"] = None
                session["expires"] = 0
            else:
                SESSIONS.pop(owner, None)
            return 200, {"session": "disconnected"}
        if not session or session["expires"] <= now or not session["key"]:
            return 409, {"error": "Reconnect your API key"}
        if session["busy"]:
            return 409, {"error": "Request in progress"}
        if action == "submit":
            path, payload, kind = selected_request(body)
            if session["job"] or session["unknown"]:
                return 409, {"error": "Resolve the previous request first"}
            session["guard_until"] = now + GUARD_TTL
            session["kind"] = kind
        elif action == "reviewed":
            if body.get("checked_provider_history") is not True or session["job"] or not session["unknown"]:
                raise ValueError("Review the unknown request in the provider console first")
            session["unknown"] = False
            return 200, {"status": "reviewed"}
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
                if session.get("kind") == "image":
                    images = result.get("images")
                    urls = [safe_url(item.get("url")) for item in images[:8] if isinstance(item, dict)] if isinstance(images, list) else []
                    urls = [url for url in urls if url]
                    if urls:
                        output["image_urls"] = urls
                    else:
                        return 200, {"status": "pending", "request_id": session["job"], "error_code": "result_unavailable"}
                else:
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

"""RFC 6238 compatible TOTP, local verification and single-use recovery codes."""
import base64,hashlib,hmac,re,secrets,struct,time
from urllib.parse import urlencode,quote

def new_secret():
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii")

def code_at(secret,counter):
    digest=hmac.new(base64.b32decode(secret),struct.pack(">Q",counter),hashlib.sha1).digest()
    offset=digest[-1]&15
    return str((int.from_bytes(digest[offset:offset+4],"big")&0x7fffffff)%1000000).zfill(6)

def check(secret,code,last=-1):
    if not isinstance(code,str) or not re.fullmatch(r"[0-9]{6}",code): return None
    current=int(time.time())//30
    for counter in (current,current-1,current+1):
        if counter>=0 and counter>last and hmac.compare_digest(code_at(secret,counter),code):
            return counter
    return None

def recovery_digest(code):
    return hashlib.sha256(code.encode()).hexdigest()

def new_recovery():
    return [secrets.token_hex(16) for _ in range(8)]

def consume(secret,last,digests,code):
    counter=check(secret,code,last)
    if counter is not None: return counter,list(digests)
    if isinstance(code,str) and re.fullmatch(r"[0-9a-f]{32}",code):
        digest=recovery_digest(code)
        for stored in digests:
            if hmac.compare_digest(stored,digest): return last,[x for x in digests if x!=stored]
    raise PermissionError("Authenticator or recovery code required")

def uri(secret,email):
    return "otpauth://totp/"+quote("ZER0LIFE Academy:"+email,safe="")+"?"+urlencode({"secret":secret,"issuer":"ZER0LIFE Academy","algorithm":"SHA1","digits":6,"period":30})

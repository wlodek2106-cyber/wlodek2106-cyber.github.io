import hashlib
import hmac
import secrets

def hash_password(password):
    if not isinstance(password,str) or not 12 <= len(password) <= 256:
        raise ValueError("Password must contain 12 to 256 characters")
    salt=secrets.token_bytes(16)
    digest=hashlib.scrypt(password.encode(),salt=salt,n=16384,r=8,p=1,dklen=32)
    return salt.hex()+":"+digest.hex()

def verify_password(password,stored):
    try:
        if not isinstance(password,str) or len(password)>256:
            return False
        salt,digest=stored.split(":")
        actual=hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=16384,r=8,p=1,dklen=32)
        return hmac.compare_digest(actual,bytes.fromhex(digest))
    except (ValueError,TypeError,AttributeError):
        return False

def new_session():
    token=secrets.token_urlsafe(32)
    return token,session_digest(token)

def session_digest(token):
    return hashlib.sha256(token.encode()).hexdigest()

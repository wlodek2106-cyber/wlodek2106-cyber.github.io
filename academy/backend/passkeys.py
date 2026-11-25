"""WebAuthn passkeys for the canonical HTTPS Academy origin. No biometric data or passwords stored."""
import json, re, secrets, uuid
from database import transaction
from accounts import authenticate, lock_account, verify_mfa
from security import new_session, session_digest
from webauthn import (generate_registration_options, generate_authentication_options,
                      verify_registration_response, verify_authentication_response,
                      options_to_json)
from webauthn.helpers import base64url_to_bytes
from webauthn.helpers.structs import (AuthenticatorSelectionCriteria, AuthenticatorAttachment,
    ResidentKeyRequirement, UserVerificationRequirement, PublicKeyCredentialDescriptor)
from webauthn.helpers.exceptions import WebAuthnException

RP_ID="zer0life-academy.onrender.com"
ORIGIN="https://"+RP_ID
MAX_KEYS=10

def user_handle(sid):
    return sid.to_bytes(8,"big")

def checked_uuid(value):
    if not isinstance(value,str) or len(value)!=36: raise ValueError("Invalid challenge")
    return str(uuid.UUID(value))

def decode(value,limit=2048):
    if not isinstance(value,str) or not 1<=len(value)<=limit or not re.fullmatch(r"[A-Za-z0-9_-]+",value):
        raise ValueError("Invalid credential")
    return base64url_to_bytes(value)

def credential(body):
    value=body.get("credential")
    if not isinstance(value,dict) or not isinstance(value.get("response"),dict):
        raise ValueError("Invalid credential")
    if value.get("type")!="public-key": raise ValueError("Invalid credential")
    raw=decode(value.get("rawId"))
    if raw!=decode(value.get("id")): raise ValueError("Invalid credential")
    # Reject cross-origin ceremonies explicitly as well as library origin validation.
    client=json.loads(decode(value["response"].get("clientDataJSON"),8192))
    if not isinstance(client,dict) or client.get("crossOrigin") is True:
        raise PermissionError("Cross-origin credential")
    return value,raw

def save_challenge(cur,challenge,purpose,sid=None,digest=None):
    cur.execute("DELETE FROM passkey_challenges WHERE expires_at<=now()")
    if sid is not None:
        cur.execute("DELETE FROM passkey_challenges WHERE student_id=%s AND purpose='register'",(sid,))
    identifier=str(uuid.uuid4())
    cur.execute("""INSERT INTO passkey_challenges(id,challenge,purpose,student_id,session_digest,expires_at)
        VALUES (%s,%s,%s,%s,%s,now()+interval '5 minutes')""",(identifier,challenge,purpose,sid,digest))
    return identifier

def take_challenge(identifier,purpose,sid=None,digest=None):
    # Commit consumption before checking a signature; even a failed attempt cannot replay it.
    identifier=checked_uuid(identifier)
    with transaction() as cur:
        cur.execute("""DELETE FROM passkey_challenges WHERE id=%s AND purpose=%s AND expires_at>now()
          AND student_id IS NOT DISTINCT FROM %s AND session_digest IS NOT DISTINCT FROM %s RETURNING challenge""",
          (identifier,purpose,sid,digest))
        row=cur.fetchone()
    if not row: raise PermissionError("Challenge expired")
    return bytes(row[0])

def status(token):
    sid=authenticate(token)
    if sid is None: raise PermissionError("Sign in required")
    with transaction() as cur:
        cur.execute("SELECT count(*) FROM student_passkeys WHERE student_id=%s",(sid,))
        count=cur.fetchone()[0]
    return {"enabled":count>0,"count":count}

def register_begin(token,body):
    password=body.get("password")
    if not isinstance(password,str) or len(password)>256: raise PermissionError("Invalid credentials")
    with transaction() as cur:
        sid,email=lock_account(cur,token,password)
        verify_mfa(cur,sid,body.get("code"))
        cur.execute("SELECT credential_id FROM student_passkeys WHERE student_id=%s",(sid,))
        keys=cur.fetchall()
        if len(keys)>=MAX_KEYS: raise ValueError("Passkey limit")
        cur.execute("SELECT username FROM students WHERE id=%s",(sid,))
        name=cur.fetchone()[0] or email
        challenge=secrets.token_bytes(32)
        options=generate_registration_options(rp_id=RP_ID,rp_name="ZER0LIFE Academy",
          user_id=user_handle(sid),user_name=name,user_display_name=name,challenge=challenge,timeout=120000,
          authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,
            resident_key=ResidentKeyRequirement.REQUIRED,
            user_verification=UserVerificationRequirement.REQUIRED),
          exclude_credentials=[PublicKeyCredentialDescriptor(id=bytes(k[0])) for k in keys])
        identifier=save_challenge(cur,challenge,"register",sid,session_digest(token))
    return {"id":identifier,"options":json.loads(options_to_json(options))}

def register_finish(token,body):
    sid=authenticate(token)
    if sid is None: raise PermissionError("Sign in required")
    digest=session_digest(token)
    challenge=take_challenge(body.get("id"),"register",sid,digest)
    value,raw=credential(body)
    try:
        verified=verify_registration_response(credential=value,expected_challenge=challenge,
            expected_rp_id=RP_ID,expected_origin=ORIGIN,require_user_verification=True)
    except WebAuthnException as e:
        raise PermissionError("Invalid passkey") from e
    if verified.credential_id!=raw: raise PermissionError("Invalid credential ID")
    with transaction() as cur:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
        if not cur.fetchone(): raise PermissionError("Sign in required")
        cur.execute("SELECT 1 FROM student_sessions WHERE token_digest=%s AND student_id=%s AND revoked_at IS NULL AND expires_at>now()",(digest,sid))
        if not cur.fetchone(): raise PermissionError("Session expired")
        cur.execute("SELECT count(*) FROM student_passkeys WHERE student_id=%s",(sid,))
        if cur.fetchone()[0]>=MAX_KEYS: raise ValueError("Passkey limit")
        cur.execute("""INSERT INTO student_passkeys(credential_id,student_id,public_key,sign_count)
          VALUES (%s,%s,%s,%s) ON CONFLICT(credential_id) DO NOTHING RETURNING student_id""",
          (raw,sid,verified.credential_public_key,verified.sign_count))
        if not cur.fetchone(): raise ValueError("Credential already registered")
    return {"enabled":True}

def login_begin():
    challenge=secrets.token_bytes(32)
    options=generate_authentication_options(rp_id=RP_ID,challenge=challenge,timeout=120000,
        user_verification=UserVerificationRequirement.REQUIRED)
    with transaction() as cur:
        identifier=save_challenge(cur,challenge,"login")
    return {"id":identifier,"options":json.loads(options_to_json(options))}

def login_finish(body):
    challenge=take_challenge(body.get("id"),"login")
    value,raw=credential(body)
    handle=decode(value["response"].get("userHandle"),128)
    with transaction() as cur:
        # Serialize credential use, password changes and revocation by locking student first.
        cur.execute("""SELECT s.id FROM students s JOIN student_passkeys p ON p.student_id=s.id
           WHERE p.credential_id=%s FOR UPDATE OF s""",(raw,))
        row=cur.fetchone()
        if not row or handle!=user_handle(row[0]): raise PermissionError("Invalid credentials")
        sid=row[0]
        cur.execute("SELECT public_key,sign_count FROM student_passkeys WHERE credential_id=%s AND student_id=%s FOR UPDATE",(raw,sid))
        key=cur.fetchone()
        if not key: raise PermissionError("Invalid credentials")
        try:
            verified=verify_authentication_response(credential=value,expected_challenge=challenge,
               expected_origin=ORIGIN,expected_rp_id=RP_ID,credential_public_key=bytes(key[0]),
               credential_current_sign_count=key[1],require_user_verification=True)
        except WebAuthnException as e:
            raise PermissionError("Invalid credentials") from e
        if verified.credential_id!=raw: raise PermissionError("Invalid credentials")
        # Do not silently bypass the account's existing TOTP policy.
        verify_mfa(cur,sid,body.get("code"))
        cur.execute("UPDATE student_passkeys SET sign_count=%s,last_used_at=now() WHERE credential_id=%s",(verified.new_sign_count,raw))
        token,digest=new_session()
        cur.execute("INSERT INTO student_sessions(token_digest,student_id,expires_at) VALUES (%s,%s,now()+interval '12 hours')",(digest,sid))
    return {"token":token}

def disable(token,body):
    password=body.get("password")
    if not isinstance(password,str) or len(password)>256: raise PermissionError("Invalid credentials")
    with transaction() as cur:
        sid,_=lock_account(cur,token,password)
        verify_mfa(cur,sid,body.get("code"))
        cur.execute("DELETE FROM student_passkeys WHERE student_id=%s",(sid,))
        cur.execute("DELETE FROM passkey_challenges WHERE student_id=%s",(sid,))
        cur.execute("UPDATE student_sessions SET revoked_at=now() WHERE student_id=%s AND revoked_at IS NULL",(sid,))
    return {"enabled":False,"sign_in_required":True}

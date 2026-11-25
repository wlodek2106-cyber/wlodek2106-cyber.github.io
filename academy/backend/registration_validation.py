"""Validate public registration inputs without logging credentials or identifying users."""
import re

def validate(body):
    values={}
    for key in ("first_name","last_name"):
        value=body.get(key)
        if not isinstance(value,str):
            return None,key
        value=value.strip()
        if not 1<=len(value)<=100 or not value.isprintable():
            return None,key
        values[key]=value
    email=body.get("email")
    if not isinstance(email,str):
        return None,"email"
    email=email.strip().lower()
    if len(email)>254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",email) or not email.isprintable():
        return None,"email"
    password=body.get("password")
    if not isinstance(password,str) or not 12<=len(password)<=128 or "\x00" in password:
        return None,"password"
    referral=body.get("referral")
    if referral not in (None,"") and (not isinstance(referral,str) or not re.fullmatch(r"[0-9a-f]{24}",referral)):
        return None,"referral"
    values.update(email=email,password=password)
    return values,None

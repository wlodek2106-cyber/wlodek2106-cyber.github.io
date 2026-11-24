import os, json, base64, time, logging
from urllib.request import Request, urlopen
from database import transaction
from certificates import certificate_pdf

def configured():
    return bool(os.getenv("ACADEMY_EMAIL_ENABLED")=="true" and os.getenv("ACADEMY_RESEND_API_KEY") and os.getenv("ACADEMY_EMAIL_FROM"))

def deliver_one():
    if not configured():
        return False
    with transaction() as cur:
        cur.execute("""SELECT o.enrollment_id,c.verification_code,c.issued_at,c.recipient_name,s.email
          FROM certificate_email_outbox o JOIN certificates c USING(enrollment_id)
          JOIN enrollments e ON e.id=o.enrollment_id JOIN students s ON s.id=e.student_id
          WHERE o.sent_at IS NULL AND o.attempts<5 AND c.recipient_name IS NOT NULL
          AND o.created_at>now()-interval '23 hours'
          ORDER BY o.attempts,o.created_at LIMIT 1 FOR UPDATE OF o SKIP LOCKED""")
        row=cur.fetchone()
        if not row:
            return False
        eid,code,issued,name,email=row
        try:
            pdf=certificate_pdf({"recipient_name":name,"code":code,"issued_at":issued.isoformat(),"program":"AI Creator Professional Program"})
            payload={"from":os.environ["ACADEMY_EMAIL_FROM"],"to":[email],"subject":"Your ZER0LIFE Academy certificate","text":"Congratulations on completing the 30-day AI Creator Professional Program! Your certificate is attached. You can also access it in your student dashboard.","attachments":[{"filename":"ZER0LIFE-Certificate.pdf","content":base64.b64encode(pdf).decode("ascii")}]}
            req=Request("https://api.resend.com/emails",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+os.environ["ACADEMY_RESEND_API_KEY"],"Content-Type":"application/json","Idempotency-Key":"academy-certificate-"+code},method="POST")
            with urlopen(req,timeout=20) as response:
                if not json.load(response).get("id"):
                    raise RuntimeError("Missing email acceptance ID")
            cur.execute("UPDATE certificate_email_outbox SET sent_at=now(),attempts=attempts+1 WHERE enrollment_id=%s",(eid,))
        except Exception as exc:
            cur.execute("UPDATE certificate_email_outbox SET attempts=attempts+1 WHERE enrollment_id=%s",(eid,))
            logging.warning("Certificate email attempt failed: %s",type(exc).__name__)
        return True

def run():
    while True:
        try:
            deliver_one()
        except Exception as exc:
            logging.warning("Certificate worker unavailable: %s",type(exc).__name__)
        time.sleep(60)

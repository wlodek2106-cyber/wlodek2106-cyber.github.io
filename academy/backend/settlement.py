import os
from accounts import authenticate
from database import transaction
from solana_verify import verify_usdc
from payment_policy import TREASURY

def settle(token,invoice,signature):
    if os.getenv("ACADEMY_CHECKOUT_READY")!="true" or os.getenv("ACADEMY_PAYMENTS_ENABLED")!="true":
        raise PermissionError("Payments closed")
    student=authenticate(token)
    if student is None:
        raise PermissionError("Authentication required")
    with transaction() as cur:
        cur.execute("SELECT plan,asset,amount_atomic,reference,recipient,created_at,expires_at,signature FROM payment_invoices WHERE id=%s AND student_id=%s",(invoice,student))
        row=cur.fetchone()
    if not row:
        raise ValueError("Invoice not found")
    plan,asset,amount,ref,recipient,created,expiry,previous=row
    if previous:
        if previous==signature:
            return {"paid":True,"plan":plan}
        raise ValueError("Invoice already paid")
    if asset!="USDC" or recipient!=TREASURY or not verify_usdc(signature,amount,ref,created,expiry):
        raise ValueError("Payment not verified")
    with transaction() as cur:
        cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(student,))
        cur.execute("SELECT signature FROM payment_invoices WHERE id=%s AND student_id=%s FOR UPDATE",(invoice,student))
        previous=cur.fetchone()[0]
        if previous==signature:
            return {"paid":True,"plan":plan}
        if previous:
            raise ValueError("Invoice already paid")
        cur.execute("SELECT 1 FROM enrollments WHERE student_id=%s AND paid_at IS NOT NULL",(student,))
        if cur.fetchone():
            raise ValueError("Already enrolled; contact support")
        cur.execute("UPDATE payment_invoices SET signature=%s,paid_at=now() WHERE id=%s",(signature,invoice))
        cur.execute("INSERT INTO enrollments(student_id,plan,paid_at,payment_signature) VALUES (%s,%s,now(),%s) ON CONFLICT(student_id) DO UPDATE SET plan=excluded.plan,paid_at=excluded.paid_at,payment_signature=excluded.payment_signature WHERE enrollments.paid_at IS NULL",(student,plan,signature))
        if cur.rowcount!=1:
            raise ValueError("Enrollment conflict")
    return {"paid":True,"plan":plan}

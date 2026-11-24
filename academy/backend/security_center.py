"""Read-only owner diagnostics. No credentials, personal records or backup download."""
from datetime import datetime,timezone
from database import transaction
from partners import owner
CHECKS={
"paid_enrollment_without_matching_invoice":"""SELECT count(*) FROM enrollments e WHERE e.paid_at IS NOT NULL AND NOT EXISTS
(SELECT 1 FROM payment_invoices i WHERE i.student_id=e.student_id AND i.signature=e.payment_signature AND i.plan=e.plan AND i.paid_at IS NOT NULL)""",
"paid_invoice_without_matching_enrollment":"""SELECT count(*) FROM payment_invoices i WHERE i.paid_at IS NOT NULL AND NOT EXISTS
(SELECT 1 FROM enrollments e WHERE e.student_id=i.student_id AND e.payment_signature=i.signature AND e.plan=i.plan AND e.paid_at IS NOT NULL)""",
"certificate_without_complete_course":"""SELECT count(*) FROM certificates c JOIN enrollments e ON e.id=c.enrollment_id WHERE e.paid_at IS NULL OR
(SELECT count(*) FROM lesson_progress p WHERE p.enrollment_id=e.id AND p.score>=80 AND p.lesson BETWEEN 1 AND CASE WHEN e.plan='vip' THEN 45 ELSE 30 END)
<>CASE WHEN e.plan='vip' THEN 45 ELSE 30 END""",
"paid_partner_without_signature":"SELECT count(*) FROM influencer_payouts WHERE status='paid' AND (payout_signature IS NULL OR paid_at IS NULL)",
"invalid_project_tasks":"SELECT count(*) FROM creative_workflows WHERE jsonb_typeof(tasks)<>'array'",
"invalid_community_parent":"SELECT count(*) FROM community_posts p JOIN community_posts t ON t.id=p.parent_id WHERE t.parent_id IS NOT NULL OR p.category<>t.category",
"approved_service_without_paid_student":"SELECT count(*) FROM marketplace_services m WHERE m.status='approved' AND NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.student_id=m.student_id AND e.paid_at IS NOT NULL)"
}
COUNTS={
"students":"SELECT count(*) FROM students",
"active_sessions":"SELECT count(*) FROM student_sessions WHERE revoked_at IS NULL AND expires_at>now()",
"mfa_enabled":"SELECT count(*) FROM student_mfa WHERE secret IS NOT NULL",
"open_payment_tickets":"SELECT count(*) FROM payment_support WHERE status='open'",
"open_privacy_requests":"SELECT count(*) FROM privacy_requests WHERE status='open'",
"private_english_lessons":"SELECT count(*) FROM private_curriculum WHERE kind='lesson' AND language='en'",
"private_english_exams":"SELECT count(*) FROM private_curriculum WHERE kind='exam' AND language='en'"
}
def inspect(cur):
    checks={};counts={}
    for k,q in CHECKS.items():
        cur.execute(q);checks[k]=cur.fetchone()[0]
    for k,q in COUNTS.items():
        cur.execute(q);counts[k]=cur.fetchone()[0]
    return {"as_of":datetime.now(timezone.utc).isoformat(),"checks":checks,"counts":counts,
      "database_checks_pass":all(v==0 for v in checks.values()),"backup_status":"not_verified","live_payment_tested":False}
def report(token):
    owner(token)
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        return inspect(cur)

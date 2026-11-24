"""User data export and manual privacy requests. No automated erasure."""
from accounts import authenticate,lock_account,verify_mfa
from database import transaction
from partners import owner
from datetime import datetime,timezone
KINDS=("access","correction","erasure","restriction","objection","portability")
# Explicit projections: never export credentials, session tokens, answer keys, other students' records or internal administrator data.
DATASETS={
"account":"SELECT id,email,first_name,last_name,created_at,hire_source FROM students WHERE id=%s",
"sessions":"SELECT created_at,expires_at,revoked_at FROM student_sessions WHERE student_id=%s ORDER BY created_at DESC",
"security":"SELECT secret IS NOT NULL AS mfa_enabled,cardinality(recovery_digests) AS recovery_remaining FROM student_mfa WHERE student_id=%s",
"enrollment":"SELECT plan,paid_at,payment_signature FROM enrollments WHERE student_id=%s",
"progress":"SELECT p.lesson,p.passed_at,p.score FROM lesson_progress p JOIN enrollments e ON e.id=p.enrollment_id WHERE e.student_id=%s ORDER BY p.lesson",
"exam_attempts":"SELECT p.lesson,p.score,p.attempted_at FROM quiz_attempts p JOIN enrollments e ON e.id=p.enrollment_id WHERE e.student_id=%s ORDER BY p.id DESC",
"projects":"SELECT p.id,p.lesson,p.submission,p.submitted_at,p.score,p.feedback FROM project_submissions p JOIN enrollments e ON e.id=p.enrollment_id WHERE e.student_id=%s ORDER BY p.id DESC",
"certificates":"SELECT c.verification_code,c.issued_at,c.recipient_name FROM certificates c JOIN enrollments e ON e.id=c.enrollment_id WHERE e.student_id=%s",
"invoices":"SELECT id,plan,asset,amount_atomic,reference,recipient,created_at,expires_at,signature,paid_at FROM payment_invoices WHERE student_id=%s ORDER BY created_at DESC",
"payment_support":"SELECT t.id,t.invoice_id,t.signature,t.status,t.note,t.verification,t.created_at,t.checked_at,t.closed_at FROM payment_support t JOIN payment_invoices i ON i.id=t.invoice_id WHERE i.student_id=%s ORDER BY t.id DESC",
"tutor_history":"SELECT id,lesson,mode,language,question,answer,created_at FROM tutor_history WHERE student_id=%s ORDER BY id DESC",
"review":"SELECT rating,body,updated_at,hidden_at FROM student_reviews WHERE student_id=%s",
"referral_code":"SELECT code FROM referral_codes WHERE student_id=%s",
"partner":"SELECT profile_url,wallet,status,created_at,approved_at FROM influencer_partners WHERE student_id=%s",
"partner_payouts":"SELECT id,amount_atomic,wallet,status,created_at,reviewed_at,payout_signature,paid_at FROM influencer_payouts WHERE partner_id=%s ORDER BY id DESC",
"community":"SELECT id,parent_id,alias,category,title,body,status,created_at,reviewed_at FROM community_posts WHERE student_id=%s ORDER BY id",
"marketplace":"SELECT id,name,title,category,description,price,link,status,revision,updated_at,reviewed_at FROM marketplace_services WHERE student_id=%s",
"job_posts":"SELECT id,title,category,brief,budget_cents,contact,status,created_at,updated_at FROM academy_jobs WHERE client_id=%s ORDER BY id",
"job_applications":"SELECT id,job_id,alias,proposal,quote_cents,contact,created_at FROM academy_job_applications WHERE student_id=%s ORDER BY id",
"career_profile":"SELECT profile,updated_at FROM career_profiles WHERE student_id=%s",
"clients":"SELECT id,name,contact,notes FROM business_clients WHERE student_id=%s ORDER BY id",
"orders":"SELECT id,client_id,title,status,due,agreed_cents,received_cents,expense_cents,notes FROM business_orders WHERE student_id=%s ORDER BY id",
"tasks":"SELECT id,title,day,category,priority,minutes,done FROM student_tasks WHERE student_id=%s ORDER BY id",
"marketing_campaigns":"SELECT id,title,goal,audience FROM marketing_campaigns WHERE student_id=%s ORDER BY id",
"marketing_posts":"SELECT id,campaign_id,day,platform,status,title,caption,hashtags,asset_notes FROM marketing_posts WHERE student_id=%s ORDER BY id",
"storyboard_projects":"SELECT id,title,story,style,characters,format,updated_at FROM storyboard_projects WHERE student_id=%s ORDER BY id",
"storyboard_scenes":"SELECT s.id,s.project_id,s.position,s.seconds,s.title,s.action,s.camera,s.audio,s.continuity FROM storyboard_scenes s JOIN storyboard_projects p ON p.id=s.project_id WHERE p.student_id=%s ORDER BY s.project_id,s.position,s.id",
"creative_workflows":"SELECT id,title,kind,brief,completed,notes,updated_at,due,tasks,materials FROM creative_workflows WHERE student_id=%s ORDER BY id",
"student_prompts":"SELECT id,title,prompt,category,favorite,updated_at FROM student_prompts WHERE student_id=%s ORDER BY id",
"knowledge_notes":"SELECT id,title,content,tag,updated_at,folder,favorite FROM knowledge_notes WHERE student_id=%s ORDER BY id",
"privacy_requests":"SELECT id,kind,details,status,response,created_at,closed_at FROM privacy_requests WHERE student_id=%s ORDER BY id DESC"
}
def export_data(cur,sid):
    result={};truncated=[]
    # Bound each section; explicitly mark truncation and offer a manual access request.
    for key,query in DATASETS.items():
        cur.execute("SELECT to_jsonb(x) FROM ("+query+" LIMIT 2001) x",(sid,))
        rows=[r[0] for r in cur.fetchall()]
        if len(rows)>2000: truncated.append(key)
        result[key]=rows[:2000]
    return {"format_version":1,"generated_at":datetime.now(timezone.utc).isoformat(),"datasets":result,"truncated_sections":truncated,
            "scope":"Self-service export of selected records; not a complete legal access response. Credentials, exam keys, other users' data and internal records omitted."}
def export(token,password,code=None):
    with transaction() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        sid,_=lock_account(cur,token,password)
        verify_mfa(cur,sid,code)
        return export_data(cur,sid)
def create_record(cur,sid,kind,details):
    if kind not in KINDS: raise ValueError("Invalid request type")
    if not isinstance(details,str) or len(details)>2000 or "\x00" in details: raise ValueError("Invalid details")
    cur.execute("SELECT id FROM students WHERE id=%s FOR UPDATE",(sid,))
    cur.execute("SELECT id FROM privacy_requests WHERE student_id=%s AND kind=%s AND status='open'",(sid,kind))
    row=cur.fetchone()
    if row: return {"id":row[0],"status":"open","existing":True}
    cur.execute("INSERT INTO privacy_requests(student_id,kind,details) VALUES (%s,%s,%s) RETURNING id",(sid,kind,details.strip()))
    return {"id":cur.fetchone()[0],"status":"open","existing":False}
def create(token,password,code,kind,details):
    with transaction() as cur:
        sid,_=lock_account(cur,token,password)
        verify_mfa(cur,sid,code)
        return create_record(cur,sid,kind,details)
def list_records(cur,sid,after=0):
    if type(after) is not int or not 0<=after<=9223372036854775807: raise ValueError("Invalid cursor")
    cur.execute("""SELECT id,student_id,kind,details,status,response,created_at,closed_at FROM privacy_requests
       WHERE (%s::bigint IS NULL OR student_id=%s) AND id>%s ORDER BY id LIMIT 51""",(sid,sid,after))
    rows=cur.fetchall()
    items=[{"id":i,"student_id":s,"kind":k,"details":d,"status":st,"response":r,"created_at":c.isoformat(),"closed_at":t.isoformat() if t else None}
        for i,s,k,d,st,r,c,t in rows[:50]]
    return {"items":items,"next_after":items[-1]["id"] if len(rows)>50 else None}
def list_user(token,after):
    sid=authenticate(token)
    if sid is None: raise PermissionError("Authentication required")
    with transaction() as cur: return list_records(cur,sid,after)
def list_admin(token,after):
    owner(token)
    with transaction() as cur: return list_records(cur,None,after)
def close_record(cur,admin,request,response):
    if type(request) is not int or not 1<=request<=9223372036854775807: raise ValueError("Invalid request")
    if not isinstance(response,str) or not 10<=len(response.strip())<=2000 or "\x00" in response: raise ValueError("Resolution required")
    cur.execute("UPDATE privacy_requests SET status='closed',response=%s,closed_at=now(),closed_by=%s WHERE id=%s AND status='open' RETURNING id",(response.strip(),admin,request))
    if not cur.fetchone(): raise ValueError("Open request unavailable")
    return {"closed":True}
def close(token,request,response):
    admin=owner(token)
    with transaction() as cur: return close_record(cur,admin,request,response)

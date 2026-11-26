CREATE TABLE IF NOT EXISTS student_sessions (
 token_digest char(64) PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 created_at timestamptz NOT NULL DEFAULT now(),
 expires_at timestamptz NOT NULL,
 revoked_at timestamptz,
 CHECK(expires_at > created_at)
);
CREATE INDEX IF NOT EXISTS student_sessions_student_idx ON student_sessions(student_id);
CREATE TABLE IF NOT EXISTS assessment_sessions (
 id uuid PRIMARY KEY,
 enrollment_id bigint NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
 lesson integer NOT NULL CHECK(lesson BETWEEN 1 AND 30),
 answer_key jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 expires_at timestamptz NOT NULL,
 consumed_at timestamptz,
 CHECK(expires_at > created_at)
);
CREATE INDEX IF NOT EXISTS assessment_enrollment_idx ON assessment_sessions(enrollment_id,lesson);
CREATE TABLE IF NOT EXISTS project_submissions (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 enrollment_id bigint NOT NULL REFERENCES enrollments(id),
 lesson integer NOT NULL CHECK(lesson BETWEEN 1 AND 30),
 submission text NOT NULL,
 submitted_at timestamptz NOT NULL DEFAULT now(),
 score integer CHECK(score BETWEEN 0 AND 100),
 feedback text
);

CREATE TABLE IF NOT EXISTS certificates (
 enrollment_id bigint PRIMARY KEY REFERENCES enrollments(id),
 verification_code text UNIQUE NOT NULL,
 issued_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS payment_invoices (
 id uuid PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id),
 plan text NOT NULL CHECK(plan IN ('starter','pro','vip','elite')),
 asset text NOT NULL CHECK(asset IN ('USDC','SOL')),
 amount_atomic bigint NOT NULL CHECK(amount_atomic>0),
 reference text UNIQUE NOT NULL,
 recipient text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 expires_at timestamptz NOT NULL,
 signature text UNIQUE,
 paid_at timestamptz,
 CHECK(expires_at>created_at),
 CHECK((signature IS NULL)=(paid_at IS NULL))
);
CREATE INDEX IF NOT EXISTS payment_invoices_student_idx ON payment_invoices(student_id);

ALTER TABLE students ADD COLUMN IF NOT EXISTS first_name text;
ALTER TABLE students ADD COLUMN IF NOT EXISTS last_name text;
ALTER TABLE certificates ADD COLUMN IF NOT EXISTS recipient_name text;
CREATE TABLE IF NOT EXISTS certificate_email_outbox (enrollment_id bigint PRIMARY KEY REFERENCES certificates(enrollment_id), created_at timestamptz NOT NULL DEFAULT now(), sent_at timestamptz, attempts integer NOT NULL DEFAULT 0);

CREATE TABLE IF NOT EXISTS tutor_history (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 lesson integer NOT NULL CHECK(lesson BETWEEN 1 AND 30),
 mode text NOT NULL CHECK(mode IN ('review','practice')),
 language text NOT NULL CHECK(language IN ('en','ru','uk','pl')),
 question text NOT NULL CHECK(length(question)<=2000),
 answer text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS tutor_history_student_idx ON tutor_history(student_id,id DESC);

ALTER TABLE assessment_sessions DROP CONSTRAINT IF EXISTS assessment_sessions_lesson_check;
ALTER TABLE assessment_sessions ADD CONSTRAINT assessment_sessions_lesson_check CHECK(lesson BETWEEN 1 AND 45);

ALTER TABLE project_submissions DROP CONSTRAINT IF EXISTS project_submissions_lesson_check;
ALTER TABLE project_submissions ADD CONSTRAINT project_submissions_lesson_check CHECK(lesson BETWEEN 1 AND 45);

ALTER TABLE tutor_history DROP CONSTRAINT IF EXISTS tutor_history_lesson_check;
ALTER TABLE tutor_history ADD CONSTRAINT tutor_history_lesson_check CHECK(lesson BETWEEN 1 AND 45);

CREATE TABLE IF NOT EXISTS student_reviews (
 student_id bigint PRIMARY KEY REFERENCES students(id) ON DELETE CASCADE,
 rating integer NOT NULL CHECK(rating BETWEEN 1 AND 5),
 body text NOT NULL CHECK(length(body) BETWEEN 10 AND 1200),
 updated_at timestamptz NOT NULL DEFAULT now(),
 hidden_at timestamptz
);
CREATE INDEX IF NOT EXISTS student_reviews_date_idx ON student_reviews(updated_at DESC);

CREATE TABLE IF NOT EXISTS referral_codes (
 student_id bigint PRIMARY KEY REFERENCES students(id) ON DELETE CASCADE,
 code text UNIQUE NOT NULL CHECK(code ~ '^[0-9a-f]{24}$')
);
CREATE TABLE IF NOT EXISTS referrals (
 student_id bigint PRIMARY KEY REFERENCES students(id) ON DELETE CASCADE,
 referrer_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK(student_id<>referrer_id)
);
CREATE INDEX IF NOT EXISTS referrals_referrer_idx ON referrals(referrer_id);

CREATE TABLE IF NOT EXISTS influencer_partners (
 student_id bigint PRIMARY KEY REFERENCES students(id),
 profile_url text NOT NULL, wallet text NOT NULL,
 status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
 created_at timestamptz NOT NULL DEFAULT now(),
 approved_at timestamptz, reviewed_by bigint REFERENCES students(id)
);
CREATE TABLE IF NOT EXISTS influencer_payouts (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 invoice_id uuid NOT NULL UNIQUE REFERENCES payment_invoices(id),
 partner_id bigint NOT NULL REFERENCES influencer_partners(student_id),
 amount_atomic bigint NOT NULL CHECK(amount_atomic>0),
 wallet text NOT NULL,
 status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected','paid')),
 created_at timestamptz NOT NULL DEFAULT now(),
 reviewed_by bigint REFERENCES students(id), reviewed_at timestamptz,
 payout_signature text UNIQUE, paid_at timestamptz, paid_by bigint REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS influencer_audit (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 kind text NOT NULL CHECK(kind IN ('application','payout')),
 target_id bigint NOT NULL,
 action text NOT NULL CHECK(action IN ('approve','reject','mark_paid')),
 admin_id bigint NOT NULL REFERENCES students(id),
 created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS student_mfa (
 student_id bigint PRIMARY KEY REFERENCES students(id) ON DELETE CASCADE,
 secret text, last_counter bigint NOT NULL DEFAULT -1,
 recovery_digests text[] NOT NULL DEFAULT '{}',
 pending_secret text, pending_until timestamptz
);

CREATE TABLE IF NOT EXISTS private_curriculum (
 kind text NOT NULL CHECK(kind IN ('lesson','exam')),
 lesson integer NOT NULL CHECK(lesson BETWEEN 1 AND 45),
 language text NOT NULL CHECK(language IN ('en','ru','uk','pl')),
 content jsonb NOT NULL,
 revision integer NOT NULL DEFAULT 1,
 updated_by bigint NOT NULL REFERENCES students(id),
 updated_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(kind,lesson,language)
);
CREATE TABLE IF NOT EXISTS private_curriculum_audit (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 kind text NOT NULL,
 lesson integer NOT NULL,
 language text NOT NULL,
 revision integer NOT NULL,
 updated_by bigint NOT NULL REFERENCES students(id),
 updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS career_profiles (
 student_id bigint PRIMARY KEY REFERENCES students(id) ON DELETE CASCADE,
 profile jsonb NOT NULL,
 updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS business_clients (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 name text NOT NULL, contact text NOT NULL DEFAULT '', notes text NOT NULL DEFAULT '',
 UNIQUE(student_id,id)
);
CREATE TABLE IF NOT EXISTS business_orders (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 client_id bigint NOT NULL,
 title text NOT NULL,
 status text NOT NULL CHECK(status IN ('lead','in_progress','delivered','cancelled')),
 due date,
 agreed_cents bigint NOT NULL CHECK(agreed_cents>=0),
 received_cents bigint NOT NULL CHECK(received_cents>=0 AND received_cents<=agreed_cents),
 expense_cents bigint NOT NULL CHECK(expense_cents>=0),
 notes text NOT NULL DEFAULT '',
 FOREIGN KEY(student_id,client_id) REFERENCES business_clients(student_id,id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS business_orders_student_client ON business_orders(student_id,client_id);

CREATE TABLE IF NOT EXISTS student_tasks (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 title text NOT NULL,
 day date NOT NULL,
 category text NOT NULL CHECK(category IN ('study','client','personal')),
 priority integer NOT NULL CHECK(priority BETWEEN 1 AND 3),
 minutes integer NOT NULL CHECK(minutes BETWEEN 0 AND 1440),
 done boolean NOT NULL DEFAULT false
);
CREATE INDEX IF NOT EXISTS student_tasks_student_day ON student_tasks(student_id,day);

CREATE TABLE IF NOT EXISTS payment_support (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 invoice_id uuid NOT NULL REFERENCES payment_invoices(id),
 signature text NOT NULL,
 status text NOT NULL DEFAULT 'open' CHECK(status IN ('open','closed')),
 note text NOT NULL DEFAULT '',
 verification text NOT NULL DEFAULT 'unchecked' CHECK(verification IN ('unchecked','matched','not_matched')),
 created_at timestamptz NOT NULL DEFAULT now(),
 checked_at timestamptz, checked_by bigint REFERENCES students(id),
 closed_at timestamptz, closed_by bigint REFERENCES students(id),
 UNIQUE(invoice_id,signature)
);
CREATE INDEX IF NOT EXISTS payment_support_invoice ON payment_support(invoice_id);

CREATE TABLE IF NOT EXISTS privacy_requests (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id),
 kind text NOT NULL CHECK(kind IN ('access','correction','erasure','restriction','objection','portability')),
 details text NOT NULL DEFAULT '',
 status text NOT NULL DEFAULT 'open' CHECK(status IN ('open','closed')),
 response text NOT NULL DEFAULT '',
 created_at timestamptz NOT NULL DEFAULT now(),
 closed_at timestamptz,
 closed_by bigint REFERENCES students(id)
);
CREATE UNIQUE INDEX IF NOT EXISTS privacy_requests_open_unique ON privacy_requests(student_id,kind) WHERE status='open';

CREATE TABLE IF NOT EXISTS knowledge_notes (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 title text NOT NULL CHECK(length(title) BETWEEN 1 AND 160),
 content text NOT NULL CHECK(length(content) BETWEEN 1 AND 3000),
 tag text NOT NULL DEFAULT '' CHECK(length(tag)<=80),
 updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE knowledge_notes ADD COLUMN IF NOT EXISTS folder text NOT NULL DEFAULT '' CHECK(length(folder)<=80);
ALTER TABLE knowledge_notes ADD COLUMN IF NOT EXISTS favorite boolean NOT NULL DEFAULT false;
CREATE INDEX IF NOT EXISTS knowledge_notes_student ON knowledge_notes(student_id,id);

CREATE TABLE IF NOT EXISTS student_prompts (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 title text NOT NULL CHECK(length(title) BETWEEN 1 AND 160),
 prompt text NOT NULL CHECK(length(prompt) BETWEEN 1 AND 3000),
 category text NOT NULL CHECK(category IN ('image','video','advertising','animation','audio','agent','other')),
 favorite boolean NOT NULL DEFAULT false,
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS student_prompts_student ON student_prompts(student_id,id);

CREATE TABLE IF NOT EXISTS creative_workflows (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 title text NOT NULL CHECK(length(title) BETWEEN 1 AND 160),
 kind text NOT NULL CHECK(kind IN ('image','video','advertising','animation','audio')),
 brief text NOT NULL CHECK(length(brief) BETWEEN 1 AND 2000),
 completed text[] NOT NULL DEFAULT '{}',
 notes text NOT NULL DEFAULT '' CHECK(length(notes)<=1000),
 updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE creative_workflows ADD COLUMN IF NOT EXISTS due date;
ALTER TABLE creative_workflows ADD COLUMN IF NOT EXISTS tasks jsonb NOT NULL DEFAULT '[]'::jsonb;
ALTER TABLE creative_workflows ADD COLUMN IF NOT EXISTS materials text NOT NULL DEFAULT '';
ALTER TABLE creative_workflows DROP CONSTRAINT IF EXISTS creative_workflows_kind_check;
ALTER TABLE creative_workflows ADD CONSTRAINT creative_workflows_kind_check CHECK(kind IN ('image','video','advertising','animation','audio','product'));
CREATE INDEX IF NOT EXISTS creative_workflows_student ON creative_workflows(student_id,id);

CREATE TABLE IF NOT EXISTS storyboard_projects (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 title text NOT NULL, story text NOT NULL, style text NOT NULL, characters text NOT NULL,
 format text NOT NULL CHECK(format IN ('16:9','9:16','1:1','4:3')),
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS storyboard_projects_student ON storyboard_projects(student_id,id);
CREATE TABLE IF NOT EXISTS storyboard_scenes (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 project_id bigint NOT NULL REFERENCES storyboard_projects(id) ON DELETE CASCADE,
 position integer NOT NULL CHECK(position BETWEEN 1 AND 999),
 seconds integer NOT NULL CHECK(seconds BETWEEN 1 AND 120),
 title text NOT NULL, action text NOT NULL, camera text NOT NULL, audio text NOT NULL, continuity text NOT NULL
);
CREATE INDEX IF NOT EXISTS storyboard_scenes_project ON storyboard_scenes(project_id,position,id);

CREATE TABLE IF NOT EXISTS marketing_campaigns (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 title text NOT NULL, goal text NOT NULL, audience text NOT NULL,
 UNIQUE(id,student_id)
);
CREATE TABLE IF NOT EXISTS marketing_posts (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 campaign_id bigint NOT NULL,
 day date NOT NULL, platform text NOT NULL CHECK(platform IN ('instagram','tiktok','youtube','x','other')),
 status text NOT NULL CHECK(status IN ('draft','ready','published','cancelled')),
 title text NOT NULL, caption text NOT NULL, hashtags text NOT NULL, asset_notes text NOT NULL,
 FOREIGN KEY(campaign_id,student_id) REFERENCES marketing_campaigns(id,student_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS marketing_posts_student_day ON marketing_posts(student_id,day,id);

CREATE TABLE IF NOT EXISTS marketplace_services (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL UNIQUE REFERENCES students(id) ON DELETE CASCADE,
 name text NOT NULL,title text NOT NULL,category text NOT NULL CHECK(category IN ('design','video','audio','web','automation','marketing','other')),
 description text NOT NULL,price text NOT NULL DEFAULT '',link text NOT NULL,
 status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected','withdrawn','blocked')),
 revision bigint NOT NULL DEFAULT 1,updated_at timestamptz NOT NULL DEFAULT now(),
 reviewed_by bigint REFERENCES students(id) ON DELETE SET NULL,reviewed_at timestamptz
);
CREATE INDEX IF NOT EXISTS marketplace_services_status ON marketplace_services(status,id);

CREATE TABLE IF NOT EXISTS community_posts (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 parent_id bigint REFERENCES community_posts(id) ON DELETE CASCADE,
 alias text NOT NULL CHECK(length(alias) BETWEEN 1 AND 60),
 category text NOT NULL CHECK(category IN ('question','project','collaboration','experience')),
 title text NOT NULL CHECK(length(title)<=140),body text NOT NULL CHECK(length(body) BETWEEN 1 AND 1600),
 status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected','withdrawn','hidden')),
 created_at timestamptz NOT NULL DEFAULT now(),
 reviewed_by bigint REFERENCES students(id) ON DELETE SET NULL,reviewed_at timestamptz
);
CREATE INDEX IF NOT EXISTS community_posts_student ON community_posts(student_id,created_at);
CREATE INDEX IF NOT EXISTS community_posts_feed ON community_posts(parent_id,status,id);

CREATE TABLE IF NOT EXISTS academy_jobs (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 client_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 title text NOT NULL CHECK(length(title) BETWEEN 1 AND 120),
 category text NOT NULL CHECK(category IN ('design','video','audio','web','automation','marketing','other')),
 brief text NOT NULL CHECK(length(brief) BETWEEN 1 AND 3000),
 budget_cents bigint NOT NULL CHECK(budget_cents BETWEEN 1 AND 100000000),
 contact text NOT NULL CHECK(length(contact) BETWEEN 1 AND 200),
 status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','open','rejected','assigned','delivered','completed','cancelled')),
 selected_application bigint,
 reviewed_by bigint REFERENCES students(id) ON DELETE SET NULL,
 created_at timestamptz NOT NULL DEFAULT now(),updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS academy_jobs_status ON academy_jobs(status,id);
CREATE INDEX IF NOT EXISTS academy_jobs_client ON academy_jobs(client_id,id);
CREATE TABLE IF NOT EXISTS academy_job_applications (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 job_id bigint NOT NULL REFERENCES academy_jobs(id) ON DELETE CASCADE,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 alias text NOT NULL CHECK(length(alias) BETWEEN 1 AND 80),
 proposal text NOT NULL CHECK(length(proposal) BETWEEN 1 AND 2000),
 quote_cents bigint NOT NULL CHECK(quote_cents BETWEEN 1 AND 100000000),
 contact text NOT NULL CHECK(length(contact) BETWEEN 1 AND 200),
 created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(job_id,student_id),UNIQUE(job_id,id)
);
CREATE INDEX IF NOT EXISTS academy_job_applications_student ON academy_job_applications(student_id,id);

ALTER TABLE students ADD COLUMN IF NOT EXISTS hire_source text CHECK(hire_source IN ('direct','telegram','instagram','youtube','linkedin','facebook','tiktok','x','partner','other'));

ALTER TABLE academy_job_applications ADD COLUMN IF NOT EXISTS share_reputation boolean NOT NULL DEFAULT false;
CREATE TABLE IF NOT EXISTS academy_job_reviews (
 job_id bigint PRIMARY KEY REFERENCES academy_jobs(id) ON DELETE CASCADE,
 rating smallint NOT NULL CHECK(rating BETWEEN 1 AND 5),
 comment text NOT NULL DEFAULT '' CHECK(length(comment)<=1000),
 status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected','hidden')),
 created_at timestamptz NOT NULL DEFAULT now(),
 reviewed_by bigint REFERENCES students(id) ON DELETE SET NULL,
 reviewed_at timestamptz
);

CREATE TABLE IF NOT EXISTS academy_job_messages (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 job_id bigint NOT NULL REFERENCES academy_jobs(id) ON DELETE CASCADE,
 role text NOT NULL CHECK(role IN ('client','freelancer')),
 kind text NOT NULL CHECK(kind IN ('message','deliver','revise')),
 body text NOT NULL CHECK(length(body) BETWEEN 1 AND 1600),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS academy_job_messages_job ON academy_job_messages(job_id,id);
CREATE TABLE IF NOT EXISTS academy_job_milestones (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 job_id bigint NOT NULL REFERENCES academy_jobs(id) ON DELETE CASCADE,
 title text NOT NULL CHECK(length(title) BETWEEN 1 AND 160),
 done boolean NOT NULL DEFAULT false
);
CREATE INDEX IF NOT EXISTS academy_job_milestones_job ON academy_job_milestones(job_id,id);

CREATE TABLE IF NOT EXISTS academy_notifications (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 job_id bigint NOT NULL REFERENCES academy_jobs(id) ON DELETE CASCADE,
 kind text NOT NULL CHECK(kind IN ('job_open','job_rejected','job_cancelled','application','selected','message','delivered','revision','completed','review_approved')),
 target text NOT NULL CHECK(target IN ('mine','applications','room')),
 created_at timestamptz NOT NULL DEFAULT now(),
 read_at timestamptz
);
CREATE INDEX IF NOT EXISTS academy_notifications_student ON academy_notifications(student_id,id DESC);
CREATE INDEX IF NOT EXISTS academy_notifications_unread ON academy_notifications(student_id,created_at) WHERE read_at IS NULL;

ALTER TABLE business_orders ADD COLUMN IF NOT EXISTS source_job_id bigint REFERENCES academy_jobs(id) ON DELETE SET NULL;
CREATE UNIQUE INDEX IF NOT EXISTS business_orders_source_job ON business_orders(student_id,source_job_id) WHERE source_job_id IS NOT NULL;

ALTER TABLE academy_jobs ADD COLUMN IF NOT EXISTS payment_mode text NOT NULL DEFAULT 'external' CHECK(payment_mode IN ('external','split'));
CREATE TABLE IF NOT EXISTS academy_job_payment_wallets (
 job_id bigint PRIMARY KEY REFERENCES academy_jobs(id) ON DELETE CASCADE,
 recipient text NOT NULL
);
CREATE TABLE IF NOT EXISTS academy_job_payments (
 job_id bigint PRIMARY KEY REFERENCES academy_jobs(id),
 client_id bigint NOT NULL REFERENCES students(id),
 freelancer_id bigint NOT NULL REFERENCES students(id),
 payer text NOT NULL, recipient text NOT NULL, treasury text NOT NULL,
 reference text NOT NULL UNIQUE, quote_cents bigint NOT NULL CHECK(quote_cents BETWEEN 1 AND 100000000),
 created_at timestamptz NOT NULL DEFAULT now(), signature text UNIQUE, paid_at timestamptz,
 CHECK((signature IS NULL)=(paid_at IS NULL)),CHECK(client_id<>freelancer_id),CHECK(payer<>recipient AND payer<>treasury AND recipient<>treasury)
);

ALTER TABLE academy_job_payments ADD COLUMN IF NOT EXISTS issued_at timestamptz;

-- Separate course campaign attribution from client hiring intent; no backfill guesses.
ALTER TABLE students ADD COLUMN IF NOT EXISTS campaign_source text CHECK(campaign_source IN ('direct','telegram','instagram','youtube','linkedin','facebook','tiktok','x','partner','other'));

ALTER TABLE students ADD COLUMN IF NOT EXISTS username text;
UPDATE students SET username=CASE WHEN id=24 THEN 'zer0life'
 ELSE COALESCE(NULLIF(trim(both '-' from left(lower(regexp_replace(concat_ws('-',first_name,last_name),'[^A-Za-z0-9]+','-','g')),28)),''),'member')||'-'||id::text END WHERE username IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS students_username_unique ON students(username);

-- WebAuthn: only public keys, counters and short-lived one-time challenges.
CREATE TABLE IF NOT EXISTS student_passkeys (
 credential_id bytea PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE,
 public_key bytea NOT NULL,
 sign_count bigint NOT NULL CHECK(sign_count>=0),
 created_at timestamptz NOT NULL DEFAULT now(),
 last_used_at timestamptz
);
CREATE INDEX IF NOT EXISTS student_passkeys_student_idx ON student_passkeys(student_id);
CREATE TABLE IF NOT EXISTS passkey_challenges (
 id uuid PRIMARY KEY,
 challenge bytea NOT NULL,
 purpose text NOT NULL CHECK(purpose IN ('register','login')),
 student_id bigint REFERENCES students(id) ON DELETE CASCADE,
 session_digest char(64),
 expires_at timestamptz NOT NULL,
 CHECK((purpose='register' AND student_id IS NOT NULL AND session_digest IS NOT NULL)
    OR (purpose='login' AND student_id IS NULL AND session_digest IS NULL))
);
CREATE INDEX IF NOT EXISTS passkey_challenges_expiry_idx ON passkey_challenges(expires_at);

ALTER TABLE payment_invoices DROP CONSTRAINT IF EXISTS payment_invoices_plan_check;
ALTER TABLE payment_invoices ADD CONSTRAINT payment_invoices_plan_check CHECK(plan IN ('starter','pro','vip','elite'));
CREATE TABLE IF NOT EXISTS elite_projects (student_id bigint NOT NULL REFERENCES students(id) ON DELETE CASCADE, project text NOT NULL CHECK(project IN ('humans','film','agents','teacher','business')), evidence text NOT NULL CHECK(char_length(evidence) BETWEEN 30 AND 4000), updated_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(student_id,project));

-- ELITE review workflow: existing submissions are pending, not automatically approved.
ALTER TABLE elite_projects ADD COLUMN IF NOT EXISTS revision integer NOT NULL DEFAULT 1;
ALTER TABLE elite_projects ADD COLUMN IF NOT EXISTS review_status text NOT NULL DEFAULT 'pending' CHECK(review_status IN ('pending','revision','approved'));
ALTER TABLE elite_projects ADD COLUMN IF NOT EXISTS review_score integer CHECK(review_score BETWEEN 0 AND 100);
ALTER TABLE elite_projects ADD COLUMN IF NOT EXISTS review_feedback text CHECK(char_length(review_feedback)<=4000);
ALTER TABLE elite_projects ADD COLUMN IF NOT EXISTS reviewed_at timestamptz;
CREATE INDEX IF NOT EXISTS elite_review_queue ON elite_projects(review_status,updated_at,student_id,project);

-- Separate advanced credential; existing core certificates and codes are unchanged.
CREATE TABLE IF NOT EXISTS elite_certificates (
 enrollment_id bigint PRIMARY KEY REFERENCES enrollments(id) ON DELETE CASCADE,
 verification_code text NOT NULL UNIQUE,
 issued_at timestamptz NOT NULL DEFAULT now(),
 recipient_name text NOT NULL,
 average_score numeric(5,2) NOT NULL CHECK(average_score BETWEEN 80 AND 100)
);

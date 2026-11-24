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
 plan text NOT NULL CHECK(plan IN ('starter','pro','vip')),
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

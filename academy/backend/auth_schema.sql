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

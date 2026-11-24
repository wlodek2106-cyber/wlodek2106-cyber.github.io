CREATE TABLE IF NOT EXISTS students (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 email text NOT NULL UNIQUE,
 password_hash text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS enrollments (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id bigint NOT NULL REFERENCES students(id),
 plan text NOT NULL CHECK(plan IN ('starter','pro','vip')),
 paid_at timestamptz,
 payment_signature text UNIQUE,
 UNIQUE(student_id)
);
CREATE TABLE IF NOT EXISTS quiz_attempts (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 enrollment_id bigint NOT NULL REFERENCES enrollments(id),
 lesson integer NOT NULL CHECK(lesson BETWEEN 1 AND 30),
 score integer NOT NULL CHECK(score BETWEEN 0 AND 100),
 attempted_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS lesson_progress (
 enrollment_id bigint NOT NULL REFERENCES enrollments(id),
 lesson integer NOT NULL CHECK(lesson BETWEEN 1 AND 30),
 passed_at timestamptz NOT NULL DEFAULT now(),
 score integer NOT NULL CHECK(score BETWEEN 80 AND 100),
 PRIMARY KEY(enrollment_id,lesson)
);
CREATE OR REPLACE VIEW academy_next_unlock AS
SELECT e.id AS enrollment_id, COALESCE(p.completed,0) AS completed,
 CASE WHEN e.paid_at IS NULL OR COALESCE(p.completed,0)=30 THEN NULL
 ELSE GREATEST(e.paid_at + COALESCE(p.completed,0)*interval '1 day', COALESCE(p.last_pass + interval '1 day',e.paid_at)) END AS unlock_at
FROM enrollments e LEFT JOIN (
 SELECT enrollment_id,count(*) AS completed,max(passed_at) AS last_pass FROM lesson_progress GROUP BY enrollment_id
) p ON p.enrollment_id=e.id;
-- Only authenticated server code may write progress after checking eligibility and grading against private answer keys.

ALTER TABLE quiz_attempts DROP CONSTRAINT IF EXISTS quiz_attempts_lesson_check;
ALTER TABLE quiz_attempts ADD CONSTRAINT quiz_attempts_lesson_check CHECK(lesson BETWEEN 1 AND 40);
ALTER TABLE lesson_progress DROP CONSTRAINT IF EXISTS lesson_progress_lesson_check;
ALTER TABLE lesson_progress ADD CONSTRAINT lesson_progress_lesson_check CHECK(lesson BETWEEN 1 AND 40);

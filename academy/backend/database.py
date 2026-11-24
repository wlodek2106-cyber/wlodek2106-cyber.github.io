import os
from contextlib import contextmanager
import psycopg

@contextmanager
def transaction():
    url = os.environ.get("ACADEMY_DATABASE_URL")
    if not url:
        raise RuntimeError("Academy database is not configured")
    with psycopg.connect(url, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL search_path TO academy, pg_catalog")
            yield cur

def ready():
    try:
        with transaction() as cur:
            cur.execute("SELECT to_regclass('academy.students'), to_regclass('academy.student_sessions'), to_regclass('academy.lesson_progress')")
            return all(cur.fetchone())
    except (RuntimeError, psycopg.Error):
        return False

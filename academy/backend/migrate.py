"""Run with an administrator-provisioned ACADEMY_DATABASE_URL.
Never use another application's credentials.
"""
import os
from pathlib import Path
import psycopg

def migrate():
    url=os.environ["ACADEMY_DATABASE_URL"]
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS academy")
            cur.execute("SET LOCAL search_path TO academy, pg_catalog")
            for name in ("schema.sql","auth_schema.sql"):
                cur.execute(Path(__file__).with_name(name).read_text())
            cur.execute("SELECT to_regclass('academy.students'), to_regclass('academy.lesson_progress')")
            if not all(cur.fetchone()):
                raise RuntimeError("Migration verification failed")
if __name__=="__main__":
    migrate()

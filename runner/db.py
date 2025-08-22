import sqlite3
from pathlib import Path

DB_PATH = Path.home() / "webscraper" / "webui.sqlite"

class ProgressStore:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as c:
            c.execute("""
            CREATE TABLE IF NOT EXISTS jobs(
              job_id TEXT PRIMARY KEY,
              spider TEXT,
              start_url TEXT,
              allow_js INTEGER DEFAULT 0,
              status TEXT DEFAULT 'queued',
              items INTEGER DEFAULT 0,
              pages INTEGER DEFAULT 0,
              bytes INTEGER DEFAULT 0,
              output_path TEXT,
              output_size INTEGER DEFAULT 0,
              cancel_requested INTEGER DEFAULT 0,
              pause_requested INTEGER DEFAULT 0,
              started_at TEXT, ended_at TEXT
            );
            """)
            c.execute("""
            CREATE TABLE IF NOT EXISTS url_queue(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              label TEXT, url TEXT NOT NULL,
              spider TEXT DEFAULT 'generic',
              allow_js INTEGER DEFAULT 0,
              status TEXT DEFAULT 'queued'
            );
            """)
            c.commit()

    def _conn(self): return sqlite3.connect(DB_PATH)

    def create_job(self, job_id, spider, start_url, allow_js, output_path):
        with self._conn() as c:
            c.execute("""INSERT OR REPLACE INTO jobs(job_id, spider, start_url, allow_js, output_path, started_at)
                         VALUES(?,?,?,?,?,datetime('now'))""", (job_id, spider, start_url, 1 if allow_js else 0, output_path))
            c.commit()

    def mark_running(self, job_id):
        with self._conn() as c:
            c.execute("UPDATE jobs SET status='running' WHERE job_id=?", (job_id,))
            c.commit()

    def mark_finished_if_not_cancelled(self, job_id):
        with self._conn() as c:
            c.execute("""UPDATE jobs SET status=CASE
                        WHEN status IN ('cancelled','paused') THEN status ELSE 'finished' END,
                        ended_at=datetime('now') WHERE job_id=?""", (job_id,))
            c.commit()

    def mark_cancelled(self, job_id):
        with self._conn() as c:
            c.execute("UPDATE jobs SET status='cancelled', ended_at=datetime('now') WHERE job_id=?", (job_id,))
            c.commit()

    def mark_paused(self, job_id):
        with self._conn() as c:
            c.execute("UPDATE jobs SET status='paused', ended_at=datetime('now') WHERE job_id=?", (job_id,))
            c.commit()

    def bump_items(self, job_id, n): self._bump(job_id, "items", n)
    def bump_pages(self, job_id, n): self._bump(job_id, "pages", n)
    def bump_bytes(self, job_id, n): self._bump(job_id, "bytes", n)

    def _bump(self, job_id, col, n):
        with self._conn() as c:
            c.execute(f"UPDATE jobs SET {col}={col}+? WHERE job_id=?", (n, job_id))
            c.commit()

    def set_output_size(self, job_id, sz):
        with self._conn() as c:
            c.execute("UPDATE jobs SET output_size=? WHERE job_id=?", (sz, job_id))
            c.commit()

    def flags(self, job_id):
        with self._conn() as c:
            row = c.execute("SELECT cancel_requested, pause_requested FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row: return {}
            return {"cancel_requested": bool(row[0]), "pause_requested": bool(row[1])}

    def list_jobs(self):
        with self._conn() as c:
            cur = c.execute("""SELECT job_id, spider, start_url, status, items, pages, bytes, output_size,
                               started_at, ended_at FROM jobs ORDER BY started_at DESC""")
            return cur.fetchall()

    def request_cancel(self, job_id):
        with self._conn() as c:
            c.execute("UPDATE jobs SET cancel_requested=1 WHERE job_id=?", (job_id,))
            c.commit()

    def request_pause(self, job_id):
        with self._conn() as c:
            c.execute("UPDATE jobs SET pause_requested=1 WHERE job_id=?", (job_id,))
            c.commit()

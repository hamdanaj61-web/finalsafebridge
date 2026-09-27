"""PostgreSQL data access layer for SafeBridge AI.
Supports raw PostgreSQL via psycopg2.
"""
import base64
import os
import secrets
from collections import Counter
from datetime import datetime, timezone, timedelta
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

def get_pg_connection():
    url = st.secrets.get("DATABASE_URL", os.environ.get("DATABASE_URL"))
    if not url:
        # Fallback to Supabase URL if it's a DSN (for backwards compatibility if they just renamed it)
        url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL"))
    
    if not url or "your-project-id" in url:
        raise ConnectionError("DATABASE_URL not configured. Please set DATABASE_URL in .streamlit/secrets.toml")
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

def is_supabase_connected() -> tuple[bool, str]:
    """Verify active connection to database."""
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True, "Connected to Database"
    except Exception as e:
        return False, str(e)

def init_db():
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT key FROM settings WHERE key='allow_anonymous_reports'")
                if not cur.fetchone():
                    cur.execute("INSERT INTO settings (key, value) VALUES ('allow_anonymous_reports', '1') ON CONFLICT DO NOTHING")
                    cur.execute("INSERT INTO settings (key, value) VALUES ('external_ai_allowed', '0') ON CONFLICT DO NOTHING")
                    cur.execute("INSERT INTO settings (key, value) VALUES ('report_retention_days', '30') ON CONFLICT DO NOTHING")
                
                cur.execute("SELECT id FROM students LIMIT 1")
                if not cur.fetchone():
                    from auth import hash_password
                    now = datetime.now(timezone.utc).isoformat()
                    generated_password = secrets.token_urlsafe(12)
                    cur.execute(
                        "INSERT INTO students(username,password_hash,display_name,role,active,force_password_change,failed_attempts,created_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                        ("admin", hash_password(generated_password), "School Administrator", "admin", 1, 1, 0, now)
                    )
                    st.session_state["_first_run_admin_creds"] = {
                        "username": "admin",
                        "password": generated_password
                    }
            conn.commit()
    except Exception:
        pass

def _decode_evidence(report_dict):
    if not report_dict:
        return report_dict
    ev = report_dict.get("evidence")
    if ev and isinstance(ev, str):
        try:
            report_dict["evidence"] = base64.b64decode(ev.encode("utf-8"))
        except Exception:
            pass
    return report_dict

def query(sql, params=()):
    sql = sql.replace("?", "%s")
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
                for row in rows:
                    if "evidence" in row:
                        _decode_evidence(row)
                return rows
    except Exception as e:
        print("query error:", e)
        return []

def one(sql, params=()):
    sql = sql.replace("?", "%s")
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
                if row and "evidence" in row:
                    _decode_evidence(row)
                return row
    except Exception as e:
        print("one error:", e)
        return None

def execute(sql, params=()):
    sql = sql.replace("?", "%s")
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                if "insert into" in sql.lower() and "returning id" not in sql.lower():
                    sql += " RETURNING id"
                cur.execute(sql, params)
                res_id = None
                if "returning id" in sql.lower():
                    res = cur.fetchone()
                    if res:
                        res_id = res["id"]
                conn.commit()
                return res_id if res_id is not None else True
    except Exception as e:
        print("execute error:", e)
        return None

def get_setting(key, default=None):
    res = one("SELECT value FROM settings WHERE key=%s", (key,))
    return res["value"] if res else default

def set_setting(key, value):
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO settings(key,value) VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value", (key, str(value)))
            conn.commit()
    except Exception:
        pass

def create_report(student_id, anonymous, text, analysis, evidence=None):
    if len(text.strip()) < 10 or len(text) > 6000:
        raise ValueError("Reports must be between 10 and 6,000 characters.")
    
    evidence_name = None
    evidence_b64 = None
    if evidence:
        evidence_size = getattr(evidence, "size", None)
        if evidence_size is None:
            evidence_size = len(evidence.getvalue())
        if evidence_size > 5 * 1024 * 1024:
            raise ValueError("Evidence files must be 5 MB or smaller.")
        evidence_name = evidence.name
        evidence_b64 = base64.b64encode(evidence.getvalue()).decode("utf-8")
        
    now = datetime.now(timezone.utc).isoformat()
    return execute(
        "INSERT INTO reports(student_id, anonymous, original_report, incident_summary, category, location, severity, priority, status, evidence_name, evidence, created_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (None if anonymous else student_id, 1 if anonymous else 0, text, analysis.get("summary"), analysis.get("category"), analysis.get("location"), analysis.get("severity"), analysis.get("priority"), "Pending Review", evidence_name, evidence_b64, now)
    )

def purge_old_resolved_reports():
    try:
        days_str = get_setting("report_retention_days", "30")
        days = int(days_str) if days_str and str(days_str).isdigit() else 30
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM reports WHERE status='Resolved' AND created_at < %s RETURNING id", (cutoff,))
                deleted = cur.fetchall()
            conn.commit()
            return len(deleted)
    except Exception:
        return 0

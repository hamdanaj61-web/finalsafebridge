"""PostgreSQL / Supabase data access layer for SafeBridge AI.
Supports self-hosted PostgreSQL and Supabase PostgREST clients.
"""
import base64
import os
import secrets
from collections import Counter
from datetime import datetime, timezone, timedelta
import streamlit as st
from supabase import create_client, Client

_client: Client | None = None

def get_supabase_credentials():
    """Retrieve Supabase / Postgres REST URL and Key from Streamlit secrets or environment variables."""
    url = None
    key = None
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
    except Exception:
        pass
    if not url:
        url = os.environ.get("SUPABASE_URL")
    if not key:
        key = os.environ.get("SUPABASE_KEY")

    if url:
        url = url.strip().rstrip("/")
        if url.endswith("/rest/v1"):
            url = url[:-len("/rest/v1")].rstrip("/")
    if key:
        key = key.strip()

    return url, key

_last_credentials = None

def get_supabase() -> Client:
    """Get or initialize the Supabase client."""
    global _client, _last_credentials
    url, key = get_supabase_credentials()
    if not url or not key or "your-project-id" in url or "your-supabase" in key:
        raise ConnectionError(
            "Database credentials not configured. Please set SUPABASE_URL and SUPABASE_KEY in .streamlit/secrets.toml"
        )
    current_credentials = (url, key)
    if _client is not None and _last_credentials == current_credentials:
        return _client

    _client = create_client(url, key)
    _last_credentials = current_credentials
    return _client

def is_supabase_connected() -> tuple[bool, str]:
    """Verify active connection to database."""
    global _client
    try:
        client = get_supabase()
        client.table("settings").select("key").limit(1).execute()
        return True, "Connected to Database"
    except Exception as e:
        _client = None  # Reset client cache so subsequent checks reload fresh credentials
        return False, str(e)

def init_db():
    """Verify database connection and create initial admin account on first run only."""
    url, key = get_supabase_credentials()
    if not url or not key or "your-project-id" in url:
        return

    try:
        client = get_supabase()
        # Seed default settings if missing
        defaults = {
            "allow_anonymous_reports": "1",
            "external_ai_allowed": "0",       # Off by default (Item 5)
            "report_retention_days": "30",    # 30-day retention window (Item 7)
        }
        for k, v in defaults.items():
            existing = client.table("settings").select("key").eq("key", k).execute().data
            if not existing:
                client.table("settings").insert({"key": k, "value": v}).execute()

        # Check if students table is empty (First run only)
        # All demo credentials (student123, counselor123, admin123) have been permanently removed (Item 1).
        res = client.table("students").select("id").limit(1).execute()
        if not res.data:
            from auth import hash_password
            now = datetime.now(timezone.utc).isoformat()
            generated_password = secrets.token_urlsafe(12)
            admin_user = {
                "username": "admin",
                "password_hash": hash_password(generated_password),
                "display_name": "School Administrator",
                "role": "admin",
                "active": 1,
                "force_password_change": 1,
                "failed_attempts": 0,
                "created_at": now
            }
            try:
                client.table("students").insert(admin_user).execute()
            except Exception:
                # If custom columns have not yet been migrated in PostgreSQL schema
                admin_user.pop("force_password_change", None)
                admin_user.pop("failed_attempts", None)
                client.table("students").insert(admin_user).execute()

            st.session_state["_first_run_admin_creds"] = {
                "username": "admin",
                "password": generated_password
            }
    except Exception:
        pass

# ── Helper to decode Base64 evidence ──────────────────────────────────────────
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

# ── Core Query Compatibility Router (Postgres Compatible) ─────────────────────
def query(sql, params=()):
    """Translate application SQL queries into PostgREST / PostgreSQL queries."""
    client = get_supabase()
    # Normalize query string and normalize placeholders (? to %s equivalence)
    s = " ".join(sql.strip().split()).lower()

    # 1. Students
    if "from students" in s and "order by role" in s:
        try:
            res = client.table("students").select("id, username, display_name, role, active, created_at, force_password_change").order("role").order("display_name").execute()
            return res.data or []
        except Exception:
            res = client.table("students").select("id, username, display_name, role, active, created_at").order("role").order("display_name").execute()
            data = res.data or []
            for r in data:
                r.setdefault("force_password_change", 0)
            return data

    # 2. Reports
    if "from reports r left join students s" in s and ("where r.id=?" in s or "where r.id=%s" in s or "where r.id = ?" in s or "where r.id = %s" in s):
        res = client.table("reports").select("*, students(display_name)").eq("id", params[0]).execute()
        rows = res.data or []
        for r in rows:
            r["display_name"] = r["students"]["display_name"] if r.get("students") else None
            _decode_evidence(r)
        return rows

    if "from reports r left join students s" in s:
        res = client.table("reports").select("id, category, location, priority, status, anonymous, created_at, student_id, students(display_name)").order("created_at", desc=True).execute()
        rows = res.data or []
        for r in rows:
            r["display_name"] = r["students"]["display_name"] if r.get("students") else None
        return rows

    if "from reports where student_id=?" in s or "from reports where student_id=%s" in s or "from reports where student_id = ?" in s or "from reports where student_id = %s" in s:
        res = client.table("reports").select("id, category, priority, status, created_at").eq("student_id", params[0]).order("id", desc=True).execute()
        return res.data or []

    if "select category, count(*) as count from reports" in s:
        res = client.table("reports").select("category").execute()
        counts = Counter(r["category"] for r in (res.data or []) if r.get("category"))
        return [{"category": k, "count": v} for k, v in counts.most_common()]

    if "select location, count(*) as count from reports" in s:
        res = client.table("reports").select("location").execute()
        counts = Counter(r["location"] for r in (res.data or []) if r.get("location"))
        return [{"location": k, "count": v} for k, v in counts.most_common()]

    if "select category,location,priority,status,substr(created_at,1,10)" in s or "select category, location, priority, status" in s:
        res = client.table("reports").select("category, location, priority, status, created_at").execute()
        out = []
        for r in (res.data or []):
            out.append({
                "category": r.get("category"),
                "location": r.get("location"),
                "priority": r.get("priority"),
                "status": r.get("status"),
                "date": (r.get("created_at") or "")[:10],
            })
        return out

    # 3. Appointments
    if "from appointments a join students s" in s:
        res = client.table("appointments").select("*, students(display_name)").order("preferred_date").execute()
        rows = res.data or []
        for r in rows:
            r["display_name"] = r["students"]["display_name"] if r.get("students") else "Unknown"
        return rows

    if "from appointments where student_id=?" in s or "from appointments where student_id=%s" in s or "from appointments where student_id = ?" in s or "from appointments where student_id = %s" in s:
        res = client.table("appointments").select("reason, preferred_date, preferred_time, status, created_at").eq("student_id", params[0]).order("preferred_date", desc=True).execute()
        return res.data or []

    # 4. Checkins
    if "from checkins c join students s" in s:
        res = client.table("checkins").select("week_start, mood, mood_label, student_id, created_at, students(display_name)").order("created_at", desc=True).execute()
        rows = res.data or []
        for r in rows:
            r["display_name"] = r["students"]["display_name"] if r.get("students") else "Unknown"
        return rows

    if ("from checkins where student_id=?" in s or "from checkins where student_id=%s" in s) and "order by week_start" in s:
        res = client.table("checkins").select("week_start, mood, mood_label").eq("student_id", params[0]).order("week_start").execute()
        return res.data or []

    if "round(avg(mood),2) as wellbeing from checkins" in s or "avg(mood)" in s:
        res = client.table("checkins").select("week_start, mood").execute()
        mood_map = {}
        for r in (res.data or []):
            ws = r.get("week_start")
            m = r.get("mood")
            if ws and m is not None:
                mood_map.setdefault(ws, []).append(m)
        out = []
        for ws in sorted(mood_map.keys()):
            vals = mood_map[ws]
            avg_val = round(sum(vals) / len(vals), 2) if vals else 0.0
            out.append({"week_start": ws, "wellbeing": avg_val})
        return out

    # 5. Counselor Notes
    if "from counselor_notes" in s:
        res = client.table("counselor_notes").select("note, created_at, counselor_id, students!counselor_id(display_name)").eq("report_id", params[0]).order("created_at", desc=True).execute()
        rows = res.data or []
        for r in rows:
            r["display_name"] = r["students"]["display_name"] if r.get("students") else "Counselor"
        return rows

    # Fallback to direct PostgREST table select if simple table pattern
    for tbl in ["students", "reports", "appointments", "checkins", "settings"]:
        if f"from {tbl}" in s:
            return client.table(tbl).select("*").execute().data or []

    return []

def one(sql, params=()):
    """Fetch a single record or aggregated count (Postgres compatible)."""
    client = get_supabase()
    s = " ".join(sql.strip().split()).lower()

    # 1. Counts
    if "select count(*) n from reports where priority='high' and status='pending review'" in s:
        res = client.table("reports").select("id", count="exact").eq("priority", "High").eq("status", "Pending Review").execute()
        return {"n": res.count or 0}

    if "select count(*) n from reports where status='pending review'" in s:
        res = client.table("reports").select("id", count="exact").eq("status", "Pending Review").execute()
        return {"n": res.count or 0}

    # Month count: supports date_trunc('month', now()) and start of month
    if "from reports where created_at >=" in s and ("month" in s or "date_trunc" in s or "start of month" in s):
        first_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        res = client.table("reports").select("id", count="exact").gte("created_at", first_of_month).execute()
        return {"n": res.count or 0}

    if "select count(*) n from reports" in s:
        res = client.table("reports").select("id", count="exact").execute()
        return {"n": res.count or 0}

    if "select count(*) n from appointments where status='requested'" in s:
        res = client.table("appointments").select("id", count="exact").eq("status", "Requested").execute()
        return {"n": res.count or 0}

    if "select count(*) n from appointments" in s:
        res = client.table("appointments").select("id", count="exact").execute()
        return {"n": res.count or 0}

    if "select count(distinct student_id) n from checkins where mood <= 2" in s:
        res = client.table("checkins").select("student_id").lte("mood", 2).execute()
        unique_students = set(r["student_id"] for r in (res.data or []))
        return {"n": len(unique_students)}

    if "select count(*) n from checkins where week_start=?" in s or "select count(*) n from checkins where week_start=%s" in s:
        res = client.table("checkins").select("id", count="exact").eq("week_start", params[0]).execute()
        return {"n": res.count or 0}

    if "select count(*) n from checkins" in s:
        res = client.table("checkins").select("id", count="exact").execute()
        return {"n": res.count or 0}

    # 2. Specific Entity Lookups
    if "from students where username=?" in s or "from students where username=%s" in s:
        try:
            res = client.table("students").select("id, username, display_name, role, password_hash, active, force_password_change, failed_attempts, locked_until").ilike("username", params[0]).execute()
            return res.data[0] if res.data else None
        except Exception:
            res = client.table("students").select("id, username, display_name, role, password_hash, active").ilike("username", params[0]).execute()
            if res.data:
                row = res.data[0]
                row.setdefault("force_password_change", 0)
                row.setdefault("failed_attempts", 0)
                row.setdefault("locked_until", None)
                return row
            return None

    if "select 1 from students where username=?" in s or "select 1 from students where username=%s" in s:
        res = client.table("students").select("id").ilike("username", params[0]).execute()
        return res.data[0] if res.data else None

    if "from students where id=?" in s or "from students where id=%s" in s:
        res = client.table("students").select("*").eq("id", params[0]).execute()
        if res.data:
            row = res.data[0]
            row.setdefault("force_password_change", 0)
            row.setdefault("failed_attempts", 0)
            row.setdefault("locked_until", None)
            return row
        return None

    if "from checkins where student_id=" in s and "week_start=" in s:
        res = client.table("checkins").select("*").eq("student_id", params[0]).eq("week_start", params[1]).execute()
        return res.data[0] if res.data else None

    if "from settings where key=?" in s or "from settings where key=%s" in s:
        res = client.table("settings").select("value").eq("key", params[0]).execute()
        return res.data[0] if res.data else None

    # 3. Fallback to query
    rows = query(sql, params)
    return rows[0] if rows else None

def execute(sql, params=()):
    """Execute insert, update, or delete operations via PostgREST / PostgreSQL."""
    client = get_supabase()
    s = " ".join(sql.strip().split()).lower()
    now_iso = datetime.now(timezone.utc).isoformat()

    # Students updates / inserts
    if "insert into students" in s:
        user_record = {
            "username": params[0],
            "password_hash": params[1],
            "display_name": params[2],
            "role": params[3],
            "created_at": params[4] if len(params) > 4 else now_iso,
            "active": 1,
            "force_password_change": params[5] if len(params) > 5 else 1,
            "failed_attempts": 0
        }
        try:
            res = client.table("students").insert(user_record).execute()
        except Exception:
            user_record.pop("force_password_change", None)
            user_record.pop("failed_attempts", None)
            res = client.table("students").insert(user_record).execute()
        return res.data[0]["id"] if res.data else None

    if "update students set password_hash=?" in s and "force_password_change=" in s:
        force_val = 1 if "force_password_change=1" in s else 0
        try:
            client.table("students").update({"password_hash": params[0], "force_password_change": force_val}).eq("id", params[1]).execute()
        except Exception:
            client.table("students").update({"password_hash": params[0]}).eq("id", params[1]).execute()
        return True

    if "update students set password_hash=?" in s:
        client.table("students").update({"password_hash": params[0]}).eq("id", params[1]).execute()
        return True

    if "update students set failed_attempts=?, locked_until=?" in s:
        try:
            client.table("students").update({"failed_attempts": params[0], "locked_until": params[1]}).eq("id", params[2]).execute()
        except Exception:
            pass
        return True

    if "update students set failed_attempts=0, locked_until=null" in s:
        try:
            client.table("students").update({"failed_attempts": 0, "locked_until": None}).eq("id", params[0]).execute()
        except Exception:
            pass
        return True

    if "update students set failed_attempts=?" in s:
        try:
            client.table("students").update({"failed_attempts": params[0]}).eq("id", params[1]).execute()
        except Exception:
            pass
        return True

    if "update students set active=?" in s:
        client.table("students").update({"active": params[0]}).eq("id", params[1]).execute()
        return True

    # Reports updates
    if "update reports set status=?" in s:
        client.table("reports").update({"status": params[0]}).eq("id", params[1]).execute()
        return True

    # Appointments updates / inserts
    if "insert into appointments" in s:
        created_at_val = params[5] if len(params) > 5 else now_iso
        res = client.table("appointments").insert({
            "student_id": params[0],
            "reason": params[1],
            "preferred_date": str(params[2]),
            "preferred_time": params[3],
            "notes": params[4],
            "created_at": created_at_val,
            "status": "Requested"
        }).execute()
        return res.data[0]["id"] if res.data else None

    if "update appointments set status=?" in s:
        client.table("appointments").update({"status": params[0]}).eq("id", params[1]).execute()
        return True

    # Checkins inserts
    if "insert into checkins" in s:
        created_at_val = params[5] if len(params) > 5 else now_iso
        res = client.table("checkins").insert({
            "student_id": params[0],
            "mood": params[1],
            "mood_label": params[2],
            "note": params[3],
            "week_start": params[4],
            "created_at": created_at_val
        }).execute()
        return res.data[0]["id"] if res.data else None

    # Counselor notes inserts
    if "insert into counselor_notes" in s:
        created_at_val = params[3] if len(params) > 3 else now_iso
        res = client.table("counselor_notes").insert({
            "report_id": params[0],
            "counselor_id": params[1],
            "note": params[2],
            "created_at": created_at_val
        }).execute()
        return res.data[0]["id"] if res.data else None

    # Settings inserts/updates
    if "into settings" in s:
        client.table("settings").upsert({"key": params[0], "value": str(params[1])}).execute()
        return True

    return None

# ── Settings helpers ─────────────────────────────────────────────────────────
def get_setting(key, default=None):
    try:
        client = get_supabase()
        res = client.table("settings").select("value").eq("key", key).execute()
        return res.data[0]["value"] if res.data else default
    except Exception:
        return default

def set_setting(key, value):
    client = get_supabase()
    client.table("settings").upsert({"key": key, "value": str(value)}).execute()

# ── Report creation ──────────────────────────────────────────────────────────
def create_report(student_id, anonymous, text, analysis, evidence=None):
    """Store report and Base64-encoded evidence directly into PostgreSQL / Supabase."""
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
    client = get_supabase()
    res = client.table("reports").insert({
        "student_id": None if anonymous else student_id,
        "anonymous": 1 if anonymous else 0,
        "original_report": text,
        "incident_summary": analysis.get("summary"),
        "category": analysis.get("category"),
        "location": analysis.get("location"),
        "severity": analysis.get("severity"),
        "priority": analysis.get("priority"),
        "status": "Pending Review",
        "evidence_name": evidence_name,
        "evidence": evidence_b64,
        "created_at": now
    }).execute()
    return res.data[0]["id"] if res.data else None

# ── Data retention purge (Item 7) ─────────────────────────────────────────────
def purge_old_resolved_reports():
    """
    Purge reports with status='Resolved' older than report_retention_days (default 30 days).
    Note: In a production deployment (e.g. on Oracle Cloud VM / Linux host), this cleanup
    should be scheduled as an OS-level cron job or pg_cron task, rather than relying on
    administrative UI interaction alone.
    """
    try:
        days_str = get_setting("report_retention_days", "30")
        days = int(days_str) if days_str and str(days_str).isdigit() else 30
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        client = get_supabase()
        res = client.table("reports").select("id").eq("status", "Resolved").lt("created_at", cutoff).execute()
        rows = res.data or []
        count = len(rows)
        if count > 0:
            for r in rows:
                client.table("reports").delete().eq("id", r["id"]).execute()
        return count
    except Exception:
        return 0

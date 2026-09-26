"""SafeBridge AI — student wellbeing and anti-bullying support platform."""
import os
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st

import importlib
import auth as auth_module
import database as database_module
import styles as styles_module
import views.guided_report as guided_report_module
import views.shared as shared_module
import views.student as student_module
import views.counselor as counselor_module
import views.admin as admin_module

importlib.reload(database_module)
importlib.reload(auth_module)
importlib.reload(styles_module)
importlib.reload(guided_report_module)
importlib.reload(shared_module)
importlib.reload(student_module)
importlib.reload(counselor_module)
importlib.reload(admin_module)

from auth import init_session, login, logout, change_password
from database import init_db, is_supabase_connected
from styles import apply_styles
from views.student import render_student
from views.counselor import render_counselor
from views.admin import render_admin
from views.shared import render_anonymous, render_login
from icons import school_mark_svg

st.set_page_config(page_title="SafeBridge AI", layout="wide", initial_sidebar_state="expanded")
init_db()
init_session()
apply_styles()

_SESSION_TIMEOUT_MINUTES = 30

def school_name():
    """Optional local branding; never use branding configuration for sensitive data."""
    try:
        return st.secrets.get("SCHOOL_NAME", os.getenv("SCHOOL_NAME", "SafeBridge AI"))
    except Exception:
        return os.getenv("SCHOOL_NAME", "SafeBridge AI")

def _check_session_timeout():
    """Auto-logout after SESSION_TIMEOUT_MINUTES of inactivity."""
    now = datetime.now(timezone.utc)
    last = st.session_state.get("last_activity")
    if last and (now - last).total_seconds() > _SESSION_TIMEOUT_MINUTES * 60:
        logout()
        st.warning(f"You were signed out after {_SESSION_TIMEOUT_MINUTES} minutes of inactivity.")
        st.rerun()
    st.session_state.last_activity = now

# ── Sidebar Branding (Logo mark, school name, sentence case, no emoji) ───────
with st.sidebar:
    logo = os.getenv("SCHOOL_LOGO_PATH")
    if logo and Path(logo).is_file():
        st.image(logo, width=40)
    else:
        st.markdown(school_mark_svg(40), unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top: 0.45rem; margin-bottom: 0.2rem;">
        <div style="font-size: 1.1rem; font-weight: 700; color: #111827; letter-spacing: -0.01em;">SafeBridge</div>
        <div style="font-size: 0.85rem; color: #6B7280;">{school_name()}</div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("A safer place to speak up")
    st.divider()

    if st.session_state.user:
        st.write(f"**{st.session_state.user['display_name']}**")
        st.caption(st.session_state.user["role"].capitalize())
        if st.button("Log out", use_container_width=True, type="secondary"):
            logout()
            st.rerun()

    # Staff status indicators (clean dots, no emoji)
    user_role = (st.session_state.user or {}).get("role", "")
    if user_role in ("admin", "counselor"):
        from ai import test_gemini_key
        ok, err_msg = test_gemini_key()
        db_ok, db_msg = is_supabase_connected()
        st.divider()
        st.markdown("<p style='font-size: 0.76rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #9CA3AF; margin-bottom: 0.5rem;'>System status</p>", unsafe_allow_html=True)
        if db_ok:
            st.markdown("<div style='display: flex; align-items: center; gap: 0.45rem; font-size: 0.83rem; color: #166534;'><span style='width: 7px; height: 7px; border-radius: 50%; background: #22C55E;'></span> Database connected</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='display: flex; align-items: center; gap: 0.45rem; font-size: 0.83rem; color: #991B1B;'><span style='width: 7px; height: 7px; border-radius: 50%; background: #EF4444;'></span> Database offline</div>", unsafe_allow_html=True)
            st.caption(db_msg)
        if ok:
            st.markdown("<div style='display: flex; align-items: center; gap: 0.45rem; font-size: 0.83rem; color: #166534;'><span style='width: 7px; height: 7px; border-radius: 50%; background: #22C55E;'></span> Counselor AI ready</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='display: flex; align-items: center; gap: 0.45rem; font-size: 0.83rem; color: #92400E;'><span style='width: 7px; height: 7px; border-radius: 50%; background: #F59E0B;'></span> Counselor AI offline</div>", unsafe_allow_html=True)
            st.caption(err_msg or "Local safety engine active.")

# ── Display initial admin credentials on first run (Item 1) ─────────────────
if admin_creds := st.session_state.pop("_first_run_admin_creds", None):
    st.warning(
        f"**Initial setup notice:** A new administrator account was generated on first initialization.\n\n"
        f"- **Username:** `{admin_creds['username']}`\n"
        f"- **Temporary password:** `{admin_creds['password']}`\n\n"
        f"*Please record this password now. It will only be shown once, and you must change it upon first login.*"
    )

# ── Routing: anonymous mode takes priority, then auth check, then user portal ─
db_ok, db_msg = is_supabase_connected()
if not db_ok:
    st.warning(
        "**Database connection needed:** SafeBridge AI requires a configured PostgreSQL database.\n\n"
        "1. Execute `supabase_schema.sql` (or self-hosted PostgreSQL setup) on your database.\n"
        "2. Add your `SUPABASE_URL` and `SUPABASE_KEY` to `.streamlit/secrets.toml`.\n\n"
        f"Status details: `{db_msg}`"
    )

if st.session_state.get("anonymous_mode"):
    render_anonymous()
elif not st.session_state.user:
    render_login(login)
else:
    _check_session_timeout()
    user = st.session_state.user

    # ── Enforce mandatory password change (Item 3: Flat styling, sentence case) ──
    if user.get("force_password_change"):
        st.markdown("""
        <div style="padding: 1.25rem 0 1rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.5rem;">
            <h1 style="font-size: 1.6rem; font-weight: 700; margin: 0 0 0.25rem 0; color: #111827;">Password change required</h1>
            <p style="font-size: 0.95rem; color: #6B7280; margin: 0;">For school security compliance, you must choose a new password before continuing.</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("Your new password must be at least 10 characters long.")
        with st.form("force_password_change_form"):
            new_pw = st.text_input("New password", type="password")
            conf_pw = st.text_input("Confirm new password", type="password")
            submitted = st.form_submit_button("Update password and continue", type="primary")
        if submitted:
            if len(new_pw) < 10:
                st.error("Password must be at least 10 characters long.")
            elif new_pw != conf_pw:
                st.error("Passwords do not match.")
            else:
                change_password(user["id"], new_pw)
                st.success("Password updated successfully. Redirecting...")
                st.rerun()
    else:
        # Notice banner if staff and Gemini is offline
        if user["role"] in ("admin", "counselor"):
            from database import get_setting
            if get_setting("external_ai_allowed", "0") == "1":
                from ai import test_gemini_key
                ok, err_msg = test_gemini_key()
                if not ok:
                    st.info(
                        f"External AI note: {err_msg} — counselor suggestions will use the local safety engine."
                    )

        if user["role"] == "student":
            render_student(user)
        elif user["role"] == "counselor":
            render_counselor(user)
        else:
            render_admin(user)

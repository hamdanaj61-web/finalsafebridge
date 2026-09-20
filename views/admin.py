"""Administrator portal views: aggregated insights, pseudonymized user accounts, platform settings, QR access, and exports.
Zero emoji, outline SVG icons, flat card styling, sentence case throughout.
"""
import io
from datetime import datetime, timezone
import streamlit as st
import pandas as pd
from database import execute, one, query, get_setting, set_setting, purge_old_resolved_reports
from utils import csv_bytes
from icons import icon_svg

def render_admin(user):
    page = st.sidebar.radio(
        "Administrator analytics",
        ["Dashboard", "Users", "Settings", "QR access", "Export"],
        format_func=lambda x: {
            "Dashboard": "Dashboard",
            "Users":     "User management",
            "Settings":  "Settings",
            "QR access": "QR access",
            "Export":    "Export",
        }[x],
    )
    if page == "Dashboard": dashboard()
    elif page == "Users":    users_page(user)
    elif page == "Settings": settings_page()
    elif page == "QR access": qr_page()
    else: export_page()

# ── Dashboard (Aggregated Trends, Flat Metric Cards) ──────────────────────────
def dashboard():
    st.markdown("""
    <div style="padding: 1.25rem 0 1rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.5rem;">
        <h1 style="font-size: 1.6rem; font-weight: 700; margin: 0 0 0.25rem 0; color: #111827;">School wellbeing insights</h1>
        <p style="font-size: 0.95rem; color: #6B7280; margin: 0;">Aggregated school trends only. No student conversations or identifying report details are displayed.</p>
    </div>
    """, unsafe_allow_html=True)

    total = one("SELECT count(*) n FROM reports")['n']
    month = one("SELECT count(*) n FROM reports WHERE created_at >= date_trunc('month', NOW())")['n']
    appointments = one("SELECT count(*) n FROM appointments")['n']
    checkins = one("SELECT count(*) n FROM checkins")['n']

    cols = st.columns(4)
    labels = ["Total reports", "Reports this month", "Appointments requested", "Weekly check-ins"]
    values = [total, month, appointments, checkins]
    for c, label, v in zip(cols, labels, values):
        with c:
            st.metric(label, v)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    categories = query("SELECT category, count(*) AS count FROM reports GROUP BY category ORDER BY count DESC")
    locations = query("SELECT location, count(*) AS count FROM reports GROUP BY location ORDER BY count DESC")
    wellbeing = query("SELECT week_start,round(avg(mood),2) AS wellbeing FROM checkins GROUP BY week_start ORDER BY week_start")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Report categories")
        if categories:
            st.bar_chart(pd.DataFrame(categories).set_index('category'))
        else:
            st.caption("No report categories recorded yet.")
    with c2:
        st.subheader("Common incident locations")
        if locations:
            st.bar_chart(pd.DataFrame(locations).set_index('location'))
        else:
            st.caption("No location data recorded yet.")

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
    st.subheader("Weekly wellbeing trend")
    if wellbeing:
        st.line_chart(pd.DataFrame(wellbeing).set_index('week_start'))
    else:
        st.caption("No weekly wellbeing check-in data yet.")

# ── User Management (Pseudonymized, 10+ char passwords, sentence case) ────────
def users_page(current_admin):
    st.markdown("""
    <div style="padding: 1rem 0 0.8rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.25rem;">
        <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0; color: #111827;">User management</h2>
        <p style="font-size: 0.9rem; color: #6B7280; margin: 0.25rem 0 0 0;">Provision user credentials, reset passwords, and manage active status.</p>
    </div>
    """, unsafe_allow_html=True)

    # MOE Student Privacy Guidance Callout
    st.markdown(f"""
    <div class="sb-notice-block">
        <div class="sb-notice-title">
            {icon_svg("lock", size=18, color="#4B5563")}
            <span>Student pseudonymization policy</span>
        </div>
        <div class="sb-notice-body">
            The application database stores pseudonyms and handles only (e.g. <code>Student-204</code>, <code>BlueFalcon</code>).
            Real student identities must never be entered into this system. Maintain the official real-name mapping exclusively on school-managed, encrypted storage with designated backup keyholders.
        </div>
    </div>
    """, unsafe_allow_html=True)

    users = query("SELECT id, username, display_name, role, active, created_at FROM students ORDER BY role, display_name")
    if users:
        df = pd.DataFrame(users).copy()
        # Sentence-case status text badges without emoji
        df["status"] = df["active"].map({1: "Active", 0: "Inactive"})
        df_disp = df[["id", "username", "display_name", "role", "status", "created_at"]].copy()
        df_disp.columns = ["ID", "Username", "Pseudonym / Handle", "Role", "Status", "Created at"]
        st.dataframe(df_disp, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

    # ── Create new user ──────────────────────────────────────────────────────
    with st.expander("Create new user", expanded=False):
        with st.form("create_user_form"):
            c1, c2 = st.columns(2)
            new_username = c1.text_input("Username (login ID)")
            new_display_name = c2.text_input("Handle / Nickname (Pseudonym — not real name)")
            new_role = st.selectbox("Role", ["student", "counselor", "admin"])
            new_password = st.text_input("Initial password (minimum 10 characters)", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            created = st.form_submit_button("Create user", type="primary")

        if created:
            if not new_username.strip() or not new_display_name.strip():
                st.error("Username and pseudonym handle are required.")
            elif len(new_password) < 10:
                st.error("Password must be at least 10 characters long (security policy).")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif one("SELECT 1 FROM students WHERE username=?", (new_username.strip().lower(),)):
                st.error(f"Username '{new_username.strip().lower()}' is already taken.")
            else:
                from auth import hash_password
                now_iso = datetime.now(timezone.utc).isoformat()
                execute(
                    "INSERT INTO students(username,password_hash,display_name,role,created_at,force_password_change) VALUES(?,?,?,?,?,?)",
                    (new_username.strip().lower(), hash_password(new_password), new_display_name.strip(), new_role, now_iso, 1),
                )
                st.success(f"User '{new_username.strip().lower()}' created successfully. Password change will be required on first login.")
                st.rerun()

    st.divider()

    # ── Manage existing user ─────────────────────────────────────────────────
    st.subheader("Manage existing user")
    user_opts = {u['id']: f"{u['display_name']} ({u['username']} · {u['role']})" for u in users}
    if not user_opts:
        st.caption("No users found.")
        return
    selected_id = st.selectbox("Select user to manage", list(user_opts.keys()), format_func=lambda x: user_opts[x])
    selected = one("SELECT * FROM students WHERE id=?", (selected_id,))

    col1, col2 = st.columns(2)

    with col1:
        with st.form("reset_password_form"):
            st.markdown("<p style='font-size: 0.9rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;'>Reset password</p>", unsafe_allow_html=True)
            new_pw = st.text_input("New password (minimum 10 characters)", type="password")
            conf_pw = st.text_input("Confirm new password", type="password")
            reset = st.form_submit_button("Update password", type="primary")
        if reset:
            if len(new_pw) < 10:
                st.error("Password must be at least 10 characters long (security policy).")
            elif new_pw != conf_pw:
                st.error("Passwords do not match.")
            else:
                from auth import hash_password
                execute("UPDATE students SET password_hash=?, force_password_change=1 WHERE id=?", (hash_password(new_pw), selected_id))
                st.success("Password updated. User must change it upon next login.")

    with col2:
        st.markdown("<p style='font-size: 0.9rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;'>Account access</p>", unsafe_allow_html=True)
        is_active = bool(selected.get("active", 1))
        if selected_id == current_admin['id']:
            st.caption("You cannot deactivate your own active session account.")
        else:
            label = "Deactivate account" if is_active else "Reactivate account"
            if st.button(label, type="secondary", use_container_width=True):
                execute("UPDATE students SET active=? WHERE id=?", (0 if is_active else 1, selected_id))
                st.success(f"Account {'deactivated' if is_active else 'reactivated'}.")
                st.rerun()

# ── Settings Page: Grouped Visually with Labeled Sections & Dividers ─────────
def settings_page():
    st.markdown("""
    <div style="padding: 1rem 0 0.8rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.25rem;">
        <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0; color: #111827;">Platform settings</h2>
        <p style="font-size: 0.9rem; color: #6B7280; margin: 0.25rem 0 0 0;">School-wide configurations for reporting access, counselor tools, and data retention.</p>
    </div>
    """, unsafe_allow_html=True)

    # Section 1: Anonymous Reporting
    st.markdown("### Anonymous reporting")
    st.caption("Allow students or community members to submit concerns without logging in.")
    allow_anon = get_setting("allow_anonymous_reports", "1") == "1"
    new_anon = st.toggle(
        "Enable anonymous reporting portal",
        value=allow_anon,
        help="When disabled, the anonymous reporting option is hidden from the login screen.",
    )
    if new_anon != allow_anon:
        set_setting("allow_anonymous_reports", "1" if new_anon else "0")
        st.success("Anonymous reporting setting saved.")
        st.rerun()

    st.divider()

    # Section 2: AI Assistance
    st.markdown("### AI assistance")
    st.caption("Controls external generative AI usage. Student flows never contact external AI regardless of this setting.")
    ai_allowed = get_setting("external_ai_allowed", "0") == "1"
    new_ai = st.toggle(
        "Enable external AI for counselor action suggestions",
        value=ai_allowed,
        help="When disabled (default), counselor suggestions run strictly on the built-in local rule engine. When enabled, suggestions use Gemini with automated identifier redaction.",
    )
    if new_ai != ai_allowed:
        set_setting("external_ai_allowed", "1" if new_ai else "0")
        st.success(f"AI assistance updated: {'Enabled (Redacted prompt mode)' if new_ai else 'Disabled (Local safety engine only)'}.")
        st.rerun()

    st.divider()

    # Section 3: Data Retention & Lifecycle
    st.markdown("### Data retention")
    st.caption("Policy for purging old resolved incident reports to honor data minimization.")
    current_days = int(get_setting("report_retention_days", "30") or "30")
    new_days = st.number_input(
        "Retention period for resolved reports (days)",
        min_value=7,
        max_value=365,
        value=current_days,
        step=1,
        help="Resolved incident reports older than this threshold will be permanently deleted.",
    )
    if new_days != current_days:
        set_setting("report_retention_days", str(new_days))
        st.success(f"Retention period set to {new_days} days.")
        st.rerun()

    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    if st.button("Run cleanup now", type="secondary"):
        purged = purge_old_resolved_reports()
        st.success(f"Cleanup complete. {purged} resolved report(s) older than {new_days} days were purged.")
    st.caption("A scheduled daily OS-level cron job on the production server runs this lifecycle purge automatically.")

# ── QR Access Page: Flat Card Styling ────────────────────────────────────────
def qr_page():
    st.markdown("""
    <div style="padding: 1rem 0 0.8rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.25rem;">
        <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0; color: #111827;">Student QR access</h2>
        <p style="font-size: 0.9rem; color: #6B7280; margin: 0.25rem 0 0 0;">Generate and download quick-access QR codes for school posters or student planners.</p>
    </div>
    """, unsafe_allow_html=True)

    url = st.text_input("Portal destination URL", value="https://your-school.example/safebridge")
    try:
        import qrcode
        image = qrcode.make(url)
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        st.markdown("<div class='card' style='max-width: 320px; text-align: center;'>", unsafe_allow_html=True)
        st.image(buf.getvalue(), width=240)
        st.download_button("Download QR code", buf.getvalue(), "safebridge-student-qr.png", "image/png", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)
    except ImportError:
        st.warning("QR generation library not available.")

# ── Export Analytics: Flat Styling, Sentence Case ────────────────────────────
def export_page():
    st.markdown("""
    <div style="padding: 1rem 0 0.8rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.25rem;">
        <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0; color: #111827;">Export analytics</h2>
        <p style="font-size: 0.9rem; color: #6B7280; margin: 0.25rem 0 0 0;">Download non-identifying report metadata for school board or compliance records.</p>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Exports contain per-report metadata (category, location, priority, status, date). Student pseudonyms, real names, and free-text details are strictly omitted.")
    data = query("SELECT category,location,priority,status,substr(created_at,1,10) AS date FROM reports")
    st.download_button(
        "Download analytics CSV",
        csv_bytes(data),
        "safebridge-analytics.csv",
        "text/csv",
        disabled=not bool(data),
        type="primary" if bool(data) else "secondary",
    )

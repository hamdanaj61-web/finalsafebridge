"""Counselor workspace: overview, high-stakes report triage, distinct content styling, and appointments.
Vibrant modern aesthetics with clear human-led safeguarding controls.
"""
from datetime import datetime, timezone
import streamlit as st
import pandas as pd
from database import execute, one, query
from utils import report_pdf, week_start
from icons import icon_svg

def render_counselor(user):
    urgent = (lambda r: r['n'] if r else 0)(one("SELECT count(*) n FROM reports WHERE priority='High' AND status='Pending Review'"))
    if urgent:
        st.sidebar.markdown(f"""
        <div style="background: var(--sb-amber-light); border: 1.5px solid var(--sb-amber-border); border-radius: 12px; padding: 0.75rem 1rem; margin-bottom: 1rem; font-size: 0.86rem; color: var(--sb-amber-dark); display: flex; align-items: center; gap: 0.5rem; font-weight: 600;">
            {icon_svg("alert", size=18, color="#D97706")}
            <span><strong>{urgent} high-priority</strong> report(s) pending review</span>
        </div>
        """, unsafe_allow_html=True)

    page = st.sidebar.radio(
        "Counselor workspace",
        ["Overview", "Reports", "Appointments", "Check-ins"],
        format_func=lambda p: {"Overview": "Overview", "Reports": "Incident reports", "Appointments": "Appointment requests", "Check-ins": "Weekly check-ins"}[p]
    )
    if page == "Overview": overview()
    elif page == "Reports": reports_page(user)
    elif page == "Appointments": appointments_page()
    else: checkins_page()

def overview():
    st.markdown(f"""
    <div class="sb-page-header">
        <div class="sb-pill-badge">
            {icon_svg("shield_check", size=14, color="#4F46E5")}
            <span>Counselor Safeguarding Workspace</span>
        </div>
        <h1>Counselor workspace</h1>
        <p>Prioritize student care with a clear, human-led view of support needs and incident reports.</p>
    </div>
    """, unsafe_allow_html=True)

    pending = one("SELECT count(*) n FROM reports WHERE status='Pending Review'")['n']
    appts = one("SELECT count(*) n FROM appointments WHERE status='Requested'")['n']
    support = one("SELECT count(DISTINCT student_id) n FROM checkins WHERE mood <= 2")['n']
    checks = one("SELECT count(*) n FROM checkins WHERE week_start=?", (week_start(),))['n']

    cols = st.columns(4)
    labels = ["Pending reports", "Appointment requests", "Students requesting support", "Weekly check-ins"]
    values = [pending, appts, support, checks]
    for col, label, value in zip(cols, labels, values):
        with col:
            st.metric(label, value)

    # Calm standing inline note
    st.markdown(f"""
    <div class="sb-ai-disclaimer" style="margin-top: 1.8rem;">
        <strong>Safeguarding notice:</strong> AI recommendations are organizational aids only. Counselors make all safeguarding decisions, evaluations, and student outreach.
    </div>
    """, unsafe_allow_html=True)

def reports_page(user):
    st.markdown(f"""
    <div style="padding: 1.2rem 0 1rem 0; border-bottom: 1px solid var(--sb-border); margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="sb-icon-box" style="width: 40px; height: 40px;">
                {icon_svg("file_text", size=22, color="#4F46E5")}
            </div>
            <div>
                <h2 style="font-size: 1.5rem; font-weight: 800; margin: 0; color: #0F172A;">Incident reports</h2>
                <p style="font-size: 0.92rem; color: #64748B; margin: 0.15rem 0 0 0;">Review, categorize, and document follow-up actions on student concerns.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rows = query("SELECT r.id,r.category,r.location,r.priority,r.status,r.anonymous,r.created_at,s.display_name FROM reports r LEFT JOIN students s ON r.student_id=s.id ORDER BY r.created_at DESC")
    f1, f2 = st.columns(2)
    search = f1.text_input("Search reports", placeholder="Search by student pseudonym, category, or location...")
    status = f2.selectbox("Filter by status", ["All", "Pending Review", "Under Review", "Resolved", "Escalated"])

    filtered = [r for r in rows if (status == "All" or r['status'] == status) and (not search or search.lower() in str(r).lower())]

    if filtered:
        df = pd.DataFrame(filtered).copy()
        df["reporter"] = df.apply(lambda row: "Anonymous" if row["anonymous"] else (row.get("display_name") or "Unknown"), axis=1)
        table_df = df[["id", "reporter", "category", "location", "priority", "status", "created_at"]].copy()
        table_df.columns = ["Report ID", "Reporter handle", "Category", "Location", "Priority", "Status", "Date"]
        st.dataframe(table_df, use_container_width=True, hide_index=True)
    else:
        st.caption("No matching reports found.")
        return

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
    rid = st.selectbox("Select report to review", [r['id'] for r in filtered], format_func=lambda x: f"Report #{x}")
    report = one("SELECT r.*,s.display_name FROM reports r LEFT JOIN students s ON r.student_id=s.id WHERE r.id=?", (rid,))

    with st.container(border=True):
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 0.85rem; margin-bottom: 1.2rem;">
            <div>
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #0F172A;">Report #{rid}</h3>
                <span style="font-size: 0.88rem; color: #64748B;">Reporter: {'Anonymous' if report['anonymous'] else (report.get('display_name') or 'Confidential handle')}</span>
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <span class="sb-badge sb-badge-neutral">{report.get('status', 'Pending Review')}</span>
                <span class="sb-badge {'sb-badge-danger' if report.get('priority') == 'High' else 'sb-badge-warning'}">{report.get('priority', 'Medium')} priority</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Clear visual separation: Original Report
        st.markdown("<p style='font-size: 0.88rem; font-weight: 700; color: #334155; margin-bottom: 0.35rem;'>Original student report</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='sb-content-original'>{report['original_report']}</div>", unsafe_allow_html=True)

        # Clear visual separation: Incident Summary
        st.markdown("<p style='font-size: 0.88rem; font-weight: 700; color: #334155; margin-bottom: 0.35rem;'>Structured incident summary</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='sb-content-ai'>{report.get('incident_summary') or 'No summary provided.'}</div>", unsafe_allow_html=True)

        # Calm inline disclaimer note
        st.markdown(f"""
        <div class="sb-ai-disclaimer">
            {icon_svg("info", size=14, color="#4F46E5")}
            AI recommendation only, human review required.
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Category", report.get('category', 'General'))
        c2.metric("Location", report.get('location', 'Unspecified'))
        c3.metric("Suggested priority", report.get('priority', 'Medium'))

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if report.get('evidence_name'):
                st.download_button("Download attached evidence", report['evidence'], file_name=report['evidence_name'], type="secondary", use_container_width=True)
        with col_d2:
            st.download_button("Download review PDF", report_pdf(report), file_name=f"safebridge-report-{rid}.pdf", mime="application/pdf", type="secondary", use_container_width=True)

        # Counselor AI suggested actions
        action_key = f"counselor_actions_{rid}"
        if st.button("Get suggested actions", key=f"ai_actions_{rid}", type="secondary"):
            with st.spinner("Generating suggestions..."):
                from ai import suggest_actions
                analysis = {"summary": report.get('incident_summary'), "category": report.get('category'), "location": report.get('location'), "priority": report.get('priority')}
                actions_data = suggest_actions(report['original_report'], analysis)
                if actions_data and "actions" in actions_data:
                    st.session_state[action_key] = actions_data
                else:
                    st.error("Could not generate actions at this time.")

        if action_data := st.session_state.get(action_key):
            st.markdown(f"""
            <div class="sb-notice-block" style="border-left: 3px solid #10B981; margin-top: 0.75rem;">
                <div class="sb-notice-title">
                    <span>Suggested actions & risk evaluation</span>
                    <span class="sb-badge sb-badge-accent">{action_data.get('risk_level', 'Medium')} risk</span>
                </div>
                <div class="sb-notice-body">{action_data.get('risk_rationale', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            for act in action_data.get("actions", []):
                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 0.85rem 1.1rem; margin-bottom: 0.5rem; box-shadow: var(--sb-shadow-sm);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: #0F172A; font-size: 0.92rem;">{act['title']}</strong>
                        <span class="sb-badge sb-badge-neutral">{act['urgency']}</span>
                    </div>
                    <p style="color: #64748B; font-size: 0.85rem; margin: 0.3rem 0 0 0;">{act['detail']}</p>
                </div>
                """, unsafe_allow_html=True)

        # Clear visual separation: Counselor Notes
        st.markdown("<p style='font-size: 0.88rem; font-weight: 700; color: #334155; margin-top: 1.5rem; margin-bottom: 0.35rem;'>Counselor review history & notes</p>", unsafe_allow_html=True)
        notes = query("SELECT n.note,n.created_at,s.display_name FROM counselor_notes n JOIN students s ON s.id=n.counselor_id WHERE n.report_id=? ORDER BY n.created_at DESC", (rid,))
        if notes:
            for n in notes:
                st.markdown(f"""
                <div class='sb-content-notes'>
                    <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.25rem;">
                        <strong>{n.get('display_name', 'Counselor')}</strong> · {n.get('created_at', '')[:16]}
                    </div>
                    <div style="font-size: 0.92rem; color: #1E293B;">{n['note']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No notes recorded yet.")

        with st.form("review_form_" + str(rid)):
            statuses = ["Pending Review", "Under Review", "Resolved", "Escalated"]
            curr_status_idx = statuses.index(report['status']) if report.get('status') in statuses else 0
            new_status = st.selectbox("Update status", statuses, index=curr_status_idx)
            note = st.text_area("Add counselor note", max_chars=3000, placeholder="Document actions taken, interviews, or safeguarding escalations...")
            saved = st.form_submit_button("Save review", type="primary")

        if saved:
            execute("UPDATE reports SET status=? WHERE id=?", (new_status, rid))
            if note.strip():
                now_iso = datetime.now(timezone.utc).isoformat()
                execute("INSERT INTO counselor_notes(report_id,counselor_id,note,created_at) VALUES(?,?,?,?)", (rid, user['id'], note.strip(), now_iso))
            st.success("Review recorded.")
            st.rerun()

def appointments_page():
    st.markdown(f"""
    <div style="padding: 1.2rem 0 1rem 0; border-bottom: 1px solid var(--sb-border); margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="sb-icon-box" style="width: 40px; height: 40px;">
                {icon_svg("calendar", size=22, color="#4F46E5")}
            </div>
            <div>
                <h2 style="font-size: 1.5rem; font-weight: 800; margin: 0; color: #0F172A;">Appointment requests</h2>
                <p style="font-size: 0.92rem; color: #64748B; margin: 0.15rem 0 0 0;">Manage student meeting requests and follow-ups.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rows = query("SELECT a.*,s.display_name FROM appointments a JOIN students s ON a.student_id=s.id ORDER BY a.preferred_date")
    if rows:
        df = pd.DataFrame(rows).copy()
        disp_cols = ["id", "display_name", "reason", "preferred_date", "preferred_time", "status", "notes"]
        df_sub = df[[c for c in disp_cols if c in df.columns]].copy()
        df_sub.columns = [c.replace("_", " ").title() for c in df_sub.columns]
        st.dataframe(df_sub, use_container_width=True, hide_index=True)

        aid = st.selectbox("Select appointment to update", [r['id'] for r in rows], format_func=lambda x: f"Request #{x}")
        selected_appt = next((r for r in rows if r['id'] == aid), None)
        appt_statuses = ["Requested", "Confirmed", "Completed", "Cancelled"]
        curr_appt_idx = appt_statuses.index(selected_appt['status']) if selected_appt and selected_appt['status'] in appt_statuses else 0
        status = st.selectbox("Appointment status", appt_statuses, index=curr_appt_idx)
        if st.button("Update appointment", key=f"btn_update_appt_{aid}", type="primary"):
            execute("UPDATE appointments SET status=? WHERE id=?", (status, aid))
            st.success("Appointment updated.")
            st.rerun()
    else:
        st.caption("No appointment requests recorded.")

def checkins_page():
    st.markdown(f"""
    <div style="padding: 1.2rem 0 1rem 0; border-bottom: 1px solid var(--sb-border); margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="sb-icon-box" style="width: 40px; height: 40px; background: #ECFDF5; color: #10B981;">
                {icon_svg("smile", size=22, color="#10B981")}
            </div>
            <div>
                <h2 style="font-size: 1.5rem; font-weight: 800; margin: 0; color: #0F172A;">Weekly wellbeing signals</h2>
                <p style="font-size: 0.92rem; color: #64748B; margin: 0.15rem 0 0 0;">Aggregated signals to notice where outreach may be supportive. Not clinical diagnoses.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rows = query("SELECT c.week_start,c.mood,c.mood_label,s.display_name FROM checkins c JOIN students s ON c.student_id=s.id ORDER BY c.created_at DESC")
    if rows:
        df = pd.DataFrame(rows).copy()
        cols = ["week_start", "mood", "mood_label", "display_name"]
        df_disp = df[[c for c in cols if c in df.columns]].copy()
        df_disp.columns = ["Week start", "Mood score", "Mood label", "Student handle"][:len(df_disp.columns)]
        st.dataframe(df_disp, use_container_width=True, hide_index=True)
        st.caption("Student private notes are kept strictly confidential unless an active safeguarding review is opened.")
        if "mood_label" in df.columns:
            st.bar_chart(df.groupby('mood_label').size())
    else:
        st.caption("No weekly check-ins recorded yet.")

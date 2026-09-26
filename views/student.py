"""Student portal views: home, help reporting, weekly check-ins, appointments, learning, and activity.
Vibrant modern aesthetics with button-guided reporting options.
"""
from datetime import date, timedelta, datetime, timezone
import streamlit as st
import pandas as pd
from ai import analyze_report, format_report_from_state, DEFAULT_REPORT_STATE
from database import execute, one, query, create_report, get_setting
from utils import week_start
from icons import icon_svg
from views.guided_report import render_guided_report_wizard

def nav(user):
    options = {
        "Home": "Home",
        "Help": "I need help",
        "Check-in": "Weekly check-in",
        "Book": "Book counselor",
        "Learn": "Learn and stay safe",
        "My activity": "My activity"
    }
    if st.session_state.get("page") not in options:
        st.session_state.page = "Home"
    picked = st.sidebar.radio(
        "Navigation",
        list(options),
        format_func=lambda x: options[x],
        index=list(options).index(st.session_state.page)
    )
    st.session_state.page = picked
    return picked

def render_student(user):
    page = nav(user)
    if page == "Home": home(user)
    elif page == "Help": help_page(user)
    elif page == "Check-in": checkin_page(user)
    elif page == "Book": booking_page(user)
    elif page == "Learn": learning_page()
    else: activity_page(user)

def home(user):
    disp = user.get("display_name", "Student")
    st.markdown(f"""
    <div class="sb-page-header">
        <div class="sb-pill-badge">
            {icon_svg("shield_check", size=14, color="#4F46E5")}
            <span>Student Wellbeing Portal</span>
        </div>
        <h1>Welcome, {disp}</h1>
        <p>A safe, private, and supportive space to speak up, complete wellbeing check-ins, or request time with a counselor.</p>
    </div>
    """, unsafe_allow_html=True)

    # Primary action cards
    cards = [
        ("shield", "I need help", "Share a concern step-by-step or in writing with a counselor", "Help"),
        ("smile", "Weekly check-in", "A brief pulse on how your week is going", "Check-in"),
        ("calendar", "Book counselor", "Request a private, one-on-one session", "Book"),
    ]
    cols = st.columns(3)
    for col, (icon_name, title, desc, target) in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class='card'>
                <div class="sb-icon-box">{icon_svg(icon_name, size=24, color="#4F46E5")}</div>
                <h3>{title}</h3>
                <p class='muted'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open", key="go_" + target, use_container_width=True):
                st.session_state.page = target
                st.rerun()

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    cards2 = [
        ("book", "Learn and stay safe", "Practical tools and guidance for digital safety and respect", "Learn"),
        ("clock", "My activity", "Review your submitted reports and appointment requests", "My activity")
    ]
    cols2 = st.columns(2)
    for col, (icon_name, title, desc, target) in zip(cols2, cards2):
        with col:
            st.markdown(f"""
            <div class='card'>
                <div class="sb-icon-box">{icon_svg(icon_name, size=24, color="#4F46E5")}</div>
                <h3>{title}</h3>
                <p class='muted'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open", key="go_" + target, use_container_width=True):
                st.session_state.page = target
                st.rerun()

# ── I Need Help Flow (Dual Options: Button-Guided & Written Form) ────────────
def help_page(user):
    st.markdown(f"""
    <div style="padding: 1.2rem 0 1rem 0; border-bottom: 1px solid var(--sb-border); margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="sb-icon-box" style="width: 40px; height: 40px;">
                {icon_svg("shield", size=22, color="#4F46E5")}
            </div>
            <div>
                <h2 style="font-size: 1.5rem; font-weight: 800; margin: 0; color: #0F172A;">Tell us what happened</h2>
                <p style="font-size: 0.92rem; color: #64748B; margin: 0.15rem 0 0 0;">A school counselor reviews every report to ensure safety, care, and support.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("report_submitted"):
        st.success("Your report has been submitted for counselor review. Thank you for speaking up.")
        if st.button("Submit another concern", type="secondary"):
            st.session_state.report_submitted = False
            for k in ["help_messages", "help_report_state", "help_show_review", "student_guided_step", "student_guided_data"]:
                st.session_state.pop(k, None)
            st.rerun()
        return

    # Visual separation for consent notice (bordered block, calm aesthetic)
    st.markdown(f"""
    <div class="sb-notice-block">
        <div class="sb-notice-title">
            {icon_svg("info", size=18, color="#4F46E5")}
            <span>Privacy and reporting notice</span>
        </div>
        <div class="sb-notice-body">
            <strong>What is collected:</strong> Details of the concern you share and optional attached evidence.<br>
            <strong>Identity options:</strong> You may submit anonymously or with your student handle.<br>
            <strong>Reviewers:</strong> Designated school counseling and safeguarding staff only.<br>
            <strong>Advisory assistance:</strong> Any automated categorization is strictly an organizational aid. All decisions and follow-ups are led by human counselors.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("If you or someone else is in immediate danger, please contact local emergency services or alert a trusted adult now.")

    # ── Report Submission Mode Selector: Guided vs Written ─────────────────
    tab_guided, tab_written = st.tabs([
        "Button-guided report (Interactive & quick)",
        "Standard written form (Type your description)"
    ])

    with tab_guided:
        st.markdown("<p style='font-size: 0.9rem; color: #64748B; margin-bottom: 1rem;'>Select options at each step to build your report with simple clicks.</p>", unsafe_allow_html=True)
        render_guided_report_wizard(user=user, prefix="student_")

    with tab_written:
        st.markdown("<p style='font-size: 0.9rem; color: #64748B; margin-bottom: 1rem;'>Write about what occurred in your own words.</p>", unsafe_allow_html=True)
        with st.form("help_report_form"):
            text = st.text_area("Describe what happened", max_chars=6000, placeholder="Take your time and describe what occurred in your own words.")
            allow_anon = get_setting("allow_anonymous_reports", "1") == "1"
            if allow_anon:
                anonymous = st.checkbox("Submit anonymously (omit student handle from counselor view)", value=False)
            else:
                anonymous = False
                st.caption("Anonymous reporting is disabled by school administration. Your student handle will be included.")

            evidence = st.file_uploader("Optional image or document evidence", type=["png", "jpg", "jpeg", "pdf"], help="PNG, JPG, or PDF up to 5 MB")
            consent = st.checkbox("I understand how this report will be reviewed by school counselors", value=True)
            submitted = st.form_submit_button("Send report", type="primary")

        if submitted:
            if not consent:
                st.error("Please confirm you understand how your report is handled before submitting.")
            elif len(text.strip()) < 10:
                st.error("Please provide at least a short description of the concern (minimum 10 characters).")
            else:
                try:
                    analysis = analyze_report(text.strip())
                    create_report(user['id'], anonymous, text.strip(), analysis, evidence)
                    st.session_state.report_submitted = True
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

# ── Weekly Check-in ─────────────────────────────────────────────────────────
def checkin_page(user):
    st.markdown(f"""
    <div style="padding: 1.2rem 0 1rem 0; border-bottom: 1px solid var(--sb-border); margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="sb-icon-box" style="width: 40px; height: 40px; background: #ECFDF5; color: #10B981;">
                {icon_svg("smile", size=22, color="#10B981")}
            </div>
            <div>
                <h2 style="font-size: 1.5rem; font-weight: 800; margin: 0; color: #0F172A;">Weekly wellbeing check-in</h2>
                <p style="font-size: 0.92rem; color: #64748B; margin: 0.15rem 0 0 0;">A brief check-in helps counselors notice when additional support may be helpful.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    existing = one("SELECT * FROM checkins WHERE student_id=? AND week_start=?", (user['id'], week_start()))
    if existing:
        st.success("You have completed this week's check-in. Thank you for checking in with yourself.")
        return

    moods = {
        "Excellent": 5,
        "Good": 4,
        "Neutral": 3,
        "Difficult": 2,
        "Need support": 1
    }
    with st.form("checkin_form"):
        mood = st.radio("How has your week been overall?", list(moods), horizontal=True)
        note = st.text_area("Would you like to share anything? (optional)", max_chars=1200, placeholder="Anything you want to note about your week...")
        sent = st.form_submit_button("Save check-in", type="primary")

    if sent:
        now_iso = datetime.now(timezone.utc).isoformat()
        execute(
            "INSERT INTO checkins(student_id, mood, mood_label, note, week_start, created_at) VALUES(?,?,?,?,?,?)",
            (user['id'], moods[mood], mood, note.strip(), week_start(), now_iso),
        )
        st.success("Check-in saved. Counselors can view aggregate signals, keeping private notes confidential unless needed.")

# ── Book Counselor ──────────────────────────────────────────────────────────
def booking_page(user):
    st.markdown(f"""
    <div style="padding: 1.2rem 0 1rem 0; border-bottom: 1px solid var(--sb-border); margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="sb-icon-box" style="width: 40px; height: 40px;">
                {icon_svg("calendar", size=22, color="#4F46E5")}
            </div>
            <div>
                <h2 style="font-size: 1.5rem; font-weight: 800; margin: 0; color: #0F172A;">Book time with a counselor</h2>
                <p style="font-size: 0.92rem; color: #64748B; margin: 0.15rem 0 0 0;">Request a private, one-on-one session at a convenient school time.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("appointment_form"):
        reason = st.selectbox("Reason for meeting", ["Wellbeing support", "Bullying concern", "Friendship or social conflict", "Academic stress", "Other"])
        c1, c2 = st.columns(2)
        day = c1.date_input("Preferred date", min_value=date.today())
        time = c2.selectbox("Preferred time", ["Before school", "Morning", "Lunch break", "After school"])
        notes = st.text_area("Additional notes (optional)", max_chars=1200, placeholder="Any details that help the counselor prepare...")
        sent = st.form_submit_button("Request appointment", type="primary")

    if sent:
        now_iso = datetime.now(timezone.utc).isoformat()
        execute(
            "INSERT INTO appointments(student_id, reason, preferred_date, preferred_time, notes, created_at) VALUES(?,?,?,?,?,?)",
            (user['id'], reason, str(day), time, notes.strip(), now_iso),
        )
        st.success("Appointment request submitted. A counselor will confirm details with you.")

# ── Learning Hub ────────────────────────────────────────────────────────────
def learning_page():
    topics = {
        "Bullying": {
            "intro": "Bullying is repeated hurtful behavior. You deserve respect and support.",
            "steps": [
                "Move to a safer space whenever possible.",
                "Keep a record of dates, times, and what occurred.",
                "Speak with a trusted adult or submit a report here."
            ]
        },
        "Cyberbullying": {
            "intro": "Online harassment is real and unacceptable. Support is always available.",
            "steps": [
                "Pause before reacting or responding to hurtful messages.",
                "Save evidence, screenshots, timestamps, and usernames.",
                "Block and report the offending accounts."
            ]
        },
        "Digital safety": {
            "intro": "Habits to protect your privacy and wellbeing online.",
            "steps": [
                "Use strong, distinct passwords and two-factor authentication.",
                "Never share private location data or credentials.",
                "Ask a trusted adult if an online interaction feels uncomfortable."
            ]
        },
        "Mental wellbeing": {
            "intro": "Difficult emotions are common; seeking support is a sign of strength.",
            "steps": [
                "Notice and acknowledge feelings without self-judgment.",
                "Take a small pause: hydration, steady breathing, or quiet time.",
                "Reach out to your school counselor or a supportive adult."
            ]
        },
        "Respect": {
            "intro": "Mutual respect fosters healthy friendships and safe schools.",
            "steps": [
                "Listen actively and honor personal boundaries.",
                "Include peers and treat differing perspectives with kindness.",
                "Speak up or seek adult assistance when someone is treated unfairly."
            ]
        },
    }

    st.markdown(f"""
    <div style="padding: 1.2rem 0 1rem 0; border-bottom: 1px solid var(--sb-border); margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="sb-icon-box" style="width: 40px; height: 40px;">
                {icon_svg("book", size=22, color="#4F46E5")}
            </div>
            <div>
                <h2 style="font-size: 1.5rem; font-weight: 800; margin: 0; color: #0F172A;">Learn and stay safe</h2>
                <p style="font-size: 0.92rem; color: #64748B; margin: 0.15rem 0 0 0;">Guidance and resources for safety, wellbeing, and digital respect.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected = st.session_state.get("learning_topic")
    if selected in topics:
        topic = topics[selected]
        if st.button("Back to all topics", type="secondary"):
            st.session_state.learning_topic = None
            st.rerun()
        st.subheader(selected)
        st.write(topic['intro'])
        st.markdown("<p style='font-size: 0.95rem; font-weight: 700; color: #0F172A; margin-top: 1.2rem;'>Recommended steps</p>", unsafe_allow_html=True)
        for number, step in enumerate(topic["steps"], 1):
            st.markdown(f"<div class='sb-notice-block' style='padding: 0.85rem 1.1rem; margin-bottom: 0.6rem;'><strong>{number}.</strong> {step}</div>", unsafe_allow_html=True)
        return

    cols = st.columns(3)
    for i, (topic, body) in enumerate(topics.items()):
        col = cols[i % 3]
        with col:
            st.markdown(f"""
            <div class='card' style="min-height: 170px;">
                <div class="sb-icon-box">{icon_svg("book", size=22, color="#4F46E5")}</div>
                <h3>{topic}</h3>
                <p class='muted'>{body['intro']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Read guide", key="read_" + topic, use_container_width=True):
                st.session_state.learning_topic = topic
                st.rerun()

# ── Activity ────────────────────────────────────────────────────────────────
def activity_page(user):
    st.markdown(f"""
    <div style="padding: 1.2rem 0 1rem 0; border-bottom: 1px solid var(--sb-border); margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="sb-icon-box" style="width: 40px; height: 40px;">
                {icon_svg("clock", size=22, color="#4F46E5")}
            </div>
            <div>
                <h2 style="font-size: 1.5rem; font-weight: 800; margin: 0; color: #0F172A;">My activity</h2>
                <p style="font-size: 0.92rem; color: #64748B; margin: 0.15rem 0 0 0;">View your submitted reports, appointment requests, and wellbeing trends.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Submitted reports")
    reports = query("SELECT id,category,priority,status,created_at FROM reports WHERE student_id=? ORDER BY id DESC", (user['id'],))
    if reports:
        df_rep = pd.DataFrame(reports)
        df_rep.columns = [c.replace("_", " ").title() for c in df_rep.columns]
        st.dataframe(df_rep, use_container_width=True, hide_index=True)
    else:
        st.caption("No reports submitted under this account.")

    st.divider()

    st.subheader("Appointment requests")
    appts = query("SELECT reason, preferred_date, preferred_time, status, created_at FROM appointments WHERE student_id=? ORDER BY preferred_date DESC", (user['id'],))
    if appts:
        df_appts = pd.DataFrame(appts)
        df_appts.columns = [c.replace("_", " ").title() for c in df_appts.columns]
        st.dataframe(df_appts, use_container_width=True, hide_index=True)
    else:
        st.caption("No appointment requests recorded.")

    st.divider()

    st.subheader("Wellbeing check-in history")
    checkins = query("SELECT week_start,mood,mood_label FROM checkins WHERE student_id=? ORDER BY week_start", (user['id'],))
    if checkins:
        st.line_chart(pd.DataFrame(checkins).set_index("week_start")["mood"])
    else:
        st.caption("No check-in history recorded yet.")

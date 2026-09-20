"""Student portal views: home, help reporting, weekly check-ins, appointments, learning, and activity.
Zero emoji, outline SVG icons, flat card styling, sentence case throughout.
Buddy chat is hidden per design direction.
"""
from datetime import date, timedelta, datetime, timezone
import streamlit as st
import pandas as pd
from ai import analyze_report, format_report_from_state, DEFAULT_REPORT_STATE
from database import execute, one, query, create_report, get_setting
from utils import week_start
from icons import icon_svg

def nav(user):
    # Sentence case, zero emoji. Note: Buddy chat is hidden per design specification.
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
    # Calm bright header on white background (no gradient banner)
    st.markdown(f"""
    <div style="padding: 1.25rem 0 1rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.5rem;">
        <h1 style="font-size: 1.6rem; font-weight: 700; margin: 0 0 0.25rem 0; color: #111827;">Welcome, {disp}</h1>
        <p style="font-size: 0.95rem; color: #6B7280; margin: 0;">A private, supportive space to ask for guidance, complete check-ins, or request time with a counselor.</p>
    </div>
    """, unsafe_allow_html=True)

    # Flat cards with hairline borders and outline icons (no buddy chat)
    cards = [
        ("shield", "I need help", "Share a concern with a school counselor", "Help"),
        ("smile", "Weekly check-in", "A brief pulse on how your week is going", "Check-in"),
        ("calendar", "Book counselor", "Request a private meeting", "Book"),
    ]
    cols = st.columns(3)
    for col, (icon_name, title, desc, target) in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class='card'>
                <div style="margin-bottom: 0.5rem; color: #4B5563;">{icon_svg(icon_name, size=24, color="#4B5563")}</div>
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
                <div style="margin-bottom: 0.5rem; color: #4B5563;">{icon_svg(icon_name, size=24, color="#4B5563")}</div>
                <h3>{title}</h3>
                <p class='muted'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open", key="go_" + target, use_container_width=True):
                st.session_state.page = target
                st.rerun()

# ── I Need Help Flow (Sentence case, clean bordered consent block, flat styling) ──
def help_page(user):
    st.markdown(f"""
    <div style="padding: 1rem 0 0.8rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.25rem;">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            {icon_svg("shield", size=22, color="#4B5563")}
            <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0; color: #111827;">Tell us what happened</h2>
        </div>
        <p style="font-size: 0.9rem; color: #6B7280; margin: 0.25rem 0 0 0;">A school counselor reviews every report to ensure safety and support.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("report_submitted"):
        st.success("Your report has been submitted for counselor review. Thank you for speaking up.")
        if st.button("Submit another concern", type="secondary"):
            st.session_state.report_submitted = False
            for k in ["help_messages", "help_report_state", "help_show_review"]:
                st.session_state.pop(k, None)
            st.rerun()
        return

    # Visual separation for consent notice (bordered block, calm aesthetic)
    st.markdown(f"""
    <div class="sb-notice-block">
        <div class="sb-notice-title">
            {icon_svg("info", size=18, color="#4B5563")}
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
        # Single primary green action button
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

# ── Weekly Check-in (Flat form, sentence case) ───────────────────────────────
def checkin_page(user):
    st.markdown(f"""
    <div style="padding: 1rem 0 0.8rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.25rem;">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            {icon_svg("smile", size=22, color="#4B5563")}
            <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0; color: #111827;">Weekly wellbeing check-in</h2>
        </div>
        <p style="font-size: 0.9rem; color: #6B7280; margin: 0.25rem 0 0 0;">A brief check-in helps counselors notice when additional support may be helpful.</p>
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

# ── Book Counselor (Flat form, sentence case) ────────────────────────────────
def booking_page(user):
    st.markdown(f"""
    <div style="padding: 1rem 0 0.8rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.25rem;">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            {icon_svg("calendar", size=22, color="#4B5563")}
            <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0; color: #111827;">Book time with a counselor</h2>
        </div>
        <p style="font-size: 0.9rem; color: #6B7280; margin: 0.25rem 0 0 0;">Request a private, one-on-one session at a convenient school time.</p>
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

# ── Learning Hub (Flat card layout, sentence case) ───────────────────────────
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
    <div style="padding: 1rem 0 0.8rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.25rem;">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            {icon_svg("book", size=22, color="#4B5563")}
            <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0; color: #111827;">Learn and stay safe</h2>
        </div>
        <p style="font-size: 0.9rem; color: #6B7280; margin: 0.25rem 0 0 0;">Guidance and resources for safety, wellbeing, and digital respect.</p>
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
        st.markdown("<p style='font-size: 0.9rem; font-weight: 600; color: #374151; margin-top: 1rem;'>Recommended steps</p>", unsafe_allow_html=True)
        for number, step in enumerate(topic["steps"], 1):
            st.markdown(f"<div class='sb-notice-block' style='padding: 0.75rem 1rem; margin-bottom: 0.5rem;'><strong>{number}.</strong> {step}</div>", unsafe_allow_html=True)
        return

    cols = st.columns(3)
    for i, (topic, body) in enumerate(topics.items()):
        col = cols[i % 3]
        with col:
            st.markdown(f"""
            <div class='card' style="min-height: 160px;">
                <h3>{topic}</h3>
                <p class='muted'>{body['intro']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Read guide", key="read_" + topic, use_container_width=True):
                st.session_state.learning_topic = topic
                st.rerun()

# ── Activity (Flat table, sentence case) ─────────────────────────────────────
def activity_page(user):
    st.markdown(f"""
    <div style="padding: 1rem 0 0.8rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.25rem;">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            {icon_svg("clock", size=22, color="#4B5563")}
            <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0; color: #111827;">My activity</h2>
        </div>
        <p style="font-size: 0.9rem; color: #6B7280; margin: 0.25rem 0 0 0;">View your submitted reports, appointment requests, and wellbeing trends.</p>
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

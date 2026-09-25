"""Shared views: calm light entry screen, role selection cards, sign in, and anonymous reporting."""
import streamlit as st
from ai import analyze_report
from database import create_report, get_setting
from icons import icon_svg, school_mark_svg

def render_login(login_fn):
    # ── Calm, bright header with the real school crest ──
    st.markdown(f"""
    <div style="padding: 1.5rem 0 1.25rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.75rem;">
        <div style="display: flex; align-items: center; gap: 0.85rem; margin-bottom: 0.5rem;">
            <img src="app/static/dps-rak-logo.png" style="width: 48px; height: 48px; object-fit: contain;" alt="Delhi Private School, Ras Al Khaimah logo" />
            <div>
                <h1 style="font-size: 1.6rem; font-weight: 700; letter-spacing: -0.02em; margin: 0; color: #111827;">SafeBridge</h1>
            </div>
        </div>
        <p style="font-size: 0.95rem; color: #6B7280; margin: 0; line-height: 1.45;">
            A private, human-led space to ask for support or raise a concern.
        </p>
        <p style="font-size: 0.8rem; color: #9CA3AF; margin: 0.35rem 0 0 0;">
            Built for Delhi Private School, Ras Al Khaimah.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 0.9rem; font-weight: 600; color: #374151; margin-bottom: 0.75rem;'>Select an option to continue</p>", unsafe_allow_html=True)

    cols = st.columns(4)

    # 1. Student card — blue
    with cols[0]:
        st.markdown(f"""
        <div class='card accent-blue'>
            <div class="sb-icon-chip blue">{icon_svg("user", size=20)}</div>
            <h3>Student</h3>
            <p class='muted'>Wellbeing tools, check-ins, and appointments</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Continue", key="role_btn_student", use_container_width=True):
            st.session_state.login_role = "student"

    # 2. Counselor card — purple
    with cols[1]:
        st.markdown(f"""
        <div class='card accent-purple'>
            <div class="sb-icon-chip purple">{icon_svg("compass", size=20)}</div>
            <h3>Counselor</h3>
            <p class='muted'>Review concerns and support students</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Continue", key="role_btn_counselor", use_container_width=True):
            st.session_state.login_role = "counselor"

    # 3. Administrator card — amber
    with cols[2]:
        st.markdown(f"""
        <div class='card accent-amber'>
            <div class="sb-icon-chip amber">{icon_svg("chart", size=20)}</div>
            <h3>Administrator</h3>
            <p class='muted'>Privacy-preserving analytics and settings</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Continue", key="role_btn_admin", use_container_width=True):
            st.session_state.login_role = "admin"

    # 4. Anonymous Reporting card — green (its own tinted highlight card)
    allow_anon = get_setting("allow_anonymous_reports", "1") == "1"
    with cols[3]:
        if allow_anon:
            st.markdown(f"""
            <div class="sb-anon-marker"></div>
            <div class='sb-card-highlight'>
                <div class="sb-icon-chip green">{icon_svg("anonymous", size=20)}</div>
                <h3>Anonymous report</h3>
                <p>Speak up without signing in</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Speak up safely", key="btn_anon_flow", type="primary", use_container_width=True):
                st.session_state.anonymous_mode = True
                st.rerun()
        else:
            st.markdown(f"""
            <div class='card' style="opacity: 0.7;">
                <div class="sb-icon-chip" style="background:#F3F4F6; color:#9CA3AF;">{icon_svg("anonymous", size=20)}</div>
                <h3>Anonymous report</h3>
                <p class='muted'>Disabled by school administrator</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Role Login Form ──
    if role := st.session_state.get("login_role"):
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        st.subheader(f"{role.title()} sign in")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            # Sign in button gets the filled green primary treatment
            submitted = st.form_submit_button("Sign in", type="primary")
        if submitted:
            if login_fn(username, password, role):
                st.rerun()
            else:
                err = st.session_state.get("login_error") or "Those details do not match this account type, or the account is inactive."
                st.error(err)

def render_anonymous():
    st.markdown(f"""
    <div style="padding: 1rem 0 0.8rem 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 1.25rem;">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            {icon_svg("anonymous", size=22, color="#27500A")}
            <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0; color: #111827;">Anonymous report</h2>
        </div>
        <p style="font-size: 0.9rem; color: #6B7280; margin: 0.25rem 0 0 0;">Your submission is completely unlinked from any account.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("anon_submitted"):
        st.success("Your anonymous report has been sent for counselor review. Thank you for speaking up.")
        if st.button("Back to home", type="secondary"):
            st.session_state.anon_submitted = False
            st.session_state.anonymous_mode = False
            st.rerun()
        return

    # Visual separation for consent notice (bordered block)
    st.markdown(f"""
    <div class="sb-notice-block">
        <div class="sb-notice-title">
            {icon_svg("info", size=18, color="#4B5563")}
            <span>Privacy and reporting notice</span>
        </div>
        <div class="sb-notice-body">
            <strong>What is collected:</strong> Only the details and optional evidence you provide below.<br>
            <strong>Identity:</strong> Fully anonymous. No IP addresses or account identifiers are stored.<br>
            <strong>Reviewers:</strong> Designated school safeguarding counselors only.<br>
            <strong>Advisory tools:</strong> Any automated categorization is an organizational aid only. All safeguarding decisions and outreach are made by human counselors.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("If someone is in immediate physical danger, please contact local emergency services or alert a trusted adult now.")

    if st.button("Back to home", type="secondary"):
        st.session_state.anonymous_mode = False
        st.rerun()

    with st.form("anonymous_report"):
        text = st.text_area("Describe what happened", max_chars=6000, placeholder="Share only what you feel safe sharing.")
        evidence = st.file_uploader("Optional evidence", type=["png", "jpg", "jpeg", "pdf"], help="PNG, JPG, or PDF up to 5 MB")
        consent = st.checkbox("I understand how this report will be reviewed and handled", value=True)
        # Primary green action button
        sent = st.form_submit_button("Send report", type="primary")

    if sent:
        if not consent:
            st.error("Please confirm you understand how your report is handled before submitting.")
        elif len(text.strip()) < 10:
            st.error("Please provide a little more detail (at least 10 characters) so a counselor can understand the concern.")
        else:
            try:
                create_report(None, True, text.strip(), analyze_report(text), evidence)
                st.session_state.anon_submitted = True
                st.rerun()
            except ValueError as error:
                st.error(str(error))

"""Interactive Button-Guided Report Submission Component for SafeBridge AI.
Allows students and anonymous reporters to submit concerns step-by-step
using intuitive, colorful choice buttons rather than freeform writing alone.
"""

from datetime import datetime, timezone
import streamlit as st
from ai import analyze_report
from database import create_report, get_setting
from icons import icon_svg

STEPS = [
    {
        "id": "category",
        "title": "What happened?",
        "subtitle": "Select the option that best describes what you experienced or witnessed.",
        "icon": "shield",
        "options": [
            {
                "label": "Verbal Bullying",
                "desc": "Name-calling, insults, teasing, hurtful remarks, or yelling",
                "icon": "message_square",
                "tag": "Verbal"
            },
            {
                "label": "Physical Bullying",
                "desc": "Pushing, hitting, kicking, tripping, or damaging personal items",
                "icon": "alert",
                "tag": "Physical"
            },
            {
                "label": "Cyberbullying & Online",
                "desc": "Harassing messages, hurtful social media posts, group chat exclusion, or fake accounts",
                "icon": "send",
                "tag": "Online"
            },
            {
                "label": "Social Exclusion & Rumors",
                "desc": "Being intentionally left out, gossiped about, or isolated by peers",
                "icon": "users",
                "tag": "Social"
            },
            {
                "label": "Threats or Intimidation",
                "desc": "Threats of violence, blackmail, or being pressured to do things against your will",
                "icon": "lock",
                "tag": "Threat"
            },
            {
                "label": "Concern for a Classmate",
                "desc": "You are worried about another student's emotional, mental, or physical safety",
                "icon": "heart",
                "tag": "Peer care"
            },
            {
                "label": "Other Safety Concern",
                "desc": "Something else that doesn't fit the categories above",
                "icon": "help_circle",
                "tag": "General"
            }
        ]
    },
    {
        "id": "location",
        "title": "Where did it happen?",
        "subtitle": "Choose the location where this incident took place.",
        "icon": "map_pin",
        "options": [
            {
                "label": "Classroom or Study Hall",
                "desc": "During class time or in an academic room",
                "icon": "book",
                "tag": "Classroom"
            },
            {
                "label": "Hallway, Stairs, or Lockers",
                "desc": "In transit between classes or near locker bays",
                "icon": "compass",
                "tag": "Hallway"
            },
            {
                "label": "Playground, Field, or Gym",
                "desc": "During recess, sports, PE, or outdoor break",
                "icon": "smile",
                "tag": "Sports/Play"
            },
            {
                "label": "Cafeteria or Lunch Area",
                "desc": "During lunch or snack breaks",
                "icon": "users",
                "tag": "Cafeteria"
            },
            {
                "label": "Restroom or Locker Room",
                "desc": "Restrooms, changing rooms, or unmonitored facilities",
                "icon": "lock",
                "tag": "Restroom"
            },
            {
                "label": "Online (Social Media, Chats, Games)",
                "desc": "Instagram, Snapchat, Discord, WhatsApp, TikTok, Roblox, or SMS",
                "icon": "send",
                "tag": "Online"
            },
            {
                "label": "School Bus or Commute",
                "desc": "On the bus or walking to/from school",
                "icon": "clock",
                "tag": "Transit"
            },
            {
                "label": "Off Campus / Outside School",
                "desc": "Outside of school property or after school hours",
                "icon": "map_pin",
                "tag": "Off-campus"
            }
        ]
    },
    {
        "id": "timing",
        "title": "When did this occur?",
        "subtitle": "Helps counselors understand urgency and timing.",
        "icon": "clock",
        "options": [
            {
                "label": "Just Today / A Few Hours Ago",
                "desc": "Happened today and is very recent",
                "icon": "zap",
                "tag": "Today"
            },
            {
                "label": "Earlier This Week",
                "desc": "Occurred within the past few days",
                "icon": "calendar",
                "tag": "This week"
            },
            {
                "label": "Happening Repeatedly / Ongoing",
                "desc": "This is an ongoing pattern over days or weeks",
                "icon": "alert",
                "tag": "Ongoing"
            },
            {
                "label": "Over a Week Ago",
                "desc": "Happened further in the past but still impacts you",
                "icon": "clock",
                "tag": "Past"
            },
            {
                "label": "Not Sure / Gradual Pattern",
                "desc": "Hard to pinpoint a single date",
                "icon": "help_circle",
                "tag": "Pattern"
            }
        ]
    },
    {
        "id": "who",
        "title": "Who was involved?",
        "subtitle": "You can be as specific as you feel comfortable.",
        "icon": "users",
        "options": [
            {
                "label": "Another Student in My Grade / Class",
                "desc": "A peer from your regular classes or year level",
                "icon": "user",
                "tag": "Classmate"
            },
            {
                "label": "A Group of Multiple Students",
                "desc": "Two or more students acting together",
                "icon": "users",
                "tag": "Group"
            },
            {
                "label": "An Older or Younger Student",
                "desc": "Someone in a different grade level",
                "icon": "user",
                "tag": "Other grade"
            },
            {
                "label": "Someone Online / Unknown Identity",
                "desc": "An anonymous profile or online contact",
                "icon": "anonymous",
                "tag": "Unknown"
            },
            {
                "label": "I Prefer Not to Say Right Now",
                "desc": "You can share this in private with a counselor later",
                "icon": "lock",
                "tag": "Confidential"
            }
        ]
    },
    {
        "id": "feeling",
        "title": "How are you feeling right now?",
        "subtitle": "Your wellbeing matters most. Let us know how this is affecting you.",
        "icon": "heart",
        "options": [
            {
                "label": "I feel unsafe or scared at school",
                "desc": "You feel anxious about being in school or around certain areas",
                "icon": "alert",
                "tag": "Urgent support"
            },
            {
                "label": "I feel very upset, sad, or overwhelmed",
                "desc": "This is hurting your emotional wellbeing or focus",
                "icon": "heart",
                "tag": "Emotional care"
            },
            {
                "label": "I feel frustrated or angry and want it to stop",
                "desc": "You want counselors to address the situation directly",
                "icon": "shield",
                "tag": "Action requested"
            },
            {
                "label": "I am safe right now, but wanted counselors aware",
                "desc": "You are currently okay, but want this on record",
                "icon": "shield_check",
                "tag": "Informational"
            },
            {
                "label": "I am worried about someone else's wellbeing",
                "desc": "You are reporting on behalf of a friend or peer",
                "icon": "users",
                "tag": "Peer concern"
            }
        ]
    }
]

def init_guided_state(prefix=""):
    """Initialize session state for guided report wizard."""
    step_key = f"{prefix}guided_step"
    data_key = f"{prefix}guided_data"
    
    if step_key not in st.session_state:
        st.session_state[step_key] = 0
    if data_key not in st.session_state:
        st.session_state[data_key] = {
            "category": None,
            "location": None,
            "timing": None,
            "who": None,
            "feeling": None,
            "who_detail": "",
            "extra_notes": "",
            "anonymous": False,
        }

def render_guided_stepper(current_step, total_steps):
    """Render a modern visual stepper with pills indicating progress."""
    steps_html = []
    labels = ["Concern", "Location", "Timing", "Involved", "Wellbeing", "Review"]
    
    for i, label in enumerate(labels):
        if i < current_step:
            status = "completed"
            symbol = "&#10003;"
        elif i == current_step:
            status = "active"
            symbol = str(i + 1)
        else:
            status = ""
            symbol = str(i + 1)
        
        steps_html.append(
            f'<div class="sb-step-item {status}">'
            f'<div class="sb-step-circle">{symbol}</div>'
            f'<span>{label}</span>'
            f'</div>'
        )
    
    html = f'<div class="sb-stepper-wrap">{"".join(steps_html)}</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_guided_report_wizard(user=None, prefix=""):
    """
    Renders an interactive, button-guided reporting experience.
    Works for both logged-in students and anonymous users.
    """
    init_guided_state(prefix)
    step_key = f"{prefix}guided_step"
    data_key = f"{prefix}guided_data"
    
    current_step = st.session_state[step_key]
    state_data = st.session_state[data_key]
    
    total_steps = len(STEPS) + 1  # 5 question steps + 1 review step
    render_guided_stepper(current_step, total_steps)
    
    # ── Questions Steps (0 to 4) ─────────────────────────────────────────────
    if current_step < len(STEPS):
        step_info = STEPS[current_step]
        step_id = step_info["id"]
        
        header_html = (
            f'<div style="margin-bottom: 1.25rem;">'
            f'<div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.35rem;">'
            f'<div class="sb-icon-box" style="width: 36px; height: 36px;">'
            f'{icon_svg(step_info["icon"], size=20, color="#4F46E5")}'
            f'</div>'
            f'<h3 style="margin: 0; font-size: 1.35rem; font-weight: 700; color: #0F172A;">'
            f'{step_info["title"]}'
            f'</h3>'
            f'</div>'
            f'<p style="margin: 0; color: #64748B; font-size: 0.92rem;">'
            f'{step_info["subtitle"]}'
            f'</p>'
            f'</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)
        
        selected_val = state_data.get(step_id)
        
        # Display options as interactive grid cards
        options = step_info["options"]
        cols = st.columns(2)
        
        for idx, opt in enumerate(options):
            col = cols[idx % 2]
            with col:
                is_selected = (selected_val == opt["label"])
                border_color = "#4F46E5" if is_selected else "#E2E8F0"
                bg_color = "#EEF2FF" if is_selected else "#FFFFFF"
                check_badge = '<span class="sb-badge sb-badge-accent" style="margin-left:auto;">&#10003; Selected</span>' if is_selected else f'<span class="sb-badge sb-badge-neutral" style="margin-left:auto;">{opt["tag"]}</span>'
                
                card_html = (
                    f'<div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 14px; padding: 1rem 1.15rem; margin-bottom: 0.75rem; min-height: 105px; display: flex; flex-direction: column; justify-content: space-between;">'
                    f'<div style="display: flex; align-items: flex-start; gap: 0.65rem;">'
                    f'<div style="color: #4F46E5; margin-top: 2px;">{icon_svg(opt["icon"], size=20, color="#4F46E5")}</div>'
                    f'<div style="flex-grow: 1;">'
                    f'<div style="font-weight: 700; font-size: 0.96rem; color: #0F172A; margin-bottom: 0.2rem;">{opt["label"]}</div>'
                    f'<div style="font-size: 0.84rem; color: #64748B; line-height: 1.4;">{opt["desc"]}</div>'
                    f'</div>'
                    f'</div>'
                    f'<div style="display: flex; justify-content: flex-end; margin-top: 0.5rem;">{check_badge}</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
                
                btn_label = f"✓ Chosen: {opt['label']}" if is_selected else f"Select: {opt['label']}"
                btn_type = "primary" if is_selected else "secondary"
                
                if st.button(btn_label, key=f"{prefix}opt_{step_id}_{idx}", type=btn_type, use_container_width=True):
                    state_data[step_id] = opt["label"]
                    # Auto advance to next step for swift, responsive experience!
                    if current_step < len(STEPS):
                        st.session_state[step_key] = current_step + 1
                    st.rerun()

        # If on the 'who' step, allow optional text clarification
        if step_id == "who":
            st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
            who_note = st.text_input(
                "Optional: Names, handles, or nicknames of who was involved (strictly confidential)",
                value=state_data.get("who_detail", ""),
                placeholder="Only share if you feel comfortable doing so..."
            )
            state_data["who_detail"] = who_note

        # Navigation buttons for wizard
        st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
        nav_c1, nav_c2, nav_c3 = st.columns([1, 2, 1])
        
        with nav_c1:
            if current_step > 0:
                if st.button("← Previous", key=f"{prefix}prev_{current_step}", use_container_width=True):
                    st.session_state[step_key] = current_step - 1
                    st.rerun()
                    
        with nav_c3:
            can_advance = bool(state_data.get(step_id))
            if st.button("Next step →", key=f"{prefix}next_{current_step}", type="primary", disabled=not can_advance, use_container_width=True):
                st.session_state[step_key] = current_step + 1
                st.rerun()
                
        if not can_advance:
            st.caption("Please select an option above to proceed to the next step.")

    # ── Step 5: Review & Submit (Final Step) ──────────────────────────────────
    else:
        rev_header = (
            '<div style="margin-bottom: 1.25rem;">'
            '<div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.35rem;">'
            '<div class="sb-icon-box" style="width: 36px; height: 36px; background: #ECFDF5; color: #10B981;">'
            '<span style="font-size: 1.2rem;">📋</span>'
            '</div>'
            '<h3 style="margin: 0; font-size: 1.35rem; font-weight: 700; color: #0F172A;">Review & Send Your Report</h3>'
            '</div>'
            '<p style="margin: 0; color: #64748B; font-size: 0.92rem;">Here is a summary of what you selected. You can add extra details or attachments before sending.</p>'
            '</div>'
        )
        st.markdown(rev_header, unsafe_allow_html=True)
        
        # Assembled visual preview card
        cat = state_data.get("category") or "Not specified"
        loc = state_data.get("location") or "Not specified"
        timing = state_data.get("timing") or "Not specified"
        who = state_data.get("who") or "Not specified"
        if state_data.get("who_detail"):
            who += f" ({state_data['who_detail']})"
        feeling = state_data.get("feeling") or "Not specified"
        
        rev_card = (
            f'<div class="sb-review-card">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #E2E8F0; padding-bottom: 0.75rem;">'
            f'<span style="font-size: 1.05rem; font-weight: 700; color: #0F172A;">Generated Report Summary</span>'
            f'<span class="sb-badge sb-badge-accent">Guided Mode</span>'
            f'</div>'
            f'<div class="sb-review-item">'
            f'<div class="sb-review-label">Concern Type</div>'
            f'<div class="sb-review-val"><span class="sb-badge sb-badge-warning">{cat}</span></div>'
            f'</div>'
            f'<div class="sb-review-item">'
            f'<div class="sb-review-label">Location</div>'
            f'<div class="sb-review-val">{loc}</div>'
            f'</div>'
            f'<div class="sb-review-item">'
            f'<div class="sb-review-label">When</div>'
            f'<div class="sb-review-val">{timing}</div>'
            f'</div>'
            f'<div class="sb-review-item">'
            f'<div class="sb-review-label">Involved</div>'
            f'<div class="sb-review-val">{who}</div>'
            f'</div>'
            f'<div class="sb-review-item">'
            f'<div class="sb-review-label">Current Impact</div>'
            f'<div class="sb-review-val"><span class="sb-badge sb-badge-success">{feeling}</span></div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(rev_card, unsafe_allow_html=True)
        
        with st.form(f"{prefix}guided_final_form"):
            extra_notes = st.text_area(
                "Would you like to add anything else in your own words? (Optional)",
                value=state_data.get("extra_notes", ""),
                placeholder="Any extra context, background, or message for the counselor...",
                max_chars=4000
            )
            evidence = st.file_uploader(
                "Optional evidence (Screenshot, photo, or document)",
                type=["png", "jpg", "jpeg", "pdf"],
                help="PNG, JPG, or PDF up to 5 MB"
            )
            
            # Anonymity option
            allow_anon = get_setting("allow_anonymous_reports", "1") == "1"
            if user:
                if allow_anon:
                    is_anon = st.checkbox("Submit anonymously (omit student handle from counselor view)", value=state_data.get("anonymous", False))
                else:
                    is_anon = False
                    st.caption("Anonymous reporting is currently disabled by school administration.")
            else:
                is_anon = True
                st.markdown("<p style='font-size: 0.85rem; color: #059669; font-weight: 600;'>&#10003; Submitting anonymously — no personal account details will be attached.</p>", unsafe_allow_html=True)

            consent = st.checkbox("I confirm this information is accurate to the best of my knowledge and understand it will be reviewed confidentially by school counseling staff.", value=True)
            
            col_b1, col_b2 = st.columns([1, 1])
            submitted = st.form_submit_button("Submit report to counselors", type="primary", use_container_width=True)

        col_nav1, col_nav2 = st.columns([1, 3])
        with col_nav1:
            if st.button("← Edit answers", key=f"{prefix}edit_answers", use_container_width=True):
                st.session_state[step_key] = 0
                st.rerun()

        if submitted:
            if not consent:
                st.error("Please confirm your understanding by checking the acknowledgment box before submitting.")
            else:
                # Compile comprehensive report text
                report_lines = [
                    f"Incident Category: {cat}",
                    f"Location: {loc}",
                    f"When: {timing}",
                    f"People Involved: {who}",
                    f"Student Wellbeing & Feelings: {feeling}",
                ]
                if extra_notes.strip():
                    report_lines.append(f"Additional Notes: {extra_notes.strip()}")
                
                compiled_text = "\n".join(report_lines)
                
                try:
                    analysis = analyze_report(compiled_text)
                    student_id = user["id"] if user and not is_anon else (user["id"] if user else None)
                    create_report(student_id, is_anon, compiled_text, analysis, evidence)
                    
                    # Reset wizard state
                    st.session_state[step_key] = 0
                    st.session_state[data_key] = {
                        "category": None, "location": None, "timing": None,
                        "who": None, "feeling": None, "who_detail": "",
                        "extra_notes": "", "anonymous": False,
                    }
                    
                    if prefix == "anon_":
                        st.session_state["anon_submitted"] = True
                    else:
                        st.session_state["report_submitted"] = True
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

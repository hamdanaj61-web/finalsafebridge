"""AI assistance and safety engine for SafeBridge AI.
Restricted exclusively to counselor-triggered suggestions with privacy-preserving redaction.
Student-facing flows operate entirely on deterministic local safety logic.
AI never decides guilt, discipline, or safeguarding outcomes.
"""
import json
import os
import re

CATEGORIES = ["Verbal Bullying", "Physical Bullying", "Cyberbullying", "Exclusion", "Harassment", "Mental Health Concern", "Other"]

SYSTEM = """You help school counselors organize a student concern. Never decide guilt, discipline, or a consequence. Return strictly JSON with summary, category, location, severity, priority. category must be one allowed category; severity and priority Low/Medium/High. Use neutral, factual language and say unknown when absent."""

CHAT_SYSTEM = """You are SafeBridge, a supportive school wellbeing helper. Reply in one short, warm sentence. Never promise secrecy, decide guilt, or tell a student to confront anyone. Thank them for sharing and ask only the requested next question. If there is immediate danger, say to find a trusted adult right now."""

BUDDY_SYSTEM = """You are SafeBridge Buddy, a warm, safe school wellbeing companion for students.
Rules you must always follow:
- NEVER promise secrecy or full confidentiality — say a trusted adult may need to know if there is danger
- NEVER decide who is at fault or what the punishment should be
- If immediate danger (self-harm, violence, abuse): always include "Please find a trusted adult or call emergency services right now."
- Keep replies warm, concise (2-3 sentences), and supportive — use clear language
- Validate feelings first, then offer gentle guidance
- Gently suggest formal reporting or booking a counselor for ongoing concerns
- NEVER give medical, legal, or diagnostic advice
- End each reply with either a gentle follow-up question or an encouraging statement
Return only the reply text with no markdown formatting."""

ACTION_SYSTEM = """You are a school safeguarding and wellbeing advisor reviewing an incident concern report.
Suggest 3-5 specific, practical actions a school counselor should consider taking.
Return strictly JSON: {
  "actions": [{"title": "short action title", "detail": "1-2 sentence explanation", "urgency": "Immediate|Soon|Routine"}],
  "risk_level": "Low|Medium|High",
  "risk_rationale": "one sentence explaining the risk assessment"
}
Be specific to a supportive school safeguarding context. Focus on student care, safety assessment, and de-escalation.
Never suggest punitive discipline — that is for designated safeguarding leads, not this advisory tool."""

DEFAULT_REPORT_STATE = {
    "incident": None,
    "location": None,
    "when": None,
    "people_involved": None,
    "frequency": None,
    "feelings": None,
    "safety_concerns": None,
    "anonymity_preference": None,
}

DYNAMIC_CHAT_SYSTEM = """You are SafeBridge Buddy — a warm, friendly wellbeing companion for school students. You talk like a caring mentor, not a form or a robot.

Your personality:
- Casual, warm, and genuinely caring — like a supportive older mentor
- You adapt your tone: friendly for casual chat, gentle and empathetic for hard topics
- You NEVER sound scripted, stiff, or like you are reading from a checklist
- You are curious and ask natural follow-up questions based on what the student said

INTENT CLASSIFICATION (choose one):
- "casual_chat": greetings, small talk, jokes, food, games, random chitchat — respond naturally and playfully!
- "wellbeing": expressing emotions (sad, anxious, lonely, stressed) without describing a specific incident
- "bullying_report": describing bullying, harassment, being hurt, threatened, excluded, or cyberbullied
- "book_counselor": wants to speak to / schedule with a school counselor
- "ask_advice": asking how to handle a social/school conflict
- "learn_bullying": asking to learn what bullying or cyberbullying is

CRITICAL RULES — breaking these is a failure:
1. For greetings/casual chat: be natural! Say "Hey!" or "Hi, great to hear from you!" — NEVER say "Thank you for sharing" for a greeting.
2. NEVER decide guilt or punishment.
3. NEVER follow a fixed question sequence. Ask only what makes sense NEXT based on the conversation.
4. NEVER re-ask something the student already told you.
5. If IMMEDIATE DANGER (self-harm, suicide, violence, weapons): set immediate_danger=true and urgently advise finding a trusted adult or emergency services.
6. For bullying_report: naturally and gently gather missing details ONE AT A TIME through conversation. Only ask for the single most important missing piece. When you have incident + at least one of (location / who / when), set is_report_ready=true.
7. Keep replies SHORT (2-3 sentences max) and conversational. No long paragraphs.

Return STRICTLY valid JSON (no markdown, no extra text):
{
  "intent": "casual_chat" | "wellbeing" | "bullying_report" | "book_counselor" | "ask_advice" | "learn_bullying",
  "reply": "string — natural conversational response",
  "extracted_info": {
    "incident": string or null,
    "location": string or null,
    "when": string or null,
    "people_involved": string or null,
    "frequency": string or null,
    "feelings": string or null,
    "safety_concerns": string or null,
    "anonymity_preference": "anonymous" | "with_name" | null
  },
  "is_report_ready": false,
  "immediate_danger": false
}"""

def gemini_key():
    """Load API key from environment variable or .streamlit/secrets.toml (server-side only)."""
    _INVALID = {"YOUR_API_KEY_HERE", "paste-your-key-here", "your-gemini-api-key", ""}

    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key and key not in _INVALID:
        return key

    try:
        import streamlit as st
        k = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        if k and k not in _INVALID:
            return k
    except Exception:
        pass

    return ""

def test_gemini_key():
    """
    Perform a real minimal call to verify the API key is valid.
    Returns (True, None) if OK, or (False, error_string) if it fails.
    Runs in a thread with a 10-second timeout so it never hangs the UI.
    """
    import threading

    try:
        import streamlit as st
        cache = st.session_state.get("_gemini_key_test_result")
        if cache is not None:
            return cache
    except Exception:
        pass

    key = gemini_key()
    if not key:
        result = (False, "No API key configured.")
        _cache_test_result(result)
        return result

    outcome = {}

    def _do_test():
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=key)
            resp = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents="Reply with one word: hello",
                config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=10),
            )
            outcome["ok"] = True
            outcome["text"] = resp.text
        except Exception as e:
            outcome["ok"] = False
            outcome["err"] = str(e)

    t = threading.Thread(target=_do_test, daemon=True)
    t.start()
    t.join(timeout=10)

    if t.is_alive():
        result = (True, None)
        _cache_test_result(result)
        return result

    if outcome.get("ok"):
        result = (True, None)
        _cache_test_result(result)
        return result

    combined = outcome.get("err", "unknown error")
    if "API_KEY_INVALID" in combined or "invalid" in combined.lower() or "401" in combined:
        msg = "API key is invalid — get a valid key at aistudio.google.com/apikey"
    elif "403" in combined or "permission" in combined.lower():
        msg = "API key does not have permission to use this model."
    elif "quota" in combined.lower() or "429" in combined:
        msg = "API quota exceeded — try again later."
    elif "no longer available" in combined.lower() or ("not found" in combined.lower() and "model" in combined.lower()) or "404" in combined:
        msg = "Model deprecated — update GEMINI_MODEL in secrets.toml to 'gemini-2.5-flash'."
    else:
        msg = f"Gemini error: {combined[:200]}"

    result = (False, msg)
    _cache_test_result(result)
    return result

def _cache_test_result(result):
    try:
        import streamlit as st
        st.session_state["_gemini_key_test_result"] = result
    except Exception:
        pass

def _call_gemini(prompt, *, json_mode=False, temperature=0.2):
    """Unified Gemini caller — used strictly for counselor-triggered suggested actions."""
    api_key = gemini_key()
    if not api_key:
        return None
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    # New google-genai SDK
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        cfg_kwargs = {"temperature": temperature}
        if json_mode:
            cfg_kwargs["response_mime_type"] = "application/json"
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(**cfg_kwargs),
        )
        return response.text
    except Exception:
        pass

    # Legacy google-generativeai SDK fallback
    try:
        from google import generativeai as lg
        lg.configure(api_key=api_key)
        model = lg.GenerativeModel(model_name)
        gen_cfg = {"temperature": temperature}
        if json_mode:
            try:
                gen_cfg["response_mime_type"] = "application/json"
                return model.generate_content(prompt, generation_config=gen_cfg).text
            except Exception:
                prompt += "\n\nRETURN STRICTLY JSON AND NOTHING ELSE."
                return model.generate_content(prompt, generation_config={"temperature": temperature}).text
        return model.generate_content(prompt, generation_config=gen_cfg).text
    except Exception:
        return None

# ── Identifier Redaction (Item 5) ─────────────────────────────────────────────
def redact_direct_identifiers(text):
    """
    Best-effort redaction of obvious direct identifiers (emails, phone numbers,
    and explicit name patterns) applied strictly to the copy sent to external AI.
    
    NOTE:
    This regex pass is a best-effort heuristic filter and does NOT provide an absolute
    guarantee against all possible identifying details or nuanced free-text disclosures.
    The original unredacted text is preserved in the database for authorized counselor review.
    """
    if not text or not isinstance(text, str):
        return text or ""

    # 1. Strip email addresses
    redacted = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[REDACTED_EMAIL]', text)

    # 2. Strip phone numbers (international and local formats)
    redacted = re.sub(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b', '[REDACTED_PHONE]', redacted)

    # 3. Strip obvious explicit name patterns ("my name is X", "I am X", "call me X", "this is X")
    name_regex = re.compile(r'\b(my name is|i am|i\'m|this is|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', re.IGNORECASE)
    redacted = name_regex.sub(r'\1 [REDACTED_NAME]', redacted)

    return redacted

# ── Report Ingestion (Item 5: Purely Local / No External LLM in Student Flow) ─
def analyze_report(text):
    """
    Analyze report using deterministic rule-based safety classification.
    Student-facing flows never send report content to external generative AI.
    """
    lower = text.lower()
    category = "Cyberbullying" if any(x in lower for x in ["online", "chat", "message", "social media", "instagram", "snapchat", "tiktok", "whatsapp"]) else \
               "Physical Bullying" if any(x in lower for x in ["hit", "pushed", "hurt", "punched", "kicked", "tripped"]) else \
               "Mental Health Concern" if any(x in lower for x in ["anxious", "sad", "self harm", "unsafe", "depressed", "scared", "suicide"]) else \
               "Verbal Bullying" if any(x in lower for x in ["called", "name", "tease", "bullied", "bully", "insult", "shouted"]) else "Other"
    priority = "High" if any(x in lower for x in ["unsafe", "hurt", "threat", "self harm", "suicide", "weapon", "kill", "danger"]) else "Medium"
    location = next((p for p in ["classroom", "hallway", "playground", "bus", "online", "cafeteria", "bathroom", "gym"] if p in lower), "Unknown")
    return {
        "summary": local_summary(text),
        "category": category,
        "location": location.title(),
        "severity": priority,
        "priority": priority,
        "source": "Local safety engine",
    }

def local_summary(text):
    """Create a readable factual summary locally; never echo raw input blindly."""
    fields = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip().lower()] = value.strip()
    incident = fields.get("what happened", text.strip())
    details = []
    if fields.get("location"): details.append(f"at {fields['location']}")
    if fields.get("when"): details.append(f"around {fields['when']}")
    if fields.get("how often"): details.append(f"reported frequency: {fields['how often']}")
    summary = f"The student reports: {incident.rstrip('.')}"
    if details: summary += ". It reportedly occurred " + ", ".join(details) + "."
    if fields.get("who was involved"): summary += " The student identified: " + fields["who was involved"].rstrip(".") + "."
    return summary[:2000]

def chat_reply(answer, next_prompt):
    """Safe scripted response for guided flows without external LLM calls."""
    return f"Thank you for sharing. {next_prompt}", "Safe guided flow"

def next_question(turn):
    questions = ["Where did this happen?", "When did it happen?", "Who was involved, if you feel comfortable sharing?", "How often has this happened?", "Would you like this report to be anonymous?"]
    idx = max(0, min(turn - 1, len(questions) - 1))
    return questions[idx]

def quick_replies(turn):
    options = [
        ["Something someone said", "Something someone did", "Something online", "I feel worried"],
        ["Classroom", "Playground", "Hallway", "Online"],
        ["Today", "This week", "A long time ago", "I am not sure"],
        ["A student", "A group", "Someone online", "I do not want to say"],
        ["Once", "A few times", "A lot", "I am not sure"],
        ["Yes, keep it anonymous", "No, use my name / handle"],
    ]
    return options[min(turn, len(options)-1)]

def format_report_from_state(state):
    """Format structured state dictionary into readable text for counselor review and database storage."""
    lines = []
    if state.get("incident"):
        lines.append(f"Incident: {state['incident']}")
    if state.get("location"):
        lines.append(f"Location: {state['location']}")
    if state.get("when"):
        lines.append(f"When: {state['when']}")
    if state.get("people_involved"):
        lines.append(f"People involved: {state['people_involved']}")
    if state.get("frequency"):
        lines.append(f"Frequency: {state['frequency']}")
    if state.get("feelings"):
        lines.append(f"Student feelings: {state['feelings']}")
    if state.get("safety_concerns"):
        lines.append(f"Safety concerns: {state['safety_concerns']}")
    if state.get("anonymity_preference"):
        lines.append(f"Anonymity preference: {state['anonymity_preference']}")
    return "\n".join(lines)

def _local_process_student_turn(messages, current_state, forced_report=False):
    """Deterministic, local student turn processor — zero external AI calls."""
    user_msg = messages[-1]["content"] if messages else ""
    lower = user_msg.lower().strip()

    danger_words = ["suicide", "kill myself", "self harm", "cut myself", "want to die", "bring a gun", "weapon", "bomb"]
    has_danger = any(w in lower for w in danger_words)

    # Classify intent
    if forced_report:
        intent = "bullying_report"
    elif (("book" in lower or "schedule" in lower or "make" in lower or "need" in lower or "want" in lower) and ("counselor" in lower or "appointment" in lower)) or ("counselor" in lower and any(v in lower for v in ["see", "talk", "meet", "speak", "chat", "session"])):
        intent = "book_counselor"
    elif (("what is" in lower or "tell me about" in lower or "explain" in lower or "meaning of" in lower or "define" in lower) and ("bullying" in lower or "cyberbullying" in lower)) or ("types of bullying" in lower):
        intent = "learn_bullying"
    elif any(w in lower for w in ["what should i do", "what can i do", "how do i handle", "give me advice", "any advice", "how do i deal", "how can i stop", "what to do if"]):
        intent = "ask_advice"
    elif any(w in lower for w in ["hit", "pushed", "punched", "called me", "bullied", "bullying", "harass", "threatened", "threatening", "stole", "took my", "spreading rumors", "rumor", "making fun of", "teasing", "excluded me", "spit", "kicked", "hurt me"]):
        intent = "bullying_report"
    elif current_state.get("incident") and any(q in lower for q in ["today", "yesterday", "class", "hallway", "bus", "once", "always", "student"]):
        intent = "bullying_report"
    elif any(w in lower for w in ["sad", "anxious", "stressed", "depressed", "lonely", "overwhelmed", "upset", "crying", "scared", "nervous", "tired", "unhappy"]):
        intent = "wellbeing"
    else:
        intent = "casual_chat"

    merged_state = dict(current_state)

    if intent == "bullying_report":
        if not merged_state.get("incident"):
            merged_state["incident"] = user_msg[:300]
        loc_map = {
            "classroom": "Classroom", "class": "Classroom", "hallway": "Hallway", "hall": "Hallway",
            "playground": "Playground", "cafeteria": "Cafeteria", "canteen": "Cafeteria", "lunchroom": "Cafeteria",
            "bus": "School Bus", "gym": "Gymnasium", "locker room": "Locker Room", "bathroom": "Bathroom",
            "library": "Library", "online": "Online", "instagram": "Instagram", "snapchat": "Snapchat",
            "tiktok": "TikTok", "whatsapp": "WhatsApp", "discord": "Discord"
        }
        for k, v in loc_map.items():
            if k in lower:
                merged_state["location"] = v
                break

        when_map = {
            "yesterday": "Yesterday", "today": "Today", "this morning": "This morning", "this afternoon": "This afternoon",
            "last week": "Last week", "at lunch": "At lunch", "recess": "During recess", "after school": "After school",
            "break": "During break"
        }
        for k, v in when_map.items():
            if k in lower:
                merged_state["when"] = v
                break

        people_cues = ["older kid", "classmate", "group of kids", "students", "someone in my class", "another student", "friend"]
        for p in people_cues:
            if p in lower:
                merged_state["people_involved"] = p.title()
                break

        freq_map = {
            "first time": "First time", "once": "First time", "only once": "First time",
            "every day": "Daily / Every day", "daily": "Daily / Every day",
            "keeps happening": "Repeatedly", "always": "Repeatedly", "multiple times": "Multiple times",
            "few times": "A few times", "a lot": "Frequently"
        }
        for k, v in freq_map.items():
            if k in lower:
                merged_state["frequency"] = v
                break

        feel_cues = ["scared", "worried", "sad", "angry", "upset", "anxious", "embarrassed", "humiliated", "alone"]
        for f in feel_cues:
            if f in lower:
                merged_state["feelings"] = f.title()
                break

        if any(w in lower for w in ["secret", "anonymous", "don't share", "hide my name"]):
            merged_state["anonymity_preference"] = "anonymous"
        elif any(w in lower for w in ["use my name", "not anonymous", "tell them", "handle"]):
            merged_state["anonymity_preference"] = "with_name"

    has_core = bool(merged_state.get("incident") and (merged_state.get("location") or merged_state.get("when") or merged_state.get("people_involved")))
    is_ready = has_core and (merged_state.get("frequency") is not None or len(messages) >= 4)

    if has_danger:
        reply = "Please know that your immediate safety is the most important thing right now. Please reach out to a trusted adult, speak to your school counselor, or contact emergency services immediately."
    elif intent == "casual_chat":
        if any(w in lower for w in ["ice cream", "cer crea", "cream", "pizza", "burger", "cookie", "cake", "candy", "chocolate", "hungry", "food", "lunch", "dinner", "snack", "taco", "fries"]):
            reply = "Treats and good food sound delicious! What is your favorite meal or snack after school?"
        elif any(g in lower for g in ["hi", "hello", "hey", "good morning", "howdy", "sup", "yo"]):
            reply = "Hello! I am SafeBridge Buddy. How are you doing today?"
        elif any(q in lower for q in ["how are you", "how r u", "how you doing", "how are things"]):
            reply = "I am doing well, thank you for asking! I am always here to listen and help. How has your day been?"
        elif any(q in lower for q in ["who are you", "what are you", "what can you do", "your name"]):
            reply = "I am SafeBridge Buddy! I am here to chat about your day, listen, share tips, or help you connect with a counselor whenever you need."
        elif any(j in lower for j in ["joke", "funny", "laugh", "make me laugh"]):
            reply = "Why did the math book look so sad? Because it had too many problems! Want to hear another one?"
        elif any(b in lower for b in ["bored", "boring", "nothing to do"]):
            reply = "Being bored is no fun! What is something you usually like doing, like music, games, or drawing?"
        elif any(g in lower for g in ["game", "gaming", "play", "roblox", "minecraft", "fortnite", "switch", "xbox", "playstation"]):
            reply = "Gaming can be a great way to relax! What games have you been enjoying recently?"
        elif any(a in lower for a in ["dog", "cat", "pet", "puppy", "kitten", "animal"]):
            reply = "Animals are amazing! Do you have pets, or what is your favorite animal?"
        elif any(t in lower for t in ["thank", "thanks", "thx", "appreciate"]):
            reply = "You are very welcome! Remember you are never alone."
        elif any(b in lower for b in ["bye", "goodbye", "see ya", "later"]):
            reply = "Goodbye! Have a great day, and remember you can return anytime you need support!"
        elif any(s in lower for s in ["homework", "math", "science", "english", "exam", "test", "school"]):
            reply = "School work can sometimes feel overwhelming! How are your classes feeling this week?"
        else:
            clean_msg = user_msg.replace("\\", "").strip()
            reply = f"Thank you for sharing that with me. What has been the highlight or challenge of your day so far?"
    elif intent == "wellbeing":
        reply = "I hear you, and it is completely okay to feel that way. You do not have to carry tough feelings alone. Would you like to tell me more about what is making you feel this way, or would you like to take a mindful reset together?"
    elif intent == "book_counselor":
        reply = "Talking directly with a counselor is a great, supportive step. You can book an appointment using the Book Counselor button to choose a time that fits your day."
    elif intent == "learn_bullying":
        reply = "Bullying is repeated, unwanted behavior where someone uses power to hurt or intimidate someone else. It can be verbal, social, physical, or online. You can explore more anytime in our 'Learn & Stay Safe' guide!"
    elif intent == "ask_advice":
        reply = "Dealing with conflicts or hurtful behavior can be hard. The most helpful steps are to stay calm, set clear boundaries if safe, keep records or screenshots of what happened, and inform a trusted adult or counselor."
    else:
        if not merged_state.get("location"):
            reply = "Thank you for letting me know. Where did this happen (for example, in class, the playground, or online)?"
        elif not merged_state.get("when"):
            reply = "Understood. When did this happen (such as today, yesterday, or recently)?"
        elif not merged_state.get("people_involved"):
            reply = "Got it. If you feel comfortable sharing, who was involved?"
        elif not merged_state.get("frequency"):
            reply = "Has this happened before, or was this the first time?"
        elif not merged_state.get("anonymity_preference"):
            reply = "Thank you for sharing these details. Would you like this report to be anonymous, or can we include your handle for the counselor?"
        else:
            reply = "I've organized the details you shared into a report draft. You can review it below and submit it to your counselor whenever you're ready, or continue chatting if you'd like to add anything else."

    return {
        "intent": intent,
        "reply": reply,
        "report_state": merged_state,
        "is_report_ready": is_ready,
        "immediate_danger": has_danger,
        "source": "Local safety engine",
    }

def process_student_turn(messages, current_state=None, forced_report=False):
    """
    Main student turn processor.
    Strictly uses local deterministic safety logic.
    Student-facing flows NEVER invoke external generative AI.
    """
    state = dict(DEFAULT_REPORT_STATE)
    if current_state:
        for k, v in current_state.items():
            if k in state and v:
                state[k] = v

    return _local_process_student_turn(messages, state, forced_report=forced_report)

def safebridge_chat(history, user_message):
    """Backwards-compatible wrapper delegating to process_student_turn."""
    msgs = list(history) + [{"role": "user", "content": user_message}]
    result = process_student_turn(msgs)
    return result["reply"], result.get("source", "SafeBridge Local")

# ── Counselor-Triggered Actions (Item 5: Off by default, PII redacted) ────────
def suggest_actions(report_text, analysis):
    """
    Counselor-triggered action suggestions.
    Checks external_ai_allowed setting (defaults to '0' / OFF).
    Applies direct identifier redaction to report excerpt sent to Gemini.
    """
    from database import get_setting
    external_allowed = get_setting("external_ai_allowed", "0") == "1"

    if external_allowed:
        # Redact direct personal identifiers before sending excerpt to Gemini
        safe_excerpt = redact_direct_identifiers(report_text[:1200])
        prompt = (
            f"{ACTION_SYSTEM}\n\n"
            f"Report details:\n"
            f"  Category : {analysis.get('category','Unknown')}\n"
            f"  Severity : {analysis.get('severity','Unknown')}\n"
            f"  Priority : {analysis.get('priority','Unknown')}\n"
            f"  Location : {analysis.get('location','Unknown')}\n"
            f"  Summary  : {analysis.get('summary','')}\n"
            f"  Original report (redacted excerpt): {safe_excerpt}"
        )
        raw = _call_gemini(prompt, json_mode=True, temperature=0.2)
        if raw:
            try:
                data = json.loads(raw)
                if "actions" in data:
                    data.setdefault("source", "Gemini (Redacted Prompt)")
                    return data
            except Exception:
                pass

    # Local fallback logic (used whenever external_ai_allowed is '0' or offline)
    priority = analysis.get("priority", "Medium")
    actions = []
    if priority == "High":
        actions.append({"title": "Immediate welfare check", "detail": "Contact the student today to assess immediate safety and wellbeing.", "urgency": "Immediate"})
        actions.append({"title": "Notify safeguarding lead", "detail": "Escalate to the Designated Safeguarding Lead; this report indicates a high-priority concern.", "urgency": "Immediate"})
    actions.append({"title": "Schedule counselor meeting", "detail": "Arrange a private meeting with the student within the next 2 school days.", "urgency": "Soon"})
    actions.append({"title": "Document and file", "detail": "Record all details in the school's safeguarding system with today's date.", "urgency": "Soon"})
    actions.append({"title": "Consider parent contact", "detail": "Assess whether notifying parents/guardians is appropriate given the student's age and circumstances.", "urgency": "Routine"})
    return {"actions": actions, "risk_level": priority, "risk_rationale": "Assessed from reported priority level.", "source": "Local safety fallback (Human review required)"}

# ── Child Mode Flow (Item 4: Non-negotiable Static Lists / No Generative AI) ──
def child_adapt_questions(stage, answers_so_far):
    """
    Curated static question and option lists for junior student reporting.
    Generative AI has been completely removed from this function to guarantee child safety.
    Always returns pre-defined, age-appropriate questions and options regardless of any settings.
    """
    fallbacks = [
        {
            "question": "What happened?",
            "options": [
                {"label": "Someone said mean things"},
                {"label": "Someone hurt me"},
                {"label": "Online problem"},
                {"label": "Other concern"}
            ]
        },
        {
            "question": "Where did it happen?",
            "options": [
                {"label": "In class"},
                {"label": "Playground"},
                {"label": "Bathroom or hallway"},
                {"label": "Online or off-campus"}
            ]
        },
        {
            "question": "Who was it?",
            "options": [
                {"label": "Another student"},
                {"label": "A group"},
                {"label": "I do not know"},
                {"label": "I do not want to say"}
            ]
        },
        {
            "question": "How would you like to submit?",
            "options": [
                {"label": "Use my student handle"},
                {"label": "Keep it anonymous"},
                {"label": "I am not sure"},
                {"label": "Either is fine"}
            ]
        }
    ]
    idx = max(0, min(stage - 1, len(fallbacks) - 1))
    return fallbacks[idx]

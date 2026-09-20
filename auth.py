"""Session-based authentication layer with PBKDF2 hashing and brute-force protection."""
import hashlib, hmac, os
from datetime import datetime, timezone, timedelta
import streamlit as st
from database import one, execute

def hash_password(password):
    """PBKDF2 hashes with 310,000 iterations for secure password storage."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"

def verify_password(password, stored):
    """PBKDF2-SHA256 verification only. Legacy unsalted SHA256 has been removed."""
    if stored and stored.startswith("pbkdf2_sha256$"):
        try:
            _, salt_hex, expected = stored.split("$", 2)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 310_000).hex()
            return hmac.compare_digest(expected, actual)
        except Exception:
            return False
    return False

def init_session():
    defaults = {
        "user": None,
        "dark_mode": False,
        "page": "Home",
        "anonymous_mode": False,
        "last_activity": None,  # for session-timeout tracking
        "login_error": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

def login(username, password, role):
    st.session_state.login_error = None
    clean_username = username.strip().lower()
    user = one(
        "SELECT id, username, display_name, role, password_hash, active, force_password_change, failed_attempts, locked_until FROM students WHERE username=?",
        (clean_username,),
    )

    if not user:
        st.session_state.login_error = "Invalid username or password."
        return False

    now_utc = datetime.now(timezone.utc)

    # Check brute-force temporary lockout
    locked_until_raw = user.get("locked_until")
    if locked_until_raw:
        try:
            if isinstance(locked_until_raw, str):
                locked_dt = datetime.fromisoformat(locked_until_raw)
            else:
                locked_dt = locked_until_raw
            if locked_dt.tzinfo is None:
                locked_dt = locked_dt.replace(tzinfo=timezone.utc)
            if locked_dt > now_utc:
                remaining_mins = max(1, int((locked_dt - now_utc).total_seconds() // 60))
                st.session_state.login_error = f"Account temporarily locked due to repeated failed logins. Try again in ~{remaining_mins} minutes."
                return False
        except Exception:
            pass

    # Check role and active status
    if user["role"] != role or not user.get("active", 1):
        st.session_state.login_error = "Those details don't match this account type, or the account is inactive."
        return False

    # Verify PBKDF2 password
    if not verify_password(password, user["password_hash"]):
        failed = int(user.get("failed_attempts") or 0) + 1
        locked_iso = None
        if failed >= 5:
            locked_dt = now_utc + timedelta(minutes=15)
            locked_iso = locked_dt.isoformat()
            execute("UPDATE students SET failed_attempts=?, locked_until=? WHERE id=?", (failed, locked_iso, user["id"]))
            st.session_state.login_error = "Too many failed attempts. Account locked for 15 minutes."
        else:
            execute("UPDATE students SET failed_attempts=? WHERE id=?", (failed, user["id"]))
            attempts_left = 5 - failed
            st.session_state.login_error = f"Invalid password. {attempts_left} attempt(s) remaining before temporary lockout."
        return False

    # Successful login: reset failed_attempts and locked_until
    execute("UPDATE students SET failed_attempts=0, locked_until=NULL WHERE id=?", (user["id"],))

    user_dict = dict(user)
    user_dict.pop("password_hash", None)
    user_dict.pop("active", None)
    user_dict.pop("failed_attempts", None)
    user_dict.pop("locked_until", None)

    st.session_state.user = user_dict
    st.session_state.anonymous_mode = False
    st.session_state.last_activity = now_utc
    st.session_state.login_error = None
    return True

def change_password(user_id, new_password):
    """Enforce minimum 10-character password and clear force_password_change flag."""
    if len(new_password) < 10:
        raise ValueError("Password must be at least 10 characters long.")
    new_hash = hash_password(new_password)
    execute("UPDATE students SET password_hash=?, force_password_change=0 WHERE id=?", (new_hash, user_id))
    if st.session_state.get("user") and st.session_state.user.get("id") == user_id:
        st.session_state.user["force_password_change"] = 0
    return True

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session()

def require_role(*roles):
    return st.session_state.user and st.session_state.user["role"] in roles

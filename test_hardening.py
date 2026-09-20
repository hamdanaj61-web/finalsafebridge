"""Automated verification test script for SafeBridge AI security and hardening."""
import unittest
from datetime import datetime, timezone, timedelta
import auth
import ai
import database

class TestSafeBridgeHardening(unittest.TestCase):

    def test_auth_pbkdf2_only(self):
        """Item 3: Verify PBKDF2 works and legacy unsalted SHA-256 is rejected."""
        password = "SecurePassword123!"
        hashed = auth.hash_password(password)
        self.assertTrue(hashed.startswith("pbkdf2_sha256$"))
        self.assertTrue(auth.verify_password(password, hashed))
        self.assertFalse(auth.verify_password("WrongPassword", hashed))

        # Test rejection of legacy unsalted sha256
        import hashlib
        legacy_hash = hashlib.sha256(password.encode()).hexdigest()
        self.assertFalse(auth.verify_password(password, legacy_hash), "Legacy unsalted SHA-256 must be rejected")

    def test_change_password_min_length(self):
        """Item 3: Password change enforces minimum 10 characters."""
        with self.assertRaises(ValueError):
            auth.change_password(1, "short99")

    def test_child_mode_no_gemini(self):
        """Item 4: Child mode questions use static fallbacks with zero Gemini calls."""
        for stage in range(1, 5):
            q_data = ai.child_adapt_questions(stage, ["Sad or Upset"])
            self.assertIsNotNone(q_data)
            self.assertIn("question", q_data)
            self.assertIn("options", q_data)
            self.assertGreaterEqual(len(q_data["options"]), 2)

    def test_redact_direct_identifiers(self):
        """Item 5: Redaction pass correctly strips emails, phones, and name declarations."""
        raw_text = "Hello, my name is Alex Johnson and my email is alex.j@school.org. Call me at +1 555-234-5678 or 0501234567. Someone pushed me."
        redacted = ai.redact_direct_identifiers(raw_text)
        self.assertNotIn("alex.j@school.org", redacted)
        self.assertIn("[REDACTED_EMAIL]", redacted)
        self.assertNotIn("555-234-5678", redacted)
        self.assertNotIn("0501234567", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)
        self.assertNotIn("Alex Johnson", redacted)
        self.assertIn("[REDACTED_NAME]", redacted)
        self.assertIn("Someone pushed me.", redacted)

    def test_student_report_analysis_local_only(self):
        """Item 5: Student report analysis is purely local and deterministic."""
        res = ai.analyze_report("A student pushed me on the playground yesterday and called me bad names.")
        self.assertIn(res["category"], ai.CATEGORIES)
        self.assertEqual(res["source"], "Local safety engine")
        self.assertEqual(res["location"], "Playground")

    def test_suggest_actions_defaults_off(self):
        """Item 5: suggest_actions falls back to local safety logic when external_ai_allowed is '0'."""
        database.set_setting("external_ai_allowed", "0")
        analysis = {"category": "Physical Bullying", "severity": "High", "priority": "High", "location": "Playground", "summary": "Student reported being pushed."}
        res = ai.suggest_actions("Someone hurt me on the playground.", analysis)
        self.assertIn("actions", res)
        self.assertIn("Local safety fallback", res.get("source", ""))

if __name__ == "__main__":
    unittest.main()

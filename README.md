# SafeBridge AI

A privacy-first Streamlit wellbeing and anti-bullying support platform for schools. SafeBridge AI provides student reporting, weekly check-ins, appointment requests, psychoeducational content, counselor safeguarding workflows, and privacy-preserving administrator analytics.

## Security & MOE Compliance Highlights

1. **Zero Hardcoded Credentials**: No pre-seeded demo accounts exist in code or database schemas. On first run with an empty database, a single `admin` account is created with a cryptographically secure random password displayed once via a secure banner.
2. **Student Pseudonymization**: The application database stores only pseudonyms/handles (e.g. `Student-101`, `BlueFalcon`). The real-name ↔️ handle mapping is kept entirely outside the application on school-owned, encrypted, and backup-protected storage.
3. **Password Security & Brute-Force Lockout**: PBKDF2-SHA256 password hashing (310,000 iterations), minimum 10-character password policy, forced password resets on first login, and automated 15-minute temporary lockout after 5 consecutive failed login attempts.
4. **No Generative AI for Students**: Child reporting mode and student chat operate strictly on curated deterministic workflows and local safety engines. No student interaction ever contacts external generative AI.
5. **Counselor-Only Advisory AI (Off by Default)**: Generative AI is restricted to counselor-triggered action suggestions (`suggest_actions`). It ships **disabled by default** (`external_ai_allowed = '0'`) and applies automated regex redaction to personal identifiers (emails, phone numbers, self-identification phrases) before calling external APIs.
6. **PostgreSQL Compatibility**: All queries use PostgreSQL standards (`date_trunc`, bound UTC ISO timestamps, standard placeholders).
7. **Automated Data Retention**: Configurable retention window for resolved reports (defaults to 30 days) with automated and manual purging routines.
8. **Informed Consent Disclosures**: Plain-language consent and privacy notices appear before report submissions in both anonymous and authenticated student flows.
9. **Self-Hosted Row Level Security & Encryption**: Full support for self-hosted PostgreSQL with Row Level Security (RLS) policies, mandatory TLS, and encrypted volumes at rest.

## Database Setup (Self-Hosted PostgreSQL or Supabase)

SafeBridge AI connects to any PostgreSQL database via PostgREST or Supabase:

1. **Execute Schema**:
   Run `supabase_schema.sql` in your PostgreSQL or Supabase SQL Editor. This initializes all tables, indexes, RLS policies, and default platform settings.

2. **Configure Credentials**:
   Add database and API credentials to `.streamlit/secrets.toml`:

   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   SUPABASE_URL = "https://your-project-ref.supabase.co" # or self-hosted PostgREST URL
   SUPABASE_KEY = "your-anon-or-service-role-key"
   ```

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## First Login

On first run against an empty database, a secure temporary password will be generated for the `admin` account and shown once on screen. You will be prompted to choose a new, secure password (minimum 10 characters) immediately upon logging in.

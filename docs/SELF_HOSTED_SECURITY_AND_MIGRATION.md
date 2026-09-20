# SafeBridge AI: Self-Hosted Infrastructure, Security & Compliance Guide

This guide documents the security architecture, encryption standards, offline identity mapping procedures, and automated maintenance workflows required for school and Ministry of Education (MOE) governance.

---

## 1. School-Owned Student Identity Mapping Protocol (Item 2)

To prevent centralized correlation and protect student confidentiality in compliance with MOE and data protection regulations:

### Architecture
- **Inside SafeBridge AI Database:** Only store a pseudonym/handle (e.g. `Student-104`, `AmberFox`, `Falcon-09`) in the `display_name` column of the `students` table. Real student names, government IDs, and civil registry details **must never be entered into the database**.
- **Outside SafeBridge AI Database:** The mapping between real student identities and their SafeBridge pseudonyms must be maintained in a standalone, encrypted file.

### Storage & Keyholder Safeguards
1. **School-Managed Storage Only:** The mapping file must reside exclusively on school-managed, access-controlled infrastructure (e.g., school enterprise OneDrive/SharePoint with DLP, or an encrypted internal network share). It must **never** be stored on an individual staff member's personal laptop or unmanaged portable USB drive.
2. **Encryption at Rest:** The file must be encrypted with AES-256 or hosted in an encrypted volume with BitLocker/VeraCrypt.
3. **Designated Backup Access-Holders:**
   - Primary Access: Designated Safeguarding Lead (DSL) / Head of Counseling.
   - Secondary Access (Designated Backup): School Principal / Compliance Officer.
   - Single-person dependency is prohibited; at least one designated backup access-holder must be formally appointed.
4. **Emergency Unmasking Protocol:** Pseudonym unmasking may only occur when an immediate safeguarding risk, statutory child protection notification, or life-safety emergency arises. Every unmasking event must be logged in the school's official safeguarding incident book with date, reason, and signature of the DSL.

### Mapping File Template Example
```csv
Student_Internal_ID,Official_School_ID,Student_Real_Name,Assigned_Handle,Grade,Created_Date,DSL_Signature
SB-001,SCH-98214,Confidential Student 1,Falcon-09,Grade 9,2026-09-01,DSL_Approved
SB-002,SCH-98215,Confidential Student 2,BlueSparrow,Grade 7,2026-09-01,DSL_Approved
```

---

## 2. Self-Hosted PostgreSQL & Plain-SQL Row Level Security (Item 9)

Row Level Security (RLS) is an intrinsic feature of PostgreSQL, independent of any cloud vendor.

### Plain SQL RLS Implementation
Run the following standard SQL statements in PostgreSQL:

```sql
-- Enable Row Level Security on all application tables
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkins ENABLE ROW LEVEL SECURITY;
ALTER TABLE counselor_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

-- Define security policies for application service roles
CREATE POLICY "app_students_policy" ON students
  FOR ALL
  USING (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin')
  WITH CHECK (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin');

CREATE POLICY "app_reports_policy" ON reports
  FOR ALL
  USING (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin')
  WITH CHECK (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin');

CREATE POLICY "app_appointments_policy" ON appointments
  FOR ALL
  USING (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin')
  WITH CHECK (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin');

CREATE POLICY "app_checkins_policy" ON checkins
  FOR ALL
  USING (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin')
  WITH CHECK (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin');

CREATE POLICY "app_counselor_notes_policy" ON counselor_notes
  FOR ALL
  USING (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin')
  WITH CHECK (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin');

CREATE POLICY "app_settings_policy" ON settings
  FOR ALL
  USING (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin')
  WITH CHECK (CURRENT_USER = 'safebridge_app' OR CURRENT_ROLE = 'safebridge_admin');
```

---

## 3. App-to-Database In-Transit TLS Verification (Item 9)

All communication between the Streamlit application container and the PostgreSQL database instance must enforce TLS 1.3/1.2 encryption.

### Verification Checklist:
1. **Connection String Enforcement:** Ensure the connection parameters or URI specify `sslmode=require` or `sslmode=verify-full`:
   ```ini
   postgresql://user:password@host:5432/safebridge?sslmode=require
   ```
2. **PostgreSQL Server TLS Configuration (`postgresql.conf`):**
   ```conf
   ssl = on
   ssl_cert_file = '/etc/ssl/certs/server.crt'
   ssl_key_file = '/etc/ssl/private/server.key'
   ssl_min_protocol_version = 'TLSv1.2'
   ```
3. **Client Verification Command:**
   ```bash
   psql "sslmode=require host=<DB_HOST> user=<USER> dbname=safebridge" -c "SELECT version(), pg_ssl.ssl, pg_ssl.version FROM pg_stat_ssl pg_ssl JOIN pg_stat_activity act ON pg_ssl.pid = act.pid WHERE act.pid = pg_backend_pid();"
   ```

---

## 4. Oracle Cloud Infrastructure (OCI) Volume Encryption at Rest (Item 9)

When hosted on an Oracle Cloud Infrastructure (OCI) Virtual Machine:

### Verification Procedures:
1. **Boot Volume Encryption:**
   - In the OCI Console: Navigate to **Compute** -> **Instances** -> Select SafeBridge Instance -> **Boot Volume**.
   - Verify that **Encryption** displays **"Oracle-managed key"** or a configured **"Customer-managed key (Vault)"**.
   - OCI encrypts all boot and block volumes at rest by default using 256-bit AES encryption.
2. **Block Volume CLI Verification:**
   Using the OCI CLI, confirm volume encryption status:
   ```bash
   oci bv boot-volume get --boot-volume-id <BOOT_VOLUME_OCID> --query "data.{\"Volume-Name\":\"display-name\",\"Encrypted\":\"is-hydrated\",\"KMS-Key-Id\":\"kms-key-id\"}"
   ```

---

## 5. Automated OS-Level Scheduled Data Retention (Item 7)

While the SafeBridge Administrator UI includes a manual cleanup trigger, production environments must execute lifecycle retention automatically via an OS-level cron job on the VM.

### Retention Logic
Incident reports with `status = 'Resolved'` that were created more than `report_retention_days` (default: 30 days) ago are permanently removed, fulfilling data minimization mandates.

### Standalone Cleanup Script (`cron_cleanup.py`)
Run the following script daily via cron:

```python
#!/usr/bin/env python3
"""Scheduled maintenance task for SafeBridge AI data retention."""
import os, sys
from datetime import datetime, timezone

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import purge_old_resolved_reports

if __name__ == "__main__":
    count = purge_old_resolved_reports()
    print(f"[{datetime.now(timezone.utc).isoformat()}] SafeBridge Retention Cron: Purged {count} resolved reports.")
```

### Crontab Schedule (Runs Daily at 02:00 AM UTC):
```bash
0 2 * * * cd /opt/safebridge && /opt/safebridge/.venv/bin/python cron_cleanup.py >> /var/log/safebridge_retention.log 2>&1
```

# 03 — Features

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Product Lead  

---

## Purpose of This Document

This document defines every feature in Job Finder AI. Each feature is described from six angles: purpose, workflow, database, API, frontend, backend, edge cases, and acceptance criteria. This is the contract between product, engineering, and design.

Before building any feature, read this document. Before marking a feature complete, verify it passes all acceptance criteria listed here.

---

## Feature ID Convention

```
F-[MODULE]-[NUMBER]
```

Modules:
- `AUTH`   — Authentication & Access
- `PROF`   — Student Profile
- `SCRP`   — Scraper Pipeline
- `AGNT`   — AI Agent Pipeline
- `JOBS`   — Job Listings & Feed
- `NOTIF`  — Notification System
- `TRACK`  — Application Tracking
- `ADMN`   — Admin Dashboard

Priority levels: `P0` (MVP blocker) · `P1` (MVP quality) · `P2` (Phase 2) · `P3` (Phase 3+)

---

## Feature Index

| ID | Feature | Module | Priority | Phase |
|---|---|---|---|---|
| [F-AUTH-01](#f-auth-01--email--password-registration) | Email & Password Registration | Auth | P0 | 1 |
| [F-AUTH-02](#f-auth-02--google-oauth-login) | Google OAuth Login | Auth | P0 | 1 |
| [F-AUTH-03](#f-auth-03--jwt-session-management) | JWT Session Management | Auth | P0 | 1 |
| [F-AUTH-04](#f-auth-04--password-reset) | Password Reset via Email | Auth | P1 | 1 |
| [F-AUTH-05](#f-auth-05--account-deletion) | Account Deletion (GDPR) | Auth | P1 | 1 |
| [F-PROF-01](#f-prof-01--skills-selection) | Skills Selection | Profile | P0 | 1 |
| [F-PROF-02](#f-prof-02--job-preferences) | Job Role & Location Preferences | Profile | P0 | 1 |
| [F-PROF-03](#f-prof-03--notification-preferences) | Notification Preferences & Quiet Hours | Profile | P1 | 1 |
| [F-PROF-04](#f-prof-04--resume-upload--skill-extraction) | Resume Upload & AI Skill Extraction | Profile | P2 | 2 |
| [F-SCRP-01](#f-scrp-01--ats-auto-detector) | ATS Auto-Detector | Scraper | P0 | 1 |
| [F-SCRP-02](#f-scrp-02--scraper-adapters) | Scraper Adapters (Workday / Greenhouse / Lever / iCIMS / Taleo) | Scraper | P0 | 1 |
| [F-SCRP-03](#f-scrp-03--scrape-scheduler) | Scrape Scheduler (15-min cron) | Scraper | P0 | 1 |
| [F-SCRP-04](#f-scrp-04--scrape-run-logging) | Scrape Run Logging | Scraper | P0 | 1 |
| [F-SCRP-05](#f-scrp-05--robots-compliance--rate-limiting) | robots.txt Compliance & Rate Limiting | Scraper | P0 | 1 |
| [F-AGNT-01](#f-agnt-01--duplicate-detector) | Duplicate Detector | Agents | P0 | 1 |
| [F-AGNT-02](#f-agnt-02--job-extractor) | Job Extractor Agent | Agents | P0 | 1 |
| [F-AGNT-03](#f-agnt-03--skill-extractor) | Skill Extractor Agent | Agents | P0 | 1 |
| [F-AGNT-04](#f-agnt-04--jd-summarizer) | JD Summarizer Agent | Agents | P0 | 1 |
| [F-AGNT-05](#f-agnt-05--job-classifier) | Job Classifier Agent | Agents | P0 | 1 |
| [F-JOBS-01](#f-jobs-01--job-listings-feed) | Job Listings Feed | Jobs | P0 | 1 |
| [F-JOBS-02](#f-jobs-02--job-filters--search) | Job Filters & Search | Jobs | P0 | 1 |
| [F-JOBS-03](#f-jobs-03--job-detail-view) | Job Detail View | Jobs | P0 | 1 |
| [F-JOBS-04](#f-jobs-04--posted-x-minutes-ago-timestamp) | "Posted X Minutes Ago" Timestamp | Jobs | P0 | 1 |
| [F-JOBS-05](#f-jobs-05--apply-link) | Direct Apply Link | Jobs | P0 | 1 |
| [F-NOTIF-01](#f-notif-01--telegram-bot-connection) | Telegram Bot Connection | Notifications | P0 | 1 |
| [F-NOTIF-02](#f-notif-02--telegram-instant-alert) | Telegram Instant Job Alert | Notifications | P0 | 1 |
| [F-NOTIF-03](#f-notif-03--daily-email-digest) | Daily Email Digest | Notifications | P1 | 1 |
| [F-NOTIF-04](#f-notif-04--notification-delivery-log) | Notification Delivery Log | Notifications | P0 | 1 |
| [F-TRACK-01](#f-track-01--save-job) | Save Job (Bookmark) | Tracking | P1 | 2 |
| [F-TRACK-02](#f-track-02--application-status-tracker) | Application Status Tracker | Tracking | P1 | 2 |
| [F-TRACK-03](#f-track-03--deadline-reminder) | Closing Soon Reminder | Tracking | P2 | 2 |
| [F-ADMN-01](#f-admn-01--scraper-health-dashboard) | Scraper Health Dashboard | Admin | P0 | 1 |
| [F-ADMN-02](#f-admn-02--company-management) | Company Management (Add / Deactivate) | Admin | P0 | 1 |
| [F-ADMN-03](#f-admn-03--low-confidence-review-queue) | Low-Confidence Job Review Queue | Admin | P1 | 1 |
| [F-ADMN-04](#f-admn-04--user-management) | User Management | Admin | P1 | 1 |
| [F-ADMN-05](#f-admn-05--admin-telegram-alerts) | Admin Telegram Failure Alerts | Admin | P1 | 1 |

---

## MODULE: AUTHENTICATION

---

### F-AUTH-01 — Email & Password Registration

**Priority:** P0 · **Phase:** 1 · **Persona:** All

#### Purpose
Allow any user to create an account using an email address and password. Email verification is required before the account becomes active, preventing bots and fake accounts.

#### Workflow
```
1. User submits registration form: name, email, password
2. Backend validates input (email format, password strength min 8 chars)
3. Backend checks: email already registered? → return 409 Conflict
4. Backend creates user record with is_verified = false
5. Backend generates a verification token (UUID, stored in DB, expires 24h)
6. Backend sends verification email with link: /verify-email?token={uuid}
7. User clicks link → backend validates token (exists? not expired?)
8. Backend sets is_verified = true, deletes token
9. User is redirected to profile setup step 1
10. If token expired → user can request a new verification email
```

#### Database
```sql
-- Tables touched
users (id, name, email, password_hash, role, is_verified, created_at)
email_verification_tokens (id, user_id, token, expires_at, created_at)
```

#### API
```
POST /api/auth/register
  Body: { name, email, password }
  Returns: 201 { message: "Verification email sent" }
  Errors: 400 (validation), 409 (email exists)

GET /api/auth/verify-email?token={uuid}
  Returns: 200 { message: "Email verified" } + redirect to /onboarding
  Errors: 400 (invalid token), 410 (token expired)

POST /api/auth/resend-verification
  Body: { email }
  Returns: 200 { message: "Verification email resent" }
  Rate limit: 3 requests per email per hour
```

#### Frontend
- `/register` page: name, email, password, confirm password fields
- Inline validation: email format, password length, password match
- After submit: "Check your email" confirmation screen
- `/verify-email` page: success state or expired token state with resend option
- On success: redirect to `/onboarding/step-1`

#### Backend
- Password hashed with bcrypt, cost factor 12 minimum
- Verification token is a UUID v4, stored hashed in DB
- Email sent via configured email service (SendGrid / Resend)
- Token cleanup: expired tokens deleted by a nightly cron job

#### Edge Cases
| Case | Handling |
|---|---|
| Email already registered but unverified | Return 409 with message "Account exists — check your email for the verification link" |
| User registers twice with same email | Second registration blocked at DB unique constraint level |
| Verification token used twice | Token deleted after first use; second use returns 400 |
| Token expired (>24h) | Returns 410 with link to resend verification |
| Email delivery failure | Log error, return 201 still — user can request resend |
| SQL injection in email field | Pydantic validation rejects non-email-format strings before hitting DB |

#### Acceptance Criteria
- [ ] User can register with valid email and password (≥8 chars)
- [ ] Duplicate email registration returns 409
- [ ] Verification email is sent within 30 seconds of registration
- [ ] Clicking verification link activates account and redirects to onboarding
- [ ] Expired tokens (>24h) return 410 and offer resend option
- [ ] Password is never stored in plaintext or logged anywhere
- [ ] Unverified users cannot access any protected endpoint

---

### F-AUTH-02 — Google OAuth Login

**Priority:** P0 · **Phase:** 1 · **Persona:** All

#### Purpose
Allow users to register and log in with their Google account in one click — reducing onboarding friction significantly, especially on mobile. No password required.

#### Workflow
```
1. User clicks "Continue with Google" on login or register page
2. Frontend redirects to Google OAuth consent screen
3. User approves → Google redirects to /api/auth/oauth/google/callback with auth code
4. Backend exchanges auth code for Google ID token
5. Backend extracts: google_id, email, name, profile_picture from token
6. If user with this google_id exists → generate JWT, log in
7. If user with this email exists (password account) → link Google ID to existing account
8. If new user → create account (is_verified = true, no password), redirect to onboarding
9. JWT access + refresh tokens issued, user logged in
```

#### Database
```sql
users (id, name, email, password_hash [nullable], google_id [nullable],
       profile_picture_url, is_verified, role, created_at)
```

#### API
```
GET /api/auth/oauth/google
  → Redirects to Google OAuth consent URL

GET /api/auth/oauth/google/callback?code={code}&state={state}
  → Processes callback, issues tokens, redirects to app
  Errors: 400 (invalid state/CSRF), 500 (Google API failure)
```

#### Frontend
- "Continue with Google" button on `/login` and `/register`
- Google-branded button per OAuth branding guidelines
- Loading state during OAuth redirect
- On error: toast notification "Google login failed — please try again"

#### Backend
- State parameter used for CSRF protection — validated on callback
- Google ID token verified against Google's public keys
- Profile picture URL stored but never proxied through our servers
- If email from Google matches an existing password account: accounts merged, google_id added

#### Edge Cases
| Case | Handling |
|---|---|
| User denies Google consent | Redirect back to /login with error param |
| Google returns email already used by password account | Merge accounts silently; user can use both methods |
| Google API is down | Return 503 with "Google login unavailable — try email login" |
| Google revokes app access | Next login attempt fails; user prompted to reconnect or use email |
| State mismatch (CSRF attempt) | Return 400, log security event |

#### Acceptance Criteria
- [ ] "Continue with Google" button present on login and register pages
- [ ] New Google users are auto-created with is_verified = true
- [ ] Existing email accounts are linked to Google ID on first Google login
- [ ] State parameter prevents CSRF on callback
- [ ] JWT tokens issued same as email login flow
- [ ] Google OAuth error returns to login page with user-friendly message

---

### F-AUTH-03 — JWT Session Management

**Priority:** P0 · **Phase:** 1 · **Persona:** All

#### Purpose
Secure, stateless session management using short-lived access tokens and long-lived refresh tokens. Allows users to stay logged in without re-entering credentials daily.

#### Workflow
```
Login:
1. User logs in → backend issues access token (JWT, 15 min TTL)
   + refresh token (opaque UUID, 7 days TTL, stored in DB)
2. Access token returned in response body
3. Refresh token set as httpOnly cookie (Secure, SameSite=Strict)

Request:
4. Frontend includes access token in Authorization: Bearer {token} header
5. Backend middleware validates JWT signature + expiry
6. If valid → request proceeds
7. If expired → frontend receives 401

Token Refresh:
8. Frontend detects 401 → sends POST /api/auth/refresh
9. Backend reads refresh token from httpOnly cookie
10. Validates refresh token (exists in DB, not expired, not revoked)
11. Issues new access token + rotates refresh token
12. Old refresh token deleted from DB

Logout:
13. Frontend sends POST /api/auth/logout
14. Backend deletes refresh token from DB
15. Frontend clears access token from memory
```

#### Database
```sql
refresh_tokens (id, user_id, token_hash, expires_at, created_at, revoked_at)
```

#### API
```
POST /api/auth/refresh
  Cookie: refresh_token={uuid}
  Returns: 200 { access_token, expires_in }
  Errors: 401 (invalid/expired refresh token)

POST /api/auth/logout
  Cookie: refresh_token={uuid}
  Returns: 200 { message: "Logged out" }
  Effect: Refresh token deleted from DB, cookie cleared
```

#### Backend
- Access token: JWT signed with RS256 or HS256 (configured via env)
- Access token payload: `{ user_id, role, exp, iat }`
- Refresh token: UUID v4, stored as bcrypt hash in DB (not plaintext)
- Token rotation: every refresh issues a new refresh token; old one deleted
- Revocation: logout deletes the refresh token — access token expires naturally

#### Edge Cases
| Case | Handling |
|---|---|
| Access token tampered | JWT signature validation fails → 401 |
| Refresh token stolen and used twice | Token rotation detects reuse (token not found after first use) → revoke all tokens for user |
| User logs out on one device | Only that device's refresh token revoked; other sessions continue |
| "Logout all devices" (future) | Delete all refresh_tokens for user_id |
| Refresh token expired (>7 days) | Returns 401; frontend redirects to /login |

#### Acceptance Criteria
- [ ] Access token expires in exactly 15 minutes
- [ ] Refresh token stored in httpOnly cookie, never in localStorage
- [ ] Token refresh issues new access token without requiring re-login
- [ ] Logout deletes refresh token from DB
- [ ] Tampered access tokens return 401 immediately
- [ ] Role claims in JWT are re-verified against DB on sensitive admin actions

---

### F-AUTH-04 — Password Reset

**Priority:** P1 · **Phase:** 1 · **Persona:** All

#### Purpose
Allow users who have forgotten their password to securely reset it via a time-limited email link.

#### Workflow
```
1. User visits /forgot-password, enters email
2. Backend looks up user by email
3. If not found → return 200 anyway (don't reveal email existence)
4. Generate reset token (UUID, expires 1 hour), store hashed in DB
5. Send email with link: /reset-password?token={uuid}
6. User clicks link → enters new password + confirm
7. Backend validates token (valid? not expired? not used?)
8. Backend updates password_hash, deletes token, revokes all refresh tokens
9. User redirected to /login with "Password reset successful" message
```

#### Database
```sql
password_reset_tokens (id, user_id, token_hash, expires_at, used_at, created_at)
```

#### Edge Cases
| Case | Handling |
|---|---|
| Email not registered | Return 200 same as success — never reveal email existence |
| Reset token expired (>1h) | Return 410 with link to request a new one |
| Reset token used twice | Second use returns 400 (token already deleted on first use) |
| User requests reset twice quickly | Only latest token is valid; previous invalidated |
| New password same as old | No restriction — user's choice |

#### Acceptance Criteria
- [ ] Reset email sent within 30 seconds of request
- [ ] Token expires in exactly 1 hour
- [ ] Using an expired token returns a user-friendly error with a resend option
- [ ] Successful reset revokes all active refresh tokens (forces re-login on all devices)
- [ ] Non-existent email returns 200 (no email enumeration)
- [ ] New password is hashed before storage

---

### F-AUTH-05 — Account Deletion (GDPR)

**Priority:** P1 · **Phase:** 1 · **Persona:** All

#### Purpose
Allow users to permanently delete their account and all associated data. Required for GDPR compliance and user trust.

#### Workflow
```
1. User navigates to Settings → Danger Zone → "Delete Account"
2. Confirmation modal: user types their email to confirm
3. Backend validates email matches authenticated user
4. Account enters soft-delete state: is_deleted = true, deleted_at = now
5. All active sessions revoked immediately
6. Scheduled job runs after 30-day grace period:
   - Hard-delete: user row, profile, saved jobs, notification logs
   - Anonymize: notification_logs (replace user_id with null)
   - Delete: resume from object storage
7. Confirmation email sent at initiation and at completion of hard delete
```

#### Edge Cases
| Case | Handling |
|---|---|
| User tries to log in during grace period | Return 403 "Account scheduled for deletion — contact support to cancel" |
| User requests cancellation during grace period | Set is_deleted = false if within 30 days |
| User has active saved jobs at deletion | Deleted with user data |
| User re-registers with same email after hard delete | Allowed — treated as new account |

#### Acceptance Criteria
- [ ] Account soft-deleted immediately on confirmation
- [ ] All sessions revoked on soft-delete
- [ ] Hard delete runs exactly 30 days after soft-delete
- [ ] Confirmation email sent at initiation and completion
- [ ] Deleted user data is unrecoverable after hard delete
- [ ] User can cancel deletion within 30-day grace period

---

## MODULE: STUDENT PROFILE

---

### F-PROF-01 — Skills Selection

**Priority:** P0 · **Phase:** 1 · **Persona:** Aarav, Rahul, Sneha, Priya

#### Purpose
Allow students to declare their skills from a canonical list. These skills are the primary matching signal for job notifications. The better the skills are specified, the more relevant the matches.

#### Workflow
```
1. User reaches Profile Setup Step 2 (or visits /profile/edit)
2. Searchable multi-select input renders with canonical skill list
3. User types "Py" → filtered results: Python, PyTorch, Pytest, PySpark
4. User selects skills by clicking (chips appear above input)
5. User can remove chips by clicking X
6. Minimum 1 skill required before proceeding
7. On save: user_skills table updated (replace all, not append)
8. Change takes effect on next notification matching run
```

#### Database
```sql
skills (id, name, slug, category)
  -- Canonical skill list, seeded. Example categories: language, framework,
  -- database, cloud, tool, domain

user_skills (id, user_id, skill_id, created_at)
  -- Many-to-many: one row per user-skill pair
  -- Indexed on user_id for fast profile reads
```

#### API
```
GET /api/skills?q={search_term}
  Returns: [{ id, name, slug, category }]
  No auth required (public endpoint)
  Cache: Redis, 1 hour TTL (skill list rarely changes)

GET /api/profile/skills
  Returns: [{ id, name, slug, category }]  (user's current skills)
  Auth: Required

PUT /api/profile/skills
  Body: { skill_ids: [1, 4, 17, 23] }
  Returns: 200 { updated_skills: [...] }
  Behavior: Replaces all current skills
  Validation: All IDs must exist in skills table
```

#### Frontend
- Searchable chip-input component (Combobox pattern)
- Skills grouped by category in dropdown (Languages, Frameworks, Databases, etc.)
- Selected skills shown as removable chips above input
- Counter: "12 skills selected"
- Popular skills suggested when input is empty (top 20 most common)
- Mobile-optimized: larger tap targets, keyboard-friendly

#### Backend
- Skill search: case-insensitive ILIKE on `skills.name`
- Skills canonical list seeded at database setup from `database/seeds/skills.json`
- New skills can be added by admin only — no user-submitted skills to prevent spam
- `user_skills` table uses ON CONFLICT DO NOTHING for idempotent saves

#### Edge Cases
| Case | Handling |
|---|---|
| User saves 0 skills | Return 400 "At least 1 skill is required" |
| User tries to add non-existent skill_id | Return 400 "Invalid skill ID" |
| Skill list search returns 0 results | Show "No matching skills — request a skill via feedback" |
| User has 100+ skills | No hard limit, but UI shows warning at 30+ "Broad profiles may receive lower-quality matches" |
| Skill added to canonical list mid-session | User must refresh to see new skill in search |

#### Acceptance Criteria
- [ ] Skill search returns results within 200ms (Redis cached)
- [ ] User can select, view, and remove skills
- [ ] Minimum 1 skill enforced before saving
- [ ] Saving with invalid skill IDs returns 400
- [ ] `user_skills` table accurately reflects final state after save
- [ ] Skill changes are reflected in notification matching within 15 minutes

---

### F-PROF-02 — Job Role & Location Preferences

**Priority:** P0 · **Phase:** 1 · **Persona:** All

#### Purpose
Define the types of jobs and locations the user wants to see. Along with skills, these are the core matching signals. A job is only sent to a user if it matches their role type AND location (or remote preference).

#### Workflow
```
1. Profile Setup Step 3 (or /profile/edit)
2. Role type: multi-select from canonical role list
   (Software Engineer, Data Analyst, Product Manager, Marketing, etc.)
3. Location: city multi-select + "Remote" toggle + "Open to relocation" toggle
4. Experience level: single select
   (Fresher, 0–1 year, 1–2 years, 2–3 years)
5. On save: user_preferences table updated
6. Takes effect on next matching run
```

#### Database
```sql
role_types (id, name, slug)
  -- e.g. software_engineer, data_analyst, product_manager

cities (id, name, state, country)
  -- Seeded list of major Indian cities + "Remote"

user_preferences (
  id, user_id,
  experience_level ENUM('fresher','0-1yr','1-2yr','2-3yr'),
  open_to_remote BOOLEAN,
  open_to_relocation BOOLEAN,
  created_at, updated_at
)

user_preferred_roles (id, user_id, role_type_id)
user_preferred_locations (id, user_id, city_id)
```

#### API
```
GET /api/preferences/role-types
  Returns: [{ id, name, slug }]
  Cache: Redis, 24h TTL

GET /api/preferences/cities
  Returns: [{ id, name, state }]
  Cache: Redis, 24h TTL

GET /api/profile/preferences
  Returns: { experience_level, open_to_remote, role_type_ids, city_ids }
  Auth: Required

PUT /api/profile/preferences
  Body: { experience_level, open_to_remote, open_to_relocation,
          role_type_ids, city_ids }
  Returns: 200 { updated: true }
```

#### Edge Cases
| Case | Handling |
|---|---|
| User selects 0 role types | Return 400 — at least 1 required |
| User selects 0 locations and remote = false | Return 400 — at least 1 location or remote must be selected |
| User selects "Remote" only | Valid — only remote jobs matched |
| User changes experience level mid-search | Takes effect on next match run; historical notifications unaffected |

#### Acceptance Criteria
- [ ] Role type multi-select works with at least 10 role options
- [ ] City multi-select includes major Indian cities + "Remote" option
- [ ] Experience level single-select has exactly 4 options
- [ ] At least 1 role type and 1 location (or remote) required
- [ ] Changes take effect within 15 minutes of saving

---

### F-PROF-03 — Notification Preferences & Quiet Hours

**Priority:** P1 · **Phase:** 1 · **Persona:** Priya, Sneha

#### Purpose
Let users control how and when they receive notifications. Critical for users like Priya (digest-only) and Sneha (weekday quiet hours). Over-notification is the fastest path to bot disconnection.

#### Workflow
```
1. Profile → Notification Settings
2. Notification channel: Telegram only / Email only / Both (default: Both)
3. Telegram frequency: All matches / Only exact matches (all prefs aligned)
4. Email digest: Daily (default) / Weekly / Off
5. Quiet hours: Toggle on → set start time and end time
   (e.g., 9:00 AM – 7:00 PM on weekdays)
6. On save: notification_preferences updated
7. Scheduler reads these preferences before dispatching each notification
```

#### Database
```sql
notification_preferences (
  id, user_id,
  telegram_enabled BOOLEAN DEFAULT true,
  email_enabled BOOLEAN DEFAULT true,
  telegram_frequency ENUM('all','exact_match') DEFAULT 'all',
  email_digest_frequency ENUM('daily','weekly','off') DEFAULT 'daily',
  quiet_hours_enabled BOOLEAN DEFAULT false,
  quiet_start TIME,         -- e.g., '09:00'
  quiet_end TIME,           -- e.g., '19:00'
  quiet_days VARCHAR[],     -- e.g., ['mon','tue','wed','thu','fri']
  timezone VARCHAR DEFAULT 'Asia/Kolkata',
  updated_at TIMESTAMP
)
```

#### API
```
GET /api/profile/notification-preferences
  Returns: full notification_preferences object

PUT /api/profile/notification-preferences
  Body: { telegram_enabled, email_enabled, telegram_frequency,
          email_digest_frequency, quiet_hours_enabled,
          quiet_start, quiet_end, quiet_days, timezone }
  Returns: 200 { updated: true }
```

#### Backend — Quiet Hours Logic
```python
def should_notify(user_pref, now_utc):
    if not user_pref.quiet_hours_enabled:
        return True
    user_now = now_utc.astimezone(user_pref.timezone)
    day = user_now.strftime('%a').lower()  # 'mon', 'tue', etc.
    if day not in user_pref.quiet_days:
        return True
    return not (user_pref.quiet_start <= user_now.time() <= user_pref.quiet_end)
    # If in quiet hours: queue notification for dispatch after quiet_end
```

#### Edge Cases
| Case | Handling |
|---|---|
| Telegram disabled but user never set up email | Warn: "You have no active notification channel" |
| Quiet hours span midnight (e.g., 11 PM – 7 AM) | quiet_start > quiet_end → handled as overnight range |
| Notification queued during quiet hours | Held in Redis queue, dispatched at quiet_end time |
| User in non-IST timezone | timezone field stored; all quiet hour comparisons done in user's timezone |
| User turns off all channels | Show warning, allow save — it's their choice |

#### Acceptance Criteria
- [ ] Users can enable/disable Telegram and email independently
- [ ] Quiet hours suppress notifications during configured time window
- [ ] Notifications queued during quiet hours are sent at quiet_end (not dropped)
- [ ] "Exact match only" Telegram mode only fires when all 3 preference types match the job
- [ ] Timezone is stored and used correctly for quiet hour calculations
- [ ] Changes take effect within 15 minutes

---

### F-PROF-04 — Resume Upload & AI Skill Extraction

**Priority:** P2 · **Phase:** 2 · **Persona:** Priya, Rahul

#### Purpose
Let users upload their resume PDF so the platform can automatically extract their skills and pre-populate their profile. Reduces onboarding friction for users who find the skill multi-select tedious.

#### Workflow
```
1. User navigates to Profile → Resume → "Upload Resume"
2. File picker opens: PDF only, max 5MB
3. Frontend validates file type and size before upload
4. File uploaded to object storage (S3/R2) via signed URL
5. Storage path saved to user_profiles.resume_url (private — no public access)
6. AI agent triggered: Resume Skill Extractor
7. Agent reads PDF text, extracts skills, maps to canonical skill list
8. Results shown to user: "We found these skills in your resume"
9. User reviews and confirms (or removes/adds skills)
10. On confirm: user_skills updated with merged set
```

#### Database
```sql
user_profiles (
  id, user_id,
  resume_url VARCHAR,       -- S3/R2 private path
  resume_uploaded_at TIMESTAMP,
  resume_extraction_status ENUM('pending','processing','done','failed')
)
```

#### Edge Cases
| Case | Handling |
|---|---|
| Non-PDF file uploaded | Rejected client-side (file type check) and server-side (MIME type check) |
| PDF over 5MB | Rejected with "File too large — max 5MB" |
| PDF with no text (scanned image) | Agent returns empty extraction; user notified to use the manual selector |
| Agent extraction fails | Mark status as 'failed', notify user, allow manual entry |
| Skills extracted not in canonical list | Agent maps to closest canonical skills; unrecognized skills are logged for admin review |
| User uploads new resume | Old resume deleted from storage; extraction reruns |

#### Acceptance Criteria
- [ ] Only PDF files accepted (validated on both frontend and backend)
- [ ] Files over 5MB rejected before upload
- [ ] Resume stored in private object storage (no public URL)
- [ ] Skill extraction completes within 60 seconds of upload
- [ ] Extracted skills presented for user confirmation before saving
- [ ] User can proceed without uploading a resume at any point

---

## MODULE: SCRAPER PIPELINE

---

### F-SCRP-01 — ATS Auto-Detector

**Priority:** P0 · **Phase:** 1 · **Persona:** Karan (Admin)

#### Purpose
Before scraping a company's career page, automatically identify which ATS (Applicant Tracking System) it uses. This selects the correct scraper adapter, avoiding generic failures.

#### Workflow
```
1. Receive career page URL for a company
2. Fetch the page HTML (HEAD request first to check robots.txt)
3. Run fingerprinting checks in order:
   a. URL pattern match (e.g., .workday.com, .greenhouse.io, .lever.co)
   b. HTML signature match (unique class names, meta tags, script src)
   c. API endpoint probe (e.g., /api/v1/boards for Greenhouse)
4. Return detected ATS type as string
5. If no match: return "generic"
6. Log detection result to scrape_runs
```

#### Detection Signatures

| ATS | URL Signal | HTML Signal | API Probe |
|---|---|---|---|
| Workday | `*.myworkdayjobs.com` | `wd3-app.com` script | — |
| Greenhouse | `boards.greenhouse.io` | `#grnhse_app` div | `/embed/job_board` |
| Lever | `jobs.lever.co` | `lever-jobs-embed` | — |
| iCIMS | `*.icims.com` | `iCIMS_Header` class | — |
| Taleo | `*.taleo.net` | `TaleoContainer` class | — |
| SmartRecruiters | `careers.smartrecruiters.com` | `smartrecruiters-widget` | — |
| Generic | — | None of the above | — |

#### Edge Cases
| Case | Handling |
|---|---|
| Company uses custom domain masking ATS | Fall through to HTML/API probe stages |
| Page returns 403/429 on detection | Log failure, skip company for this run |
| Company recently switched ATS | Detection runs fresh each scrape — no cached ATS type |
| New ATS not in signature list | Returns "generic"; admin can manually override |

#### Acceptance Criteria
- [ ] Correctly identifies Workday, Greenhouse, Lever, iCIMS, Taleo from URL and HTML signals
- [ ] Returns "generic" instead of crashing on unknown ATS
- [ ] Detection completes within 5 seconds per company
- [ ] Detection result is logged with each scrape run record

---

### F-SCRP-02 — Scraper Adapters (Workday / Greenhouse / Lever / iCIMS / Taleo)

**Priority:** P0 · **Phase:** 1 · **Persona:** Karan (Admin)

#### Purpose
Extract job listings from each supported ATS. Each adapter is tailored to that ATS's specific HTML structure, pagination pattern, and data format.

#### Workflow (per adapter)
```
1. Receive company career page URL + ATS type
2. Fetch job listings page (with rate limiting + retry logic)
3. Parse job list: extract title, job URL, location from listing page
4. For each job URL: fetch job detail page
5. Extract: apply_url, raw_description, company_posted_at, salary_range, deadline
6. Return list of raw job objects
```

#### Adapter-Specific Details

**Workday**
- Job list: fetched from `/wday/cxs/{tenant}/jobs` JSON API
- Pagination: `offset` + `limit` params (default 20/page)
- Posted date: `postedOn` field in response JSON
- Apply URL: direct link to Workday application form

**Greenhouse**
- Job list: `boards.greenhouse.io/embed/job_board/for/{company}` JSON
- Pagination: single JSON response, all jobs
- Posted date: `updated_at` field (approximate)
- Apply URL: `absolute_url` field

**Lever**
- Job list: `api.lever.co/v0/postings/{company}?mode=json`
- Pagination: `next` cursor in response headers
- Posted date: `createdAt` Unix timestamp
- Apply URL: `applyUrl` field

**iCIMS**
- Job list: iFrame-based, requires HTML parsing
- Pagination: page query param
- Posted date: scraped from detail page HTML
- Apply URL: constructed from job ID

**Taleo**
- Job list: XML/JSON API (`/careersection/rest/jobboard/searchjobs`)
- Pagination: `start` + `pageSize` params
- Posted date: `referenceDate` field
- Apply URL: redirect through Taleo's application gateway

#### Output Schema (all adapters)
```json
{
  "title": "Software Engineer — Backend",
  "company": "Razorpay",
  "location": "Bengaluru, Karnataka",
  "apply_url": "https://boards.greenhouse.io/razorpay/jobs/12345",
  "raw_description": "<full HTML or plain text of JD>",
  "company_posted_at": "2025-06-22T08:30:00Z",
  "salary_range": "₹12–18 LPA",
  "deadline": "2025-07-15",
  "source_ats": "greenhouse"
}
```

#### Edge Cases
| Case | Handling |
|---|---|
| ATS API returns 429 (rate limited) | Back off for 60 seconds, retry once, then skip run |
| Adapter finds 0 jobs | Log as success with jobs_found = 0 (company may have no open roles) |
| Job detail page returns 404 | Skip job, log as missing_detail |
| Raw description is empty | Flag for admin review; still save job record with empty description |
| company_posted_at not available | Use current time as fallback; do NOT use this as a "posted 2 seconds ago" signal — mark as approximate |
| Salary field missing | Set salary_range = null (acceptable — many jobs don't list salary) |

#### Acceptance Criteria
- [ ] All 5 adapters return jobs in the standard output schema
- [ ] Each adapter handles pagination (all jobs fetched, not just first page)
- [ ] Rate limiting and retry logic applied at the BaseScraper level
- [ ] Adapters recover gracefully from missing optional fields (salary, deadline)
- [ ] company_posted_at is populated from the ATS source, not scraped_at
- [ ] Each adapter tested against at least 3 real company career pages

---

### F-SCRP-03 — Scrape Scheduler (15-min Cron)

**Priority:** P0 · **Phase:** 1

#### Purpose
Continuously trigger scrape batches at regular intervals so that new jobs are discovered within 15–30 minutes of being posted on a company career page.

#### Workflow
```
1. APScheduler fires every 15 minutes
2. Query companies table: active = true, ordered by last_scraped_at ASC
   (companies not scraped recently are prioritized)
3. Select batch of N companies (configurable, default 20 per run)
4. For each company in batch:
   a. Run ATS detector
   b. Run appropriate adapter
   c. For each raw job: push to AI agent pipeline queue (Redis)
5. Update company.last_scraped_at = now (success or failure)
6. Write scrape_run record
```

#### Configuration
```python
# scheduler/config.py
SCRAPE_INTERVAL_MINUTES = 15
SCRAPE_BATCH_SIZE = 20         # companies per run
MAX_JOBS_PER_COMPANY = 50      # cap to prevent runaway scrapes
SCRAPER_TIMEOUT_SECONDS = 30   # per company
```

#### Edge Cases
| Case | Handling |
|---|---|
| Previous batch still running when next fires | Skip trigger, log "batch already running" |
| All companies scraped recently (< 15 min ago) | Run with smallest batch; update last_scraped_at anyway |
| Scheduler process crashes | APScheduler resumes on restart; no missed run compensation needed for MVP |
| Redis queue full | Log error, skip queuing for that run, alert admin |

#### Acceptance Criteria
- [ ] Scheduler fires within ±30 seconds of the 15-minute interval
- [ ] Companies sorted by last_scraped_at ASC (least recently scraped first)
- [ ] Concurrent run prevention works correctly
- [ ] Batch size configurable via environment variable
- [ ] Scheduler logs each trigger event

---

### F-SCRP-04 — Scrape Run Logging

**Priority:** P0 · **Phase:** 1 · **Persona:** Karan (Admin)

#### Purpose
Record every scrape run for every company. This is the primary data source for the admin scraper health dashboard and failure alerting.

#### Database
```sql
scrape_runs (
  id UUID PRIMARY KEY,
  company_id INTEGER REFERENCES companies(id),
  started_at TIMESTAMP NOT NULL,
  completed_at TIMESTAMP,
  status ENUM('success','partial','failed') NOT NULL,
  jobs_found INTEGER DEFAULT 0,
  jobs_new INTEGER DEFAULT 0,
  jobs_duplicate INTEGER DEFAULT 0,
  error_message TEXT,           -- human-readable, not stack trace
  error_type VARCHAR,           -- 'layout_change', 'rate_limited', 'captcha', 'timeout', 'unknown'
  adapter_used VARCHAR,         -- 'workday', 'greenhouse', etc.
  duration_seconds FLOAT
)

-- Indexes
CREATE INDEX idx_scrape_runs_company_id ON scrape_runs(company_id);
CREATE INDEX idx_scrape_runs_started_at ON scrape_runs(started_at DESC);
CREATE INDEX idx_scrape_runs_status ON scrape_runs(status);
```

#### Acceptance Criteria
- [ ] Every scrape attempt creates a scrape_run record (success or failure)
- [ ] error_message is in plain English, not a Python exception string
- [ ] jobs_new correctly counts only jobs not previously in the DB
- [ ] duration_seconds is populated for all completed runs
- [ ] Old scrape_runs purged after 90 days (retention policy)

---

### F-SCRP-05 — robots.txt Compliance & Rate Limiting

**Priority:** P0 · **Phase:** 1

#### Purpose
Ensure all scraping respects site rules and does not overload target servers. Legal, ethical, and practical requirement.

#### robots.txt Compliance
```python
# scrapers/base_scraper.py
def is_allowed(url: str) -> bool:
    robots_url = f"{get_base_url(url)}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch("JobFinderAI-Bot/1.0", url)
```

#### Rate Limiting
```python
# Per-domain rate limit: 1 request per 3 seconds
# Implemented via Redis token bucket per domain
# Key: rate_limit:{domain}
# Value: last_request_timestamp

def rate_limit(domain: str):
    now = time.time()
    last = redis.get(f"rate_limit:{domain}") or 0
    wait = max(0, 3.0 - (now - float(last)))
    if wait > 0:
        time.sleep(wait)
    redis.set(f"rate_limit:{domain}", now, ex=60)
```

#### Retry with Exponential Backoff
```python
# 3 retries, delays: 2s, 4s, 8s
for attempt in range(3):
    try:
        response = fetch(url, timeout=30)
        return response
    except (Timeout, ConnectionError) as e:
        if attempt == 2:
            raise ScraperFailure(str(e))
        time.sleep(2 ** (attempt + 1))
```

#### Acceptance Criteria
- [ ] robots.txt fetched and parsed before every scrape (cached 1 hour per domain)
- [ ] Disallowed paths are skipped and logged
- [ ] Maximum 1 request per 3 seconds per domain enforced via Redis
- [ ] Retry logic fires on timeout and connection errors (not on 4xx responses)
- [ ] CAPTCHA response codes (403 with CAPTCHA body, 429) skip and alert

---

## MODULE: AI AGENT PIPELINE

---

### F-AGNT-01 — Duplicate Detector

**Priority:** P0 · **Phase:** 1

#### Purpose
Prevent the same job from being inserted twice into the database. Without deduplication, users receive duplicate notifications and the DB fills with noise.

#### Workflow
```
1. Receive raw job object from scraper
2. Compute canonical hash:
   SHA256(normalize(title) + "|" + normalize(company) + "|" + normalize(apply_url))
3. Check jobs table: WHERE content_hash = computed_hash
4. If found: skip job, increment jobs_duplicate in scrape_run
5. If not found: proceed to Job Extractor agent
```

#### Normalization Rules
```python
def normalize(s: str) -> str:
    return s.lower().strip()
         .replace("–", "-")         # em dash normalization
         .replace("\u200b", "")     # zero-width spaces
         .replace("  ", " ")        # double spaces
```

#### Database
```sql
jobs (
  ...
  content_hash VARCHAR(64) UNIQUE NOT NULL,
  ...
)
CREATE UNIQUE INDEX idx_jobs_content_hash ON jobs(content_hash);
```

#### Edge Cases
| Case | Handling |
|---|---|
| Same job reposted with slightly different title | Hash differs → treated as new job (acceptable) |
| Same job on two different ATS portals | Different apply_url → different hash → two records. Semantic dedup is Phase 3. |
| Job URL changes when company migrates ATS | New hash → new record (acceptable) |
| Hash collision | SHA256 collision probability negligible; no special handling needed |

#### Acceptance Criteria
- [ ] Duplicate jobs never inserted into the DB (UNIQUE constraint enforces)
- [ ] Deduplication check completes in < 10ms (single indexed lookup)
- [ ] jobs_duplicate counter incremented in scrape_run for every skipped job
- [ ] Normalization handles unicode, whitespace, and punctuation variants

---

### F-AGNT-02 — Job Extractor Agent

**Priority:** P0 · **Phase:** 1

#### Purpose
Transform raw job HTML or JSON from a scraper into a clean, structured record. This is the most critical agent — if extraction fails, no downstream agents run.

#### Workflow
```
1. Receive raw job object (title, apply_url, raw_description, company_posted_at)
2. Build prompt (loaded from docs/20_PROMPTS.md — version: extractor_v1)
3. Call LLM API (GPT-4o or claude-sonnet) with raw_description
4. Parse JSON response
5. If parse fails: retry once with explicit JSON repair instruction
6. If second parse fails: log to agent_logs as 'failed', flag for admin review
7. If extraction_confidence < 0.75: flag for admin review queue
8. Merge extracted fields with scraper-provided fields (scraper fields take precedence for apply_url)
9. Save to jobs table
```

#### Output Schema
```json
{
  "title": "Software Engineer — Backend",
  "company": "Razorpay",
  "location": "Bengaluru, Karnataka",
  "location_type": "hybrid",
  "salary_range": "₹12–18 LPA",
  "deadline": "2025-07-15",
  "apply_url": "https://...",
  "raw_description": "...",
  "extraction_confidence": 0.92
}
```

#### Agent Log Schema
```sql
agent_logs (
  id UUID PRIMARY KEY,
  job_id UUID REFERENCES jobs(id),
  agent_name VARCHAR NOT NULL,     -- 'job_extractor', 'skill_extractor', etc.
  prompt_version VARCHAR NOT NULL, -- 'extractor_v1'
  model_used VARCHAR NOT NULL,     -- 'gpt-4o', 'claude-sonnet-4-6'
  input_hash VARCHAR(64),          -- SHA256 of prompt input (for cache lookup)
  output_json JSONB,
  status ENUM('success','failed','retried'),
  latency_ms INTEGER,
  error_message TEXT,
  created_at TIMESTAMP
)
```

#### Edge Cases
| Case | Handling |
|---|---|
| LLM returns malformed JSON | Retry once with "respond ONLY with valid JSON" instruction |
| LLM hallucinates a salary not in JD | Confidence scored low; flagged for admin review |
| JD is in a language other than English | Extraction attempted; confidence likely low; flagged |
| JD is extremely long (>8000 tokens) | Truncate to 6000 tokens; log truncation in agent_log |
| LLM API rate limit hit | Back off 30s, retry up to 3 times; if all fail, log and skip |

#### Acceptance Criteria
- [ ] Structured JSON output produced for >95% of job descriptions
- [ ] All agent calls logged to agent_logs table
- [ ] Parse failure retries exactly once before marking as failed
- [ ] extraction_confidence < 0.75 flags job for admin review
- [ ] Prompt loaded from config, never hardcoded in agent code

---

### F-AGNT-03 — Skill Extractor Agent

**Priority:** P0 · **Phase:** 1

#### Purpose
Parse the job description and return two lists: required skills (must-have for the role) and preferred skills (nice-to-have). These are used for user-to-job matching and the skill match overlay on job cards.

#### Output Schema
```json
{
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "preferred_skills": ["Go", "Redis", "Kubernetes"],
  "degree_required": false,
  "degree_note": "equivalent experience accepted"
}
```

Note: `degree_required` and `degree_note` are extracted here because they are critical for Persona 3 (Rahul — self-taught developer). See `02_USER_PERSONAS.md` for context.

#### Database
```sql
job_skills (
  id UUID,
  job_id UUID REFERENCES jobs(id),
  skill_id INTEGER REFERENCES skills(id),
  is_required BOOLEAN,      -- true = required, false = preferred
  created_at TIMESTAMP
)
```

#### Skill Mapping Logic
```
Agent returns raw skill names: ["Python 3.10", "FastAPI (>=0.95)", "Postgres"]
↓
Normalization: ["Python", "FastAPI", "PostgreSQL"]
↓
Match against canonical skills table (case-insensitive exact match)
↓
Unmatched skills logged to agent_logs.output_json['unmatched_skills']
↓
Matched skills inserted into job_skills table
```

#### Acceptance Criteria
- [ ] required_skills and preferred_skills returned as separate arrays
- [ ] Skills mapped to canonical skills table entries where possible
- [ ] degree_required field extracted from JD when clearly stated
- [ ] Unmatched skill names logged for canonical list review
- [ ] Skill data available for matching within 5 minutes of job insert

---

### F-AGNT-04 — JD Summarizer Agent

**Priority:** P0 · **Phase:** 1 · **Persona:** All (highest user-facing impact)

#### Purpose
Generate exactly 5 bullet points that answer the question a student actually asks: "Is this job worth 30 minutes of my application time?" Each bullet must be plain English, specific, and actionable.

#### Output Schema
```json
{
  "summary": [
    "Build payment APIs used by 10M+ merchants across India and Southeast Asia",
    "Python and FastAPI are required; 0–2 years of experience accepted",
    "Hybrid role in Bengaluru — 3 days office, 2 days remote",
    "Competitive salary with ESOP — exact range not disclosed",
    "Small team of 6 engineers; direct ownership of features from day one"
  ]
}
```

#### Quality Rules (enforced via prompt)
1. Each bullet must be a complete sentence, 10–20 words
2. No corporate jargon ("synergize", "leverage", "ecosystem")
3. Bullet 2 must always mention experience requirement if stated in JD
4. Bullet 3 must mention location/remote status
5. If salary is in JD, include it. If not, say so explicitly.
6. No bullet should repeat information from another bullet

#### Edge Cases
| Case | Handling |
|---|---|
| JD contains no experience requirement | Bullet 2 says "No specific experience level mentioned in the job description" |
| JD is extremely vague | Summary reflects vagueness; confidence scored low |
| JD mentions relocation required | Must appear in one of the 5 bullets |
| JD only has a list of requirements (no role description) | Agent generates summary from requirements alone |

#### Acceptance Criteria
- [ ] Exactly 5 bullet points returned (no more, no less)
- [ ] Each bullet is ≤ 25 words and plain English
- [ ] Experience level mentioned in summary when present in JD
- [ ] Location/remote status mentioned in summary
- [ ] Summary displayed on both job card (first 2 bullets) and job detail (all 5)

---

### F-AGNT-05 — Job Classifier Agent

**Priority:** P0 · **Phase:** 1

#### Purpose
Classify the job by role type, domain, seniority level, and work mode. These classifications power the filter system and match-scoring logic.

#### Output Schema
```json
{
  "role_type": "software_engineer",
  "domain": "fintech",
  "experience_level": "fresher",
  "is_remote": false,
  "is_hybrid": true,
  "is_internship": false,
  "company_type": "product",
  "classification_confidence": 0.89
}
```

#### Classification Taxonomy

**role_type options:**
`software_engineer`, `data_analyst`, `data_scientist`, `product_manager`, `devops_engineer`, `ml_engineer`, `frontend_developer`, `backend_developer`, `fullstack_developer`, `marketing_manager`, `growth_manager`, `business_analyst`, `ux_designer`, `qa_engineer`, `technical_writer`, `other`

**domain options:**
`fintech`, `edtech`, `healthtech`, `ecommerce`, `saas`, `gaming`, `media`, `logistics`, `enterprise`, `startup`, `other`

**experience_level options:**
`fresher`, `0-1yr`, `1-2yr`, `2-3yr`, `3-5yr`, `5+yr`

**company_type options:**
`product`, `services`, `startup`, `enterprise`, `agency`, `unknown`

Note: `company_type` is one of the highest-value fields for Persona 4 (Sneha), who explicitly wants to avoid services companies.

#### Acceptance Criteria
- [ ] All 6 fields present in every classifier output
- [ ] role_type matches one of the defined taxonomy values (or "other")
- [ ] experience_level extracted from JD where stated; inferred from requirements where not
- [ ] is_internship correctly identified from title and JD content
- [ ] Classification used immediately for user-to-job matching
- [ ] Low-confidence classifications (< 0.75) flagged for review

---

## MODULE: JOB LISTINGS & FEED

---

### F-JOBS-01 — Job Listings Feed

**Priority:** P0 · **Phase:** 1 · **Persona:** All

#### Purpose
The main page of the web app. A paginated, sortable list of all scraped and processed jobs. The student's home base for manual discovery.

#### Workflow
```
1. User lands on /jobs (or / → redirect to /jobs)
2. Page fetches GET /api/jobs?page=1&limit=20
3. Jobs rendered as cards, sorted by company_posted_at DESC
4. Infinite scroll or pagination loads next page on demand
5. Filter bar at top — changes trigger new API call with filter params
6. Each card shows: company logo, title, company name, location,
   "Posted X ago", required skills chips (max 4 shown), apply button
```

#### Database Query
```sql
SELECT j.*, c.name as company_name, c.logo_url,
       array_agg(s.name) FILTER (WHERE js.is_required = true) as required_skills
FROM jobs j
JOIN companies c ON j.company_id = c.id
LEFT JOIN job_skills js ON j.id = js.job_id
LEFT JOIN skills s ON js.skill_id = s.id
WHERE j.is_active = true
  AND j.extraction_confidence >= 0.75
  AND (filter conditions from query params)
GROUP BY j.id, c.name, c.logo_url
ORDER BY j.company_posted_at DESC
LIMIT 20 OFFSET {page * 20};

-- Indexes required:
-- idx_jobs_company_posted_at (DESC)
-- idx_jobs_is_active
-- idx_jobs_role_type
-- idx_jobs_experience_level
```

#### API
```
GET /api/jobs
  Query params:
    page (int, default 0)
    limit (int, default 20, max 50)
    role_type (string, comma-separated)
    location (string, comma-separated city slugs)
    experience_level (string)
    is_remote (boolean)
    q (string, full-text search)
  Returns: {
    jobs: [JobCard],
    total: int,
    page: int,
    has_more: boolean
  }
  Auth: Optional (authenticated users see skill match overlay)
  Cache: 2-minute Redis cache per unique query param combination
```

#### Frontend Components
```
/jobs
  └── FilterBar
        ├── RoleTypeFilter (multi-select dropdown)
        ├── LocationFilter (multi-select with search)
        ├── ExperienceFilter (single-select)
        └── RemoteToggle
  └── JobFeed
        └── JobCard (×20 per page)
              ├── CompanyLogo
              ├── JobTitle
              ├── CompanyName + Location + PostedAt
              ├── SkillChips (required_skills, max 4)
              └── ApplyButton
  └── Pagination / InfiniteScroll trigger
```

#### Edge Cases
| Case | Handling |
|---|---|
| Zero results for filter combination | Show "No jobs match your filters" + "Clear filters" button |
| Job removed from company career page | Set is_active = false; hidden from feed |
| Scraper finds new job mid-session | User must refresh; no real-time feed updates in MVP |
| Large skill chip list (15+ required skills) | Show first 4 + "+11 more" badge; all visible in detail view |

#### Acceptance Criteria
- [ ] Feed loads in < 2.5s on 4G (LCP target)
- [ ] Pagination works correctly across 100+ pages
- [ ] All 4 filters work independently and in combination
- [ ] Jobs sorted by company_posted_at DESC, not scraped_at
- [ ] Unauthenticated users see jobs but not skill match overlay
- [ ] API response cached in Redis for 2 minutes per query fingerprint

---

### F-JOBS-02 — Job Filters & Search

**Priority:** P0 (filters) · P1 (search) · **Phase:** 1

#### Purpose
Allow users to narrow the job feed to only relevant listings. Filters must be fast and combinable.

#### Filter Specs

| Filter | Type | Options |
|---|---|---|
| Role Type | Multi-select | All role_type taxonomy values |
| Location | Multi-select + search | All cities in DB + "Remote" |
| Experience Level | Single-select | Fresher / 0–1yr / 1–2yr / 2–3yr |
| Remote Only | Toggle | Boolean |

#### Full-Text Search
```sql
-- PostgreSQL full-text search
ALTER TABLE jobs ADD COLUMN search_vector TSVECTOR;

UPDATE jobs SET search_vector = 
  to_tsvector('english', title || ' ' || COALESCE(raw_description, ''));

CREATE INDEX idx_jobs_search_vector ON jobs USING GIN(search_vector);

-- Search query
WHERE search_vector @@ plainto_tsquery('english', :query)
```

#### Acceptance Criteria
- [ ] Filter changes update results without full page reload
- [ ] Multiple filters combine with AND logic
- [ ] Full-text search queries title and description
- [ ] Search returns results within 300ms on 10,000 job records
- [ ] "Clear all filters" resets to unfiltered feed

---

### F-JOBS-03 — Job Detail View

**Priority:** P0 · **Phase:** 1 · **Persona:** All

#### Purpose
The full information page for a single job. Contains everything a student needs to decide whether to apply: AI summary, full JD, skill breakdown, company info, and the apply button.

#### Layout Sections
```
1. Header
   Company logo | Company name | Job title
   Location | Work mode | Experience level | Posted at

2. AI Summary (most prominent — big, above the fold)
   5-point summary bullets, rendered with icons

3. Skill Match (authenticated users only)
   Required Skills: [Python ✅] [FastAPI ✅] [Go ❌] [Docker ❌]
   Preferred Skills: [Redis ⬜] [Kubernetes ⬜]
   Match: 2/4 required skills matched

4. Apply CTA
   [Apply Now →] (external link, opens in new tab)
   [Save Job] [Mark Applied]

5. Full Job Description
   Collapsible — hidden by default, "View Full JD" to expand

6. Company Info
   Company name, ATS type (so user knows what apply form to expect),
   other open roles at this company
```

#### API
```
GET /api/jobs/{job_id}
  Returns: full job object with skills, summary, company info
  Auth: Optional (skill match overlay requires auth)
  Cache: 5-minute Redis cache per job_id
```

#### Acceptance Criteria
- [ ] AI summary displayed above the fold on both mobile and desktop
- [ ] Full JD accessible via expand (not removed — students like Sneha want it)
- [ ] Skill match overlay shows green/grey chips for authenticated users
- [ ] Apply button opens original ATS URL in new tab
- [ ] Page loads in < 300ms from cache

---

### F-JOBS-04 — "Posted X Minutes Ago" Timestamp

**Priority:** P0 · **Phase:** 1 · **Persona:** Aarav, Rahul

#### Purpose
Show how long ago a job was posted on the company career page — not how long ago the platform scraped it. This is one of the most motivating pieces of information for early applicants.

#### Implementation
```python
# Use company_posted_at, not scraped_at
def format_posted_at(company_posted_at: datetime) -> str:
    delta = datetime.utcnow() - company_posted_at
    if delta.seconds < 3600:
        return f"{delta.seconds // 60} minutes ago"
    if delta.days == 0:
        return f"{delta.seconds // 3600} hours ago"
    if delta.days == 1:
        return "Yesterday"
    if delta.days < 7:
        return f"{delta.days} days ago"
    return company_posted_at.strftime("%d %b %Y")
```

#### Edge Cases
| Case | Handling |
|---|---|
| company_posted_at is null (scraper couldn't extract it) | Show "Posted recently" — never show scraped_at as if it were the post date |
| company_posted_at is in the future (timezone bug) | Cap at "Just now" — never show negative time |
| company_posted_at is 6 months ago (stale job) | Show exact date; don't show "180 days ago" |

#### Acceptance Criteria
- [ ] Timestamp uses company_posted_at exclusively
- [ ] "X minutes ago" shown for jobs < 1 hour old
- [ ] Null company_posted_at shows "Posted recently" (not scrape time)
- [ ] Timestamp updates on page refresh (not cached indefinitely)

---

### F-JOBS-05 — Direct Apply Link

**Priority:** P0 · **Phase:** 1 · **Persona:** All

#### Purpose
Provide a single-tap path from job discovery to the application form. No friction. No intermediate pages. The apply URL goes directly to the ATS application form.

#### Implementation
- Button: `<a href={apply_url} target="_blank" rel="noopener noreferrer">`
- Click is logged to notification_logs as `action: 'apply_click'`
- No redirect through our servers — direct link to ATS

#### Acceptance Criteria
- [ ] Apply button opens ATS URL in a new tab
- [ ] No intermediate redirect page
- [ ] Apply click is logged (for analytics, not for tracking students)
- [ ] Button present on both job card and job detail page
- [ ] Button disabled / shows warning if apply_url is null

---

## MODULE: NOTIFICATION SYSTEM

---

### F-NOTIF-01 — Telegram Bot Connection

**Priority:** P0 · **Phase:** 1 · **Persona:** Aarav, Rahul, Sneha

#### Purpose
Link a user's Job Finder AI account to their Telegram account so the bot can send them personal job alerts.

#### Workflow
```
1. User reaches Profile Setup Step 4 (or Notification Settings)
2. Platform generates a unique one-time link code (UUID, 10 min TTL)
3. UI shows:
   Option A: QR code → scan with Telegram app
   Option B: Link → t.me/JobFinderAIBot?start={code}
4. User opens bot → sends /start {code}
5. Bot webhook receives message
6. Backend: validate code, link telegram_id to user account
7. Bot sends confirmation: "✅ Your account is connected. You'll receive job alerts here."
8. UI updates: "Telegram Connected ✅"
```

#### Database
```sql
users (id, ..., telegram_id BIGINT UNIQUE, telegram_linked_at TIMESTAMP)
telegram_link_codes (id, user_id, code UUID, expires_at, used_at)
```

#### Bot Commands
```
/start {code}   → Link account (if code provided) OR show welcome message
/start          → Show welcome message + link instructions
/pause          → Pause all notifications
/resume         → Resume notifications
/settings       → Show current notification preferences
/unlink         → Unlink Telegram from account
/help           → List all commands
```

#### Edge Cases
| Case | Handling |
|---|---|
| Code expired (>10 min) | Bot responds "Link expired — please generate a new one from the website" |
| Code already used | Bot responds "This link has already been used" |
| User tries to link same Telegram to two accounts | Return error — one Telegram per account |
| Telegram account already linked to different user | Return error, show support contact |
| User sends /start without a code | Show welcome message + instructions to connect via the website |

#### Acceptance Criteria
- [ ] Link code generated and displayed within 2 seconds
- [ ] QR code scannable from phone camera
- [ ] /start command links account within 5 seconds
- [ ] Confirmation message sent immediately after linking
- [ ] Web UI reflects linked status within 10 seconds (polling or websocket)
- [ ] Code expires after 10 minutes
- [ ] /pause and /resume commands work immediately

---

### F-NOTIF-02 — Telegram Instant Job Alert

**Priority:** P0 · **Phase:** 1 · **Persona:** Aarav, Rahul, Sneha

#### Purpose
The core product experience. When a new job matches a user's profile, they receive a Telegram message within 2 minutes — with enough information to decide "apply" or "skip" in under 30 seconds.

#### Matching Logic
```python
def find_matching_users(job: Job) -> list[User]:
    """
    A user matches a job if ALL of the following are true:
    1. Their experience_level matches job.experience_level (±1 level)
    2. At least 1 of their preferred role_types matches job.role_type
    3. At least 1 of their preferred locations matches job.location
       OR (user.open_to_remote = true AND job.is_remote = true)
    4. At least 1 of their skills matches job.required_skills
    5. Their telegram_id is set and telegram_enabled = true
    6. Current time is NOT within their quiet hours
    """
```

#### Message Format
```
🚀 New Job Match

{title}
{company} · {location} · {work_mode}
Posted {posted_at}

📋 What this involves:
• {summary[0]}
• {summary[1]}
• {summary[2]}
• {summary[3]}
• {summary[4]}

🛠 Skills: {required_skills_with_match_icons}

[Apply Now 🔗]  [Save 📌]  [Not Interested ❌]
```

#### Skill Match Icons in Message
```
Required: Python ✅  FastAPI ✅  Go ❌  Docker ❌
(✅ = in user's skill profile  ❌ = not in their profile)
```

#### Notification Pipeline
```
New job saved to DB
  ↓
Notification matching runs (async, within 1 minute)
  ↓
For each matched user:
  Check quiet hours → queue or send immediately
  ↓
Redis notification queue (key: notif:{user_id}:{job_id})
  ↓
Telegram dispatcher: bot.send_message(chat_id=user.telegram_id, ...)
  ↓
Log to notification_logs (status: delivered / failed)
  ↓
On failure: retry queue (up to 3 attempts, 30s apart)
```

#### Edge Cases
| Case | Handling |
|---|---|
| User blocked the bot | Telegram returns 403; mark telegram_enabled = false; send email alert to user |
| User deleted Telegram account | Telegram returns 400; mark telegram_enabled = false |
| Message sending rate limited by Telegram | Queue with delay; Telegram allows 30 messages/second per bot |
| Job matches 10,000 users simultaneously | Batch dispatch with Redis queue; rate-limit to Telegram API limits |
| User receives duplicate notification | Prevented by notification_logs uniqueness check (user_id + job_id + channel) |

#### Acceptance Criteria
- [ ] Notification sent within 2 minutes of job being saved to DB
- [ ] All 5 summary points included in message
- [ ] Skill match icons (✅/❌) correctly reflect user's skill profile
- [ ] Inline keyboard buttons: Apply, Save, Not Interested
- [ ] Quiet hours respected — notification queued, not dropped
- [ ] Duplicate notifications prevented (same user + same job)
- [ ] Delivery logged to notification_logs regardless of success/failure

---

### F-NOTIF-03 — Daily Email Digest

**Priority:** P1 · **Phase:** 1 · **Persona:** Priya

#### Purpose
For users who prefer email over Telegram, or who want a daily summary of all matches. Sent every morning at 8 AM (user's timezone).

#### Workflow
```
1. Scheduler fires daily at 7:30 AM UTC (converts to 1 PM IST — adjust per user timezone)
2. For each user where email_enabled = true AND email_digest = 'daily':
   a. Query all jobs matched to this user in last 24 hours not yet in digest
   b. If 0 matches → skip (don't send empty digest)
   c. Compile top 10 matches sorted by company_posted_at DESC
   d. Render HTML email template with job cards
   e. Send via email service
   f. Log to notification_logs
```

#### Email Content
```
Subject: Your Daily Job Digest — {N} New Matches

Header: Job Finder AI logo + "Good morning, {name}"
Body: Up to 10 job cards, each with:
  - Company + Title
  - Location + Work mode
  - Posted: X hours ago
  - First 2 summary bullets
  - Skills matched: 3/5 required ✅
  - [Apply Now] button
Footer: Unsubscribe link | Change preferences | View all matches on web
```

#### Edge Cases
| Case | Handling |
|---|---|
| User has 0 matches in 24h | Skip digest — don't send empty email |
| User unsubscribed from email | Check notification_preferences before sending |
| Email delivery fails | Retry once after 5 minutes; log failure |
| User's timezone not set | Default to Asia/Kolkata (IST) |

#### Acceptance Criteria
- [ ] Digest sent between 7:30–8:30 AM user local time
- [ ] Empty digest not sent when 0 matches
- [ ] Maximum 10 jobs per digest
- [ ] Unsubscribe link present and functional in every email
- [ ] Each job card has a direct apply link
- [ ] Delivery logged to notification_logs

---

### F-NOTIF-04 — Notification Delivery Log

**Priority:** P0 · **Phase:** 1 · **Persona:** Karan (Admin)

#### Purpose
Record every notification attempt. Enables admin to monitor delivery health, debug failures, and prevent duplicate sends.

#### Database
```sql
notification_logs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  job_id UUID REFERENCES jobs(id),
  channel ENUM('telegram','email') NOT NULL,
  action ENUM('sent','failed','queued','skipped') NOT NULL,
  failure_reason TEXT,
  sent_at TIMESTAMP,
  retry_count INTEGER DEFAULT 0,
  created_at TIMESTAMP,

  UNIQUE(user_id, job_id, channel)  -- prevent duplicate notifications
)

CREATE INDEX idx_notif_logs_user_id ON notification_logs(user_id);
CREATE INDEX idx_notif_logs_sent_at ON notification_logs(sent_at DESC);
CREATE INDEX idx_notif_logs_action ON notification_logs(action);
```

#### Acceptance Criteria
- [ ] Every notification attempt creates a log record
- [ ] UNIQUE constraint prevents duplicate notification for same user+job+channel
- [ ] failure_reason populated in plain English (not exception class)
- [ ] Logs retained for 90 days then purged

---

## MODULE: APPLICATION TRACKING

---

### F-TRACK-01 — Save Job (Bookmark)

**Priority:** P1 · **Phase:** 2 · **Persona:** Priya, Aarav

#### Purpose
Let users bookmark jobs they want to review or apply to later. Creates a personal shortlist separate from the full feed.

#### Workflow
```
1. User clicks "Save" on job card or job detail page
   OR taps "Save 📌" button in Telegram notification
2. Job added to user_saved_jobs with status = 'saved'
3. Button toggles to "Saved ✓" (tap again to unsave)
4. Visible in /my-jobs → Saved tab
```

#### Database
```sql
user_saved_jobs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  job_id UUID REFERENCES jobs(id),
  status ENUM('saved','applied','interviewing','rejected','offer') DEFAULT 'saved',
  notes TEXT,
  saved_at TIMESTAMP DEFAULT now(),
  status_updated_at TIMESTAMP,

  UNIQUE(user_id, job_id)
)
```

#### API
```
POST /api/saved-jobs
  Body: { job_id }
  Returns: 201 { saved_job_id, status: 'saved' }
  Error: 409 if already saved

DELETE /api/saved-jobs/{job_id}
  Returns: 200 { message: "Job unsaved" }

GET /api/saved-jobs
  Query: ?status=saved,applied
  Returns: paginated list of saved jobs with full job details
```

#### Acceptance Criteria
- [ ] Save action works from job card, job detail, and Telegram inline button
- [ ] Duplicate save returns 409 (not an error from user perspective — idempotent)
- [ ] Unsave removes from My Jobs view
- [ ] Saved jobs visible in /my-jobs immediately after saving

---

### F-TRACK-02 — Application Status Tracker

**Priority:** P1 · **Phase:** 2 · **Persona:** Priya, Aarav

#### Purpose
Let users track the lifecycle of each job application from saved through offer or rejection.

#### Status States
```
saved → applied → interviewing → offer
                              → rejected
```

#### UI: My Jobs Page (`/my-jobs`)
```
Tabs: All | Saved | Applied | Interviewing | Offer | Rejected

Each row:
  Company logo | Job title | Company | Location | Status badge
  Saved on: date | Status updated: date
  [Open Job] [Update Status ▼] [Add Notes]
  
Update Status dropdown:
  → Applied
  → Interviewing
  → Offer Received
  → Rejected
  → Remove
```

#### API
```
PATCH /api/saved-jobs/{job_id}
  Body: { status, notes }
  Returns: 200 { updated: true }

GET /api/saved-jobs/stats
  Returns: {
    saved: 12, applied: 8, interviewing: 2,
    offer: 1, rejected: 5
  }
```

#### Acceptance Criteria
- [ ] Status can be updated from any state to any other state
- [ ] Status update reflected immediately in UI
- [ ] Notes field allows free text (max 500 chars)
- [ ] Stats summary visible at top of My Jobs page
- [ ] Status history not tracked in MVP (just current status)

---

### F-TRACK-03 — Closing Soon Reminder

**Priority:** P2 · **Phase:** 2 · **Persona:** Aarav, Priya

#### Purpose
Notify users when a saved job's application deadline is approaching, so they don't miss it.

#### Workflow
```
1. Daily scheduler at 9 AM scans user_saved_jobs
2. Find all saved jobs where:
   - job.deadline IS NOT NULL
   - job.deadline <= now + 48 hours
   - user_saved_jobs.status IN ('saved') (not yet applied)
   - reminder not already sent (reminder_sent_at IS NULL)
3. Send Telegram/email reminder per user preferences
4. Set reminder_sent_at = now
```

#### Message
```
⏰ Closing Soon — Don't Miss This

{Job Title} at {Company}
Application closes in {N} hours

[Apply Now] [Mark Applied] [Remove from Saved]
```

#### Acceptance Criteria
- [ ] Reminder sent exactly once per saved job (no repeat reminders)
- [ ] Reminder only sent if job deadline is within 48 hours
- [ ] Reminder only sent for jobs with status = 'saved' (not if already applied)
- [ ] "Closing Soon" badge also shown on job cards in feed and My Jobs

---

## MODULE: ADMIN DASHBOARD

---

### F-ADMN-01 — Scraper Health Dashboard

**Priority:** P0 · **Phase:** 1 · **Persona:** Karan (Admin)

#### Purpose
Give the admin a real-time view of every company's scraper status. The single most important admin tool — it surfaces failures before users are affected.

#### UI Layout
```
Scraper Health

Summary row: ✅ 21 Healthy  ⚠️ 2 Warning  ❌ 1 Failed
Last updated: 2 minutes ago  [Refresh]

Table:
Company      | ATS        | Last Run        | Status  | Jobs (24h) | Errors | Actions
-------------|------------|-----------------|---------|------------|--------|--------
Razorpay     | Greenhouse | 12 min ago      | ✅ OK   | 3 new      | 0      | [Run Now]
Zomato       | Workday    | 2 hours ago     | ⚠️ Warn | 0 new      | 2      | [Run Now] [View Errors]
Freshworks   | Greenhouse | 9 hours ago     | ❌ FAIL | 0 new      | 3      | [Run Now] [View Errors]
```

**Warning** = last run > 1 hour ago OR last 2 runs failed  
**Failed** = last 3+ consecutive runs failed  

#### API
```
GET /api/admin/scraper-health
  Auth: Admin only
  Returns: [{
    company_id, company_name, ats_type,
    last_scraped_at, consecutive_failures,
    jobs_found_24h, jobs_new_24h,
    last_error_message, last_error_type,
    status: 'healthy' | 'warning' | 'failed'
  }]
```

#### Acceptance Criteria
- [ ] Table shows all active companies
- [ ] Status calculated correctly (healthy / warning / failed)
- [ ] last_error_message in plain English (not Python exception)
- [ ] "View Errors" shows last 10 scrape_runs for that company
- [ ] Auto-refreshes every 60 seconds
- [ ] Admin-only: non-admin access returns 403

---

### F-ADMN-02 — Company Management (Add / Deactivate)

**Priority:** P0 · **Phase:** 1 · **Persona:** Karan (Admin)

#### Purpose
Allow the admin to add new companies to the scrape list and deactivate companies that should no longer be scraped — without engineering involvement.

#### Add Company Workflow
```
1. Admin clicks "Add Company"
2. Form: company name, career page URL, ATS type (dropdown + "Auto-detect")
3. Submit → backend runs ATS auto-detector on provided URL
4. Result shown: "Detected: Greenhouse"
5. Admin confirms → company saved as active = true
6. First scrape queued within 5 minutes
```

#### Deactivate Workflow
```
1. Admin clicks "Deactivate" next to a company
2. Confirmation: "Stop scraping {company name}?"
3. Confirm → company.active = false
4. No more scrape runs for this company
5. Existing jobs remain visible in the feed
```

#### Database
```sql
companies (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  career_page_url VARCHAR NOT NULL UNIQUE,
  ats_type VARCHAR,
  active BOOLEAN DEFAULT true,
  scrape_frequency_minutes INTEGER DEFAULT 15,
  last_scraped_at TIMESTAMP,
  added_by_admin_id UUID REFERENCES users(id),
  created_at TIMESTAMP,
  deactivated_at TIMESTAMP
)
```

#### Acceptance Criteria
- [ ] Add Company form validates URL format
- [ ] ATS auto-detection runs within 15 seconds of URL submission
- [ ] Deactivated companies immediately stop being scraped
- [ ] Existing jobs from deactivated companies remain visible
- [ ] Adding a duplicate URL returns 409 with company name

---

### F-ADMN-03 — Low-Confidence Job Review Queue

**Priority:** P1 · **Phase:** 1 · **Persona:** Karan (Admin)

#### Purpose
Surface jobs where AI extraction produced uncertain results so the admin can approve or reject before they reach students.

#### Queue Entry Conditions
A job enters the review queue when:
- `extraction_confidence < 0.75` (AI unsure about extracted fields)
- `title IS NULL` or `apply_url IS NULL` (critical fields missing)
- Admin manually flags a job reported by a user

#### UI
```
Review Queue — 8 pending

Job #1 of 8                              [← Prev] [Next →]

Company: Razorpay (Greenhouse)
Raw title from scraper:  "SDE II - Backend (Payments Team) [Req#12345]"
Extracted title:         "Software Engineer — Backend"
Confidence:              0.68

Raw apply_url:   "https://boards.greenhouse.io/..."  ✅ Looks correct
Extracted location: "Bengaluru" — but JD says "Remote / Bengaluru"  ⚠️

AI Summary:
• [bullet 1]
• [bullet 2]  ← "Competitive compensation" — vague
...

Required Skills: Python, FastAPI, PostgreSQL  ✅ Looks accurate

[✅ Approve]  [✏️ Edit & Approve]  [❌ Reject]
```

#### API
```
GET /api/admin/review-queue?page=0&limit=10
  Returns: flagged jobs with raw extraction data + AI output side by side

POST /api/admin/review-queue/{job_id}/approve
  Body: { edited_fields? }  ← optional corrections
  Effect: sets extraction_confidence = 1.0, is_active = true

POST /api/admin/review-queue/{job_id}/reject
  Effect: sets is_active = false, removed from feed and notifications
```

#### Acceptance Criteria
- [ ] Queue shows raw scraper output alongside AI extraction for comparison
- [ ] Admin can approve without editing (accept AI output as-is)
- [ ] Admin can edit individual fields before approving
- [ ] Rejected jobs never reach students
- [ ] Queue clears correctly after approve/reject (no zombie items)
- [ ] Badge count on admin nav shows pending queue size

---

### F-ADMN-04 — User Management

**Priority:** P1 · **Phase:** 1 · **Persona:** Karan (Admin)

#### Purpose
Allow admin to view registered users, monitor activity, and suspend or delete accounts for abuse.

#### User Table
```
Users — 347 registered

Search: [__________________]  Filter: All | Active | Suspended | Unverified

Name          | Email              | Joined    | Last Active | Telegram | Status
Aarav Shah    | aarav@...          | 3 days ago| 2h ago      | ✅       | Active
Priya Menon   | priya@...          | 1 week ago| 1 day ago   | ❌       | Active
Unknown User  | spam@...           | Today     | Today       | ❌       | Unverified

[View] [Suspend] [Delete]
```

#### Actions
- **View**: full profile, notification history, saved jobs count
- **Suspend**: account is_active = false; user gets 403 on login with "Account suspended" message
- **Delete**: triggers soft-delete flow (same as F-AUTH-05)

#### Acceptance Criteria
- [ ] User list paginated (50/page)
- [ ] Search by name or email
- [ ] Suspend takes effect immediately (active session revoked)
- [ ] Delete follows the same soft-delete + 30-day grace period as F-AUTH-05
- [ ] Admin cannot accidentally delete their own account from this view

---

### F-ADMN-05 — Admin Telegram Failure Alerts

**Priority:** P1 · **Phase:** 1 · **Persona:** Karan (Admin)

#### Purpose
Proactively notify the admin when a scraper fails repeatedly — without requiring them to check the dashboard manually.

#### Alert Trigger Logic
```python
def check_and_alert(company_id: int):
    recent_runs = get_last_n_runs(company_id, n=3)
    all_failed = all(r.status == 'failed' for r in recent_runs)
    if all_failed and not alert_already_sent_today(company_id):
        send_admin_telegram_alert(company_id, recent_runs[-1])
        log_alert_sent(company_id)
```

#### Alert Message Format
```
⚠️ SCRAPER FAILURE ALERT

Company: Freshworks
ATS Type: Greenhouse
Consecutive failures: 3
Last error: "Job listing container not found — page layout may have changed"
Last successful run: 9 hours ago
Jobs missed (estimated): 12

[View in Dashboard →]
```

#### Alert Conditions
- Triggered after exactly 3 consecutive failed runs
- Only 1 alert per company per 24 hours (no alert spam)
- Sent to admin Telegram channel (configurable in env: `ADMIN_TELEGRAM_CHAT_ID`)

#### Acceptance Criteria
- [ ] Alert fires after 3rd consecutive failure (not 2nd, not 4th)
- [ ] Maximum 1 alert per company per 24 hours
- [ ] Alert message includes company name, ATS type, last error (human-readable), and dashboard link
- [ ] Alert configurable via ADMIN_TELEGRAM_CHAT_ID env variable
- [ ] Alert channel is separate from the student-facing bot

---

*This document defines every feature as a contract. If a feature is built differently from what is described here, this document must be updated before the change is merged. Features not in this document do not exist.*
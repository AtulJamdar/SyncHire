# 17 — Tasks

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Engineering Lead  

---

## Purpose of This Document

This is the living task board for Job Finder AI. Every piece of work that needs to happen — infrastructure, backend, frontend, scraping, AI agents, notifications, testing, deployment — is tracked here, organized by phase and domain.

Tasks are not vague reminders. Each task is specific enough that any engineer can pick it up without asking for clarification. When a task is complete, mark it `[x]`. When a task is in progress, mark it `[-]`. When a task is blocked, mark it `[~]` and add a note.

**Before starting any task:** Read the relevant doc from the documentation suite. The docs are the spec — tasks are just the checklist.

---

## Status Key

```
[ ]  Not started
[-]  In progress
[x]  Complete
[~]  Blocked — note below the task
```

---

## Task Index

| Phase | Domain | Description |
|---|---|---|
| [Phase 1](#phase-1--foundation) | Infrastructure | Docker, env, DB, Redis, CI skeleton |
| [Phase 1](#phase-1--foundation) | Authentication | Registration, OAuth, JWT, sessions |
| [Phase 1](#phase-1--foundation) | Database | Migrations, seeds, all tables |
| [Phase 1](#phase-1--foundation) | Core API | FastAPI app, middleware, health |
| [Phase 1](#phase-1--foundation) | Scraper Pipeline | ATS detector, 5 adapters, scheduler, logging |
| [Phase 1](#phase-1--foundation) | AI Agent Pipeline | All 5 agents, BaseAgent, caching |
| [Phase 1](#phase-1--foundation) | Notification System | Matching, Telegram bot, email client, digest |
| [Phase 1](#phase-1--foundation) | Admin Dashboard | Scraper health, company mgmt, review queue |
| [Phase 1](#phase-1--foundation) | Frontend — Auth | Login, register, verify pages |
| [Phase 1](#phase-1--foundation) | Frontend — Onboarding | 4-step onboarding flow |
| [Phase 1](#phase-1--foundation) | Frontend — Jobs Feed | Feed, filters, job detail |
| [Phase 1](#phase-1--foundation) | Deployment | Docker Compose, CI/CD, staging |
| [Phase 2](#phase-2--product-quality) | Application Tracking | Save job, status tracker, reminders |
| [Phase 2](#phase-2--product-quality) | Resume Intelligence | Upload, extraction, skill mapping |
| [Phase 2](#phase-2--product-quality) | Notification Enhancements | Weekly digest, deadline reminders |
| [Phase 2](#phase-2--product-quality) | More ATS Adapters | SmartRecruiters, BreezyHR, Ashby |
| [Phase 2](#phase-2--product-quality) | Admin Enhancements | Manual scrape trigger, user mgmt |
| [Phase 2](#phase-2--product-quality) | Frontend — My Jobs | Pipeline tracker page |
| [Phase 2](#phase-2--product-quality) | Frontend — Settings | Full settings page |
| [Phase 2](#phase-2--product-quality) | Testing — Full Suite | Unit, integration, E2E |
| [Phase 3](#phase-3--scale--revenue) | Match Score | Score algorithm, UI overlay |
| [Phase 3](#phase-3--scale--revenue) | Recruiter Portal | Accounts, posting, billing |
| [Phase 3](#phase-3--scale--revenue) | College Integration | Placement officer dashboard |

---

# Phase 1 — Foundation

**Goal:** A student can register, set their profile, and receive a Telegram notification within 30 minutes of a job being posted on a company career page.  
**Target timeline:** Weeks 1–8

---

## Infrastructure

### Docker & Local Dev

- [✔️] Create `docker-compose.yml` with services: postgres, redis, backend, scheduler, frontend
  - **Backend:** `uvicorn main:app --reload`
  - **Frontend:** `npm run dev`
  - **Both:** volume-mounted source for hot reload
  - **Ref:** `14_DEPLOYMENT.md` Section 3.2

- [✔️] Write `backend/Dockerfile` (slim Python 3.12, Playwright deps, Gunicorn CMD)
  - **Ref:** `14_DEPLOYMENT.md` Section 3.3

- [✔️] Write `frontend/Dockerfile` (multi-stage: dev / builder / production)
  - **Ref:** `14_DEPLOYMENT.md` Section 3.4

- [✔️] Write `.dockerignore` for both backend and frontend
  - **Ref:** `14_DEPLOYMENT.md` Section 3.5

- [✔️] Write `.env.example` with all required variables and generation instructions
  - **Ref:** `14_DEPLOYMENT.md` Section 4.2

- [✔️] Verify `docker compose up` starts all 5 services cleanly on a fresh clone
  - Frontend accessible at `http://localhost:3000`
  - Backend accessible at `http://localhost:8000`
  - FastAPI docs at `http://localhost:8000/docs`

### Backend Foundation

- [✔️] Create FastAPI app in `backend/main.py`
  - Register all routers
  - Register all middleware (CORS, security headers, rate limit, trace ID)
  - Register startup event (`wait_for_db`)
  - **Ref:** `05_ARCHITECTURE.md` Section 2, `13_SECURITY.md` Section 6.3

- [✔️] Create `backend/config.py` using Pydantic `BaseSettings`
  - Load all env variables
  - Validate required vars on startup (fail fast if missing)

- [✔️] Create `backend/core/database.py`
  - SQLAlchemy async engine
  - Session factory
  - `wait_for_db()` with retry loop
  - **Ref:** `14_DEPLOYMENT.md` Section 7

- [✔️] Create `backend/core/redis_client.py`
  - Async Redis connection pool
  - Health check function

- [✔️] Create `backend/core/logging.py`
  - JSON formatter
  - Trace ID context var
  - Sensitive field redaction filter
  - **Ref:** `14_DEPLOYMENT.md` Section 9, `13_SECURITY.md` Section 11.4

- [✔️] Create `/health` endpoint
  - Checks DB connectivity + Redis connectivity
  - Returns `200 ok` or `503 degraded` with JSON body
  - **Ref:** `14_DEPLOYMENT.md` Section 8.1

### Frontend Foundation

- [✔️] Initialize Next.js app with App Router, TypeScript, Tailwind
  - `npx create-next-app@latest --typescript --tailwind --app`

- [✔️] Install and configure shadcn/ui
  - Copy in all required primitive components: Button, Badge, Card, Dialog, Input, Select, Tabs, Skeleton, Sheet, Toast, Label, DropdownMenu
  - **Ref:** `12_FRONTEND.md` Section 2

- [✔️] Set up CSS design tokens in `globals.css`
  - All color variables for light + dark mode
  - **Ref:** `12_FRONTEND.md` Section 9

- [✔️] Create `frontend/types/index.ts` with all TypeScript types
  - **Ref:** `12_FRONTEND.md` Section 14

- [✔️] Create `frontend/lib/api.ts`
  - Axios instance with base URL
  - Request interceptor (attach access token)
  - Response interceptor (401 → refresh → retry)
  - All domain-grouped API functions
  - **Ref:** `12_FRONTEND.md` Section 7

- [✔️] Create `frontend/lib/utils.ts`
  - `cn()` (clsx + tailwind-merge)
  - `formatPostedAt()` (relative time from ISO string)
  - `formatDate()` (readable date)

- [✔️] Configure `middleware.ts` for route protection
  - Public paths: login, register, verify-email, unsubscribe
  - All others require `refresh_token` cookie presence
  - Admin paths: additional role check in page-level server component
  - **Ref:** `12_FRONTEND.md` Section 8

---

## Authentication

### Backend

- [✔️] Create `users` table migration (Alembic)
  - All columns from `07_DATABASE.md` Section 2
  - All indexes

- [✔️] Create `refresh_tokens` table migration
  - **Ref:** `07_DATABASE.md` Section 3

- [✔️] Create `email_verification_tokens` table migration
  - **Ref:** `07_DATABASE.md` Section 4

- [✔️] Create `password_reset_tokens` table migration
  - **Ref:** `07_DATABASE.md` Section 5

- [✔️] Create `audit_logs` table migration
  - **Ref:** `07_DATABASE.md` (referenced from `13_SECURITY.md` Section 14.2)

- [✔️] Implement `backend/core/security.py`
  - `hash_password()` — bcrypt, cost 12
  - `verify_password()` — timing-safe
  - `create_access_token()` — HS256, 15-min TTL, `type: "access"` claim
  - `decode_access_token()` — raises on expired or invalid
  - `create_refresh_token()` — 64-byte random, returns (raw, hash)
  - `set_refresh_cookie()` — httpOnly, Secure, SameSite=Strict, `/api/auth` path
  - **Ref:** `13_SECURITY.md` Sections 2, 4

- [✔️] Implement `backend/middleware/auth_middleware.py`
  - `get_current_user()` FastAPI dependency
  - `require_admin()` FastAPI dependency
  - **Ref:** `13_SECURITY.md` Section 3.2

- [✔️] Implement `POST /api/auth/register`
  - Validate name, email, password (strength + common password check)
  - Check for existing email → 409
  - Hash password, create user (is_verified=false)
  - Generate verification token, send email
  - **Ref:** `08_API.md`, `13_SECURITY.md` Section 2.2

- [✔️] Implement `GET /api/auth/verify-email?token={uuid}`
  - Validate token (exists, not expired, not used)
  - Set `is_verified=true`, delete token
  - Return 200 or 410 (expired)
  - **Ref:** `08_API.md`

- [✔️] Implement `POST /api/auth/resend-verification`
  - Rate limit: 3 req/hour/email
  - Same 200 response whether email exists or not
  - **Ref:** `08_API.md`

- [✔️] Implement `GET /api/auth/oauth/google` + `GET /api/auth/oauth/google/callback`
  - State parameter for CSRF
  - Create or link account on callback
  - **Ref:** `08_API.md`, `13_SECURITY.md` Section 2.3

- [✔️] Implement `POST /api/auth/login`
  - Rate limit: 5 req/min/IP
  - Login lockout after 10 consecutive failures (per email, 15-min lock)
  - Issue access token + set refresh cookie
  - **Ref:** `08_API.md`, `13_SECURITY.md` Section 8.3

- [✔️] Implement `POST /api/auth/refresh`
  - Read cookie, validate hash, rotate token, return new access token
  - Reuse detection → revoke all sessions
  - **Ref:** `08_API.md`, `13_SECURITY.md` Section 4.3

- [✔️] Implement `POST /api/auth/logout`
  - Delete refresh token from DB, clear cookie
  - **Ref:** `08_API.md`

- [✔️] Implement `POST /api/auth/forgot-password`
  - Rate limit: 3 req/hour/email
  - Always return 200 (no email enumeration)
  - **Ref:** `08_API.md`

- [✔️] Implement `POST /api/auth/reset-password`
  - Validate token, update hash, revoke all refresh tokens
  - **Ref:** `08_API.md`

- [✔️] Implement `DELETE /api/auth/account`
  - Confirm email matches
  - Soft-delete + revoke all sessions + send confirmation email
  - **Ref:** `08_API.md`, `03_FEATURES.md` F-AUTH-05

- [✔️] Write audit log calls for all auth events
  - user.registered, user.verified, user.login, user.login_failed, user.logout, user.password_reset_*, user.deletion_initiated
  - **Ref:** `13_SECURITY.md` Section 14.1

### Frontend — Auth Pages

- [ ] Build `/login` page
  - Email + password form with inline validation
  - "Continue with Google" button
  - Links to `/register` and `/forgot-password`
  - On success: redirect to `/jobs` (or `?redirect=` param destination)
  - **Ref:** `12_FRONTEND.md` Section 3.1

- [ ] Build `/register` page
  - Name, email, password, confirm password
  - Password strength indicator
  - On success: "Check your email" confirmation screen
  - **Ref:** `12_FRONTEND.md` Section 3.2

- [ ] Build `/verify-email` page
  - Reads `?token=` from URL
  - Calls `GET /api/auth/verify-email`
  - Success state → redirect to `/onboarding/1`
  - Expired state → resend option

- [ ] Build `/forgot-password` and `/reset-password` pages

### Testing — Auth

- [ ] Unit test: `hash_password` / `verify_password` (bcrypt round-trip)
- [ ] Unit test: `create_access_token` / `decode_access_token` (expiry, tamper)
- [ ] Unit test: `create_refresh_token` (entropy, hash stored correctly)
- [ ] Integration test: full registration → verification → login flow
- [ ] Integration test: duplicate email returns 409
- [ ] Integration test: login with wrong password returns 401 (generic message)
- [ ] Integration test: login lockout fires at 11th attempt
- [ ] Integration test: refresh token rotation (old token rejected after use)
- [ ] Integration test: admin endpoint returns 403 for student role

---

## Database

- [ ] Create all remaining table migrations in order:
  - `skills` + seed data (from `database/seeds/skills.json`)
  - `role_types` + seed data
  - `cities` + seed data (major Indian cities + Remote)
  - `user_skills`
  - `user_preferences`
  - `user_preferred_roles`
  - `user_preferred_locations`
  - `notification_preferences`
  - `user_profiles`
  - `companies` + seed data (initial 50–100 company career pages)
  - `jobs`
  - `job_skills`
  - `scrape_runs`
  - `agent_logs`
  - `notification_logs`
  - `telegram_link_codes`
  - `user_saved_jobs`
  - `admin_alert_logs`
  - **Ref:** `07_DATABASE.md` Sections 6–23

- [ ] Write `database/seeds/skills.json` — canonical skill list
  - Categories: language, framework, database, cloud, tool, domain
  - Minimum 150 skills covering common tech stack

- [ ] Write `database/seeds/role_types.json`
  - All 16 role_type slugs from F-AGNT-05 taxonomy

- [ ] Write `database/seeds/cities.json`
  - 25+ major Indian cities + Remote row

- [ ] Write `database/seeds/companies.json`
  - 50–100 initial companies with career page URLs
  - Include well-known Indian tech companies + startups covering all 5 ATS types

- [ ] Write `scripts/seed_db.py`
  - Seeds all reference data in correct order
  - Idempotent — safe to run multiple times (`ON CONFLICT DO NOTHING`)

- [ ] Verify all indexes exist after migrations
  - Compare `07_DATABASE.md` index definitions against `\di` in psql

- [ ] Write `scripts/verify_schema.py`
  - Reads all table definitions from DB and compares against expected schema
  - Fails CI if schema drift is detected

---

## Core API

### Profile Endpoints

- [ ] Implement `GET /api/skills?q=`
  - Redis cache, 1-hour TTL
  - Case-insensitive search
  - **Ref:** `08_API.md`

- [ ] Implement `GET + PUT /api/profile/skills`
  - PUT replaces all (delete + insert, not append)
  - Validate all skill IDs exist
  - **Ref:** `08_API.md`

- [ ] Implement `GET /api/preferences/role-types`
  - Redis cache, 24-hour TTL
  - **Ref:** `08_API.md`

- [ ] Implement `GET /api/preferences/cities`
  - Redis cache, 24-hour TTL
  - **Ref:** `08_API.md`

- [ ] Implement `GET + PUT /api/profile/preferences`
  - Validate experience_level enum
  - Require at least 1 role type and 1 location (or open_to_remote=true)
  - **Ref:** `08_API.md`

- [ ] Implement `GET + PUT /api/profile/notification-preferences`
  - Validate quiet_hours time format, valid timezone string
  - **Ref:** `08_API.md`

### Jobs Endpoints

- [ ] Implement `GET /api/jobs`
  - Paginated (page + limit)
  - Filters: role_type, location, experience_level, is_remote, q (full-text)
  - Redis cache, 2-min TTL per filter fingerprint
  - Returns `summary_preview` (first 2 bullets) for authenticated users
  - **Ref:** `08_API.md`, `07_DATABASE.md` Section 16

- [ ] Implement `GET /api/jobs/{job_id}`
  - Full job detail including all 5 summary bullets
  - Skill match overlay for authenticated users
  - Redis cache, 5-min TTL per job_id
  - **Ref:** `08_API.md`

### Testing — Core API

- [ ] Integration test: `GET /api/jobs` returns paginated results with correct shape
- [ ] Integration test: filter by `role_type` returns only matching jobs
- [ ] Integration test: filter by `is_remote=true` returns only remote jobs
- [ ] Integration test: full-text search returns relevant results
- [ ] Integration test: `GET /api/jobs/{id}` for non-existent job returns 404
- [ ] Integration test: skill match overlay appears only for authenticated requests

---

## Scraper Pipeline

### Base Infrastructure

- [ ] Implement `scrapers/base_scraper.py`
  - Abstract `get_job_list()` + `get_job_detail()` interface
  - `fetch()` with rate limiting, retry, robots.txt check, CAPTCHA detection
  - User-agent rotation pool
  - **Ref:** `09_SCRAPER.md` Section 2

- [ ] Implement `scrapers/ats_detector.py`
  - Stage 1: URL pattern match (regex per ATS)
  - Stage 2: HTML signature match
  - Stage 3: API probe
  - Falls back to `"generic"` if all stages fail
  - **Ref:** `09_SCRAPER.md` Section 3

- [ ] Implement `scrapers/runner.py`
  - Batch selection query (least-recently-scraped first)
  - Per-company error handling (one failure doesn't stop the batch)
  - `consecutive_failures` increment + admin alert trigger
  - `scrape_runs` record written for every attempt
  - **Ref:** `09_SCRAPER.md` Section 13

### ATS Adapters

- [ ] Implement `scrapers/adapters/workday.py`
  - Tenant discovery from URL
  - POST-based JSON API pagination
  - Workday date format parser
  - **Ref:** `09_SCRAPER.md` Section 4

- [ ] Implement `scrapers/adapters/greenhouse.py`
  - Single-request department-grouped JSON response
  - Company slug extraction
  - **Ref:** `09_SCRAPER.md` Section 5

- [ ] Implement `scrapers/adapters/lever.py`
  - `Link` header cursor pagination
  - Unix millisecond timestamp conversion
  - **Ref:** `09_SCRAPER.md` Section 6

- [ ] Implement `scrapers/adapters/icims.py`
  - HTML parsing with BeautifulSoup
  - Page number pagination
  - Playwright fallback for JS-rendered pages
  - **Ref:** `09_SCRAPER.md` Section 7

- [ ] Implement `scrapers/adapters/taleo.py`
  - REST API with `careersection` discovery
  - `start` + `pageSize` pagination
  - **Ref:** `09_SCRAPER.md` Section 8

- [ ] Implement `scrapers/adapters/generic.py`
  - Heuristic CSS selector waterfall
  - Always uses Playwright
  - Auto-sets `extraction_confidence -= 0.15` and `needs_review=true`
  - **Ref:** `09_SCRAPER.md` Section 9

### Scheduler

- [ ] Implement `scheduler/main.py`
  - APScheduler instance
  - Register all jobs: `scrape_batch` (every 15 min), `daily_digest` (daily 8 AM IST), `deadline_reminder` (daily 9 AM IST)
  - `max_instances=1` per job to prevent overlapping runs
  - **Ref:** `05_ARCHITECTURE.md` Section 5, `14_DEPLOYMENT.md` Section 7

- [ ] Implement `scheduler/jobs/scrape_batch.py`
  - Calls `runner.run_scrape_batch()`
  - **Ref:** `04_USER_FLOWS.md` Flow 4

### Testing — Scrapers

- [ ] Unit test: ATS detector correctly identifies Workday from URL pattern
- [ ] Unit test: ATS detector correctly identifies Greenhouse from HTML signature
- [ ] Unit test: ATS detector returns "generic" for unknown HTML
- [ ] Unit test: rate limiter enforces 3-second delay between requests to same domain
- [ ] Unit test: retry logic fires on 429 and 503, not on 404
- [ ] Unit test: CAPTCHA detection returns True for Cloudflare challenge page
- [ ] Unit test: `compute_hash` normalization handles unicode, em-dashes, zero-width spaces
- [ ] Integration test: Greenhouse adapter fetches real jobs from 3 test companies
- [ ] Integration test: Workday adapter fetches real jobs from 3 test companies
- [ ] Integration test: duplicate job is correctly detected and skipped (jobs_duplicate++)
- [ ] Integration test: scrape_run record is written on both success and failure
- [ ] Integration test: `consecutive_failures` increments on failure and resets on success

---

## AI Agent Pipeline

- [ ] Implement `agents/base_agent.py`
  - `run()` method with: cache check → LLM call → parse → repair → cache + log
  - `REPAIR_SUFFIX` constant
  - Redis cache by SHA256 of prompt
  - `agent_logs` insert on every call (including cache hits)
  - **Ref:** `10_AI_AGENTS.md` Section 2

- [ ] Implement `agents/llm_client.py`
  - OpenAI primary + Anthropic fallback
  - `AGENT_MODELS` config dict (logical names → real model strings)
  - **Ref:** `10_AI_AGENTS.md` Section 11

- [ ] Implement `agents/duplicate_detector.py`
  - `normalize()` with unicode handling
  - `compute_hash()` — SHA256 of title|company|apply_url
  - Single indexed DB lookup
  - **Ref:** `10_AI_AGENTS.md` Section 3

- [ ] Implement `agents/job_extractor.py`
  - Prompt loaded from `20_PROMPTS.md` (`extractor_v1`)
  - Input truncation at 6,000 tokens
  - Merge rules (scraper fields take precedence)
  - `extraction_confidence < 0.75` → set `needs_review=true`, `is_active=false`
  - **Ref:** `10_AI_AGENTS.md` Section 4

- [ ] Implement `agents/skill_extractor.py`
  - Prompt: `skill_extractor_v1`
  - Post-LLM canonicalization against `skills` table
  - `SKILL_ALIASES` dict
  - `degree_required` + `degree_note` fields
  - Unmatched skills logged to `agent_logs.output_json`
  - **Ref:** `10_AI_AGENTS.md` Section 5

- [ ] Implement `agents/jd_summarizer.py`
  - Prompt: `summarizer_v1`
  - Exactly 5 bullets enforced in `parse_output()`
  - Max 30 words per bullet enforced
  - Repair suffix on parse failure
  - **Ref:** `10_AI_AGENTS.md` Section 6

- [ ] Implement `agents/job_classifier.py`
  - Prompt: `classifier_v1` (GPT-4o-mini)
  - Taxonomy validation in `parse_output()`
  - Graceful degradation to `"other"` / `"unknown"` on parse failure
  - **Ref:** `10_AI_AGENTS.md` Section 7

- [ ] Implement `agents/notification_generator.py`
  - Prompt: `notif_generator_v1` (GPT-4o-mini)
  - Skill match icons computed in application code (not LLM)
  - Static fallback template when agent fails
  - **Ref:** `10_AI_AGENTS.md` Section 8

- [ ] Write all prompt templates in `docs/20_PROMPTS.md`
  - `extractor_v1`
  - `skill_extractor_v1`
  - `summarizer_v1`
  - `classifier_v1`
  - `notif_generator_v1`
  - Each prompt: template text, variables list, output schema, example

- [ ] Implement `agents/pipeline_runner.py`
  - Orchestrates: Duplicate Detector → Extractor → Skill Extractor → Summarizer → Classifier → DB save → Matching Service
  - Each agent failure is handled without crashing the pipeline
  - **Ref:** `10_AI_AGENTS.md` Section 1

### Testing — AI Agents

- [ ] Unit test: `normalize()` correctly handles em-dash, zero-width space, non-breaking space
- [ ] Unit test: JD Summarizer `parse_output()` raises ParseError on 4 bullets
- [ ] Unit test: JD Summarizer `parse_output()` raises ParseError on bullet > 30 words
- [ ] Unit test: Job Classifier `parse_output()` raises ParseError on invalid `role_type`
- [ ] Unit test: cache hit returns cached result without calling LLM
- [ ] Unit test: repair suffix fires on first parse failure, not before
- [ ] Unit test: skill alias mapping (e.g., "JS" → "JavaScript")
- [ ] Integration test: full pipeline on 5 real job descriptions (assess output quality)
- [ ] Integration test: agent failure mid-pipeline does not crash subsequent agents
- [ ] Integration test: duplicate job is skipped correctly (content_hash exists)
- [ ] Integration test: `needs_review=true` set when `extraction_confidence < 0.75`

---

## Notification System

- [ ] Implement `notifications/matching_service.py`
  - Core matching SQL query (4-condition AND logic)
  - Experience level ±1 band comparison
  - Returns users with notification preferences included
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 4

- [ ] Implement `notifications/router.py`
  - `route_notification()` — channel selection, quiet hours gate
  - `should_telegram_notify()` — handles `exact_match` frequency mode
  - `enqueue_for_digest()` — pushes to Redis digest queue
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 3

- [ ] Implement `notifications/telegram/bot.py`
  - python-telegram-bot `Application` setup
  - All command handlers registered
  - Webhook setup function (`set_webhook`)
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 5

- [ ] Implement `notifications/telegram/dispatcher.py`
  - `send_job_alert()` with inline keyboard (Apply / Save / Not Interested)
  - Exception handling per Telegram error type (Forbidden, BadRequest, TimedOut)
  - `handle_bot_blocked()` — sets `telegram_enabled=false`
  - Batch send rate limiting (35ms delay between sends)
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 5

- [ ] Implement `notifications/telegram/templates.py`
  - `job_alert_message()` — full formatted message with all fields
  - `deadline_reminder_message()`
  - `CONNECTED_MESSAGE` constant
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 8.1–8.3

- [ ] Implement `notifications/telegram/commands.py`
  - `/start` — account linking via code + welcome message
  - `/pause` — sets `telegram_enabled=false`
  - `/resume` — sets `telegram_enabled=true`
  - `/settings` — shows current preferences in formatted message
  - `/unlink` — clears `telegram_id` from user record
  - `/help` — full command list
  - Inline button callback handler (Save / Dismiss / Applied)
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 14

- [ ] Implement Telegram link code flow
  - `POST /api/telegram/generate-link-code` — generates UUID code, stores in DB + Redis (10-min TTL)
  - `GET /api/profile/telegram-status` — returns `{ connected: bool }`
  - `DELETE /api/profile/telegram` — unlinks account
  - **Ref:** `08_API.md`, `03_FEATURES.md` F-NOTIF-01

- [ ] Implement `backend/api/webhooks/telegram.py`
  - Validate `X-Telegram-Bot-Api-Secret-Token` header
  - Dispatch update to bot application asynchronously
  - Return `{ ok: true }` within 1 second
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 15

- [ ] Implement `notifications/email/client.py`
  - Provider-agnostic wrapper (Resend initially)
  - `send()` with unsubscribe header (RFC 8058)
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 6

- [ ] Implement `scheduler/jobs/daily_digest.py`
  - Fetches queued job IDs from Redis per user
  - Skips users with 0 matches (no empty digest)
  - Renders email template, sends, logs
  - Clears Redis digest queue after send
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 9

- [ ] Implement `notifications/retry_worker.py`
  - Redis sorted-set retry queue
  - 3-attempt limit with 30s / 2m / 10m delays
  - Runs as background async task
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 10

- [ ] Implement quiet hours logic
  - `is_quiet_now()` — handles normal and overnight ranges
  - `queue_for_after_quiet_hours()` — Redis ZSET with release timestamp
  - `quiet_hours_release_worker()` — polls every 60 seconds
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Sections 12–13

### Testing — Notifications

- [ ] Unit test: `is_quiet_now()` correctly identifies quiet period for normal range (09:00–19:00)
- [ ] Unit test: `is_quiet_now()` correctly handles overnight range (23:00–07:00)
- [ ] Unit test: matching query returns correct users for a given job fixture
- [ ] Unit test: matching query excludes users with no matching role type
- [ ] Unit test: matching query excludes users with experience_level 2+ bands away
- [ ] Unit test: `UNIQUE(user_id, job_id, channel)` constraint prevents duplicate log insert
- [ ] Integration test: Telegram bot responds to `/start {code}` and links account
- [ ] Integration test: `/pause` sets `telegram_enabled=false`; notifications stop
- [ ] Integration test: notification queued (not dropped) when user is in quiet hours
- [ ] Integration test: retry queue re-dispatches after delay on Telegram timeout

---

## Admin Dashboard

### Backend

- [ ] Implement `GET /api/admin/scraper-health`
  - Company list with computed status (healthy/warning/failed)
  - Redis cache, 60-second TTL
  - **Ref:** `08_API.md`

- [ ] Implement `GET + POST /api/admin/companies`
  - POST triggers ATS auto-detection on provided URL
  - Returns detected ATS type in response
  - **Ref:** `08_API.md`

- [ ] Implement `PATCH /api/admin/companies/{id}`
  - Deactivate / reactivate company
  - **Ref:** `08_API.md`

- [ ] Implement `GET /api/admin/review-queue`
  - Jobs where `needs_review=true` and `is_active=false`
  - Returns raw scraper output alongside AI-extracted fields side by side
  - **Ref:** `08_API.md`

- [ ] Implement `POST /api/admin/review-queue/{job_id}/approve`
  - Optional `edited_fields` to correct extraction
  - Sets `is_active=true`, `extraction_confidence=1.0`, `needs_review=false`
  - **Ref:** `08_API.md`

- [ ] Implement `POST /api/admin/review-queue/{job_id}/reject`
  - Sets `is_active=false` permanently
  - **Ref:** `08_API.md`

- [ ] Implement admin failure alert system
  - `check_and_send_admin_alert()` — dedup via `admin_alert_logs` (1 per company per 24h)
  - All 3 alert templates: scraper_failure, agent_failure_spike, notification_delivery_low
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 16

### Frontend — Admin

- [ ] Build `/admin/scraper-health` page with `ScraperHealthTable`
  - Status badges (✅ / ⚠️ / ❌) with correct thresholds
  - Auto-refresh every 60 seconds
  - `ErrorDetailsButton` showing last error message
  - **Ref:** `12_FRONTEND.md` Section 4.8

- [ ] Build `/admin/companies` page with `CompanyForm` modal
  - Add company form with ATS type dropdown (+ Auto-detect option)
  - Shows detected ATS type in confirmation step
  - Company list table with active/inactive toggle

- [ ] Build `/admin/review-queue` page with `ReviewQueueCard`
  - Side-by-side: raw scraper fields vs. AI-extracted fields
  - Approve / Edit & Approve / Reject actions
  - Badge count in admin nav showing pending queue size

### Testing — Admin

- [ ] Integration test: non-admin access to `/api/admin/*` returns 403
- [ ] Integration test: adding a company runs ATS detection and returns detected type
- [ ] Integration test: approving a flagged job sets `is_active=true`
- [ ] Integration test: admin alert not sent twice within 24 hours for same company

---

## Frontend — Onboarding

- [ ] Build `(onboarding)/layout.tsx` with progress step indicator
  - **Ref:** `12_FRONTEND.md` Section 3.3

- [ ] Build onboarding Step 1 — Skills (`/onboarding/1`)
  - `SkillPicker` component — searchable combobox + chips
  - Minimum 1 skill required validation
  - **Ref:** `12_FRONTEND.md` Section 4.5

- [ ] Build onboarding Step 2 — Preferences (`/onboarding/2`)
  - `RolePicker` multi-select
  - `LocationPicker` with city search + Remote toggle
  - Experience level single-select

- [ ] Build onboarding Step 3 — Notifications (`/onboarding/3`)
  - `TelegramConnect` component with QR code + polling
  - Email digest toggle
  - "Skip for now" option
  - **Ref:** `12_FRONTEND.md` Section 4.6

- [ ] Build onboarding Step 4 — Complete (`/onboarding/4`)
  - Summary of what was configured
  - "Go to Jobs Feed" CTA

- [ ] Implement `useTelegramStatus` hook (polls every 3 seconds when enabled)
  - **Ref:** `12_FRONTEND.md` Section 5.5

---

## Frontend — Jobs Feed

- [ ] Build `/jobs` page shell (Server Component)
  - SSR metadata
  - `FilterBar` + `Suspense`-wrapped `JobFeed`
  - **Ref:** `12_FRONTEND.md` Section 3.4

- [ ] Build `FilterBar` component (Client Component)
  - Filters synced to URL query params via `router.replace`
  - Debounced 300ms on input changes
  - "Clear all" resets to `/jobs`
  - **Ref:** `12_FRONTEND.md` Section 4.3

- [ ] Build `JobFeed` component (Client Component)
  - Infinite scroll using `react-intersection-observer`
  - `useJobs` hook with `useInfiniteQuery`
  - `FeedSkeleton` loading state (matches final layout)
  - `EmptyFeed` zero-results state
  - **Ref:** `12_FRONTEND.md` Sections 4.2, 5.1

- [ ] Build `JobCard` component
  - All fields: logo, title, company, location, posted label, badges, skill chips, apply button
  - `PostedLabel` with green text for jobs < 1 hour old
  - **Ref:** `12_FRONTEND.md` Sections 4.1, 4.7

- [ ] Build `/jobs/[id]` page (Server Component with `generateMetadata`)
  - JSON-LD `JobPosting` structured data
  - `JobDetail` component: full summary, skill match overlay, apply CTA
  - Full JD collapsible section
  - **Ref:** `12_FRONTEND.md` Section 3.5

- [ ] Build `SkillMatchChips` component
  - Green for matched, grey for unmatched
  - Max 4 visible + "+N more" badge
  - **Ref:** `12_FRONTEND.md` Section 4.4

- [ ] Implement `useJobs` hook
  - `useInfiniteQuery` with 2-min stale time
  - **Ref:** `12_FRONTEND.md` Section 5.1

### Testing — Frontend

- [ ] Component test: `JobCard` renders correct posted label for job < 1 hour old
- [ ] Component test: `SkillMatchChips` shows green for matched skills, grey for others
- [ ] Component test: `FilterBar` updates URL params on filter change
- [ ] Component test: `FeedSkeleton` renders with correct number of placeholder cards
- [ ] E2E test: `/jobs` page loads and shows job cards
- [ ] E2E test: applying role_type filter updates results
- [ ] E2E test: clearing filters restores full feed

---

## Deployment — Phase 1

- [ ] Configure GitHub repository
  - Branch protection on `main` (require PR + CI pass before merge)
  - GitHub Environments: `staging` (auto) and `production` (manual approval)

- [ ] Write `.github/workflows/deploy.yml`
  - Jobs: lint → test → build → deploy-staging → deploy-production
  - PostgreSQL + Redis service containers in test job
  - Docker image build + push to GitHub Container Registry
  - **Ref:** `14_DEPLOYMENT.md` Section 5

- [ ] Configure Railway project
  - Services: `backend`, `scheduler`
  - Environment variables set for staging and production
  - Health check path: `/health`
  - Scheduler: `max_instances=1`, single deployment

- [ ] Configure Vercel project
  - Connect to GitHub repo
  - Set `NEXT_PUBLIC_API_URL` environment variable
  - Preview deployments on every PR

- [ ] Configure Cloudflare
  - DNS for `jobfinderai.com` → Vercel
  - DNS for `api.jobfinderai.com` → Railway
  - Proxy enabled (DDoS protection + TLS termination)

- [ ] Set up Upstash Redis for staging and production

- [ ] Set up Supabase or Railway managed PostgreSQL for staging and production

- [ ] Configure UptimeRobot monitors
  - `https://api.jobfinderai.com/health` — 1-min check
  - `https://jobfinderai.com` — 1-min check
  - TLS expiry alert — 14 days

- [ ] First production deployment
  - Run DB migrations
  - Seed reference data
  - Register Telegram webhook
  - Verify scraper runs at least one successful batch
  - Verify Telegram bot responds to `/start`

---

# Phase 2 — Product Quality

**Goal:** Add the features that turn early adopters into retained users — application tracking, email digest, resume upload, deadline reminders, and expanded ATS coverage.  
**Target timeline:** Weeks 9–16

---

## Application Tracking

### Backend

- [ ] Implement `POST /api/saved-jobs` — save a job
- [ ] Implement `DELETE /api/saved-jobs/{job_id}` — unsave
- [ ] Implement `GET /api/saved-jobs` — list with status filter, paginated
- [ ] Implement `PATCH /api/saved-jobs/{job_id}` — update status + notes
- [ ] Implement `GET /api/saved-jobs/stats` — counts per status
- [ ] **Ref:** `08_API.md`, `03_FEATURES.md` F-TRACK-01/02

- [ ] Implement Telegram inline button callback for "Save 📌"
  - Calls `POST /api/saved-jobs` on behalf of the user
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 15

### Frontend

- [ ] Build `/my-jobs` page
  - `StatsBar` — counts per status
  - Tabs: All / Saved / Applied / Interviewing / Offer / Rejected
  - `SavedJobRow` — status badge, deadline badge ("Closing Soon" if ≤ 48h)
  - `useUpdateJobStatus` mutation with toast feedback
  - **Ref:** `12_FRONTEND.md` Section 3.6

- [ ] Add `SaveButton` to `JobCard` and `JobDetail`
  - Toggles saved state optimistically
  - Shows "Saved ✓" when in saved list

### Testing

- [ ] Integration test: save → list → update status → stats reflect change
- [ ] Integration test: duplicate save returns 409
- [ ] Integration test: unsave removes from list

---

## Resume Intelligence

### Backend

- [ ] Implement `POST /api/profile/resume` — receive storage path, trigger extraction
- [ ] Implement `GET /api/profile/resume/status` — poll extraction status
- [ ] Implement `agents/resume_skill_extractor.py`
  - `pdfplumber` PDF text extraction
  - Image-only PDF detection
  - Prompt: `resume_extractor_v1`
  - Canonical skill mapping
  - **Ref:** `10_AI_AGENTS.md` Section 9

### Frontend

- [ ] Build resume upload UI in `/settings` → Resume tab
  - Client-side PDF validation (type + 5MB size)
  - Upload via signed URL to R2
  - Polling for extraction status
  - Review screen — confirm or edit extracted skills

### Testing

- [ ] Unit test: image-only PDF raises `ResumeExtractionError`
- [ ] Integration test: upload → extract → extracted skills appear in review screen

---

## Notification Enhancements

- [ ] Implement weekly email digest
  - `scheduler/jobs/weekly_summary.py` — runs Monday 8 AM
  - Top 10 matches from the past 7 days per user
  - **Ref:** `11_NOTIFICATION_SYSTEM.md`, `03_FEATURES.md` F-NOTIF-03

- [ ] Implement deadline reminder notifications
  - `scheduler/jobs/deadline_reminder.py`
  - Sends 48h before deadline to saved (not-yet-applied) jobs
  - Sets `reminder_sent_at` to prevent duplicates
  - **Ref:** `11_NOTIFICATION_SYSTEM.md` Section 9

- [ ] Add "Closing Soon" badge to job cards
  - Displayed when `deadline - now <= 48 hours`
  - **Ref:** `03_FEATURES.md` F-JOBS-10

### Testing

- [ ] Integration test: deadline reminder sent exactly once per saved job
- [ ] Integration test: reminder not sent if job already marked applied

---

## More ATS Adapters

- [ ] Implement `scrapers/adapters/smartrecruiters.py`
  - **Ref:** `09_SCRAPER.md` Section 10

- [ ] Implement `scrapers/adapters/breezyhr.py`
  - **Ref:** `09_SCRAPER.md` Section 11

- [ ] Implement `scrapers/adapters/ashby.py`
  - GraphQL query implementation
  - **Ref:** `09_SCRAPER.md` Section 12

- [ ] Add detection signatures for all 3 new adapters to `ats_detector.py`

- [ ] Test each new adapter against 3 real companies each

---

## Admin Enhancements

- [ ] Implement `POST /api/admin/companies/{id}/run-now` — manual scrape trigger
- [ ] Implement `GET + POST /api/admin/users` — list and search users
- [ ] Implement `GET /api/admin/users/{id}` — user detail
- [ ] Implement `POST /api/admin/users/{id}/suspend` — revoke sessions
- [ ] Implement `POST /api/admin/users/{id}/reactivate`
- [ ] Build `/admin/users` page with `UserTable` and search
- [ ] **Ref:** `08_API.md`, `12_FRONTEND.md` Section 3.8

---

## Frontend — Settings

- [ ] Build full `/settings` page with 4 tabs
  - Profile: skills + role/location/experience preferences
  - Notifications: channel toggles, frequency, quiet hours
  - Resume: upload widget (Phase 2)
  - Account: change password + DangerZone (delete account)
  - **Ref:** `12_FRONTEND.md` Section 3.7

---

## Testing — Full Suite

- [ ] Set up Playwright E2E test runner
  - Install + configure `playwright.config.ts`
  - CI job running E2E against staging environment

- [ ] E2E: Full registration → onboarding → first notification received flow
- [ ] E2E: Browse jobs → apply filter → clear filter → all results return
- [ ] E2E: Save a job → navigate to My Jobs → update status to Applied
- [ ] E2E: Admin adds company → appears in scraper health table
- [ ] E2E: Admin reviews and approves a flagged job → job appears in feed

- [ ] Achieve ≥ 70% backend test coverage (enforced in CI via `--cov-fail-under=70`)
- [ ] Achieve ≥ 70% frontend component test coverage

---

# Phase 3 — Scale & Revenue

**Goal:** Match score display, recruiter portal, college integrations.  
**Target timeline:** Months 6–12  
**Note:** These tasks are not yet broken into subtasks. They will be detailed when Phase 2 is complete.

---

## Match Score

- [ ] Implement `agents/match_score_calculator.py` — deterministic algorithm
  - Required skills 80%, preferred 10%, experience band 10%
  - **Ref:** `10_AI_AGENTS.md` Section 10

- [ ] Expose match score on job list and detail API responses
- [ ] Display match score on job cards and in Telegram notifications
- [ ] A/B test: does match score display increase or decrease application rate?

---

## Recruiter Portal

- [ ] Design recruiter account data model (`companies_posted`, `recruiter_users`)
- [ ] Implement recruiter registration + company verification flow
- [ ] Build recruiter job posting form (bypasses scraper pipeline — direct DB insert)
- [ ] Build recruiter analytics dashboard (anonymized match + application stats)
- [ ] Integrate Stripe for subscription billing
- [ ] Implement `recruiter` RBAC role with scoped endpoints

---

## College Integration

- [ ] Design college data model (`colleges`, `college_batches`, `placement_officers`)
- [ ] Build placement officer dashboard
  - View job matches for their batch
  - Bulk notification to cohort
- [ ] Implement college email domain verification
- [ ] Build college analytics (top matched companies, skill gap analysis for batch)

---

*This document is the single source of truth for what work is pending, in progress, and complete. Update task status every time work changes state. If a task is completed without being checked off here, that is the same as it not being done from the team's perspective.*
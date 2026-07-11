# 19 — File Explanations

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Engineering Lead  

---

## Purpose of This Document

This is the developer knowledge base for every folder and key file in Job Finder AI. New engineers, AI coding assistants, and returning contributors use this document to orient themselves quickly without reading source code.

Every entry answers five questions:
1. **Why it exists** — what problem this folder/file solves
2. **What it does** — what it contains or produces
3. **When it runs** — at what point in the system lifecycle it is active
4. **Who uses it** — which other parts of the system depend on it
5. **Common modifications** — what changes here most often, and what to do when making them

**Rule:** When a new file or folder is added to the project, an entry is added here in the same pull request. When a file's purpose changes, this document is updated before the code is merged.

---

## Table of Contents

1. [Root Directory](#1-root-directory)
2. [docs/](#2-docs)
3. [.openspec/](#3-openspec)
4. [backend/](#4-backend)
5. [backend/api/](#5-backendapi)
6. [backend/services/](#6-backendservices)
7. [backend/models/](#7-backendmodels)
8. [backend/schemas/](#8-backendschemas)
9. [backend/middleware/](#9-backendmiddleware)
10. [backend/core/](#10-backendcore)
11. [scrapers/](#11-scrapers)
12. [scrapers/adapters/](#12-scrapersadapters)
13. [agents/](#13-agents)
14. [notifications/](#14-notifications)
15. [notifications/telegram/](#15-notificationstelegram)
16. [notifications/email/](#16-notificationsemail)
17. [scheduler/](#17-scheduler)
18. [database/](#18-database)
19. [frontend/](#19-frontend)
20. [frontend/app/](#20-frontendapp)
21. [frontend/components/](#21-frontendcomponents)
22. [frontend/hooks/](#22-frontendhooks)
23. [frontend/lib/](#23-frontendlib)
24. [tests/](#24-tests)
25. [scripts/](#25-scripts)

---

## 1. Root Directory

### `/`

| File / Folder | Purpose |
|---|---|
| `README.md` | First file anyone reads. Quick start guide, what the project does, how to run it locally in 5 commands. Not a duplicate of the docs — links to them instead. |
| `LICENSE` | Open source license (if applicable). Legal requirement for public repos. |
| `.gitignore` | Prevents committing `.env`, `__pycache__`, `.next`, `node_modules`, `*.pyc`, build artifacts. Must be reviewed whenever a new language, framework, or build tool is added. |
| `.env.example` | **Canonical list of all environment variables.** Every variable used anywhere in the codebase must appear here with a placeholder value and a comment explaining what it is. No variable should exist in code that isn't in this file. Updated in the same commit that adds a new env variable. |
| `docker-compose.yml` | Local development environment. Defines 5 services (postgres, redis, backend, scheduler, frontend) with health checks and volume mounts for hot reload. **This is the only way to start the full local stack.** |
| `docker-compose.prod.yml` | Production overrides (different CMD, no volume mounts, production env flags). Used by CI/CD pipeline via `docker compose -f docker-compose.yml -f docker-compose.prod.yml`. |
| `.pre-commit-config.yaml` | Pre-commit hooks: `detect-secrets` baseline check prevents accidental credential commits. Run `pre-commit install` after cloning. |

**When modifying the root:**
- Adding a new service to the stack → add to `docker-compose.yml` + document in `14_DEPLOYMENT.md`
- Adding a new environment variable → add to `.env.example` + document in `14_DEPLOYMENT.md` Section 4.2
- Changing the project name or structure → update `README.md`

---

## 2. docs/

### `docs/`

**Why it exists:** Documentation is the single source of truth for this project. All architecture decisions, feature specifications, API contracts, database schemas, and operational procedures live here — not scattered across Notion, Confluence, or tribal knowledge.

**What it contains:** 22+ Markdown documents organized by concern, numbered for reading order. The numbering conveys priority: 00–04 define the product, 05–08 define the technical architecture, 09–14 define the subsystems, 15–22 define project operations.

**Who uses it:** Everyone. Engineers read it before writing code. AI coding assistants read it before making suggestions. Admins read operational docs during incidents. Product reads it to understand what's been built vs. what's planned.

**Rule:** If it's not in docs, it doesn't exist. If it exists in code but not in docs, the docs are wrong and must be updated.

### Key files in `docs/`

| File | Read When |
|---|---|
| `00_PROJECT_OVERVIEW.md` | You're new to the project and need the 5-minute orientation |
| `01_PRD.md` | You need to understand what the product must do and why |
| `02_USER_PERSONAS.md` | You're making a UX or feature priority decision |
| `03_FEATURES.md` | You're implementing a feature and need its full spec with acceptance criteria |
| `04_USER_FLOWS.md` | You need to understand how a user moves through a workflow end-to-end |
| `05_ARCHITECTURE.md` | You're making a system-level change or need to understand data flow |
| `06_TECH_STACK.md` | You're adding a dependency or questioning an existing technology choice |
| `07_DATABASE.md` | You're writing a query, adding a column, or creating a migration |
| `08_API.md` | You're building or consuming an API endpoint |
| `09_SCRAPER.md` | You're working on a scraper adapter or debugging a scrape failure |
| `10_AI_AGENTS.md` | You're working on an AI agent or iterating on a prompt |
| `11_NOTIFICATION_SYSTEM.md` | You're working on notification delivery or debugging a missed notification |
| `12_FRONTEND.md` | You're building a frontend component, page, or hook |
| `13_SECURITY.md` | You're implementing auth, handling sensitive data, or doing a security review |
| `14_DEPLOYMENT.md` | You're deploying, debugging production, or writing a runbook |
| `16_ROADMAP.md` | You need to understand what phase we're in and what comes next |
| `17_TASKS.md` | You're picking up work or tracking what's done |
| `18_DECISIONS.md` | You're wondering why something was built a certain way |
| `20_PROMPTS.md` | You're working on an AI agent and need to find or update a prompt |
| `AI_RULES.md` | You're an AI assistant starting a new session on this project |

---

## 3. .openspec/

### `.openspec/`

**Why it exists:** A compressed, AI-assistant-optimized summary of the entire project context. Where `docs/` is comprehensive and human-readable, `.openspec/` is dense and machine-consumable. AI coding assistants can read all 7 files here in one context window and have enough information to work effectively without reading all 22 doc files.

**What it contains:**

| File | Contents |
|---|---|
| `project.md` | Mission, scope, current phase, key stakeholders |
| `architecture.md` | Canonical system design in compact form — the same content as `05_ARCHITECTURE.md` but condensed to 2 pages |
| `coding-standards.md` | Naming conventions, formatting rules, error handling patterns, test requirements |
| `workflow.md` | Development lifecycle — how PRs work, branch naming, commit message format, review process |
| `constraints.md` | Non-negotiable rules: no prompts in code, all schema changes via Alembic, scheduler single instance, etc. |
| `ai-guidelines.md` | Specific instructions for AI coding assistants: what to read first, what to never do, how to handle uncertainty |
| `changelog.md` | A running log of significant changes to architecture or documentation — the `.openspec/` equivalent of `22_CHANGELOG.md` |

**When it runs:** Not a runtime artifact — read by AI assistants and engineers at session start.

**Who uses it:** AI coding assistants (Cursor, GitHub Copilot, Claude Code) and any engineer who wants a rapid re-orientation after time away from the project.

**Common modifications:** Update `changelog.md` whenever a significant architectural decision changes. Update `constraints.md` whenever a new hard rule is established. These files should always reflect the current state — they are synopses of the full docs, not originals.

---

## 4. backend/

### `backend/`

**Why it exists:** The FastAPI application that powers all API endpoints, business logic, database access, and serves as the integration point for scrapers, agents, and the notification system.

**What it contains:** The entire Python backend, organized into layers (api → services → models) per the architecture in `05_ARCHITECTURE.md` Section 2.

**When it runs:** On every HTTP request (via Uvicorn/Gunicorn workers) and as the execution environment for background pipeline code.

**Who uses it:** The Next.js frontend calls the FastAPI API. The Telegram webhook fires into it. The scheduler process imports from it. The scraper and agent modules are co-located here.

### `backend/main.py`

**Why it exists:** The FastAPI application entrypoint. Every request starts here.

**What it does:**
- Creates the `FastAPI()` app instance
- Registers all middleware (CORS, security headers, rate limiting, request tracing)
- Mounts all API routers from `backend/api/`
- Registers startup events (`wait_for_db`, `setup_webhook`)
- Registers the `/health` endpoint

**When it runs:** At process startup. Every HTTP request passes through the middleware registered here.

**Common modifications:**
- Adding a new router → `app.include_router(new_router, prefix="/api")`
- Adding new middleware → `app.add_middleware(...)` — add in the correct order (middleware executes in reverse registration order)
- Adding a startup task → `@app.on_event("startup")`

### `backend/config.py`

**Why it exists:** Centralized configuration loaded from environment variables. All settings the application needs at runtime live here — no env var reads scattered through the codebase.

**What it does:** Pydantic `BaseSettings` class that reads from the process environment or `.env` file. Validates required settings on startup — the application crashes with a clear error if a required variable is missing rather than failing silently later.

**Common modifications:** When adding a new environment variable, add it here first, then to `.env.example`. Never read `os.environ` directly in application code — always use `settings.VARIABLE_NAME`.

### `backend/alembic.ini`

**Why it exists:** Alembic database migrations configuration.

**What it does:** Configures the database connection URL loader, script location (pointing to `../database/migrations`), and logging levels for database migrations.

---

## 5. backend/api/

### `backend/api/`

**Why it exists:** HTTP route handlers, organized by domain. Each file in this directory handles one area of the API surface.

**What it contains:** FastAPI `APIRouter` instances, one per domain. Routers define HTTP methods, paths, request validation (via Pydantic schemas), and call into the service layer. Routers never contain business logic and never call the database directly.

**Rule:** If a router file imports `sqlalchemy`, that is a code review violation. Routers call services; services call models.

| File | Handles |
|---|---|
| `auth.py` | Register, login, OAuth, refresh, logout, forgot/reset password, account deletion |
| `profile.py` | Skills, preferences, notification prefs, resume upload/status |
| `jobs.py` | Job listing feed, job detail |
| `saved_jobs.py` | Save, unsave, list, update status, stats |
| `notifications.py` | Notification preferences, history |
| `health.py` | Uptime monitor liveness and readiness check (database and Redis connectivity) |
| `admin/companies.py` | Company CRUD, ATS detection, manual scrape trigger |
| `admin/scraper_health.py` | Scraper health aggregate |
| `admin/review_queue.py` | Flagged job approve/reject |
| `admin/users.py` | User list, detail, suspend, reactivate |
| `webhooks/telegram.py` | Incoming Telegram updates (messages, callback queries) |

**When it runs:** On every matching HTTP request.

**Common modifications:**
- Adding an endpoint → add to the relevant router file; update `08_API.md` in the same PR
- Adding an admin endpoint → use `Depends(require_admin)` — never forget this
- Changing a response schema → update the Pydantic schema in `backend/schemas/` and update `08_API.md`

---

## 6. backend/services/

### `backend/services/`

**Why it exists:** Business logic layer. This is where the actual decisions happen — validation, orchestration of multiple model calls, complex queries, side effects. Separating this from routers means the same logic can be called from an API endpoint, a scheduler job, or a test without duplication.

**What it contains:** One Python file per domain, each exporting async functions that routers and schedulers call.

| File | Responsibilities |
|---|---|
| `auth_service.py` | Token creation/validation, OAuth flow, login lockout logic |
| `profile_service.py` | Profile CRUD, skill normalization, preference updates |
| `job_service.py` | Job retrieval, filtering, full-text search, cache management |
| `matching_service.py` | **Core matching algorithm** — finds users whose profile matches a given job |
| `notification_service.py` | Notification routing, digest queue management, delivery orchestration |
| `admin_service.py` | Company management, ATS detection trigger, review queue operations |

**When it runs:** Called by API routers and scheduler jobs. Never called directly from an HTTP request handler without going through a router.

**Common modifications:**
- Changing matching logic → `matching_service.py` → verify `11_NOTIFICATION_SYSTEM.md` Section 4 is still accurate
- Adding a new business rule → add to the relevant service file; never add to a router
- Caching a slow query → add Redis cache in the service layer, not in the router

---

## 7. backend/models/

### `backend/models/`

**Why it exists:** SQLAlchemy ORM model definitions. Each file maps a Python class to a database table. Models define the shape of the data and the relationships between tables.

**What it contains:** One file per table, each defining a `Base`-inheriting SQLAlchemy model class with columns, relationships, and indexes.

| File | Table |
|---|---|
| `user.py` | `users` |
| `profile.py` | `user_profiles`, `user_preferences`, `user_preferred_roles`, `user_preferred_locations` |
| `notification_preference.py` | `notification_preferences` |
| `skill.py` | `skills`, `user_skills` |
| `company.py` | `companies` |
| `job.py` | `jobs`, `job_skills` |
| `scrape_run.py` | `scrape_runs` |
| `agent_log.py` | `agent_logs` |
| `notification_log.py` | `notification_logs` |
| `saved_job.py` | `user_saved_jobs` |
| `token.py` | `refresh_tokens`, `email_verification_tokens`, `password_reset_tokens`, `telegram_link_codes` |
| `admin_alert_log.py` | `admin_alert_logs` |
| `audit_log.py` | `audit_logs` |

**When it runs:** Models are loaded at application startup. They are used whenever a service layer function reads or writes the database.

**Common modifications:** When changing a model (adding a column, changing a type, adding a relationship):
1. Edit the model class here
2. Run `alembic revision --autogenerate -m "description"`
3. Review the generated migration — autogenerate is a starting point, not a guarantee
4. Update `07_DATABASE.md` with the schema change
5. Never edit the model without also creating the migration — the two must stay in sync

---

## 8. backend/schemas/

### `backend/schemas/`

**Why it exists:** Pydantic request and response models. These are separate from SQLAlchemy models — SQLAlchemy models represent database rows, Pydantic schemas represent what the API accepts and returns. They are deliberately separate because the API contract and the database schema evolve at different rates.

**What it contains:** One file per domain, each defining `Request` and `Response` Pydantic models.

| File | Contains |
|---|---|
| `auth_schemas.py` | `RegisterRequest`, `LoginRequest`, `TokenResponse`, `PasswordResetRequest` |
| `job_schemas.py` | `JobListItem`, `JobDetail`, `JobFilters` |
| `profile_schemas.py` | `SkillsUpdate`, `PreferencesUpdate`, `NotificationPreferencesUpdate` |
| `admin_schemas.py` | `NewCompanyRequest`, `CompanyHealthItem`, `ReviewQueueItem` |
| `saved_job_schemas.py` | `SaveJobRequest`, `SavedJobResponse`, `UpdateStatusRequest` |

**When it runs:** On every API request — Pydantic validates the incoming request body before the router function even runs. On every API response — Pydantic serializes the return value.

**Common modifications:**
- Adding a new field to an API response → add to the response schema here; update `08_API.md`
- Adding request validation → add a `@field_validator` method to the request schema
- Never add validation logic to a router function directly — it belongs in the schema

---

## 9. backend/middleware/

### `backend/middleware/`

**Why it exists:** Cross-cutting concerns that apply to every request — authentication, rate limiting, request tracing, security headers. Middleware runs before any router handler and after any response is returned.

| File | Does |
|---|---|
| `auth_middleware.py` | `get_current_user()` and `require_admin()` FastAPI dependencies — validates JWT, checks user active/deleted status, enforces role |
| `rate_limit_middleware.py` | Sliding-window rate limiter backed by Redis — applied per-endpoint with different limits per `08_API.md` |
| `logging_middleware.py` | Attaches `trace_id` (UUID) to each request; logs request/response at INFO level with timing |
| `security_headers.py` | Adds `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`, `Referrer-Policy` to every response |

**When it runs:** On every HTTP request, before the router handler executes.

**Common modifications:**
- Changing rate limits → update `rate_limit_middleware.py` and `13_SECURITY.md` Section 8.2 simultaneously
- Adding a new security header → add to `security_headers.py`; document in `13_SECURITY.md` Section 6.3
- Adding a new authentication check → add to `auth_middleware.py` as a new FastAPI dependency — do not inline it in a router

---

## 10. backend/core/

### `backend/core/`

**Why it exists:** Foundational infrastructure that every part of the backend depends on — database connection, Redis client, security utilities, logging setup. These are not business logic; they are the plumbing everything else plugs into.

| File | Does |
|---|---|
| `database.py` | Creates the SQLAlchemy async engine and session factory. `get_db()` FastAPI dependency. `wait_for_db()` startup retry loop |
| `redis_client.py` | Creates the async Redis connection pool. Provides `get_redis()` — a single shared client used by rate limiter, cache, and queue modules |
| `security.py` | `hash_password()`, `verify_password()`, `create_access_token()`, `decode_access_token()`, `create_refresh_token()`, `set_refresh_cookie()` — all cryptographic operations |
| `logging.py` | JSON log formatter, trace ID context variable, sensitive field redaction filter, `setup_logging()` called at app startup |
| `audit.py` | `log_audit_event()` — writes to `audit_logs` table for security-relevant events |

**When it runs:** `core/` modules are initialized at application startup. `get_db()` and `get_redis()` are called on every request that touches the database or cache.

**Common modifications:**
- Changing password hashing parameters → `security.py` — review `13_SECURITY.md` Section 2.1 first; changing bcrypt cost factor requires re-hashing all passwords
- Adding a new audit event type → `audit.py` + `13_SECURITY.md` Section 14.1
- Connection pool tuning → `database.py` `create_async_engine(pool_size=...)` parameters

---

## 11. scrapers/

### `scrapers/`

**Why it exists:** All scraping infrastructure — the ATS detector, base scraper class, and the runner that orchestrates batches. This is where raw job data originates before it enters the AI agent pipeline.

| File | Does |
|---|---|
| `base_scraper.py` | Abstract base class all adapters inherit from. Provides: `fetch()` (rate-limited, retried, CAPTCHA-checked HTTP requests), `is_allowed_by_robots()`, `detect_captcha()`, user-agent rotation. **No adapter should re-implement any of these.** |
| `ats_detector.py` | Three-stage ATS fingerprinting: URL patterns → HTML signatures → API probes. Returns an ATS type string or `"generic"`. Called once per company per scrape run. |
| `runner.py` | Orchestrates the scrape batch: queries companies ordered by `last_scraped_at ASC`, calls the right adapter per company, handles per-company failures without stopping the batch, writes `scrape_run` records, triggers `consecutive_failures` alerts. |

**When it runs:** Called by `scheduler/jobs/scrape_batch.py` every 15 minutes. Can also be triggered manually by an admin via `POST /api/admin/companies/{id}/run-now`.

**Who uses it:** The scheduler calls `runner.run_scrape_batch()`. The admin API calls individual company scrapes. The `agents/pipeline_runner.py` receives raw job objects from here.

**Common modifications:**
- Adding a new ATS signature → `ats_detector.py` — update the URL_PATTERNS, HTML_SIGNATURES, and API_PROBES dicts; document in `09_SCRAPER.md` Section 3
- Changing rate limiting → `base_scraper.py` `rate_limit()` function; update `09_SCRAPER.md` Section 15
- Changing retry behavior → `base_scraper.py` `fetch()` retry loop; update `09_SCRAPER.md` Section 16

---

## 12. scrapers/adapters/

### `scrapers/adapters/`

**Why it exists:** One file per supported ATS. Each adapter knows how to fetch job listings and job details from one specific ATS platform. The adapter selection is determined by `ats_detector.py` — adapters never select themselves.

| File | ATS | Status |
|---|---|---|
| `workday.py` | Workday HCM | Phase 1 |
| `greenhouse.py` | Greenhouse by Rippling | Phase 1 |
| `lever.py` | Lever | Phase 1 |
| `icims.py` | iCIMS Talent Cloud | Phase 1 |
| `taleo.py` | Oracle Taleo Enterprise | Phase 1 |
| `generic.py` | Unknown / custom career pages | Phase 1 |
| `smartrecruiters.py` | SmartRecruiters | Phase 2 |
| `breezyhr.py` | BreezyHR | Phase 2 |
| `ashby.py` | Ashby | Phase 2 |

**When it runs:** Each adapter is instantiated and called during a scrape run for a company that uses that ATS.

**Interface every adapter must implement:**
```python
class XyzAdapter(BaseScraper):
    ats_type = "xyz"                              # must match a key in ats_detector.py
    def get_job_list(company) -> list[RawJobListing]
    def get_job_detail(job_url) -> RawJobDetail
```

**Common modifications:**
- ATS layout changed, adapter is broken → update the CSS selectors, API endpoint path, or JSON field names in the relevant adapter file; add an entry to `09_SCRAPER.md` Section 19 explaining the change
- Adding a Phase 2 adapter → follow the checklist in `09_SCRAPER.md` Section 20; create the file here, add detection signatures to `ats_detector.py`, write the section in `09_SCRAPER.md`
- Changing pagination logic → update the adapter's `get_job_list()` loop; document in the adapter's section of `09_SCRAPER.md`

---

## 13. agents/

### `agents/`

**Why it exists:** AI agent definitions. Each agent takes structured input, calls the LLM API, validates the JSON output, and returns structured results. Agents never touch the database directly and never call other agents — they are orchestrated by `pipeline_runner.py`.

| File | Agent | Model |
|---|---|---|
| `base_agent.py` | Abstract base — cache, retry, logging | — |
| `llm_client.py` | OpenAI primary + Anthropic fallback | — |
| `duplicate_detector.py` | Hash-based deduplication (no LLM) | None |
| `job_extractor.py` | Structured field extraction from JD | GPT-4o |
| `skill_extractor.py` | Required/preferred skills + degree flag | GPT-4o |
| `jd_summarizer.py` | 5-bullet student-friendly summary | GPT-4o |
| `job_classifier.py` | role_type, domain, experience, company_type | GPT-4o-mini |
| `notification_generator.py` | Telegram message body | GPT-4o-mini |
| `resume_skill_extractor.py` | Skills from resume PDF text | GPT-4o (Phase 2) |
| `match_score_calculator.py` | Match % score (no LLM, deterministic) | None (Phase 3) |
| `pipeline_runner.py` | Orchestrates the 5-agent sequence per job | — |
| `config.py` | `AGENT_MODELS` dict — maps logical model names to real model strings | — |

**When it runs:** `pipeline_runner.py` is called by the scraper runner for each new job dequeued from Redis. `notification_generator.py` is called by the notification dispatcher per user-job pair at send time.

**Important rule:** Prompts are never written inside agent files. Every prompt template lives in `docs/20_PROMPTS.md` and is loaded via the config. Agent files build the prompt from the template + input data.

**Common modifications:**
- Iterating on a prompt → edit `docs/20_PROMPTS.md` (bump the version number); update the `prompt_version` constant in the corresponding agent file; never edit prompt text in the agent file itself
- Changing a model → edit `agents/config.py` `AGENT_MODELS` dict; add a decision record to `18_DECISIONS.md`
- Adding output validation → add to the agent's `parse_output()` method; add tests in `tests/unit/agents/`

---

## 14. notifications/

### `notifications/`

**Why it exists:** Everything related to delivering information to users after a job has been processed. Separating this from the agent pipeline means notification logic can evolve independently — adding a new channel (WhatsApp, push) never requires touching agent code.

| File | Does |
|---|---|
| `router.py` | The single decision point: who gets notified, via what channel, now or after quiet hours? All channel selection and timing logic lives here. |
| `matching_service.py` | SQL-based user-to-job matching: finds all users whose profile (role_type + location + experience + skills) overlaps with a given job. Called once per new job. |
| `retry_worker.py` | Background async task that polls the Redis retry ZSET every 10 seconds and re-dispatches failed notifications. |

**When it runs:** `router.py` and `matching_service.py` run immediately after a job is saved to the database. `retry_worker.py` runs continuously as a background asyncio task.

**Common modifications:**
- Changing matching criteria → `matching_service.py` — update the SQL query and update `11_NOTIFICATION_SYSTEM.md` Section 4
- Adding a new notification channel → add a new dispatcher module, add a branch in `router.py`, add the channel to `notification_channel_enum` in the database schema (migration required)
- Changing retry delays → `retry_worker.py` `enqueue_retry()` delay dict; update `11_NOTIFICATION_SYSTEM.md` Section 10

---

## 15. notifications/telegram/

### `notifications/telegram/`

**Why it exists:** Everything specific to the Telegram Bot API — setup, message dispatch, templates, and command handlers.

| File | Does |
|---|---|
| `bot.py` | Creates the `python-telegram-bot` `Application`, registers all command and callback handlers, sets up webhook in production |
| `dispatcher.py` | `send_job_alert()` — formats and sends a job notification with inline keyboard; handles all Telegram-specific exceptions (`Forbidden`, `BadRequest`, `TimedOut`); respects Telegram's 30msg/sec rate limit |
| `templates.py` | Message format functions: `job_alert_message()`, `deadline_reminder_message()`, static constants like `CONNECTED_MESSAGE` and `HELP_MESSAGE` |
| `commands.py` | Handlers for all bot commands: `/start` (account linking), `/pause`, `/resume`, `/settings`, `/unlink`, `/help`; inline button callback handler (`save:`, `dismiss:`, `applied:`) |

**When it runs:** `bot.py` initializes at application startup. `dispatcher.py` is called by the notification router when Telegram is the selected channel. `commands.py` handlers fire on incoming Telegram updates (webhooks).

**Common modifications:**
- Adding a new bot command → add handler to `commands.py`; register it in `bot.py`; update `/help` message in `templates.py`; document in `11_NOTIFICATION_SYSTEM.md` Section 14
- Changing message format → `templates.py` — keep messages scannable; remember Telegram renders HTML (`<b>`, `<i>`, `<a>`) when `parse_mode="HTML"`
- Handling a new Telegram exception type → `dispatcher.py` `send_job_alert()` exception block

---

## 16. notifications/email/

### `notifications/email/`

**Why it exists:** Email delivery infrastructure — provider-agnostic client, digest compilation, and HTML templates.

| File | Does |
|---|---|
| `client.py` | Provider-agnostic wrapper around Resend (or SendGrid). `send()` is the single function all email-sending code calls. Switching email providers = changing only this file. |
| `digest.py` | `compile_digest()` — queries Redis digest queue per user, fetches job details, renders the HTML template, calls `client.send()`. Called by the scheduler. |
| `scheduler.py` | Calculates the correct send time per user timezone; coordinates the daily and weekly digest runs. |
| `templates/base.html` | Base Jinja2 HTML layout — header, footer, unsubscribe link. All other templates extend this. |
| `templates/digest.html` | Job card grid for daily/weekly digest. |
| `templates/deadline_reminder.html` | Single-job reminder template. |
| `templates/welcome.html` | Sent on account registration. |

**When it runs:** `digest.py` is called by `scheduler/jobs/daily_digest.py` and `scheduler/jobs/weekly_summary.py`. `client.py` is called whenever any notification module needs to send an email.

**Common modifications:**
- Switching email providers → `client.py` only — the rest of the system never imports from the provider SDK directly
- Updating email template design → edit the Jinja2 HTML files in `templates/`; test rendering in a browser before deploying (send a test digest to yourself)
- Adding a new email type → create a new template file; add a `send_{type}()` function to `client.py` or `digest.py`

---

## 17. scheduler/

### `scheduler/`

**Why it exists:** The heartbeat of the entire platform. Nothing gets scraped, no digests get sent, no reminders fire without the scheduler.

| File | Does |
|---|---|
| `main.py` | Creates the APScheduler instance, registers all recurring jobs with their intervals, starts the scheduler. **This process must run as exactly one instance — never scale it horizontally.** See `18_DECISIONS.md` D-INFRA-001. |
| `jobs/scrape_batch.py` | Fires every 15 minutes. Calls `scrapers/runner.run_scrape_batch()`. |
| `jobs/daily_digest.py` | Fires daily at 02:30 UTC (≈ 08:00 IST). Calls `notifications/email/digest.compile_digest()` for all eligible users. |
| `jobs/weekly_summary.py` | Fires every Monday at 02:30 UTC. Sends weekly summary email. (Phase 2) |
| `jobs/deadline_reminder.py` | Fires daily at 03:30 UTC (≈ 09:00 IST). Scans `user_saved_jobs` for upcoming deadlines, sends reminders. |

**When it runs:** The scheduler process starts alongside the backend and runs continuously. Jobs fire at their configured intervals via APScheduler's background thread.

**Critical constraint:** `max_instances=1` is set on every job. If the scheduler is restarted mid-run, the in-progress run is abandoned and the next cycle picks up. This is intentional — it is safer than risking duplicate runs.

**Common modifications:**
- Changing a job interval → update `scheduler/main.py` interval config; document in `14_DEPLOYMENT.md` Section 5
- Adding a new scheduled job → create `jobs/new_job.py`; register in `main.py`; document in `05_ARCHITECTURE.md` Section 5
- Debugging a missed run → check `scrape_runs` table for that time window; check scheduler process logs for errors

---

## 18. database/

### `database/`

**Why it exists:** All database lifecycle files — migrations that define the schema and seed data that populates reference tables.

| File / Folder | Does |
|---|---|
| `migrations/` | Alembic migration scripts. Every schema change produces one file here. Files are numbered and chained — run `alembic upgrade head` to apply all pending migrations in order. |
| `migrations/env.py` | Alembic configuration — connects to the database, imports SQLAlchemy models so autogenerate can detect changes. |
| `migrations/versions/` | Individual migration files. Named `{revision_id}_{description}.py`. Each has `upgrade()` and `downgrade()` functions. |
| `seeds/skills.json` | Canonical skill list: 150+ skills with name, slug, and category. Loaded by `scripts/seed_db.py`. Never edited directly — changes go through a new migration or seed script. |
| `seeds/role_types.json` | All 16 role type slugs from the classifier taxonomy. |
| `seeds/cities.json` | 25+ Indian cities + Remote. |
| `seeds/companies.json` | Initial 50–100 company career pages with ATS type. |

**When it runs:** Migrations run during deployment (CI/CD pipeline runs `alembic upgrade head` after each deploy). Seed scripts run once on initial setup and are idempotent (`ON CONFLICT DO NOTHING`).

**Common modifications:**
- Adding a table or column → modify the SQLAlchemy model in `backend/models/`; run `alembic revision --autogenerate`; review the generated file; add to `07_DATABASE.md`
- Adding a new skill → add to `seeds/skills.json`; write a short migration that inserts it (`INSERT INTO skills ... ON CONFLICT DO NOTHING`)
- Adding a new company to scrape → add to `seeds/companies.json` OR add via the admin dashboard at runtime

---

## 19. frontend/

### `frontend/`

**Why it exists:** The Next.js web application — both the student-facing jobs platform and the admin control panel.

**What it contains:** A Next.js 14 App Router project with TypeScript and Tailwind CSS. Organized by route group, with shared components, hooks, and utilities in dedicated folders.

**When it runs:** In production, served by Vercel (SSR for public pages, static for others). In development, Next.js dev server at `localhost:3000`.

**Who uses it:** Students browse jobs, set their profile, and track applications here. Admins manage scrapers and companies here. The Telegram bot complements it — most student interactions happen in Telegram, but the web app is the full experience.

| File | Does |
|---|---|
| `next.config.ts` | Next.js configuration: `output: "standalone"` for Docker, `images.domains` for company logos, environment variable exposure |
| `types/index.ts` | Standard TypeScript interfaces and response schemas mirroring Pydantic models |
| `tailwind.config.ts` | Design token configuration: color palette, spacing scale, font settings |
| `middleware.ts` | Route protection: redirects unauthenticated users from protected routes to `/login`; redirects authenticated users away from auth pages |
| `tsconfig.json` | TypeScript configuration with strict mode and path aliases (`@/` → `src/`) |

---

## 20. frontend/app/

### `frontend/app/`

**Why it exists:** All pages, organized by route group. Next.js App Router uses file-system based routing — the directory structure maps directly to URLs.

**Route groups (folders wrapped in parentheses):**

| Route Group | URL Prefix | Auth Required | Shared Layout |
|---|---|---|---|
| `(auth)` | `/login`, `/register`, `/verify-email` | None (redirect if authed) | Minimal centered layout |
| `(onboarding)` | `/onboarding/1–4` | Required | Progress step indicator |
| `(dashboard)` | `/jobs`, `/my-jobs`, `/settings` | Required | Navbar + sidebar |
| `(admin)` | `/admin/*` | Admin role | Admin sidebar nav |

**Key pages:**

| File | Page | Rendering |
|---|---|---|
| `(auth)/login/page.tsx` | Login | Client (form state) |
| `(onboarding)/onboarding/[step]/page.tsx` | Onboarding steps 1–4 | Client |
| `(dashboard)/jobs/page.tsx` | Jobs feed | Server shell + Client feed |
| `(dashboard)/jobs/[id]/page.tsx` | Job detail | SSR with `generateMetadata` |
| `(dashboard)/my-jobs/page.tsx` | Application tracker | Client |
| `(dashboard)/settings/page.tsx` | Profile & notifications | Client |
| `(admin)/admin/scraper-health/page.tsx` | Scraper health dashboard | Client (auto-refresh) |
| `(admin)/admin/review-queue/page.tsx` | Flagged job review | Client |

**When it runs:** Server Components render at request time on Vercel. Client Components hydrate in the browser.

**Common modifications:**
- Adding a new page → create the file in the correct route group; add to `12_FRONTEND.md` Section 3; add route protection if needed
- Adding a new layout → create `layout.tsx` in the route group folder
- Adding structured data (JSON-LD) → add to the relevant page's Server Component; see `12_FRONTEND.md` Section 13

---

## 21. frontend/components/

### `frontend/components/`

**Why it exists:** Reusable React components, organized by domain so related components are easy to find together.

| Subfolder | Contains |
|---|---|
| `ui/` | shadcn/ui primitives — Button, Badge, Card, Dialog, Input, Select, Tabs, Skeleton, Sheet, Toast. **Copied in and fully owned by us — not an npm dependency.** |
| `jobs/` | JobCard, JobFeed, FilterBar, JobDetail, SkillMatchChips, PostedLabel, EmptyFeed, FeedSkeleton |
| `onboarding/` | StepIndicator, SkillPicker, RolePicker, LocationPicker, TelegramConnect |
| `my-jobs/` | JobPipeline, SavedJobRow, StatsBar |
| `settings/` | SkillSettings, PreferenceSettings, NotificationSettings, DangerZone |
| `admin/` | ScraperHealthTable, ReviewQueueCard, CompanyForm, UserTable |
| `shared/` | Navbar, Sidebar, PageHeader, LoadingState, ErrorState, ConfirmDialog |

**Server vs. Client component rule:**
- Default to Server Component (no `"use client"` directive)
- Add `"use client"` only when the component uses `useState`, `useEffect`, event handlers, browser APIs, or React Query hooks
- If only part of a tree needs interactivity, extract that part into a small Client Component rather than making the whole tree a Client Component

**Common modifications:**
- Adding a new component → create in the correct subfolder; add an entry to `12_FRONTEND.md` Section 4
- Updating shadcn/ui component → edit the file in `components/ui/` directly (we own it); check Radix UI changelog for accessibility updates
- Changing the job card layout → `components/jobs/JobCard.tsx`; verify mobile layout still works correctly

---

## 22. frontend/hooks/

### `frontend/hooks/`

**Why it exists:** Custom React hooks that encapsulate data fetching and mutation logic using React Query. Keeps components clean — components declare what data they need, hooks handle how to get it.

| File | Wraps |
|---|---|
| `useJobs.ts` | `useInfiniteQuery` for the paginated jobs feed |
| `useSavedJobs.ts` | `useQuery` for saved jobs list + `useMutation` for save/unsave/update status |
| `useProfile.ts` | `useQuery` for profile + `useMutation` for skills/preferences updates |
| `useSkills.ts` | `useQuery` for canonical skill search (debounced, cached 1 hour) |
| `useTelegramStatus.ts` | `useQuery` with `refetchInterval: 3000` — polls during the Telegram linking flow |
| `useAdminHealth.ts` | `useQuery` with `refetchInterval: 60000` — auto-refreshes scraper health table |
| `useToast.ts` | shadcn/ui toast system wrapper |

**When it runs:** Hooks are called inside Client Components. They run in the browser.

**Common modifications:**
- Changing stale time → update the `staleTime` in the relevant hook; align with the backend cache TTL for the same data
- Adding a mutation → add `useMutation` with `onSuccess` cache invalidation; add a toast on error; document the optimistic update pattern if used
- Adding a new hook → follow the existing pattern; add entry to `12_FRONTEND.md` Section 5

---

## 23. frontend/lib/

### `frontend/lib/`

**Why it exists:** Non-component utilities used across the frontend — the API client, authentication config, and pure utility functions.

| File | Does |
|---|---|
| `api.ts` | Axios instance with base URL. Request interceptor attaches access token from memory. Response interceptor handles 401 → refresh token → retry. Domain-grouped API functions (`api.jobs.list()`, `api.savedJobs.save()`, etc.). **This is the only file that should make HTTP calls to the FastAPI backend.** |
| `auth.ts` | NextAuth.js configuration for Google OAuth provider. Token memory store: `getAccessToken()`, `setAccessToken()`, `clearAccessToken()`. |
| `utils.ts` | `cn()` (Tailwind class merging), `formatPostedAt()` (relative time), `formatDate()` (readable date), `hasActiveFilters()` |
| `constants.ts` | `EXPERIENCE_LEVELS`, `ROLE_TYPE_LABELS` — static lists used across multiple components |

**Common modifications:**
- Adding a new API call → add to `api.ts` in the correct domain group; add the corresponding TypeScript type to `types/index.ts`
- Updating the Axios base URL → `api.ts` — change `NEXT_PUBLIC_API_URL` in `.env.example` and Railway environment variables
- Adding a new utility function → `utils.ts` if generic; add to `constants.ts` if it's a static list

---

## 24. tests/

### `tests/`

**Why it exists:** Automated verification that the code does what the docs say it does. Organized by test type so fast tests (unit) can run independently of slow tests (integration, E2E).

| Subfolder | What's Tested | Tool | Speed |
|---|---|---|---|
| `unit/` | Pure functions — `hash_password`, `compute_hash`, `is_quiet_now`, agent `parse_output`, Pydantic validators | pytest | Very fast (< 1s each) |
| `integration/` | Full request/response cycles against a real test DB — auth flows, job listing with filters, notification matching query | pytest + real PostgreSQL + Redis | Moderate (1–5s each) |
| `e2e/` | Critical user journeys in a real browser against staging — register → onboard → job in feed → save → track | Playwright | Slow (10–30s each) |

**When it runs:**
- Unit tests: on every commit via pre-commit hook (optional) and in CI lint+test job
- Integration tests: in CI test job with PostgreSQL + Redis service containers
- E2E tests: in CI after staging deployment, before production promotion

**Structure convention:**
```
tests/
  unit/
    auth/         test_security.py, test_password_policy.py
    agents/       test_duplicate_detector.py, test_jd_summarizer.py
    scrapers/     test_ats_detector.py, test_rate_limiter.py
    notifications/ test_quiet_hours.py, test_matching.py
  integration/
    api/          test_auth_flow.py, test_jobs_api.py, test_saved_jobs.py
    scrapers/     test_greenhouse_adapter.py, test_workday_adapter.py
    agents/       test_pipeline.py
  e2e/
    test_registration.spec.ts
    test_jobs_feed.spec.ts
    test_saved_jobs.spec.ts
    test_admin_company.spec.ts
```

**Common modifications:**
- Adding a new feature → add unit tests for the service layer logic + integration test for the API endpoint in the same PR
- Fixing a bug → add a regression test that would have caught the bug before fixing it
- Coverage drops below 70% → `pytest --cov` report shows which lines are uncovered; CI will block the merge

---

## 25. scripts/

### `scripts/`

**Why it exists:** Developer utilities and one-time operational scripts. These are not part of the running application — they are tools for setup, debugging, and data management.

| File | Does | Run When |
|---|---|---|
| `seed_db.py` | Seeds all reference data (skills, role_types, cities, initial companies) from `database/seeds/*.json`. Idempotent — safe to run multiple times. | Once on fresh setup; again when seed data changes |
| `test_scraper.py` | CLI tool for testing scraper adapters against real companies. `--company-id 42 --run-now` triggers one company's scrape immediately. `--url https://...` tests ATS detection on any URL. | During development and debugging of scraper failures |
| `verify_schema.py` | Reads live DB schema and compares against the SQLAlchemy model definitions. Fails if they have drifted apart. | In CI pre-deployment check |
| `backfill_skills.py` | One-time script to re-run the Skill Extractor agent on existing jobs that have empty `job_skills` records (e.g., after adding a new canonical skill). | When canonical skills list is expanded |
| `cost_report.py` | Queries `agent_logs` and produces a cost estimate for the past 7/30 days based on model used + token counts. | Weekly; before budget reviews |
| `export_users.py` | Admin-only script to export anonymized user stats (skill distribution, role preferences) for product analytics. PII is stripped. | Quarterly analytics review |

**Rules for scripts:**
- Scripts are never imported by application code — they are standalone utilities
- Scripts that modify production data must have a `--dry-run` flag that logs what would happen without doing it
- One-time migration scripts are kept in `scripts/` permanently (not deleted after use) so the history of what ran is preserved
- Scripts that are meant to run on a schedule go in `scheduler/jobs/`, not here

---

*This document is the map to the codebase. When something exists but isn't here, it's undocumented — update this file. When something documented here no longer exists, update this file. The goal is that any engineer can read this document and immediately know where to look for anything in the project.*
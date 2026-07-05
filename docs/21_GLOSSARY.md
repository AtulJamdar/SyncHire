# 21 — Glossary

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Engineering Lead  

---

## Purpose of This Document

Every technical term, abbreviation, and platform-specific concept used in Job Finder AI's documentation and codebase is defined here. When a term appears in code or docs that isn't immediately obvious, the definition is here.

Entries are organized alphabetically within categories. Cross-references to relevant documentation sections are included where a deeper explanation exists.

---

## Categories

- [A — Architecture & System Design](#a--architecture--system-design)
- [B — Backend Technologies](#b--backend-technologies)
- [C — Core Concepts](#c--core-concepts)
- [D — Data & Database](#d--data--database)
- [F — Frontend Technologies](#f--frontend-technologies)
- [H — HTTP & Web](#h--http--web)
- [I — Infrastructure & Hosting](#i--infrastructure--hosting)
- [L — LLM & AI](#l--llm--ai)
- [M — Metrics & Business](#m--metrics--business)
- [N — Notifications](#n--notifications)
- [P — Product & Platform](#p--product--platform)
- [S — Scraping](#s--scraping)
- [T — Auth & Security](#t--auth--security)
- [U — Users & Roles](#u--users--roles)

---

## A — Architecture & System Design

### Adapter
A scraper module specific to one ATS type. Each adapter knows how to fetch and parse job listings from one particular ATS platform (Workday, Greenhouse, Lever, etc.). Adapters inherit from `BaseScraper` and implement two methods: `get_job_list()` and `get_job_detail()`.  
→ See: `09_SCRAPER.md` Sections 4–12, `scrapers/adapters/`

### Agent
An AI-powered processing step in the job extraction pipeline. Each agent takes structured input, calls an LLM via the OpenAI or Anthropic API, validates the JSON output against a schema, and returns structured results. Agents are single-purpose, stateless, and always output JSON — never free text.  
→ See: `10_AI_AGENTS.md`, `agents/`

### APScheduler
Python library used to run recurring background jobs (cron-style). Manages the 15-minute scrape batch trigger, daily email digest, and deadline reminder jobs. Runs as a single process — must never have more than one instance running simultaneously.  
→ See: `05_ARCHITECTURE.md` Section 5, `18_DECISIONS.md` D-TECH-004, `scheduler/`

### Async / Asyncio
Python's built-in concurrency model for I/O-bound operations. FastAPI and all database/Redis operations use `async/await` so the application can handle many concurrent requests without blocking. Essential because the platform makes many external I/O calls (LLM APIs, Telegram API, ATS scraping).

### Background Pipeline
The automated, continuously-running system that discovers, processes, and delivers jobs without human intervention. Consists of: Scheduler → Scraper Pipeline → AI Agent Pipeline → Notification Engine. Runs independently of any user request.  
→ See: `05_ARCHITECTURE.md` Section 1, `04_USER_FLOWS.md` Flow 4

---

## B — Backend Technologies

### Alembic
Database migration tool for Python and SQLAlchemy. Every schema change (adding a table, adding a column, creating an index) is expressed as an Alembic migration file with `upgrade()` and `downgrade()` functions. All migrations are applied via `alembic upgrade head` — never by writing SQL directly in production.  
→ See: `06_TECH_STACK.md`, `07_DATABASE.md` Section 27, `18_DECISIONS.md` D-TECH-005

### BaseScraper
Abstract Python base class in `scrapers/base_scraper.py` that all adapter classes inherit from. Provides shared infrastructure: rate-limited HTTP fetching (`fetch()`), robots.txt compliance (`is_allowed_by_robots()`), CAPTCHA detection (`detect_captcha()`), and user-agent rotation. No adapter implements these behaviours itself.  
→ See: `09_SCRAPER.md` Section 2

### BaseAgent
Abstract Python base class in `agents/base_agent.py` that all agent classes inherit from. Provides: prompt loading from config, LLM API calls via `LLMClient`, JSON parsing with repair-attempt retry, Redis caching by input hash, and logging to `agent_logs`. No agent implements these behaviours itself.  
→ See: `10_AI_AGENTS.md` Section 2

### bcrypt
Password hashing algorithm used for all user passwords. bcrypt deliberately runs slowly (configurable cost factor), making brute-force attacks expensive. The platform uses cost factor 12 — high enough for security, imperceptible to a user logging in. Raw passwords are never stored or logged anywhere.  
→ See: `13_SECURITY.md` Section 2.1

### Gunicorn
Python WSGI/ASGI process manager. In production, Gunicorn manages multiple Uvicorn worker processes, providing process supervision (restarts crashed workers), load distribution, and graceful shutdowns. Command: `gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --workers 2`.  
→ See: `14_DEPLOYMENT.md` Section 3.3

### httpx
Async-native Python HTTP client used by scrapers to fetch career pages and ATS API endpoints. Has a `requests`-like API (familiar to most Python developers) with native `async/await` support. Used instead of `requests` (synchronous only) or `aiohttp` (less familiar API).  
→ See: `06_TECH_STACK.md`, `18_DECISIONS.md` D-TECH-013

### Playwright (Python)
Browser automation library that controls a headless Chromium browser. Used selectively in scraping for career pages that load job listings via client-side JavaScript (cannot be fetched with plain HTTP). Not the default scraping method — `httpx` is used first; Playwright is the fallback for JS-rendered pages.  
→ See: `06_TECH_STACK.md`, `09_SCRAPER.md` Section 9, `18_DECISIONS.md` D-TECH-014

### Pydantic
Python library for data validation and serialization, deeply integrated with FastAPI. All API request bodies and response shapes are Pydantic models. Validation runs automatically on every request — invalid input is rejected with a 422 error before any business logic runs. Also used by agents to validate LLM output schemas.  
→ See: `08_API.md`, `backend/schemas/`

### python-telegram-bot
Python wrapper library around the Telegram Bot API. Handles webhook setup, message sending, inline keyboard creation, command routing, and callback query processing. Used in webhook mode (not polling) in production.  
→ See: `06_TECH_STACK.md`, `11_NOTIFICATION_SYSTEM.md` Section 5

### SQLAlchemy
Python ORM (Object-Relational Mapper) for database access. Provides Python class definitions that map to database tables (`backend/models/`), a query builder for constructing SQL queries safely, relationship definitions (foreign keys, joins), and async support via `sqlalchemy.ext.asyncio`.  
→ See: `06_TECH_STACK.md`, `18_DECISIONS.md` D-TECH-005

### Uvicorn
ASGI server that runs the FastAPI application. Handles incoming HTTP connections, manages the async event loop, and processes requests. In production, multiple Uvicorn workers run under Gunicorn process management.  
→ See: `14_DEPLOYMENT.md` Section 3.3

---

## C — Core Concepts

### Canonicalization
The process of standardizing a value to one authoritative form. Applied in two contexts: (1) Skill names extracted by the LLM (e.g., "JS" → "JavaScript", "Postgres" → "PostgreSQL") are mapped to canonical entries in the `skills` table; (2) Job fields used for deduplication are normalized before hashing (lowercased, whitespace collapsed, unicode normalized).  
→ See: `10_AI_AGENTS.md` Section 5, `09_SCRAPER.md` Section 14

### Canonical Skills List
The authoritative list of all skills the platform recognizes, stored in the `skills` table and seeded from `database/seeds/skills.json`. Users select skills from this list; agents map extracted skills to entries in this list. New skills are added by admin only — not by users or automatically by agents.  
→ See: `07_DATABASE.md` Section 6, `03_FEATURES.md` F-PROF-01

### content_hash
A SHA-256 hash of a job's normalized title + company + apply_url. Stored in `jobs.content_hash` with a `UNIQUE` index. Used by the Duplicate Detector agent to skip jobs already in the database. The hash is computed before any LLM calls — deduplication is deterministic and nearly instantaneous (single indexed DB lookup).  
→ See: `07_DATABASE.md` Section 16, `10_AI_AGENTS.md` Section 3, `18_DECISIONS.md` D-DB-004

### Extraction Confidence
A float (0.0–1.0) returned by the Job Extractor agent, representing the LLM's self-assessed certainty in its extraction output. Jobs with `extraction_confidence < 0.75` are automatically flagged (`needs_review = true`, `is_active = false`) and sent to the admin review queue before students ever see them.  
→ See: `10_AI_AGENTS.md` Section 4, `03_FEATURES.md` F-AGNT-02

### Exponential Backoff
A retry delay strategy where each successive retry waits twice as long as the previous. Used by scrapers when a request fails: first retry after 2 seconds, second after 4 seconds, third after 8 seconds. Prevents overwhelming a struggling target server with rapid-fire retries.  
→ See: `09_SCRAPER.md` Section 16

### Idempotent
An operation that produces the same result whether run once or many times. Critical in two places: (1) Seed scripts use `ON CONFLICT DO NOTHING` — running `seed_db.py` twice does not create duplicate data. (2) Job processing is idempotent — if a job is processed twice (e.g., due to a queue re-delivery), the second attempt fails at the `content_hash` unique constraint and is safely ignored.  
→ See: `scripts/seed_db.py`, `07_DATABASE.md` Section 16

### In-Process Scheduler
A scheduler that runs inside the same OS process as the main application (as opposed to an external managed scheduler). APScheduler in this project runs either embedded in the FastAPI process or as a separate Python worker process — but always as a single instance. No external infrastructure (AWS EventBridge, Google Cloud Scheduler) is required.  
→ See: `18_DECISIONS.md` D-TECH-004

### Matching
The process of finding users whose profile preferences (role types, locations, skills, experience level) overlap with a newly scraped and processed job's classified attributes. Matching runs once per new job, against the full active user base, using a SQL query with indexed joins. Users who match receive a notification.  
→ See: `11_NOTIFICATION_SYSTEM.md` Section 4, `04_USER_FLOWS.md` Flow 4

### Monolith
A software architecture where all functionality lives in a single deployable unit (as opposed to microservices). Job Finder AI is a structured monolith: one Python backend codebase, clear internal module boundaries (api → services → models), but no network calls between internal components. This was a deliberate decision given the team size.  
→ See: `18_DECISIONS.md` D-ARCH-004

### Pipeline
The sequential chain of processing steps a raw scraped job goes through before it reaches students: Duplicate Detector → Job Extractor → Skill Extractor → JD Summarizer → Job Classifier → DB save → Matching → Notification dispatch. Each step's output feeds the next.  
→ See: `10_AI_AGENTS.md` Section 1, `04_USER_FLOWS.md` Flow 4

### Prompt Injection
An attack where malicious text in a user-controlled input (e.g., a job description scraped from a company's career page) contains instructions designed to override the LLM's system prompt. Mitigated by: (1) sanitizing user-derived content before inserting into prompts, (2) placing user content at the end of the prompt after all instructions, and (3) validating all LLM output against strict schemas.  
→ See: `13_SECURITY.md` Section 16.1

### Seed Data
Initial reference data populated into the database when a new environment is set up. Includes: canonical skills list, role types, cities, and initial company career page URLs. Seed scripts are idempotent and safe to re-run. Seed data is distinct from migration data — seeds fill reference tables, migrations change schema.  
→ See: `database/seeds/`, `scripts/seed_db.py`, `07_DATABASE.md` Sections 6–9

### Stale Time
In React Query, the duration after which cached data is considered "stale" and should be re-fetched in the background on the next access. The jobs feed uses a 2-minute stale time, matching the backend Redis cache TTL. Skill search results use a 1-hour stale time (the canonical list rarely changes).  
→ See: `12_FRONTEND.md` Section 5

### Token Rotation
A security practice where each use of a refresh token immediately invalidates it and issues a new one. If an old (already-rotated) refresh token is presented, it signals a possible theft — the system revokes all refresh tokens for that user, forcing a full re-login. Prevents token theft from being silently exploitable.  
→ See: `13_SECURITY.md` Section 4.3

### Worker
A background process that continuously reads from a queue and processes items. In this project: (1) Scraper workers process companies from the `scrape:queue` Redis list; (2) `retry_worker.py` re-dispatches failed notifications from the `notif:retry` Redis sorted set.  
→ See: `05_ARCHITECTURE.md` Section 8, `11_NOTIFICATION_SYSTEM.md` Section 10

---

## D — Data & Database

### Audit Log
A permanent, append-only record of security-relevant events (user registration, login, password changes, admin actions, account deletion). Stored in the `audit_logs` table, retained for 1 year. Used for security incident investigation. Audit logs are never deleted in the normal retention cycle.  
→ See: `13_SECURITY.md` Section 14, `07_DATABASE.md` (audit_logs table)

### JSONB
PostgreSQL's binary JSON column type. Stores arbitrary JSON data efficiently with support for indexing into nested fields. Used in `agent_logs.output_json` (LLM output storage) and `jobs` table for raw scraped data that doesn't fit the fixed schema. Provides document-store flexibility within a relational database.  
→ See: `07_DATABASE.md` Section 16, `18_DECISIONS.md` D-DB-001

### Migration
An Alembic-managed database schema change. Every addition of a table, column, index, or constraint is expressed as a migration file with an `upgrade()` function (apply the change) and a `downgrade()` function (reverse it). Applied sequentially by `alembic upgrade head`. Never bypass with direct SQL in production.  
→ See: `07_DATABASE.md` Section 27, `14_DEPLOYMENT.md` Section 6

### ORM (Object-Relational Mapper)
Software that translates between Python objects and database rows. SQLAlchemy is the ORM used here — Python classes in `backend/models/` map to database tables; queries are written as Python method chains rather than raw SQL strings, which prevents SQL injection and provides type safety.  
→ See: `06_TECH_STACK.md`, `backend/models/`

### PgBouncer
A PostgreSQL connection pooler. Sits between the application and the database, maintaining a pool of database connections that multiple application workers share. Introduced when the number of API replicas grows beyond 3, preventing the application from exhausting PostgreSQL's connection limit.  
→ See: `14_DEPLOYMENT.md` Section 12.3

### Retention Policy
Rules defining how long different categories of data are kept before being automatically deleted. Job Finder AI retains: audit logs for 1 year, operational logs (scrape_runs, agent_logs, notification_logs) for 90 days, and admin alert logs for 30 days. User data is retained until account deletion.  
→ See: `07_DATABASE.md` Section 25

### Soft Delete
Marking a record as deleted (`is_deleted = true`) without physically removing it from the database. Gives a grace period during which the deletion can be cancelled. After the grace period (30 days for user accounts), a scheduled job performs the hard delete (physical removal).  
→ See: `03_FEATURES.md` F-AUTH-05, `13_SECURITY.md` Section 18.2

### Hard Delete
Physical removal of a database record. Triggered for user accounts after the 30-day soft-delete grace period. For users: deletes the `users` row, all related profile tables, and the resume PDF from object storage; anonymizes `notification_logs` (sets `user_id = NULL`).  
→ See: `03_FEATURES.md` F-AUTH-05, `07_DATABASE.md` Section 25

### TSVector
PostgreSQL's text search data type. Stores a preprocessed, tokenized representation of text optimized for full-text search. The `jobs.search_vector` column is a `TSVECTOR` automatically populated by a database trigger whenever a job's title or description changes. Queried via `@@` operator and indexed with GIN.  
→ See: `07_DATABASE.md` Section 16, `03_FEATURES.md` F-JOBS-02

---

## F — Frontend Technologies

### App Router
Next.js's file-based routing system introduced in Next.js 13+. Routes are defined by the file structure under `frontend/app/`. Supports React Server Components (render on server, no client JS), Client Components (`"use client"` directive, run in browser), and nested layouts via `layout.tsx` files.  
→ See: `12_FRONTEND.md` Section 1, `06_TECH_STACK.md`

### NextAuth.js
Authentication library for Next.js that handles the Google OAuth flow (state parameter, authorization code exchange, token management) on the frontend side. Not used for email/password — that's a custom implementation on the FastAPI backend. Manages the session between the Next.js frontend and the backend JWTs.  
→ See: `12_FRONTEND.md` Section 8, `18_DECISIONS.md` D-TECH-009

### React Query (TanStack Query)
Data fetching and server-state management library for React. Provides: automatic caching with configurable stale time, background refetching, infinite scroll pagination (`useInfiniteQuery`), mutation handling with cache invalidation, and loading/error states. Replaces the need for a separate global state management library (Redux) for server-derived state.  
→ See: `12_FRONTEND.md` Sections 5–6, `18_DECISIONS.md` D-TECH-008

### Server Component
A React component that renders on the server. No JavaScript is sent to the browser for these components — only HTML. Used for page shells, static content, metadata, and data fetching that doesn't require interactivity. The default in Next.js App Router.  
→ See: `12_FRONTEND.md` Section 1

### Client Component
A React component marked with `"use client"` that runs in the browser. Required for anything with `useState`, `useEffect`, event handlers, browser APIs, or React Query hooks. Should be as small and leaf-like as possible to minimize client bundle size.  
→ See: `12_FRONTEND.md` Section 1

### shadcn/ui
A component system where components are copied directly into the codebase (not installed as an npm package). Built on Radix UI primitives (accessible by default) and styled with Tailwind CSS. Because we own the component code, we can customize freely without fighting a theming system.  
→ See: `12_FRONTEND.md` Section 4, `18_DECISIONS.md` D-TECH-007

### Skeleton Loading State
A placeholder UI shown while data is loading, shaped to match the layout of the content it will replace. Prevents Cumulative Layout Shift (CLS) — the page doesn't jump when content loads because the skeleton holds the exact same space. Used on the jobs feed and job detail page.  
→ See: `12_FRONTEND.md` Section 11, `components/jobs/FeedSkeleton.tsx`

### SSR (Server-Side Rendering)
Rendering a web page's HTML on the server before sending it to the browser. Used for public job listing pages (`/jobs`, `/jobs/{id}`) so that search engines can index the content. Without SSR, Google would see a blank page (JavaScript-rendered) and the site would rank poorly for job-related searches.  
→ See: `12_FRONTEND.md` Section 1, `18_DECISIONS.md` D-TECH-006

---

## H — HTTP & Web

### CORS (Cross-Origin Resource Sharing)
A browser security mechanism that restricts which websites can make HTTP requests to an API from JavaScript. The FastAPI backend is configured to only allow requests from the production frontend origin (`jobfinderai.com`) — not from any other domain. `allow_origins=["*"]` is never used in production.  
→ See: `13_SECURITY.md` Section 10

### CSRF (Cross-Site Request Forgery)
An attack where a malicious website tricks a user's browser into making an authenticated request to a legitimate site. Mitigated by: (1) `SameSite=Strict` on refresh token cookies — browsers don't send them on cross-site requests; (2) OAuth state parameter for Google OAuth flow — a unique random value prevents CSRF on the callback.  
→ See: `13_SECURITY.md` Section 5

### httpOnly Cookie
A browser cookie that cannot be accessed by JavaScript — only sent automatically by the browser on HTTP requests to the matching domain. The refresh token is stored as an httpOnly cookie, making it immune to XSS attacks that try to steal tokens from JavaScript-accessible storage like `localStorage`.  
→ See: `13_SECURITY.md` Section 4.2, `18_DECISIONS.md` D-SEC-002

### JWT (JSON Web Token)
A compact, self-contained token format for transmitting information securely between parties as a JSON object. Used here as the access token: encodes `user_id`, `role`, `exp` (expiry), and `type`. Signed with HMAC-SHA256 (HS256) — the server can verify it was issued by itself without a database lookup.  
→ See: `13_SECURITY.md` Section 4.1, `08_API.md` (auth endpoints)

### Rate Limiting
Restricting how many requests a client can make to an endpoint within a time window. Implemented with a Redis sliding-window counter per IP (unauthenticated) or per user (authenticated). Auth endpoints have strict limits (5 requests/minute) to prevent brute-force attacks. Scraper requests to external sites are rate-limited to 1 request/3 seconds per domain.  
→ See: `13_SECURITY.md` Section 8, `09_SCRAPER.md` Section 15

### SameSite=Strict
A cookie attribute that tells the browser not to send the cookie on any cross-site request. The most restrictive setting — the cookie is only sent when the user navigates within the same site. Used on the refresh token cookie to prevent CSRF attacks.  
→ See: `13_SECURITY.md` Section 4.2

### Signed URL
A URL that includes a cryptographic signature granting temporary access to a private resource. Used for resume PDF uploads and downloads — the file itself is in a private Cloudflare R2 bucket with no public access, but the signed URL allows the specific action (upload or download) for a short window (5 minutes).  
→ See: `13_SECURITY.md` Section 13.2, `13_SECURITY.md` Section 13.3

### TTL (Time To Live)
The duration after which a cached value or token expires and must be refreshed or revalidated. Examples: access token TTL = 15 minutes; Redis job feed cache TTL = 2 minutes; Redis skill search cache TTL = 1 hour; Telegram link code TTL = 10 minutes.  
→ See: `13_SECURITY.md` Section 4, `09_SCRAPER.md` Section 15

### Webhook
An HTTP callback — instead of polling an API repeatedly ("is there anything new?"), a webhook registers a URL and the external service calls that URL when something happens. Used for: (1) Telegram bot receiving updates (Telegram calls `POST /api/webhooks/telegram` for every message or button press); (2) CI/CD deployment triggers.  
→ See: `11_NOTIFICATION_SYSTEM.md` Section 15, `18_DECISIONS.md` D-ARCH-001

### XSS (Cross-Site Scripting)
An attack where malicious JavaScript is injected into a web page and executed in a victim's browser. Mitigated by: React's built-in content escaping (JSX variables are auto-escaped), strict Content Security Policy headers, bleach-based sanitization of job description HTML before rendering, and storing access tokens in memory (not `localStorage`).  
→ See: `13_SECURITY.md` Section 6

---

## I — Infrastructure & Hosting

### Bucket
Object storage container. The `jobfinderai-resumes` bucket on Cloudflare R2 holds all resume PDFs. Configured as private (no public access). Files are accessed only via time-limited signed URLs generated by the backend.  
→ See: `13_SECURITY.md` Section 13, `06_TECH_STACK.md`

### Cloudflare R2
S3-compatible object storage by Cloudflare. Used for resume PDF storage. Key advantage over AWS S3: no egress fees (data transfer out is free). Uses the standard S3 API, so existing S3 client libraries work without modification.  
→ See: `06_TECH_STACK.md`, `18_DECISIONS.md` D-TECH-010

### Cron
A time-based job scheduler. In this project, APScheduler runs cron-style jobs: the scrape batch fires every 15 minutes, the daily digest fires at 8 AM IST, and the deadline reminder fires at 9 AM IST. Named after the Unix `cron` daemon.  
→ See: `05_ARCHITECTURE.md` Section 5, `scheduler/main.py`

### Egress
Data transferred out of a cloud provider's network. Cloud providers often charge for egress. Cloudflare R2 was chosen over AWS S3 partly because R2 has no egress fees — resumés downloaded by users don't incur per-byte transfer costs.  
→ See: `18_DECISIONS.md` D-TECH-010

### Railway
Cloud platform-as-a-service used for hosting the FastAPI backend and APScheduler process. Provides Docker-based deployments, managed PostgreSQL/Redis add-ons, environment variable management, and webhook-based deployment triggers. Used instead of raw AWS because it requires no DevOps expertise to operate.  
→ See: `14_DEPLOYMENT.md` Section 1, `18_DECISIONS.md` D-TECH-015

### Resend
Transactional email service used for all outbound emails (welcome emails, verification emails, daily digests, deadline reminders). Provides a simple HTTP API, good deliverability, and a generous free tier for MVP-scale email volume.  
→ See: `06_TECH_STACK.md`, `18_DECISIONS.md` D-TECH-011

### RPO (Recovery Point Objective)
The maximum acceptable amount of data loss in a disaster scenario, measured in time. Job Finder AI's RPO is 24 hours — in the worst case, we lose up to one day of new data (jobs scraped, notifications sent, profile changes) but recover everything else from the daily database backup.  
→ See: `14_DEPLOYMENT.md` Section 10

### RTO (Recovery Time Objective)
The maximum acceptable downtime after a disaster before the system is restored to operation. Job Finder AI's RTO is 4 hours — the system should be back online within 4 hours of a catastrophic failure. Appropriate for an MVP-stage product that is not life-critical infrastructure.  
→ See: `14_DEPLOYMENT.md` Section 10

### Supabase
Managed PostgreSQL hosting provider. Provides automated daily backups, point-in-time recovery, and a web console for database management. Used as an alternative to self-managing a PostgreSQL instance on a VPS.  
→ See: `14_DEPLOYMENT.md` Section 1

### Upstash
Managed Redis hosting provider with a serverless pricing model. Used for the platform's Redis instance (caching, queues, rate limiting). Free tier sufficient for MVP-scale usage; paid tiers available as usage grows.  
→ See: `14_DEPLOYMENT.md` Section 1, `05_ARCHITECTURE.md` Section 9

### Vercel
Cloud platform for hosting Next.js applications. Built by the creators of Next.js — provides first-party support for all App Router features, automatic preview deployments for every PR, and a global CDN edge network that improves page load times.  
→ See: `14_DEPLOYMENT.md` Section 1, `18_DECISIONS.md` D-INFRA-002

---

## L — LLM & AI

### Anthropic Claude
LLM (large language model) by Anthropic. Used as the fallback provider when OpenAI's API is unavailable or rate-limited. The specific model used is `claude-sonnet-4-6`. The `BaseAgent` abstraction makes it a drop-in replacement for OpenAI with no changes to agent logic.  
→ See: `10_AI_AGENTS.md` Section 11, `18_DECISIONS.md` D-TECH-012

### GPT-4o
OpenAI's primary LLM model, used for the three highest-stakes agents: Job Extractor, Skill Extractor, and JD Summarizer. More capable than GPT-4o-mini for nuanced language understanding tasks where output quality directly affects user experience.  
→ See: `10_AI_AGENTS.md` Section 1, `18_DECISIONS.md` D-AGENT-003

### GPT-4o-mini
OpenAI's faster, cheaper LLM model. Used for classification and generation tasks (Job Classifier, Notification Generator) where the task is more bounded and cheaper generation is appropriate. Approximately 10–100x cheaper per token than GPT-4o.  
→ See: `10_AI_AGENTS.md` Section 1, `18_DECISIONS.md` D-AGENT-003

### LLM (Large Language Model)
An AI system trained on large amounts of text data, capable of generating and understanding human language. GPT-4o and Claude are LLMs. In this project, LLMs are called via API (not self-hosted) and always produce structured JSON output — never free text that goes directly into the database.  
→ See: `10_AI_AGENTS.md`

### Prompt
The text input sent to an LLM to instruct it on what to produce. All prompts in this project are versioned in `docs/20_PROMPTS.md` and loaded by agents at runtime — never hardcoded in Python files. Prompts include: the task description, input data, output schema, and numbered rules addressing known failure modes.  
→ See: `20_PROMPTS.md`, `18_DECISIONS.md` D-AGENT-001

### Prompt Version
A string identifier for a specific version of a prompt (e.g., `extractor_v1`, `summarizer_v2`). Stored in `agent_logs.prompt_version` for every LLM call, enabling retrospective analysis of which prompt version produced which output. Incrementing the version number when a prompt changes is mandatory.  
→ See: `20_PROMPTS.md`, `10_AI_AGENTS.md` Section 14

### Structured Output / JSON Mode
An LLM API feature that constrains the model to return valid JSON. Enabled via `response_format: {"type": "json_object"}` in OpenAI's API. Reduces (but does not eliminate) parse failures. The `BaseAgent.parse_output()` method validates the JSON against the expected schema after receiving it.  
→ See: `10_AI_AGENTS.md` Section 2, `18_DECISIONS.md` D-AGENT-002

### Temperature
A parameter (0.0–1.0) that controls the randomness of LLM output. Lower temperature = more deterministic and consistent output. All extraction and classification agents use temperature 0.1 (very consistent). The Notification Generator uses 0.2 (slightly more natural language variation).  
→ See: `20_PROMPTS.md` Section "Prompt Design Principles"

---

## M — Metrics & Business

### Churn
The percentage of users who stop using the platform in a given period. Monthly churn < 5% is the Phase 2 target. High churn indicates the product is not delivering enough value to keep users coming back.  
→ See: `01_PRD.md` Section 8, `16_ROADMAP.md` Section 3

### DAU (Daily Active Users)
The number of unique users who interact with the platform on a given day. Less relevant than WAU for a job alert platform (users may check weekly, not daily), but monitored as a supplementary metric.  
→ See: `01_PRD.md` Section 15

### MRR (Monthly Recurring Revenue)
The predictable revenue generated each month from subscriptions. Phase 4 target: MRR ≥ $1,000. Used to measure the health and growth of the recruiter subscription business.  
→ See: `01_PRD.md` Section 15, `16_ROADMAP.md` Section 5

### NPS (Net Promoter Score)
A measure of customer satisfaction: "How likely are you to recommend this to a friend?" (0–10). Score above 50 is considered excellent. Measured quarterly via in-app survey. Student experience NPS must not decrease when recruiter features are introduced.  
→ See: `16_ROADMAP.md` Section 5

### SLA (Service Level Agreement)
A commitment about system performance. The primary SLA for Job Finder AI: jobs posted on a company career page must result in a matched student notification within 30 minutes. All architectural decisions (scheduler interval, pipeline latency budgets) are designed to uphold this SLA.  
→ See: `01_PRD.md` NFR-PERF-03, `10_AI_AGENTS.md` Section 1

### WAU (Weekly Active Users)
The number of unique users who receive or interact with the platform in a given week. The primary growth metric for Job Finder AI. Phase 2 target: WAU ≥ 300. Phase 3 target: WAU ≥ 2,000.  
→ See: `01_PRD.md` Section 15, `16_ROADMAP.md`

---

## N — Notifications

### Daily Digest
An email sent once per day (8 AM user local time) summarizing all matched jobs from the past 24 hours. Limited to the top 10 matches per user. Not sent if the user has 0 matches (no empty emails). Preferred by users like Priya who want to batch-process job applications rather than receive real-time interruptions.  
→ See: `03_FEATURES.md` F-NOTIF-03, `11_NOTIFICATION_SYSTEM.md` Section 7

### Dispatch
The act of sending a notification to a user via a specific channel (Telegram or email). The notification dispatcher (`notifications/telegram/dispatcher.py`) handles the actual API call, exception handling, retry queuing, and delivery logging for each individual notification.  
→ See: `11_NOTIFICATION_SYSTEM.md` Section 5

### Exact Match Mode
A Telegram notification frequency setting where alerts are only sent when the job matches all three of the user's primary preference types simultaneously (role type + location + experience level). For users like Sneha who want very few, very relevant notifications rather than more frequent partial matches.  
→ See: `03_FEATURES.md` F-PROF-03, `11_NOTIFICATION_SYSTEM.md` Section 3

### Notification Router
The single decision point (`notifications/router.py`) that determines: which channels to use for a notification, whether to send now or queue for after quiet hours, and whether the user has already been notified about this job. All channel selection logic lives here and nowhere else.  
→ See: `11_NOTIFICATION_SYSTEM.md` Section 3

### Quiet Hours
A user-configurable time window during which no notifications are sent. Notifications that would have been sent during quiet hours are held in a Redis delayed queue and dispatched after the quiet hours window closes. They are never dropped, only deferred.  
→ See: `03_FEATURES.md` F-PROF-03, `11_NOTIFICATION_SYSTEM.md` Section 13

### Weekly Summary
An email sent every Monday summarizing the top 10 matched jobs from the past 7 days. Designed for users who prefer to review opportunities on a weekly rather than daily cadence. Phase 2 feature.  
→ See: `03_FEATURES.md` F-NOTIF-03, `11_NOTIFICATION_SYSTEM.md` Section 7

---

## P — Product & Platform

### ATS (Applicant Tracking System)
Software used by companies to manage job postings and applications. Examples: Workday, Greenhouse, Lever, iCIMS, Taleo. Each ATS has a different URL structure, HTML layout, and data format — hence the need for adapter-specific scraper modules for each one.  
→ See: `09_SCRAPER.md`, `03_FEATURES.md` F-SCRP-01 through F-SCRP-05

### ATS Portal
A web interface powered by an ATS where candidates apply to jobs. Distinct from the company's main career page (which may link to the ATS portal). The company's career page URL is what the scraper starts from; the ATS portal is what it ultimately interacts with to fetch job listings.  
→ See: `09_SCRAPER.md` Section 3

### Career Page
The section of a company's website listing their open job positions. Often hosted on the company's own domain but powered by a third-party ATS (e.g., `careers.razorpay.com` powered by Greenhouse). The scraper starts at the career page URL and uses the ATS detector to determine which adapter to use.  
→ See: `09_SCRAPER.md` Section 3, `03_FEATURES.md` F-SCRP-01

### Experience Level
A classification of how many years of professional experience a job requires. Taxonomy used throughout the platform: `fresher` (0 years), `0-1yr`, `1-2yr`, `2-3yr`, `3-5yr`, `5+yr`. Used in user preferences (what they're qualified for), job classification (what the role requires), and matching (pairing users to appropriate jobs).  
→ See: `07_DATABASE.md` Section 10, `10_AI_AGENTS.md` Section 7

### JD (Job Description)
The full text of a job posting describing the role, responsibilities, requirements, and application process. The raw JD is fetched by the scraper, processed by the Job Extractor, Skill Extractor, and JD Summarizer agents, then stored in `jobs.raw_description`.  
→ See: `09_SCRAPER.md` Section 14, `10_AI_AGENTS.md`

### Job Board
A website that aggregates job listings from multiple companies (e.g., LinkedIn Jobs, Naukri, Indeed). Distinct from an ATS — job boards receive listings after companies post them, typically with a 12–72 hour delay. Job Finder AI bypasses job boards by scraping ATS portals directly.  
→ See: `01_PRD.md` Section 3.1

### Role Type
A classification of the job's function area. The platform uses a fixed 16-value taxonomy: `software_engineer`, `data_analyst`, `product_manager`, etc. Stored in the `role_types` table, used in user preferences (what roles they want), job classification (what the job is), and matching.  
→ See: `07_DATABASE.md` Section 8, `10_AI_AGENTS.md` Section 7

---

## S — Scraping

### ATS Auto-Detector
The module (`scrapers/ats_detector.py`) that identifies which ATS a career page uses before selecting an adapter. Runs three stages in order: URL pattern matching, HTML signature matching, API probing. Returns an ATS type string or "generic" if unrecognized.  
→ See: `09_SCRAPER.md` Section 3, `03_FEATURES.md` F-SCRP-01

### Scrape Run
A single execution of a scraper adapter against one company's career page. Recorded in the `scrape_runs` table with: company, start/end time, status (success/partial/failed), jobs found, jobs new, error message, and duration. The primary data source for the admin scraper health dashboard.  
→ See: `07_DATABASE.md` Section 18, `03_FEATURES.md` F-SCRP-04

### Rate Limiting (scraper)
The scraper-side enforcement that limits how many HTTP requests we send to any one domain per unit time. Maximum 1 request per 3 seconds per domain, implemented with a Redis token bucket per domain. Protects target sites from being overloaded and reduces the risk of IP bans.  
→ See: `09_SCRAPER.md` Section 15, `03_FEATURES.md` F-SCRP-05

### robots.txt
A file at `{domain}/robots.txt` that specifies which parts of a website automated crawlers are allowed to access. All scrapers check and respect this file before fetching any page. Disallowed paths are logged and skipped — not bypassed. This is a legal and ethical requirement, not just a technical courtesy.  
→ See: `09_SCRAPER.md` Section 18, `03_FEATURES.md` F-SCRP-05

---

## T — Auth & Security

### Grace Period
The window between a soft delete and a hard delete, during which the action can be reversed. Job Finder AI's account deletion grace period is 30 days — a user who initiates account deletion has 30 days to cancel before their data is permanently removed.  
→ See: `03_FEATURES.md` F-AUTH-05, `13_SECURITY.md` Section 18.2

### HS256
HMAC-SHA256 — the JWT signing algorithm used for access tokens. A symmetric algorithm: the server uses the same secret key to both sign and verify tokens. Simple and fast. Appropriate when only the server needs to verify tokens (not third parties). The secret key is a 256-bit random value stored as an environment variable.  
→ See: `13_SECURITY.md` Section 4.1

### PII (Personally Identifiable Information)
Any data that can be used to identify a specific individual. In this project: email addresses, names, Telegram IDs, resume content. PII collection is minimized (we only store what's needed for the service), protected (encrypted connections, access controls), and deletable on request (GDPR compliance).  
→ See: `13_SECURITY.md` Section 18, `01_PRD.md` Section 14

### RBAC (Role-Based Access Control)
An authorization model where permissions are assigned to roles rather than individual users. Job Finder AI has two roles: `student` (standard user) and `admin` (platform operator). Role is stored in `users.role` and enforced server-side on every admin endpoint via the `require_admin()` FastAPI dependency.  
→ See: `13_SECURITY.md` Section 3, `08_API.md`

---

## U — Users & Roles

### Admin
A platform operator with access to the admin dashboard. Can: view scraper health, add/remove companies, approve/reject flagged jobs, view and manage user accounts, trigger manual scrapes, and receive Telegram alerts on scraper failures. Assigned via `users.role = 'admin'` — there is no public sign-up for admin accounts.  
→ See: `02_USER_PERSONAS.md` Persona 5, `03_FEATURES.md` F-ADMN-*

### Fresher
A job seeker with 0–2 years of professional experience. One of the two primary user types for Job Finder AI. Distinct from a "student" in that a fresher has already graduated and may have some work experience, whereas a student is still in their final year of study.  
→ See: `02_USER_PERSONAS.md`, `01_PRD.md` Section 6

### Placement Officer
A college staff member responsible for managing campus placements. A future user type (Phase 3) who will have a dashboard showing job matches for their specific college batch and the ability to send batch notifications to students.  
→ See: `16_ROADMAP.md` Section 4

### Recruiter
A hiring manager or HR professional at a company who wants to reach student candidates. A future user type (Phase 4) who will post jobs directly and access anonymized match statistics. Never has access to individual student PII without explicit student opt-in.  
→ See: `02_USER_PERSONAS.md` Persona 6, `16_ROADMAP.md` Section 5

### Student
A college student (typically final year) actively searching for their first job or internship. The primary user of Job Finder AI in MVP. Sets up a profile with skills and preferences, connects Telegram, and receives matched job alerts.  
→ See: `02_USER_PERSONAS.md` Persona 1, `01_PRD.md` Section 6

---

*Terms are added here when they first appear in the project's documentation or codebase. If you encounter a term not listed here, add it — the glossary is only useful if it's complete.*
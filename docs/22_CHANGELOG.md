# 22 — Changelog

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Engineering Lead  

---

## Purpose of This Document

This is the running history of every significant change to Job Finder AI — architecture changes, documentation updates, prompt iterations, schema migrations, feature additions, and bug fixes. It answers the question: *"What changed, when, and why?"*

This changelog is not a git log. It is a human-readable narrative of decisions and changes that matter to engineers, operators, and AI assistants working on the project. Git provides the full code diff; this document provides the context.

---

## Format Convention

Each entry follows this structure:

```
## [version] — YYYY-MM-DD

### Added
- New features, files, endpoints, agents, adapters

### Changed
- Modifications to existing behaviour, prompts, schemas, configurations

### Fixed
- Bug fixes, edge case corrections

### Deprecated
- Items that will be removed in a future version

### Removed
- Items deleted from the codebase or documentation

### Security
- Security-relevant changes

### Decisions
- Links to new entries in 18_DECISIONS.md
```

Only sections that apply to a given release are included. Empty sections are omitted.

---

## Version Numbering

```
v{major}.{minor}.{patch}

Major  : Breaking changes — schema migrations that require downtime,
         API changes that break existing clients, complete feature rewrites
Minor  : New features, new endpoints, new agents, new adapters
Patch  : Bug fixes, performance improvements, documentation updates,
         prompt iterations, configuration changes
```

Pre-launch versions use `v0.x.x`. The first production launch is `v1.0.0`.

---

## [Unreleased]

Changes that are documented or planned but not yet deployed to production.

### Added
- Full documentation suite (docs/00 through docs/22, AI_RULES.md, .openspec/)
- Initial project structure scaffolding
- Created `backend/core/logging.py` containing a structured JSON log formatter, sensitive field redaction filter, and request trace correlation ID.
- Created `/health` endpoint checking both database and Redis connectivity.
- Initialized Next.js App Router frontend application with TypeScript, Tailwind CSS, and ESLint configs.
- Integrated `shadcn/ui` (using `@base-ui/react` v4 presets) into the Next.js frontend application.
- Added and configured required primitive UI components: Button, Badge, Card, Dialog, Input, Select, Tabs, Skeleton, Sheet, Label, and DropdownMenu.
- Created custom offline-capable `Toast`, `Toaster` and `useToast` notification helper hook supporting variants, descriptions, and auto-dismissal.
- Configured HSL color design tokens and custom theme properties in `frontend/app/globals.css` for light and dark modes.
- Created `frontend/types/index.ts` with standard TypeScript interfaces mirroring backend schemas.
- Created `frontend/lib/auth.ts` implementing XSS-secure in-memory token storage.
- Created `frontend/lib/api.ts` exposing domain-grouped API functions with auto-refresh JWT interceptors.
- Implemented core utility helpers in `frontend/lib/utils.ts` for relative timestamp formatting (`formatPostedAt`), absolute date formatting (`formatDate`), accessibility animation gating (`getMotionPreference`), and active query filter identification (`hasActiveFilters`).
- Created `frontend/middleware.ts` for global Next.js route protection, managing auth state redirects and handling unauthenticated routes transparently.
- Initialized Alembic database migration environment in the backend and configured script location to `database/migrations/`.
- Created the declarative SQLAlchemy `User` model in `backend/models/user.py` representing the core identity table.
- Created the Alembic migration script for the `users` table, including custom `user_role` PostgreSQL enum type and partial unique indexes.
- Created the declarative SQLAlchemy `RefreshToken` model in `backend/models/token.py` and established a back-populating relationship on `User`.
- Created the Alembic migration script for the `refresh_tokens` table, establishing foreign key cascading delete constraints and indexes on `user_id` and `expires_at`.
- Created the declarative SQLAlchemy `EmailVerificationToken` model in `backend/models/token.py` and established a back-populating relationship on `User`.
- Created the Alembic migration script for the `email_verification_tokens` table, establishing foreign key constraints and a unique index on the verification token.
- Created the declarative SQLAlchemy `PasswordResetToken` model in `backend/models/token.py` and established a back-populating relationship on `User`.
- Created the Alembic migration script for the `password_reset_tokens` table, establishing foreign key constraints and an index on `user_id`.
- Created the declarative SQLAlchemy `AuditLog` model in `backend/models/audit_log.py` and established a back-populating relationship on `User`.
- Created the Alembic migration script for the `audit_logs` table, establishing INET/JSONB fields, foreign key constraints with `SET NULL` on delete, and performance indexes including a descending index on `created_at`.
- Implemented `backend/core/security.py` covering bcrypt password hashing (cost=12), timing-safe verify, HS256 JWT access tokens with 15-minute expiration, 64-byte secure refresh tokens, and HttpOnly/SameSite session cookies scoped to `/api/auth`.
- Implemented `backend/middleware/auth_middleware.py` exposing `get_current_user` and `require_admin` FastAPI dependencies for backend route auth and role gating.
- Implemented `POST /api/auth/register` in `backend/api/auth.py` validating registration requests, checking for database email conflicts, hashing credentials, generating verification tokens, and dispatching verification emails.
- Added global exception handlers in `backend/main.py` converting Pydantic validation errors (422) into standard 400 validation error payloads.
- Created `backend/schemas/auth_schemas.py` defining registration validation schema matching security policies.
- Added the Daniel Miessler SecLists top 10,000 common passwords file under `backend/data/common_passwords.txt`.
- Created provider-agnostic wrapper `notifications/email/client.py` using the Resend service.
- Added `resend` package to `backend/requirements.txt`.
- Implemented `POST /api/auth/resend-verification` endpoint in `backend/api/auth.py` with Redis-based email rate limiting (3 requests/hour/email) and email enumeration protection.
- Created the `ResendVerificationRequest` validation schema in `backend/schemas/auth_schemas.py`.
- Implemented Google OAuth initiation (`GET /api/auth/oauth/google`) and callback verification (`GET /api/auth/oauth/google/callback`) routes in `backend/api/auth.py` with Redis-based CSRF state verification and auto-linking/creation of active user profiles.
- Added `httpx` package to `backend/requirements.txt`.
- Implemented `POST /api/auth/login` endpoint in `backend/api/auth.py` verifying credentials safely, enforcing timing-safe dummy validations for nonexistent profiles, tracking 15-minute email-based locks (10 failures max) via Redis, and delivering JWT tokens and secure HttpOnly refresh cookies.
- Added `LoginRequest` validation schema in `backend/schemas/auth_schemas.py`.
- Implemented `POST /api/auth/refresh` endpoint in `backend/api/auth.py` enabling refresh token rotation, tracking token reuse/replay attacks via the `revoked_at` column, revoking all active user sessions upon breach, and returning rotated credentials.
- Implemented `POST /api/auth/logout` endpoint in `backend/api/auth.py` protected by the `get_current_user` dependency, revoking the session refresh token from the database, and erasing the client browser cookie.
- Implemented `POST /api/auth/forgot-password` endpoint in `backend/api/auth.py` with Redis-based rate limiting (3 requests/hour/email) and prevention of email enumeration.
- Added `ForgotPasswordRequest` validation schema in `backend/schemas/auth_schemas.py`.


### Changed
- Configured FastAPI application startup in `backend/main.py` to initialize JSON logging via `setup_logging()`.
- Refactored `backend/models/audit_log.py`'s `metadata` attribute to `event_metadata` mapped to the database column `"metadata"` to prevent SQLAlchemy reserved keyword conflicts.
- Refactored `backend/middleware/logging_middleware.py` to route trace ID context lifecycle through the new `core.logging` module.
- Added `pydantic-settings` to `backend/requirements.txt` to enable structured configuration parsing.
- Registered `health` router on the FastAPI application in `backend/main.py` and removed the temporary mock health handler.
- Configured standalone build output (`output: "standalone"`) in `next.config.ts` for optimized production Docker images.

---

## v0.1.0 — 2025-06-22

**Theme:** Documentation foundation. All 22 documentation files written before a single line of application code. This is intentional — docs are the spec, code implements the spec.

### Added

**Documentation Suite**
- `00_PROJECT_OVERVIEW.md` — Vision, mission, problem statement, high-level architecture, success metrics, repo structure, documentation map
- `01_PRD.md` — Full 20-page PRD covering executive summary, vision, problem statement, existing solutions analysis, competitor analysis, target users, functional requirements (60+ items), non-functional requirements, user stories (22 student + 5 admin), MVP scope, future scope, risks, assumptions, constraints, KPIs
- `02_USER_PERSONAS.md` — 6 detailed personas: Aarav (final-year CS student), Priya (MBA fresher), Rahul (self-taught developer), Sneha (1.5 YOE developer switching companies), Karan (internal admin), Divya (recruiter — Phase 3)
- `03_FEATURES.md` — 35 features fully specced across 8 modules with Purpose, Workflow, Database schema, API signatures, Frontend/Backend implementation, Edge Cases table, and Acceptance Criteria checklist per feature
- `04_USER_FLOWS.md` — 17 user flows with Mermaid diagrams: onboarding, OAuth login, Telegram connection (sequence diagram), full discovery pipeline (the most detailed — scheduler to notification), Telegram alert interaction, jobs feed browsing, email digest, save/track lifecycle (state diagram), deadline reminder, resume upload, notification preferences, password reset, account deletion, admin add company, admin failure detection, admin review queue, admin user suspension
- `05_ARCHITECTURE.md` — Full system architecture with 12 Mermaid diagrams: system context, backend layered structure, request lifecycle sequence, frontend data flow, ER diagram overview, scheduler Gantt timeline, agent pipeline, notification dispatch, Redis usage map, production topology, CI/CD pipeline, monitoring surfaces
- `06_TECH_STACK.md` — 21 technology entries, each with Reason for Choice, Alternatives Considered (with Pro/Con), Pros, Cons. Technologies: Next.js, Tailwind, shadcn/ui, React Query, NextAuth.js, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, Cloudflare R2, APScheduler, httpx, Playwright, OpenAI, Anthropic, python-telegram-bot, Resend/SendGrid, Docker, GitHub Actions, Railway/Render, Vercel
- `07_DATABASE.md` — 22 tables fully specced: complete `CREATE TABLE` SQL, all indexes, relationships, constraints, sample queries, retention policy, and notes per table. Plus: full ER diagram (Mermaid), retention policy summary table, backup strategy (RPO/RTO), migration strategy rules, and 3 common query patterns including the core matching query
- `08_API.md` — 44 endpoints across 7 groups (Auth, Profile, Jobs, Saved Jobs, Telegram, Admin, System), each with: purpose, request body, validation rules per field, full response JSON, errors table (status + code + condition), auth level, rate limit, and examples. Plus: conventions reference, error code table (25 codes), and auth flow Mermaid diagram
- `09_SCRAPER.md` — Complete scraper knowledge base: BaseScraper class, ATS Auto-Detector (3-stage algorithm with full detection signature tables), 6 Phase 1 adapters (Workday, Greenhouse, Lever, iCIMS, Taleo, Generic) each with detection method, extraction logic, pagination strategy, output JSON example, rate limits, common failure cases. 3 Phase 2 adapter stubs (SmartRecruiters, BreezyHR, Ashby). Scrape runner orchestration, standard output schema, rate limiting strategy, retry/backoff strategy, CAPTCHA handling, robots.txt compliance, debugging decision tree, new adapter checklist
- `10_AI_AGENTS.md` — 8 agents fully documented: BaseAgent (Python implementation), Duplicate Detector (hash algorithm + normalization), Job Extractor (merge rules, truncation, failure handling), Skill Extractor (canonicalization + `degree_required` field), JD Summarizer (quality rules + output validation), Job Classifier (full taxonomy), Notification Generator (static fallback), Resume Extractor (Phase 2), Match Score Calculator (Phase 3, deterministic). Plus: LLM provider config, caching strategy (with TTL table), cost model (per-agent token budget + monthly projection), agent logging, failure handling flowchart, new agent checklist
- `11_NOTIFICATION_SYSTEM.md` — Complete notification system: system overview flowchart, module structure, notification router (decision table + code), matching service (SQL query + performance analysis), Telegram channel (bot setup, dispatcher with exception handling, rate limits), email channel (provider-agnostic client, unsubscribe handling), all 6 notification types, all 6 templates (full text), scheduling + dispatch (digest queue, deadline reminder query), retry logic (sorted-set queue + worker loop), delivery logging (with useful SQL queries), user preference enforcement, quiet hours implementation (overnight range handling), all 6 bot commands with handler code, webhook handler, admin alerts (3 templates + dedup logic), failure debugging flowchart
- `12_FRONTEND.md` — Complete frontend reference: architecture overview (server vs. client component strategy), full directory structure, all 8 pages with rendering strategy and code examples, 8 key components with full TypeScript/JSX implementation (JobCard, JobFeed, FilterBar, SkillMatchChips, SkillPicker, TelegramConnect, PostedLabel, ScraperHealthTable), 6 custom hooks with React Query implementations, state management rules, API client (Axios + interceptors + token memory store), auth (middleware route protection), theme & design tokens (CSS variables for light/dark mode), accessibility requirements (WCAG 2.1 AA), performance targets (Core Web Vitals) + skeleton loading, animation principles + reduced motion, SEO (metadata + JSON-LD + robots.txt + sitemap), TypeScript types (all interfaces), error handling, testing strategy
- `13_SECURITY.md` — Full security reference: threat model (assets + actors + out-of-scope), authentication (bcrypt implementation, password policy validator, OAuth state CSRF, token hashing), authorization + RBAC (role enforcement, ownership → 404 pattern), session management (JWT + refresh token + rotation + reuse detection), CSRF protection, XSS prevention (bleach sanitization + CSP headers), input validation (Pydantic, SQLi prevention, path traversal, mass assignment), rate limiting (sliding-window implementation + table for all endpoints + login lockout), transport security (HSTS + TLS + webhook secret), CORS (environment-aware origin list), secrets management (rotation policy + CI scanning + sensitive field redaction), encryption at rest, object storage security (bucket policy + signed URLs), audit logging (18 event types + schema + SQL queries), dependency security (Dependabot + pip-audit + SRI), LLM security (prompt injection sanitization + structural defense), scraper ethics, GDPR compliance (data minimization table + hard delete procedure + retention table + privacy policy requirements), pre-launch security checklist (32 items), incident response (P0–P3 severity + procedures + credential compromise runbook)
- `14_DEPLOYMENT.md` — Complete deployment reference: production topology diagram (all services + data + external), service responsibilities table, domain configuration, local development setup (prerequisites + first-time setup + common commands + hot reload), Docker config (docker-compose.yml + backend Dockerfile + frontend multi-stage Dockerfile + .dockerignore), environment management (all 35 env variables with descriptions), full CI/CD pipeline (GitHub Actions YAML + 5-job workflow), database migrations (rules + workflow + zero-downtime strategy), service startup order, monitoring & alerting (health check endpoint + UptimeRobot + application-level alerts), logging (JSON format + configuration + log levels + log aggregation + request tracing), backup strategy, rollback procedures (code-only + migration rollback + decision tree), scaling plan (triggers and responses for each component), secrets rotation procedures (4 secrets), release checklist, 6 runbooks (restart service, clear queue backlog, manual scrape trigger, revoke all sessions, disable notifications, DB emergency read-only mode)
- `16_ROADMAP.md` — 5-phase product roadmap with Mermaid Gantt chart spanning 18 months: Phase 1 Foundation (Weeks 1–8), Phase 2 Product Quality (Weeks 9–16), Phase 3 Scale & Intelligence (Weeks 17–28), Phase 4 Revenue (Weeks 29–38), Phase 5 Ecosystem (Month 13+). Each phase has: theme, goal, what gets built (week-by-week for Phase 1), entry criteria, exit criteria checklist, KPIs table. Plus: 5 prioritization principles, explicit "not building" table (9 excluded features with reasons)
- `17_TASKS.md` — 239 specific, actionable tasks organized by phase and domain. Phase 1 (14 domains): Infrastructure, Authentication, Database, Core API, Scraper Pipeline, AI Agent Pipeline, Notification System, Admin Dashboard, Frontend Auth, Frontend Onboarding, Frontend Jobs Feed, Deployment. Phase 2 (8 domains): Application Tracking, Resume Intelligence, Notification Enhancements, More ATS Adapters, Admin Enhancements, Frontend Settings, E2E Testing. Phase 3 (high-level only). Every task has a `**Ref:**` cross-reference to the exact doc section
- `18_DECISIONS.md` — 40 architectural decision records across 8 categories (TECH, ARCH, DB, SEC, AGENT, SCRP, PROD, INFRA). Each record: decision, date, status, deciders, context, alternatives considered with Pro/Con, rationale, tradeoffs accepted, revisit conditions. Includes the major PostgreSQL-over-MongoDB reversal with full explanation
- `19_FILE_EXPLANATIONS.md` — 25 folders and key files explained. Each entry answers: why it exists, what it contains, when it runs, who uses it, common modifications. Covers root directory, all backend modules (main.py, config, api, services, models, schemas, middleware, core), scrapers and adapters, agents, notifications (telegram, email), scheduler, database, frontend (app, components, hooks, lib), tests, scripts
- `20_PROMPTS.md` — 6 versioned LLM prompts: `extractor_v1`, `skill_extractor_v1`, `summarizer_v1`, `classifier_v1`, `notif_generator_v1`, `resume_extractor_v1`. Each prompt: purpose, failure modes addressed, full prompt text, example input/output, version history. Plus: prompt design principles, how prompts are loaded in code, prompt versioning workflow, standard test fixture set
- `21_GLOSSARY.md` — 85+ terms defined across 14 categories: Architecture & System Design, Backend Technologies, Core Concepts, Data & Database, Frontend Technologies, HTTP & Web, Infrastructure & Hosting, LLM & AI, Metrics & Business, Notifications, Product & Platform, Scraping, Auth & Security, Users & Roles
- `22_CHANGELOG.md` — This file

**Architectural Decisions Recorded**
- D-TECH-001 through D-TECH-015 (technology choices)
- D-ARCH-001 through D-ARCH-005 (system design decisions)
- D-DB-001 through D-DB-004 (database decisions, including PostgreSQL-over-MongoDB reversal)
- D-SEC-001 through D-SEC-003 (security decisions)
- D-AGENT-001 through D-AGENT-003 (AI agent decisions)
- D-SCRP-001 through D-SCRP-002 (scraper decisions)
- D-PROD-001 through D-PROD-004 (product decisions)
- D-INFRA-001 through D-INFRA-002 (infrastructure decisions)
- D-API-001 through D-API-002 (API design decisions)

---

## How to Add a New Entry

Every change that matters to the project — not every commit — gets an entry here. Use judgment: a typo fix does not need a changelog entry; a new endpoint does. A prompt update always does (it must be versioned).

### What Warrants a Changelog Entry

| Change Type | Example | Changelog? |
|---|---|---|
| New feature | Added resume upload endpoint | ✅ Yes |
| Schema migration | Added `degree_required` column to `jobs` | ✅ Yes |
| Prompt update | Updated `summarizer_v1` → `summarizer_v2` | ✅ Yes — always |
| New ATS adapter | Added SmartRecruiters adapter | ✅ Yes |
| Bug fix (user-facing) | Fixed duplicate notifications being sent | ✅ Yes |
| Security patch | Rotated JWT secret after exposure | ✅ Yes |
| Architecture change | Moved scraper workers to separate process | ✅ Yes |
| New decision record | Added D-TECH-016 | ✅ Yes — link here |
| Dependency upgrade | Updated FastAPI 0.111 → 0.112 (patch) | ⚠️ Only if breaking |
| Documentation update | Rewrote a glossary entry | ❌ No — docs are self-versioning via git |
| Typo fix | Fixed spelling in a comment | ❌ No |

### Entry Template

```markdown
## [v0.X.Y] — YYYY-MM-DD

**Theme:** One-line description of the release focus

### Added
- [Feature/File] Short description of what was added and why

### Changed  
- [Component] What changed, old behaviour vs. new behaviour

### Fixed
- [Bug] What was broken, what was the root cause, how it was fixed

### Security
- [Control] What security improvement was made

### Decisions
- D-XXX-NNN: Decision title (see `18_DECISIONS.md`)
```

---

## Future Entries Template

When Phase 1 development begins, entries will be added here. Example of what the log will look like once development starts:

---

## [v0.2.0] — TBD

**Theme:** Phase 1 backend foundation — auth, database, core API

### Added
- Complete Alembic migration suite: all 19 tables from `07_DATABASE.md`
- Seed scripts for skills (150+ entries), role types (16), cities (25+), companies (50–100)
- Full authentication API: register, verify-email, login, refresh, logout, OAuth, password reset, account deletion
- JWT access token (15-min TTL) + refresh token (httpOnly cookie, 7-day TTL)
- `GET /api/jobs` and `GET /api/jobs/{id}` endpoints with Redis caching
- `GET/PUT /api/profile/skills`, `GET/PUT /api/profile/preferences`, `GET/PUT /api/profile/notification-preferences`
- `/health` endpoint checking DB + Redis connectivity
- Structured JSON logging with trace_id propagation
- Security headers middleware (CSP, X-Frame-Options, HSTS)
- Rate limiting middleware (sliding window via Redis)

### Decisions
- D-TECH-001: Python over Node.js for backend
- D-DB-001: PostgreSQL over MongoDB (reversal of earlier recommendation)

---

## [v0.3.0] — TBD

**Theme:** Phase 1 scraper pipeline — 5 ATS adapters + AI agent pipeline

### Added
- ATS Auto-Detector: 3-stage fingerprinting (URL patterns, HTML signatures, API probes)
- 5 ATS adapters: Workday, Greenhouse, Lever, iCIMS, Taleo
- Generic HTML fallback adapter (Playwright-based)
- BaseScraper: rate limiting, retry/backoff, robots.txt compliance, CAPTCHA detection, user-agent rotation
- APScheduler with scrape batch job (every 15 minutes)
- 5 AI agents: Duplicate Detector, Job Extractor, Skill Extractor, JD Summarizer, Job Classifier
- BaseAgent: Redis caching by input hash, JSON repair retry, agent logging
- All 5 prompts in `docs/20_PROMPTS.md`: extractor_v1, skill_extractor_v1, summarizer_v1, classifier_v1, notif_generator_v1
- `scrape_runs` logging for admin dashboard

---

## [v0.4.0] — TBD

**Theme:** Phase 1 notification system + Telegram bot + admin dashboard

### Added
- Telegram bot: webhook mode, all 6 commands (/start, /pause, /resume, /settings, /unlink, /help)
- Telegram account linking: UUID code + QR + 10-min TTL + polling
- Notification matching service (4-condition SQL query)
- Notification router (channel selection, quiet hours gate)
- Daily email digest (Resend)
- Notification retry worker (Redis ZSET, 3 attempts, 30s/2m/10m delays)
- Quiet hours hold-and-release (Redis ZSET + background worker)
- Admin scraper health dashboard
- Company management (add + ATS detection + deactivate)
- Low-confidence job review queue (approve/edit/reject)
- Admin Telegram failure alerts (after 3 consecutive failures)

---

## [v0.5.0] — TBD

**Theme:** Phase 1 frontend — onboarding, jobs feed, job detail, deployment

### Added
- `/login`, `/register`, `/verify-email` auth pages
- 4-step onboarding flow: skills (SkillPicker), preferences (RolePicker, LocationPicker), Telegram connect (QR + polling), complete
- Jobs feed (`/jobs`) with FilterBar (URL-synced filters) and JobFeed (infinite scroll)
- Job detail (`/jobs/{id}`) with SSR, JSON-LD structured data, AI summary, skill match overlay
- All shared hooks: useJobs, useProfile, useSkills, useTelegramStatus
- Production CI/CD pipeline (GitHub Actions: lint → test → build → staging → production)
- Docker Compose local development environment
- Railway deployment for backend + scheduler
- Vercel deployment for frontend
- UptimeRobot monitors for `/health` and frontend

### Decisions
- D-INFRA-001: Scheduler single instance (never scale horizontally)
- D-INFRA-002: Frontend on Vercel, backend on Railway (not co-hosted)

---

## [v1.0.0] — TBD

**Theme:** First production launch — Phase 1 complete

### Added
- All Phase 1 features from `17_TASKS.md` implemented and verified
- Pre-launch security checklist completed (see `13_SECURITY.md` Section 19)
- Initial 50–100 company career pages seeded and scraping

### Changed
- Version bumped from `v0.x.x` to `v1.0.0` — production is live

---

*This changelog is updated with every significant release. Small patches that don't affect functionality or user experience may be grouped into the next minor or major entry. When in doubt: log it. A slightly verbose changelog is better than a gap in the history.
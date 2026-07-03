# 18 — Decisions

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Engineering Lead  

---

## Purpose of This Document

This is the permanent record of every significant architectural, technical, and product decision made for Job Finder AI. Each decision captures: what was decided, why, what alternatives were considered, what tradeoffs were accepted, and under what conditions the decision should be revisited.

This document exists because decisions that are obvious today become mysterious six months from now. Future engineers — human or AI — should never have to guess why something was built a certain way. The answer is here.

**Rules:**
- Every decision that materially affects the codebase, architecture, or product must be logged here
- Decisions are never deleted — only superseded by a new entry that references the old one
- A decision record is written before implementation, not after
- If code contradicts a decision here, the code is wrong — or a new decision must be logged

---

## Decision ID Convention

```
D-[CATEGORY]-[NUMBER]

Categories:
  ARCH   — Architectural / system design
  TECH   — Technology choice
  DB     — Database / schema
  SEC    — Security
  API    — API design
  FE     — Frontend
  SCRP   — Scraper
  AGENT  — AI agent
  NOTIF  — Notification system
  INFRA  — Infrastructure / deployment
  PROD   — Product / feature
```

---

## Decision Index

| ID | Title | Status | Date |
|---|---|---|---|
| [D-TECH-001](#d-tech-001--backend-language--python-over-nodejs) | Backend Language: Python over Node.js | Accepted | 2025-06-22 |
| [D-DB-001](#d-db-001--primary-database--postgresql-over-mongodb) | Primary Database: PostgreSQL over MongoDB | Accepted | 2025-06-22 |
| [D-TECH-002](#d-tech-002--api-framework--fastapi-over-django-or-flask) | API Framework: FastAPI over Django or Flask | Accepted | 2025-06-22 |
| [D-TECH-003](#d-tech-003--queue-system--redis-lists-over-celery--rabbitmq) | Queue System: Redis Lists over Celery + RabbitMQ | Accepted | 2025-06-22 |
| [D-TECH-004](#d-tech-004--task-scheduler--apscheduler-over-managed-job-queue) | Task Scheduler: APScheduler over managed job queue | Accepted | 2025-06-22 |
| [D-TECH-005](#d-tech-005--orm--sqlalchemy-20-over-prisma-or-tortoise) | ORM: SQLAlchemy 2.0 over Prisma or Tortoise | Accepted | 2025-06-22 |
| [D-TECH-006](#d-tech-006--frontend-framework--nextjs-app-router-over-vite--react) | Frontend Framework: Next.js App Router over Vite + React | Accepted | 2025-06-22 |
| [D-TECH-007](#d-tech-007--component-library--shadcnui-over-mui-or-chakra) | Component Library: shadcn/ui over MUI or Chakra | Accepted | 2025-06-22 |
| [D-TECH-008](#d-tech-008--data-fetching--react-query-over-redux-toolkit) | Data Fetching: React Query over Redux Toolkit | Accepted | 2025-06-22 |
| [D-TECH-009](#d-tech-009--auth-library--nextauthjs-over-custom-oauth--hosted-auth) | Auth Library: NextAuth.js over custom OAuth / hosted auth | Accepted | 2025-06-22 |
| [D-TECH-010](#d-tech-010--object-storage--cloudflare-r2-over-aws-s3) | Object Storage: Cloudflare R2 over AWS S3 | Accepted | 2025-06-22 |
| [D-TECH-011](#d-tech-011--email-provider--resend-over-aws-ses-or-postmark) | Email Provider: Resend over AWS SES or Postmark | Accepted | 2025-06-22 |
| [D-TECH-012](#d-tech-012--llm-provider--openai-primary--anthropic-fallback) | LLM Provider: OpenAI primary, Anthropic fallback | Accepted | 2025-06-22 |
| [D-TECH-013](#d-tech-013--http-client--httpx-over-requests-or-aiohttp) | HTTP Client: httpx over requests or aiohttp | Accepted | 2025-06-22 |
| [D-TECH-014](#d-tech-014--browser-automation--playwright-over-selenium) | Browser Automation: Playwright over Selenium | Accepted | 2025-06-22 |
| [D-TECH-015](#d-tech-015--hosting--railway--render-over-raw-aws) | Hosting: Railway / Render over raw AWS | Accepted | 2025-06-22 |
| [D-ARCH-001](#d-arch-001--telegram-webhook-mode-over-polling) | Telegram: Webhook mode over polling | Accepted | 2025-06-22 |
| [D-ARCH-002](#d-arch-002--sequential-agent-pipeline-over-parallel) | Agent pipeline: Sequential over parallel | Accepted | 2025-06-22 |
| [D-ARCH-003](#d-arch-003--detection-based-scrapers-over-hardcoded-selectors) | Scrapers: Detection-based over hardcoded selectors | Accepted | 2025-06-22 |
| [D-ARCH-004](#d-arch-004--single-fastapi-service-over-microservices) | Single FastAPI service over microservices | Accepted | 2025-06-22 |
| [D-ARCH-005](#d-arch-005--url-state-for-job-filters-over-global-client-state) | URL state for job filters over global client state | Accepted | 2025-06-22 |
| [D-DB-002](#d-db-002--redis-rdb-snapshots-over-aof-persistence) | Redis: RDB snapshots over AOF persistence | Accepted | 2025-06-22 |
| [D-DB-003](#d-db-003--defer-application-level-column-encryption-to-phase-2) | Defer application-level column encryption to Phase 2 | Accepted | 2025-06-22 |
| [D-DB-004](#d-db-004--jobs-table-content_hash-deduplication-over-url-only) | Jobs deduplication: content_hash over URL-only | Accepted | 2025-06-22 |
| [D-SEC-001](#d-sec-001--access-token-in-memory-over-localstorage) | Access token: in-memory over localStorage | Accepted | 2025-06-22 |
| [D-SEC-002](#d-sec-002--refresh-token-in-httponlycookie-over-response-body) | Refresh token: httpOnly cookie over response body | Accepted | 2025-06-22 |
| [D-SEC-003](#d-sec-003--no-captcha-solving-services) | No CAPTCHA-solving services | Accepted | 2025-06-22 |
| [D-AGENT-001](#d-agent-001--prompts-in-docs-never-in-code) | Prompts in docs, never in code | Accepted | 2025-06-22 |
| [D-AGENT-002](#d-agent-002--llm-output-always-parsed-as-json--never-used-as-free-text) | LLM output always parsed as JSON | Accepted | 2025-06-22 |
| [D-AGENT-003](#d-agent-003--per-agent-model-tiering-over-one-model-for-all) | Per-agent model tiering over one model for all | Accepted | 2025-06-22 |
| [D-SCRP-001](#d-scrp-001--no-captcha-bypass-in-scrapers) | No CAPTCHA bypass in scrapers | Accepted | 2025-06-22 |
| [D-SCRP-002](#d-scrp-002--generic-adapter-always-uses-playwright) | Generic adapter always uses Playwright | Accepted | 2025-06-22 |
| [D-PROD-001](#d-prod-001--telegram-as-primary-notification-channel) | Telegram as primary notification channel | Accepted | 2025-06-22 |
| [D-PROD-002](#d-prod-002--no-recruiter-features-in-mvp) | No recruiter features in MVP | Accepted | 2025-06-22 |
| [D-PROD-003](#d-prod-003--degree_required-field-extracted-from-jd) | `degree_required` field extracted from JD | Accepted | 2025-06-22 |
| [D-PROD-004](#d-prod-004--company_type-classification-in-job-classifier) | `company_type` classification in Job Classifier | Accepted | 2025-06-22 |
| [D-INFRA-001](#d-infra-001--scheduler-runs-as-single-instance--never-scaled-horizontally) | Scheduler: single instance, never scaled horizontally | Accepted | 2025-06-22 |
| [D-INFRA-002](#d-infra-002--frontend-on-vercel-backend-on-railway--not-co-hosted) | Frontend on Vercel, backend on Railway — not co-hosted | Accepted | 2025-06-22 |
| [D-API-001](#d-api-001--ownership-failures-return-404-not-403) | Ownership failures return 404, not 403 | Accepted | 2025-06-22 |
| [D-API-002](#d-api-002--no-response-envelope--resources-returned-directly) | No response envelope — resources returned directly | Accepted | 2025-06-22 |

---

## TECHNOLOGY DECISIONS

---

### D-TECH-001 — Backend Language: Python over Node.js

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
The backend is written in Python. TypeScript/Node.js was explicitly considered and rejected.

#### Context
The platform's core value — scraping, AI agent orchestration, LLM API integration — is most naturally expressed in Python. The scraping ecosystem (BeautifulSoup, Playwright-Python, httpx), AI/LLM SDKs (OpenAI, Anthropic), and data processing libraries are more mature, better documented, and more widely used in Python than in Node.js.

#### Alternatives Considered

**Node.js + TypeScript (Fastify or Express)**
- Pro: Single language across frontend and backend
- Pro: Strong async I/O performance
- Con: Scraping libraries (Playwright is JS-native but BeautifulSoup equivalent is weaker)
- Con: LLM SDK ecosystem is more mature in Python
- Con: Pydantic-style validation is more deeply integrated in Python frameworks
- Con: Team's scraping and AI experience is Python-native

#### Rationale
Language unification (frontend + backend both TypeScript) is a legitimate goal for some projects, but for this one the core value is in the scraper + AI pipeline, not in the API layer. Choosing Python for the domain where we have the strongest ecosystem and team familiarity is the correct tradeoff. The API layer is straightforward regardless of language.

#### Tradeoffs Accepted
- Two languages in the repo (Python backend, TypeScript frontend)
- Smaller Python async talent pool compared to Node.js for hiring
- Some duplicate type definitions (Pydantic schemas + TypeScript types in `types/index.ts`)

#### Revisit Conditions
- If the AI/LLM SDK ecosystem for Node.js reaches parity with Python (unlikely in the near term)
- If the team grows to a point where language fragmentation becomes a serious hiring issue

---

### D-TECH-002 — API Framework: FastAPI over Django or Flask

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
FastAPI is the backend web framework.

#### Context
The API is I/O-bound: database queries, Redis reads, external LLM calls, Telegram API calls. Async-native handling of these operations is important for throughput.

#### Alternatives Considered

**Django + DRF**
- Pro: Batteries-included (ORM, admin panel, auth)
- Pro: Largest Python web framework ecosystem
- Con: Async support is newer and less deeply integrated
- Con: Django's ORM conflicts with our choice of SQLAlchemy
- Con: Heavier than needed for an API-first service

**Flask**
- Pro: Simple, minimal, familiar
- Con: No native async support
- Con: No built-in validation (Pydantic must be bolted on)
- Con: No automatic API documentation generation

#### Rationale
FastAPI provides async-native I/O, automatic Pydantic-based request/response validation, and automatic OpenAPI documentation generation — all without Django's overhead. The "batteries not included" nature is not a disadvantage here because we explicitly chose our own ORM (SQLAlchemy), auth (custom JWT), and database migration tool (Alembic).

#### Tradeoffs Accepted
- No built-in admin panel (compensated by our custom admin dashboard)
- More upfront architectural decisions compared to Django's convention-over-configuration approach

#### Revisit Conditions
- If team grows to the point where Django's convention-over-configuration significantly reduces onboarding time

---

### D-TECH-003 — Queue System: Redis Lists over Celery + RabbitMQ

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  
**Revisit Trigger:** > 50,000 notifications/day OR > 10,000 daily active users

#### Decision
Work queues (scrape jobs, agent processing, notification dispatch) are implemented using Redis list/sorted-set data structures, not a dedicated message broker.

#### Context
The platform needs queuing for three purposes: scraper job batching, AI agent pipeline orchestration, and notification dispatch. At MVP scale (< 1,000 users, < 500 jobs/day), the volume is well within Redis's throughput capacity.

#### Alternatives Considered

**Celery + RabbitMQ**
- Pro: Purpose-built for task queuing; more features (task routing, result backends, retry policies)
- Pro: Better observability tooling (Flower)
- Con: Two additional infrastructure components (Celery workers + RabbitMQ broker)
- Con: Operational complexity disproportionate to current team size (1–3 engineers)
- Con: Introduces a second paradigm (Celery's API) alongside the application code

**AWS SQS**
- Pro: Fully managed, scales automatically
- Pro: At-least-once delivery guarantee
- Con: Vendor lock-in
- Con: Cost at high volume
- Con: Not available in local development without mocking

#### Rationale
Redis is already required for caching and rate limiting. Using it for queuing consolidates infrastructure around a single component the team already understands. The queue implementation is abstracted behind service-layer functions, so migrating to Celery/SQS later requires changing only the queue client code, not the business logic that enqueues/dequeues work.

#### Tradeoffs Accepted
- Less sophisticated retry semantics than Celery (mitigated by application-level retry logic in `retry_worker.py`)
- At-most-once delivery if Redis loses in-flight data (mitigated by idempotent processing via DB dedup)
- Limited observability vs. Celery + Flower (mitigated by queue length logging to admin dashboard)

#### Revisit Conditions
- > 50,000 notifications/day (Redis queue latency would impact delivery SLA)
- > 10,000 DAU (scrape batch queue may become a bottleneck)
- If at-most-once delivery becomes unacceptable (data integrity requirements increase)

---

### D-TECH-004 — Task Scheduler: APScheduler over Managed Job Queue

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
APScheduler runs inside the Python process (or a dedicated worker) and manages all recurring jobs: scrape batches (15 min), daily digest (daily), deadline reminders (daily).

#### Alternatives Considered

**AWS EventBridge / Google Cloud Scheduler**
- Pro: Fully managed, no code to maintain
- Pro: More reliable than an in-process scheduler (survives process crashes)
- Con: External dependency adds deployment complexity
- Con: Requires HTTP endpoint triggers, introducing network hops and auth concerns
- Con: Harder to test locally

**Celery Beat**
- Pro: Integrates naturally with Celery workers
- Con: Only relevant if we'd already chosen Celery (we chose Redis queues — D-TECH-003)

**Cron on the server**
- Pro: Simple, OS-native
- Con: Requires SSH access or deployment configuration changes to modify schedules
- Con: Not portable across hosting platforms

#### Rationale
APScheduler requires no additional infrastructure, is testable in local development, and is sufficient for the scrape cadence at MVP scale. The scheduler is deployed as a single dedicated process (never scaled horizontally — see D-INFRA-001), which eliminates the primary risk of in-process schedulers (duplicate job execution from multiple instances).

#### Tradeoffs Accepted
- Scheduler state is lost on process restart (missed run not retroactively compensated — the next 15-min cycle catches up, which is acceptable)
- Less resilient than an external managed scheduler (process crash = no jobs until restart)

#### Revisit Conditions
- If missed scrape cycles become a business problem (SLA requirement for < 15-min latency tightens)
- If the team adopts Celery for other reasons (Celery Beat becomes the natural choice)

---

### D-TECH-005 — ORM: SQLAlchemy 2.0 over Prisma or Tortoise

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
SQLAlchemy 2.0 (async) is the ORM. Alembic handles migrations.

#### Alternatives Considered

**Prisma (Python client)**
- Pro: Excellent DX, schema-first, strong type generation
- Con: Prisma's primary client is Node/TypeScript; the Python client is unofficial/community-maintained and significantly less mature
- Con: Would require maintaining a separate Node service or accepting an inferior tooling experience

**Tortoise ORM**
- Pro: Async-native, Django-ORM-like syntax
- Con: Smaller community than SQLAlchemy; less proven at scale
- Con: Migration tooling (Aerich) is less mature than Alembic

#### Rationale
SQLAlchemy is the most battle-tested Python ORM. Its 2.0 async API integrates cleanly with FastAPI. Alembic (SQLAlchemy's migration tool) provides robust upgrade/downgrade paths critical for a production schema that will evolve over time.

#### Tradeoffs Accepted
- More verbose than Prisma's schema-first DX
- 2.0's async patterns differ from 1.x tutorials, requiring engineers to learn the current idioms specifically

---

### D-TECH-006 — Frontend Framework: Next.js App Router over Vite + React

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
Next.js with the App Router is the frontend framework.

#### Alternatives Considered

**Vite + React (SPA)**
- Pro: Faster dev server, simpler mental model, no SSR complexity
- Con: No SSR means public job listing pages are not indexable by Google
- Con: Requires a separate SEO solution for job detail pages

**Remix**
- Pro: Strong data-loading model, comparable SSR
- Con: Smaller ecosystem; team had stronger Next.js familiarity

#### Rationale
Public job listing pages (`/jobs`, `/jobs/{id}`) benefit from SSR for SEO — students may discover the platform via Google search for a specific company's job. Next.js's `generateMetadata` and JSON-LD structured data support (for `JobPosting` schema) make this straightforward. The App Router's Server Components also reduce client bundle size for content-heavy pages.

#### Tradeoffs Accepted
- App Router's server/client component boundary requires discipline to avoid bloating client bundles
- Steeper learning curve than plain Vite SPA

#### Revisit Conditions
- If the SEO requirement is dropped (no organic search acquisition strategy)

---

### D-TECH-007 — Component Library: shadcn/ui over MUI or Chakra

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
shadcn/ui is used for UI components. Components are copied into the codebase and fully owned.

#### Alternatives Considered

**Material UI (MUI)**
- Pro: Comprehensive, well-documented, large community
- Con: Opinionated Material Design aesthetic is hard to fully de-brand
- Con: Heavier bundle size from components we don't use

**Chakra UI**
- Pro: Good DX, accessible
- Con: Runtime CSS-in-JS approach conflicts with React Server Components

#### Rationale
shadcn/ui's "copy the code" model means components are fully under our control — no fighting an abstraction layer when customization is needed. Built on Radix UI primitives, so accessibility (keyboard navigation, ARIA, focus management) is handled correctly without custom code. Tailwind-native, so no separate theming system.

#### Tradeoffs Accepted
- No automatic upstream security/accessibility fixes — must be manually re-pulled
- Higher initial setup effort than `npm install ui-library`

---

### D-TECH-008 — Data Fetching: React Query over Redux Toolkit

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
TanStack React Query (v5) is used for all server state management. No Redux.

#### Context
Most of the frontend's state is server-derived (jobs, saved jobs, profile, admin data). A separate global state library is not needed when React Query handles caching, background refetching, loading/error states, and mutation side effects.

#### Alternatives Considered

**Redux Toolkit + RTK Query**
- Pro: Capable, mature, handles both server and UI state
- Con: More boilerplate, steeper learning curve
- Con: Overkill when server state is the primary concern

**SWR**
- Pro: Similar philosophy to React Query, simpler API
- Con: React Query's mutation handling and devtools are more mature

#### Rationale
React Query's query key hierarchy, built-in cache invalidation on mutation, and excellent devtools make server state management straightforward. URL params handle shareable UI state (filter values). Local `useState` handles ephemeral UI state (modal open/closed). No global state library is needed.

#### Tradeoffs Accepted
- If a genuine global client-state need arises (e.g., a shopping cart equivalent), a decision record must be written before adding Zustand or Redux

#### Revisit Conditions
- A global state need that cannot be expressed as server state (React Query) or URL state

---

### D-TECH-009 — Auth Library: NextAuth.js over Custom OAuth / Hosted Auth

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
NextAuth.js handles the Google OAuth flow on the frontend. Custom JWT implementation handles the email/password flow on the FastAPI backend.

#### Alternatives Considered

**Fully custom OAuth implementation**
- Pro: Full control
- Con: OAuth has subtle security pitfalls (state validation, token storage, PKCE) better left to a maintained library

**Auth0 / Clerk (hosted auth)**
- Pro: Excellent DX, handles everything
- Con: External dependency for a core security function
- Con: Paid service; pricing scales with users
- Con: Vendor lock-in for authentication

**Better Auth**
- Pro: Modern, self-hosted, promising
- Con: Less proven in production at evaluation time; NextAuth had stronger Google provider support

#### Rationale
NextAuth handles the OAuth dance correctly (state parameter, token exchange, session management on the frontend) without requiring us to implement OAuth security details from scratch. The email/password flow is simple enough to implement directly in FastAPI without a library. See also D-SEC-001 and D-SEC-002 for how tokens are stored.

#### Tradeoffs Accepted
- Some impedance mismatch between NextAuth's session model and our FastAPI JWT model, requiring a thin adapter layer

---

### D-TECH-010 — Object Storage: Cloudflare R2 over AWS S3

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
Cloudflare R2 is used for resume PDF storage. S3-compatible API.

#### Alternatives Considered

**AWS S3**
- Pro: Industry standard, extensive ecosystem
- Con: Egress fees — significant cost at scale for a bootstrapped product
- Con: AWS console complexity for a small team

**Local filesystem**
- Pro: Zero cost
- Con: Not scalable beyond one server; breaks horizontal scaling

#### Rationale
R2's S3-compatible API means we use standard S3 client libraries with no vendor-specific code. R2 has **no egress fees**, which is a meaningful cost advantage as resume downloads scale. The only tradeoff is marginally smaller ecosystem tooling compared to AWS S3 specifically — which doesn't matter given we use the standard S3 API.

#### Tradeoffs Accepted
- Some advanced AWS-specific S3 features (certain event notifications, specific Lambda triggers) are unavailable
- Cloudflare-specific operational dependency

---

### D-TECH-011 — Email Provider: Resend over AWS SES or Postmark

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
Resend is the email delivery provider. The email client is built behind a provider-agnostic interface (`notifications/email/client.py`), so switching providers requires changing only that file.

#### Alternatives Considered

**AWS SES**
- Pro: Very cheap at scale
- Con: Requires manual SPF/DKIM/DMARC configuration and domain warmup
- Con: More operational complexity than a managed provider at MVP scale

**Postmark**
- Pro: Excellent deliverability reputation
- Con: Less favorable pricing at low volume compared to Resend's free tier

#### Rationale
Resend's modern API, generous free tier, and good out-of-box deliverability are appropriate for MVP scale. The provider-agnostic wrapper ensures migrating to SendGrid or SES at higher volume is a single-file change.

#### Tradeoffs Accepted
- Free tier limits will be outgrown as user base scales

---

### D-TECH-012 — LLM Provider: OpenAI Primary, Anthropic Fallback

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
OpenAI (GPT-4o / GPT-4o-mini) is the primary LLM provider. Anthropic (Claude Sonnet) is configured as an automatic fallback for API outages or rate limit exhaustion.

#### Context
Agents require reliable structured JSON output. Both OpenAI and Anthropic support JSON mode / structured output. The selection comes down to tooling familiarity, API stability, and model tiering options.

#### Alternatives Considered

**Anthropic as primary**
- Pro: Comparable output quality; strong instruction-following
- Con: Team had more existing production experience with OpenAI's function-calling at decision time

**Self-hosted open-source models (Llama, Mistral)**
- Pro: No per-call API cost
- Con: GPU infrastructure required; operational overhead disproportionate to team size at MVP
- Con: Structured JSON reliability lower than GPT-4o at current model sizes

#### Rationale
GPT-4o-mini for classification tasks (10–100x cheaper than GPT-4o) while GPT-4o handles extraction and summarization where quality matters most. The `BaseAgent` abstraction makes the provider selection a config change, not a code change. Anthropic fallback provides resilience without duplicating prompts (prompts are written to be provider-agnostic where possible).

#### Tradeoffs Accepted
- Per-call cost requires active management (caching, model tiering, spending caps)
- Maintaining prompt compatibility across two providers adds minor overhead

#### Revisit Conditions
- LLM cost exceeds $50/month per 1,000 users (NFR-COST-01 from `01_PRD.md`)
- Self-hosted model quality for structured JSON output reaches parity with GPT-4o

---

### D-TECH-013 — HTTP Client: httpx over requests or aiohttp

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
`httpx` is the HTTP client for all scraper HTTP requests.

#### Alternatives Considered

**requests**
- Pro: Most familiar Python HTTP library
- Con: Synchronous only — blocks in an async FastAPI/scheduler context

**aiohttp**
- Pro: Also async-native
- Con: Less `requests`-like API; slightly steeper learning curve

#### Rationale
`httpx` provides async support with an API nearly identical to `requests`, minimizing the learning curve for engineers familiar with the Python ecosystem. HTTP/2 support is available when useful.

---

### D-TECH-014 — Browser Automation: Playwright over Selenium

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
Playwright is used selectively for JS-rendered career pages (iCIMS fallback, generic adapter). It is not the default — `httpx` is used first for all adapters.

#### Alternatives Considered

**Selenium**
- Pro: Long-standing standard, widely understood
- Con: Slower and historically more brittle with modern JS-heavy sites compared to Playwright

**Puppeteer (Node.js)**
- Pro: Mature, excellent API
- Con: Would require a separate Node.js scraping service, fragmenting the Python scraping codebase

#### Rationale
Playwright's auto-waiting behavior reduces flaky scraping on JS-rendered pages. Python-native means it lives alongside our httpx-based scrapers in a single codebase. The deliberate "httpx first, Playwright fallback" design keeps the common case fast and cheap.

---

### D-TECH-015 — Hosting: Railway / Render over Raw AWS

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  
**Revisit Trigger:** Traffic significantly outgrows managed platform economics

#### Decision
Backend and scheduler are hosted on Railway (or Render as alternative). Frontend on Vercel. Managed PostgreSQL and Redis via Supabase/Railway and Upstash.

#### Alternatives Considered

**AWS (EC2 / ECS / EKS)**
- Pro: Maximum control, cheapest at very high scale
- Con: Requires meaningful DevOps expertise to operate safely
- Con: Disproportionate operational overhead for a 1–3 engineer team (per `01_PRD.md` constraints)

**Heroku**
- Pro: Pioneered this category
- Con: Pricing is less competitive than Railway/Render for comparable resources

#### Rationale
Railway/Render cover our hosting need (Docker-based deployments, managed DB/Redis add-ons, simple env var management) without requiring a dedicated DevOps engineer. The constraint from `01_PRD.md` Section 14 is explicit: the architecture must be operable by the current team size without a DevOps hire.

#### Tradeoffs Accepted
- Less raw infrastructure control
- Costs scale less favorably at very high traffic vs. raw cloud

---

## ARCHITECTURE DECISIONS

---

### D-ARCH-001 — Telegram: Webhook Mode over Polling

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
The Telegram bot uses webhook mode in production. Polling is used only in local development (optional).

#### Rationale
Webhooks receive updates immediately when Telegram sends them — no latency introduced by a polling interval. Polling would add 1–10 seconds of latency to every bot command and button press. Since our core UX is an instant job alert, latency is unacceptable.

Webhooks also avoid a persistent long-polling connection that must survive process restarts, which is operationally simpler in a stateless hosting environment.

#### Tradeoffs Accepted
- Webhook endpoint must be publicly accessible (requires a deployed staging/production environment for bot testing)
- Local development uses a tunnel (ngrok) or polling fallback

---

### D-ARCH-002 — Agent Pipeline: Sequential over Parallel

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
The 5 AI agents (Extractor → Skill Extractor → Summarizer → Classifier → Notification Generator) run sequentially per job, not in parallel.

#### Alternatives Considered

**Parallel agent execution**
- Pro: Faster total pipeline time per job
- Con: Skill Extractor output (required_skills) is an input to the Classifier — parallel execution prevents this data dependency
- Con: Parallel LLM calls for one job increase instantaneous API cost and are more complex to reason about
- Con: Error handling across parallel agents is significantly more complex

#### Rationale
Each agent's output can improve the next agent's quality:
- Extractor provides clean title/location to Summarizer
- Skill Extractor provides required_skills to Classifier (improves classification accuracy)
- Classifier output used in Notification Generator message construction

Sequential execution preserves these dependencies, is simpler to reason about, and is simpler to debug (a log shows exactly which agent ran last before a failure). The per-job latency (< 25 seconds total) is acceptable given jobs are processed asynchronously from a queue.

#### Revisit Conditions
- If per-job pipeline latency becomes a bottleneck (currently < 25 sec; SLA is < 30 min from posting to notification)

---

### D-ARCH-003 — Scrapers: Detection-Based over Hardcoded Selectors

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
The ATS Auto-Detector dynamically identifies which ATS a career page uses before selecting a scraper adapter. Adapters are not assigned per-company at setup time and then never re-checked.

#### Rationale
Companies migrate between ATS platforms (e.g., from Taleo to Greenhouse, or from custom to Workday) without notice. Hardcoding "Company X uses Greenhouse" in a config file means a migration silently breaks the scraper. Detection-based selection means a migration is automatically handled on the next scrape cycle once the new ATS is recognized. An admin can also override detection with a manual `ats_type` setting when needed.

#### Tradeoffs Accepted
- Detection adds one additional HTTP round-trip per company per scrape cycle (cached, not re-fetched every run for already-detected companies)
- Detection can fail for new or unusual ATS types (falls back to `"generic"`)

---

### D-ARCH-004 — Single FastAPI Service over Microservices

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
All backend functionality (API, scraper runner, agent pipeline, notification dispatch) lives in a single Python codebase deployed as at most two processes: the API server and the scheduler worker. No microservices.

#### Rationale
For a 1–3 engineer team, microservices introduce:
- Network latency between services (instead of in-process function calls)
- Distributed tracing complexity
- Multiple deployment pipelines to maintain
- Service discovery and inter-service auth overhead

At our current and near-future scale, a well-structured monolith with clear internal module boundaries (the layered architecture in `05_ARCHITECTURE.md` Section 2) provides all the organizational benefits of microservices without the operational overhead. The module boundaries are enforced by code convention (routers call services call models), not by network boundaries.

#### Revisit Conditions
- If the scraper pipeline's compute requirements significantly diverge from the API's (e.g., needing GPU-based scraping at scale)
- At > 100,000 users if a specific bottleneck cannot be addressed by scaling the monolith

---

### D-ARCH-005 — URL State for Job Filters over Global Client State

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
The jobs feed filter state (role_type, location, experience_level, is_remote, search query) is stored in URL query parameters, not in React component state or a global state store.

#### Rationale
URL state means:
- Filters survive page refresh
- Filtered views are shareable as links (e.g., "all remote SWE jobs for freshers" has a stable URL)
- Browser back/forward navigation moves through filter history correctly
- Server-side rendering can use filter params to fetch the correct initial data

URL state with `router.replace` (not `router.push`) for filter changes means individual filter changes don't stack up in the browser history — "back" goes to the previous page, not the previous filter state.

#### Tradeoffs Accepted
- URL becomes verbose with many active filters
- Filter state is not shareable across browser tabs via a global store (not a real use case for this product)

---

## DATABASE DECISIONS

---

### D-DB-001 — Primary Database: PostgreSQL over MongoDB

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  
**Note:** This decision reversed an earlier recommendation. The reversal is the content of this record.

#### Decision
PostgreSQL is the sole primary datastore. MongoDB was considered earlier in the project and explicitly rejected.

#### Context
Early in the project, MongoDB was recommended given the unstructured nature of scraped job data (raw HTML, variable fields per ATS). After deeper analysis of the matching logic, the relational model proved clearly superior.

#### Why MongoDB Was Initially Attractive
- Raw job descriptions vary significantly by ATS (some have salary, some don't; some have deadlines, some don't)
- Scraping produces naturally document-shaped data
- No schema migrations for evolving job fields

#### Why PostgreSQL Was Chosen Instead

**The matching query is deeply relational:**
```
Users ↔ user_preferred_roles ↔ role_types
Users ↔ user_skills ↔ skills
Users ↔ user_preferred_locations ↔ cities
Jobs ↔ job_skills ↔ skills
```
This 5-table join (with many-to-many relationships) is natural SQL. In MongoDB it requires multiple `$lookup` aggregation stages and application-level assembly — more code, less readable, harder to optimize.

**JSONB solves the document-flexibility problem:**
PostgreSQL's `JSONB` columns store raw scraped data and agent outputs without requiring a fixed schema for those fields, while the core structured fields (title, location, role_type, experience_level) remain strongly typed with indexes.

**Full-text search is built-in:**
`tsvector` + `GIN` index on `jobs.search_vector` provides the search functionality needed for the jobs feed without adding Elasticsearch.

#### Tradeoffs Accepted
- JSONB queries are less ergonomic than a true document database's native query language (acceptable given how little of our data is purely document-shaped)

---

### D-DB-002 — Redis: RDB Snapshots over AOF Persistence

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
Redis is configured with RDB (periodic snapshot) persistence, not AOF (append-only file) persistence.

#### Rationale
All data in Redis is either:
- **Ephemeral cache** (job feed responses, skill search results) — can be rebuilt from PostgreSQL on cache miss
- **Queue payloads** — reference durable PostgreSQL record IDs; reprocessing is safe because deduplication happens at the DB layer
- **Rate limit counters** — brief reset acceptable on restart
- **Session tokens** — stored hashed in PostgreSQL; Redis holds only the fast-lookup copy

A Redis restart causes at worst: a latency spike (cache miss), a brief window of less-strict rate limiting, and possible re-queuing of in-flight items (idempotently handled). There is no durable data loss. AOF would add significant write amplification overhead for data that doesn't need it.

---

### D-DB-003 — Defer Application-Level Column Encryption to Phase 2

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
Sensitive fields (`telegram_id`, `email` in `notification_logs`) are stored in plaintext in PostgreSQL at MVP. Application-level column encryption is deferred to Phase 2.

#### Context
Application-level encryption (e.g., encrypting the `telegram_id` column with a KMS-managed key before writing to DB) would:
- Prevent column-level data exposure if the DB credentials are compromised but the encryption key is not
- Require significantly more implementation complexity (key management, encryption/decryption in the ORM layer, impact on queries and indexes)

#### Why Deferred
At MVP stage:
- Database credentials are stored only in the hosting platform's secrets vault
- PostgreSQL connection is TLS-enforced in production
- Only 2–3 people have any access to the production environment
- The operational complexity of key management is disproportionate to the risk at this user scale

The risk profile changes meaningfully at scale (more users means more data at stake, larger attack surface). Phase 2 re-evaluation is explicitly required.

#### Revisit Conditions
- Before reaching 5,000 users
- After a security audit identifies this as a priority
- If any data exposure incident occurs

---

### D-DB-004 — Jobs Deduplication: content_hash over URL-Only

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
Job deduplication uses a SHA-256 hash of `normalize(title) + "|" + normalize(company) + "|" + normalize(apply_url)`, not just the `apply_url` alone.

#### Rationale
Using only `apply_url` would fail to deduplicate jobs posted at the same URL but with different titles (a rare but real case when a company reuses an ATS posting URL for a different role). Including `title` and `company` in the hash handles this correctly.

Using all three fields also handles the case where the same job is posted at slightly different URLs (e.g., with and without tracking parameters) by a future smarter normalization — adding URL normalization to `normalize()` would catch these without changing the schema.

#### Tradeoffs Accepted
- Does not deduplicate the same job posted on two different ATS portals (different `apply_url` → different hash → two records). Semantic deduplication (comparing job descriptions) is Phase 3.

---

## SECURITY DECISIONS

---

### D-SEC-001 — Access Token: In-Memory over localStorage

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
The JWT access token is stored in a JavaScript module-level variable (memory), not in `localStorage` or `sessionStorage`.

#### Rationale
`localStorage` and `sessionStorage` are accessible to any JavaScript on the page, including XSS-injected scripts. A compromised third-party script (supply chain attack) could exfiltrate the access token and perform actions as the user.

In-memory storage means the token is lost on page refresh. The cost: one additional API call (the refresh endpoint) on each page load. The benefit: XSS cannot steal the access token.

The refresh token (longer-lived) is in an httpOnly cookie (D-SEC-002) — also inaccessible to JavaScript — so the refresh call succeeds silently.

#### Tradeoffs Accepted
- One additional API call on every page refresh
- Access token is lost when user opens a new tab (mitigated by the refresh token cookie being shared across tabs in the same browser)

---

### D-SEC-002 — Refresh Token: httpOnly Cookie over Response Body

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
The refresh token is returned as an `httpOnly`, `Secure`, `SameSite=Strict` cookie, scoped to `/api/auth`. It is never included in the JSON response body.

#### Rationale
An httpOnly cookie cannot be read by JavaScript — only sent automatically by the browser to the matching URL. This means:
- XSS attacks cannot steal the refresh token
- The refresh token is sent only to `/api/auth` endpoints (path scoping), not to `/api/jobs` or any other route
- `SameSite=Strict` prevents the cookie from being sent on cross-origin requests (CSRF protection)

Returning the refresh token in the response body would require the frontend to store it somewhere — either `localStorage` (XSS-vulnerable) or memory (lost on refresh).

#### Tradeoffs Accepted
- Logout requires a server-side call (cannot just clear client-side storage)
- More complex testing (cookie handling in HTTP test clients)

---

### D-SEC-003 — No CAPTCHA-Solving Services

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
The platform will never integrate with CAPTCHA-solving services (2Captcha, Anti-Captcha, etc.) to bypass bot protection on career pages.

#### Rationale
CAPTCHA-solving services:
1. Violate the terms of service of virtually every website that uses CAPTCHA
2. Often rely on human labor (crowdsourced solvers) under exploitative conditions
3. Introduce a paid third-party dependency for a fundamentally adversarial activity
4. Create legal exposure

Our scraping is already designed to be respectful (rate limiting, robots.txt compliance). When a site deploys CAPTCHA, it is explicitly asking our scraper not to proceed. We comply. The company is logged as temporarily failed and retried on the next cycle — Cloudflare challenges are often temporary.

This decision is non-negotiable and cannot be revisited. See also D-SCRP-001.

---

## AGENT DECISIONS

---

### D-AGENT-001 — Prompts in Docs, Never in Code

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
All LLM prompts are defined in `docs/20_PROMPTS.md` under versioned entries (e.g., `extractor_v1`). Application code loads prompt templates from configuration — no prompt text appears in Python files.

#### Rationale
Prompts embedded in code are:
- Invisible to non-engineers (product, operations) who need to iterate on output quality
- Unversioned (a code commit mixes prompt changes with code changes, obscuring what changed)
- Harder to A/B test (requires a code deploy to test a prompt variant)
- Invisible to AI coding assistants reading the codebase, who can't see what prompts the system uses

Prompts in a versioned document are:
- Visible to the whole team
- Reviewable independently from code changes
- Auditable (which prompt version produced which output, via `agent_logs.prompt_version`)
- Changeable without a code deploy (in a future config-serving architecture)

#### Tradeoffs Accepted
- Extra indirection between code and prompt text
- Requires discipline to keep `20_PROMPTS.md` in sync

---

### D-AGENT-002 — LLM Output Always Parsed as JSON, Never Used as Free Text

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
Every LLM agent call uses `response_format: { type: "json_object" }` and parses the response through a strict Pydantic/JSON schema validator before use. Free-text LLM output is never stored in the database or used in application logic.

#### Rationale
Free-text LLM output is:
- Unpredictable in structure (different runs may return different field arrangements)
- Impossible to index or query reliably
- A prompt injection vector (if the model includes injected instructions in the output, free text makes it harder to detect)
- Unvalidatable — bad data silently enters the system

Structured JSON output is validated at the boundary. Parse failures are caught, logged, and retried. The downstream system only ever sees well-formed, schema-valid data.

#### Tradeoffs Accepted
- Some information that's naturally free-form (nuanced cultural assessment of a company) cannot be easily captured in structured output
- JSON mode occasionally produces less fluent output than unconstrained generation (mitigated by prompt quality)

---

### D-AGENT-003 — Per-Agent Model Tiering over One Model for All

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
Different agents use different models based on task complexity and cost sensitivity:
- Job Extractor, Skill Extractor, JD Summarizer: GPT-4o (strong model)
- Job Classifier, Notification Generator: GPT-4o-mini (fast/cheap model)

#### Rationale
Classification (role_type, domain, experience_level) is a bounded, well-defined task with a fixed taxonomy. GPT-4o-mini produces reliable results at 1/10th the cost. Using GPT-4o for classification would waste 90% of the per-call cost on capability the task doesn't require.

Extraction and summarization require more nuanced language understanding and produce user-facing output — the quality difference between GPT-4o and GPT-4o-mini is visible to users and impacts trust.

#### Tradeoffs Accepted
- Two model versions to monitor and update when OpenAI releases new versions
- Prompt compatibility must be verified for each model tier independently

---

## SCRAPER DECISIONS

---

### D-SCRP-001 — No CAPTCHA Bypass in Scrapers

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

This decision is identical in content to D-SEC-003 and exists here for cross-reference completeness. See D-SEC-003 for the full rationale.

**Bottom line:** CAPTCHA-blocked scrapes are logged as `error_type: "captcha"`, the company is skipped for the current cycle, and the admin is alerted if failures persist. We do not solve CAPTCHAs.

---

### D-SCRP-002 — Generic Adapter Always Uses Playwright

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
The generic HTML fallback adapter always renders pages via Playwright (headless Chromium), not httpx.

#### Rationale
Career pages that don't match any known ATS signature are the most likely to be custom, JavaScript-rendered SPAs. An httpx request would receive the JS bundle, not the rendered DOM, producing empty scrape results. Using Playwright as the default for unknown pages eliminates this failure mode at the cost of higher resource usage.

For known ATS types (Greenhouse, Lever, Workday) where we have clean JSON APIs, Playwright would be wasteful — these adapters use httpx directly. The iCIMS adapter uses httpx first and only falls back to Playwright when JS rendering is detected.

#### Tradeoffs Accepted
- Higher resource consumption (real Chromium instance) for generic scrapes
- Slower per-page fetch time (5–15 seconds vs. < 1 second for httpx)

---

## PRODUCT DECISIONS

---

### D-PROD-001 — Telegram as Primary Notification Channel

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Product Lead, Engineering Lead  

#### Decision
Telegram is the primary notification channel. Email is secondary. A native mobile app is explicitly out of scope for MVP.

#### Context
Students were the target audience from day one. The question was: what channel do students actually check and act on?

#### Evidence

| Channel | Open rate | Action rate | Notes |
|---|---|---|---|
| Email | ~20% | Low | Most job alert emails are muted |
| Push notification | High | Medium | Requires native app |
| Telegram | Near 100% | High | Students already use it for placement prep communities |
| WhatsApp | Near 100% | High | Business API is expensive and gated |

Telegram's Bot API is free, mature, supports inline keyboards (Apply/Save/Not Interested buttons), and has near-instant delivery. Students are already in Telegram communities checking job posts from other sources — we're meeting them in their existing workflow.

#### Tradeoffs Accepted
- Students who don't use Telegram get email-only (lower engagement)
- WhatsApp Business API would reach more users but costs ~$0.005/message

#### Revisit Conditions
- If the target user base shifts to a demographic with lower Telegram usage (e.g., recruiter-focused features in Phase 3)

---

### D-PROD-002 — No Recruiter Features in MVP

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Product Lead  

#### Decision
The recruiter portal (direct job posting, student sourcing, subscription billing) is explicitly excluded from MVP. The MVP is student-only.

#### Rationale
Building two sides of a marketplace simultaneously is a common startup failure mode. The student-side value proposition must be proven first:
- Students receive accurate, timely, matched job alerts
- Students trust the platform enough to connect their Telegram
- Students return and engage with saved/tracked jobs

Only when the student side works reliably does the recruiter side have value to offer. A recruiter portal with no student engagement data is worthless.

#### Revisit Conditions
- Phase 3 begins when WAU > 2,000 and Day-7 retention > 40% (per `16_ROADMAP.md`)

---

### D-PROD-003 — `degree_required` Field Extracted from JD

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Product Lead, Engineering Lead  

#### Decision
The Skill Extractor agent extracts `degree_required` (boolean) and `degree_note` (verbatim phrase) from every job description. This field is exposed in the job detail API and on the job detail page.

#### Context
This decision emerged from the Persona analysis. Persona 3 (Rahul — self-taught developer, no CS degree) is a significant segment of the target audience. These users are systematically filtered out by ATS keyword matching before a human reviewer ever sees their application. Their biggest pain is not knowing which companies are "degree-optional" before investing 30 minutes in an application.

#### Rationale
No existing job platform surfaces this signal. If our Skill Extractor can extract "equivalent experience accepted" or "no degree required" from JDs at >90% accuracy, this becomes a meaningful differentiator for the self-taught developer segment — and a reason to choose Job Finder AI over every other job board.

#### Tradeoffs Accepted
- LLM accuracy on this field depends on how explicitly the JD states it — ambiguous cases default to `null` (unknown), not `false` (required)
- False positives (claiming a role is degree-optional when it isn't) would damage trust; the prompt is conservative

---

### D-PROD-004 — `company_type` Classification in Job Classifier

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Product Lead, Engineering Lead  

#### Decision
The Job Classifier agent outputs a `company_type` field with values: `product`, `services`, `startup`, `enterprise`, `agency`, `unknown`.

#### Context
Persona 4 (Sneha — 1.5 YOE developer switching from services to product) represents a large and underserved segment. The distinction between a "software engineer" role at TCS (services company) and the same title at Razorpay (product company) is enormous in terms of day-to-day work, growth trajectory, and compensation. Yet job title alone provides no signal.

#### Rationale
If the classifier can distinguish product vs. services companies with > 80% accuracy from the JD text and company name, we can:
- Filter the feed by company type (a filter no other platform has)
- Surface "product company" as a notable attribute in the Telegram notification
- Help users like Sneha avoid wasting applications on roles that look right but aren't

#### Tradeoffs Accepted
- Classification accuracy depends on information available in the JD — many JDs don't make the company type obvious
- `company_type: "unknown"` is the correct fallback; never guess when evidence is insufficient
- No impact on matching logic (role+skill+location drive matching, not company_type)

---

## INFRASTRUCTURE DECISIONS

---

### D-INFRA-001 — Scheduler: Single Instance, Never Scaled Horizontally

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
The APScheduler process is deployed as exactly one instance. It must never be horizontally scaled (multiple replicas).

#### Rationale
Multiple scheduler instances would each fire the same jobs at the same time, causing:
- Duplicate scrape batches (same companies scraped 2x, 3x per cycle)
- Duplicate AI agent calls (same jobs processed multiple times)
- Duplicate notifications (same user notified multiple times for the same job)

The `UNIQUE(user_id, job_id, channel)` constraint on `notification_logs` would catch duplicates at the notification level, but wasted LLM calls and scrape traffic would occur first.

The scheduler runs as a single process with `max_instances=1` per job in APScheduler configuration. Railway/Render deployment is configured with replica count = 1 and explicit documentation that this must not be changed.

#### Revisit Conditions
- If the scrape batch duration approaches the 15-minute interval (at which point the solution is to increase batch efficiency, not add replicas)
- A leader-election pattern (e.g., Redis-based distributed lock) could theoretically enable multiple scheduler replicas — this would be a significant architectural change requiring its own decision record

---

### D-INFRA-002 — Frontend on Vercel, Backend on Railway — Not Co-hosted

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
The Next.js frontend is hosted on Vercel. The FastAPI backend is on Railway. They are not co-hosted on the same platform.

#### Rationale
Vercel is built by the creators of Next.js and provides first-party support for every App Router feature, automatic preview deployments per PR, and a global CDN edge network. These benefits are specific to Vercel and not replicated cleanly on Railway/Render for Next.js.

Railway/Render provide Docker-based backend hosting, managed PostgreSQL/Redis add-ons, and straightforward environment variable management — the right tool for a Python backend service.

Using the best platform for each service, even if it means two vendors, is the better tradeoff than compromising either service for the sake of vendor consolidation.

#### Tradeoffs Accepted
- Two hosting providers to manage (two billing accounts, two sets of environment variables, two deployment pipelines)
- Slight CORS configuration overhead (two domains — api.jobfinderai.com and jobfinderai.com must be explicitly configured)

---

## API DECISIONS

---

### D-API-001 — Ownership Failures Return 404, Not 403

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
When an authenticated user attempts to access or modify a resource they don't own (e.g., updating another user's saved job), the API returns `404 Not Found`, not `403 Forbidden`.

#### Rationale
A `403 Forbidden` response reveals that the resource exists but the requesting user doesn't have permission. This leaks information: an attacker who receives 403 knows the resource ID is valid and belongs to someone else. They receive 404 and learn nothing.

This pattern (sometimes called "security through obscurity, but correct obscurity") is explicitly recommended by OWASP for resource ownership checks. The service layer enforces this:
```python
saved = await db.get_saved_job(user_id=user_id, job_id=job_id)
if not saved:
    raise HTTPException(status_code=404, detail="Saved job not found")
```
The query filters on `user_id` — if the job exists but belongs to someone else, the query returns nothing, and the user receives 404.

---

### D-API-002 — No Response Envelope — Resources Returned Directly

**Date:** 2025-06-22  
**Status:** Accepted  
**Deciders:** Engineering Lead  

#### Decision
API responses return the resource or list directly. There is no outer envelope like `{ "status": "success", "data": { ... } }`.

#### Alternatives Considered

**Envelope pattern:** `{ "status": "success", "data": {...}, "meta": {...} }`
- Pro: Consistent structure for all responses
- Con: Adds nesting that every consumer must unwrap
- Con: HTTP status codes already convey success/failure — the `status` field is redundant

**JSend / JSON:API**
- Pro: Standardized response format
- Con: Significant overhead for the simple response shapes we use

#### Rationale
HTTP status codes carry success/failure semantics. The response body carries the resource. Adding an envelope duplicates the status information and adds unnecessary nesting. For paginated lists, the pagination metadata is included at the top level alongside `items`, not nested in a `data` field:

```json
{
  "items": [...],
  "total": 247,
  "page": 0,
  "has_more": true
}
```

Error responses use a consistent `{ "error": { "code": "...", "message": "..." } }` shape — separate from success responses, which need no such wrapper.

---

*Every decision in this document was made deliberately. Future engineers who disagree with a decision should add a new superseding entry rather than silently changing the implementation — the history of why we made certain choices is as important as what we chose.*
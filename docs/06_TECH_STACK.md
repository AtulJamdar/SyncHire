# 06 — Tech Stack

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Engineering Lead  

---

## Purpose of This Document

This document lists every technology used in Job Finder AI, why it was chosen, what alternatives were considered, and the tradeoffs accepted. This is the reference engineers and AI assistants should consult before introducing a new dependency or questioning an existing one. No technology should be swapped without a corresponding update here and a new entry in `18_DECISIONS.md`.

---

## Stack Summary Table

| Layer | Technology |
|---|---|
| Frontend Framework | Next.js (App Router, TypeScript) |
| Styling | Tailwind CSS |
| Component Library | shadcn/ui |
| Frontend State/Data | React Query (TanStack Query) |
| Frontend Auth | NextAuth.js |
| Backend Framework | FastAPI (Python) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Primary Database | PostgreSQL |
| Cache & Queue | Redis |
| Object Storage | Cloudflare R2 (S3-compatible) |
| Task Scheduling | APScheduler |
| Scraping — HTTP | httpx |
| Scraping — JS-rendered pages | Playwright |
| AI / LLM | OpenAI GPT-4o / GPT-4o-mini, Anthropic Claude (fallback) |
| Notification — Chat | python-telegram-bot |
| Notification — Email | Resend / SendGrid |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Hosting — Backend | Railway / Render |
| Hosting — Frontend | Vercel |
| Hosting — Database | Supabase / Railway Managed PostgreSQL |
| Hosting — Redis | Upstash |
| Monitoring | Better Stack / UptimeRobot |

---

## FRONTEND

---

### Next.js

**Category:** Frontend Framework

**Reason for Choice**  
Next.js gives us server-side rendering for public job listing pages (important for SEO — students may discover us via Google search for "[Company] jobs"), file-based routing that maps cleanly to our page structure, and a mature React ecosystem. The App Router's server components reduce client bundle size for content-heavy pages like the jobs feed.

**Alternatives Considered**
- **Vite + React (SPA)** — Faster dev server, simpler mental model, but no SSR out of the box. Would require a separate solution for SEO on public job pages.
- **Remix** — Strong data-loading patterns, comparable SSR support. Smaller ecosystem and community at evaluation time; team had more existing Next.js experience.
- **SvelteKit** — Excellent performance characteristics, but would require the team to learn a new framework with a smaller talent pool to hire from later.

**Pros**
- SSR/SSG support improves SEO for public job pages
- File-based routing reduces boilerplate
- Huge ecosystem — most libraries have first-class Next.js support or examples
- Vercel hosting integration is effectively zero-config

**Cons**
- App Router has a steeper learning curve than the older Pages Router
- Server/client component boundary requires discipline to avoid accidentally bloating client bundles
- More opinionated than a plain Vite setup — less flexibility for unconventional architectures

---

### Tailwind CSS

**Category:** Styling

**Reason for Choice**  
Utility-first CSS lets the small frontend team iterate on UI quickly without maintaining a separate CSS file per component or fighting specificity issues. Pairs naturally with shadcn/ui, which ships Tailwind-based components by default.

**Alternatives Considered**
- **CSS Modules** — Good encapsulation, but slower iteration speed; requires writing and naming classes manually for every variant.
- **styled-components / Emotion (CSS-in-JS)** — Runtime cost on every render; conflicts with React Server Components in the App Router.
- **Plain CSS / SCSS** — Most flexible, but highest maintenance overhead at our team size.

**Pros**
- Extremely fast iteration — no context-switching between files
- Naturally produces a consistent design system via the Tailwind config (spacing scale, color palette)
- Small production CSS bundle via purging unused classes
- First-class support across the component libraries we use

**Cons**
- HTML/JSX can look visually noisy with many utility classes
- Requires discipline to avoid "utility class soup" on complex components — mitigated by extracting repeated patterns into components, not by writing custom CSS

---

### shadcn/ui

**Category:** Component Library

**Reason for Choice**  
shadcn/ui is not an npm dependency in the traditional sense — components are copied into our codebase and fully owned by us. This avoids the common problem of being blocked by a component library's release cycle or fighting its theming system. Built on Radix UI primitives, so accessibility (keyboard navigation, ARIA attributes) is handled correctly by default.

**Alternatives Considered**
- **Material UI (MUI)** — Comprehensive, but visually opinionated in a way that's hard to fully de-brand; heavier bundle.
- **Chakra UI** — Good DX, but its runtime theming approach is less compatible with React Server Components.
- **Building everything from scratch** — Maximum control, but a poor use of a small team's time for solved problems like dropdowns, modals, and comboboxes.

**Pros**
- Full ownership of component code — easy to customize without fighting an abstraction
- Built on Radix UI — accessibility handled correctly
- Tailwind-native — no separate theming system to learn
- No bundle bloat from unused components (only the ones you copy in exist in your codebase)

**Cons**
- "Copy-paste" model means no automatic upgrades — security or accessibility fixes upstream must be manually re-pulled
- Slightly more setup friction than `npm install` for a traditional component library

---

### React Query (TanStack Query)

**Category:** Data Fetching & Client State

**Reason for Choice**  
Handles caching, background refetching, loading/error states, and request deduplication out of the box. Removes the need for a separate global state management library (like Redux) for server-derived state, which covers the vast majority of our app's state needs (jobs feed, profile, saved jobs).

**Alternatives Considered**
- **Redux Toolkit + RTK Query** — Capable, but introduces more boilerplate and a steeper learning curve than needed for our scale.
- **SWR** — Comparable to React Query in philosophy; React Query was chosen for its more mature devtools and mutation handling.
- **Manual `useEffect` + `fetch`** — No caching, no automatic refetching, error-prone; ruled out immediately for anything beyond trivial one-off calls.

**Pros**
- Automatic caching and background refetching reduce unnecessary API calls
- Built-in loading/error/success states simplify component logic
- Excellent devtools for debugging cache behavior
- Mutation handling (e.g., saving a job) integrates cleanly with cache invalidation

**Cons**
- Another concept for new contributors to learn (query keys, stale time, cache invalidation)
- Can be overused for state that should just be local component state

---

### NextAuth.js

**Category:** Frontend Authentication

**Reason for Choice**  
Handles the OAuth dance with Google cleanly, including token refresh and session management on the frontend side, while still allowing us to issue and validate our own JWTs from the FastAPI backend for the email/password flow. Reduces the amount of custom OAuth code we'd otherwise have to write and maintain.

**Alternatives Considered**
- **Custom OAuth implementation** — Full control, but OAuth has many subtle security pitfalls (state validation, token storage) better left to a maintained library.
- **Auth0 / Clerk (hosted auth)** — Excellent DX, but introduces a paid third-party dependency for something we can self-host adequately at our scale, and adds external dependency for a core security function.
- **Better Auth** — A newer, promising self-hosted auth library. Evaluated but NextAuth's maturity and Google provider support were more proven at the time of this decision; worth revisiting in a future architecture review.

**Pros**
- Mature, widely used, well-documented Google OAuth provider
- Reduces custom security-sensitive code
- Integrates with our existing FastAPI JWT issuance via the credentials provider pattern

**Cons**
- Some impedance mismatch between NextAuth's session model and our backend-issued JWT model, requiring a thin adapter layer
- Less flexible than a fully custom solution if our auth requirements grow unusually complex

---

## BACKEND

---

### FastAPI

**Category:** Backend Framework

**Reason for Choice**  
FastAPI's async-native design fits naturally with the I/O-bound nature of our workload — scraping external sites, calling LLM APIs, and querying the database are all I/O operations that benefit from async handling. Automatic OpenAPI documentation generation from Pydantic models gives us API docs for free, which matters when both human engineers and future AI coding assistants need to understand the API surface quickly.

**Alternatives Considered**
- **Django + DRF** — Batteries-included, excellent admin panel out of the box, but heavier and more opinionated than needed; async support is comparatively newer and less mature than FastAPI's.
- **Flask** — Simple and flexible, but lacks native async support and built-in validation; would require bolting on Pydantic and async extensions manually.
- **Node.js + Fastify/Express** — Would unify the stack on one language (TypeScript), but the Python ecosystem's scraping libraries (BeautifulSoup, Playwright-Python) and AI/LLM SDKs are more mature and have wider community support, which matters more for this project's core value proposition than language unification.

**Pros**
- Native async/await support, ideal for I/O-heavy scraping and LLM calls
- Automatic request/response validation via Pydantic
- Automatic OpenAPI/Swagger docs generation
- Strong typing throughout, catching errors before runtime
- Excellent performance relative to other Python frameworks

**Cons**
- Smaller talent pool than Django for hiring, though growing fast
- Less batteries-included than Django — admin panel, ORM, and auth are all separate decisions (which we made deliberately, but it is more upfront decision-making)
- Async code has a learning curve for engineers used to synchronous Python

---

### SQLAlchemy 2.0 (Async)

**Category:** ORM

**Reason for Choice**  
SQLAlchemy is the most mature ORM in the Python ecosystem, with excellent support for complex queries (joins across users, jobs, skills, companies) that our matching logic requires. The 2.0 async API aligns with FastAPI's async-first design, avoiding blocking database calls in an otherwise async application.

**Alternatives Considered**
- **Prisma (via a Python client / separate Node service)** — Excellent DX and type safety, but Prisma's primary client is Node/TypeScript; using it from Python would require an awkward separate service or unofficial client, adding complexity rather than removing it.
- **Tortoise ORM** — Async-native and Django-ORM-like syntax, but smaller community and less proven at scale than SQLAlchemy.
- **Raw SQL with a thin query builder** — Maximum control and performance, but loses migration tooling integration and increases the risk of subtle bugs in complex joins.

**Pros**
- Most mature and widely adopted Python ORM
- Powerful query builder handles our complex multi-table matching queries well
- Integrates cleanly with Alembic for migrations
- Async support aligns with FastAPI

**Cons**
- More verbose than some newer ORMs (e.g., Prisma's schema-first DX)
- 2.0's API differs meaningfully from 1.x — onboarding engineers need to learn the current async patterns specifically, not legacy tutorials

---

### Alembic

**Category:** Database Migrations

**Reason for Choice**  
The standard migration tool for SQLAlchemy. Auto-generates migration scripts from model changes and supports both upgrade and downgrade paths, which is essential for safely evolving the schema as new features (resume upload, match scoring, recruiter accounts) are added over time.

**Alternatives Considered**
- **Manual SQL migration scripts** — Full control, but error-prone and loses the auto-generation benefit when models change.
- **Django migrations** — Excellent, but only available if we had chosen Django as the framework.

**Pros**
- Auto-generates migrations from SQLAlchemy model diffs
- Supports rollback (downgrade) paths
- Mature, well-documented, integrates directly with our ORM choice

**Cons**
- Auto-generated migrations sometimes need manual review/editing for non-trivial schema changes (e.g., data backfills alongside schema changes)
- Requires discipline — the constraint in `18_DECISIONS.md` that "all schema changes go through Alembic, never manual edits" must be enforced by the team, not the tool itself

---

## DATABASE & CACHING

---

### PostgreSQL

**Category:** Primary Database

**Reason for Choice**  
PostgreSQL's relational model fits our core data shape: users, jobs, companies, and skills are naturally related entities with well-defined foreign keys. JSONB columns give us flexibility to store semi-structured data (raw scraped job descriptions, AI agent outputs) without needing a separate document database. Full-text search via `tsvector` covers our search requirements without an additional search engine like Elasticsearch.

**Alternatives Considered**
- **MongoDB** — This was the initial recommendation early in the project, given the unstructured nature of scraped job data. After deeper analysis of the matching logic (which requires joining users ↔ preferences ↔ skills ↔ jobs ↔ companies across many-to-many relationships), the relational model proved clearly superior, and JSONB columns provide the document-flexibility benefit without sacrificing relational integrity. This reversal is recorded in full in `18_DECISIONS.md`.
- **MySQL** — Comparable relational capabilities, but PostgreSQL's JSONB support and full-text search are more mature, and the team had stronger existing PostgreSQL experience.

**Pros**
- Strong relational integrity for our core matching logic
- JSONB gives document-store flexibility where needed (raw scrape data, agent outputs)
- Native full-text search sufficient for MVP search needs
- Mature ecosystem (pgAdmin, extensive hosting options, well-understood operational characteristics)

**Cons**
- Vertical scaling has practical limits eventually reached at very high write volume (not a near-term concern per our scale projections in `05_ARCHITECTURE.md`)
- JSONB queries are less ergonomic than a true document database's native query language, though this tradeoff is acceptable given how little of our data is purely document-shaped

---

### Redis

**Category:** Cache & Queue

**Reason for Choice**  
Redis serves four purposes in our system — session/response caching, work queues, rate limiting, and agent-output caching — and a single Redis instance handles all of them with namespaced keys, avoiding the need for separate infrastructure for each concern. Its low latency is essential for both our rate-limiting logic (scraper politeness) and our notification queue throughput.

**Alternatives Considered**
- **Memcached** — Excellent for simple caching, but lacks the data structures (lists, sorted sets) we need for queue implementation, and has no pub/sub.
- **A dedicated message broker (RabbitMQ/SQS) from day one** — More appropriate operational complexity for a larger team or higher message volume than we have at MVP. See the explicit decision and revisit trigger in `05_ARCHITECTURE.md` Section 8.3.

**Pros**
- Versatile — covers caching, queueing, and rate limiting with one piece of infrastructure
- Extremely low latency
- Rich data structures (lists for queues, sets for dedup checks) fit our use cases directly
- Wide availability of managed hosting (Upstash) removes operational burden

**Cons**
- Primarily in-memory — requires careful sizing as data volume grows
- Not a durable queue by default — acceptable for our use case since queue items reference durable PostgreSQL records and can be safely reprocessed, but would need RabbitMQ/SQS-level guarantees if message loss became unacceptable

---

### Cloudflare R2 (Object Storage)

**Category:** Object Storage

**Reason for Choice**  
S3-compatible API means we can use standard S3 client libraries without vendor lock-in to AWS-specific tooling. R2's lack of egress fees is a meaningful cost advantage for a bootstrapped project, since resume downloads and any future scrape archive access would otherwise incur AWS's notoriously expensive egress charges.

**Alternatives Considered**
- **AWS S3** — Industry standard, but egress fees are a real cost concern for a cost-sensitive MVP (per the `<$200/month` infrastructure constraint in `01_PRD.md`).
- **Local filesystem storage** — Zero cost initially, but doesn't scale past a single server and complicates horizontal scaling of the backend.

**Pros**
- S3-compatible API — standard tooling works unmodified
- No egress fees — significant cost savings as resume downloads grow
- Simple, predictable pricing

**Cons**
- Slightly smaller ecosystem of third-party tooling compared to AWS S3 specifically
- Some advanced S3 features (certain AWS-specific integrations) are unavailable

---

## SCRAPING

---

### httpx

**Category:** HTTP Client (Scraping)

**Reason for Choice**  
`httpx` provides a modern, async-native HTTP client for Python with an API similar to `requests`, making it easy for engineers familiar with `requests` to adopt. Async support is essential since our scraper pipeline needs to make many concurrent requests across companies without blocking.

**Alternatives Considered**
- **requests** — The most familiar library, but synchronous-only; would block our async FastAPI/scheduler architecture.
- **aiohttp** — Also async-native and capable, but `httpx`'s more `requests`-like API reduces the learning curve and its built-in HTTP/2 support is convenient for modern ATS APIs.

**Pros**
- Async-native, fits our architecture
- Familiar, `requests`-like API
- Built-in HTTP/2 support
- Good timeout and retry configuration ergonomics

**Cons**
- Slightly smaller community than `requests`, though this gap has narrowed significantly

---

### Playwright (Python)

**Category:** Browser Automation (JS-Rendered Pages)

**Reason for Choice**  
Some career pages render job listings via client-side JavaScript (particularly some iCIMS and custom career page implementations) and cannot be scraped with a plain HTTP client. Playwright provides reliable headless browser automation with good handling of modern JS frameworks, and is used selectively only for adapters that require it — not as the default scraping method, to keep the common case fast and lightweight.

**Alternatives Considered**
- **Selenium** — The long-standing standard, but slower and historically more brittle with modern JS-heavy sites compared to Playwright's more modern architecture.
- **Puppeteer (Node)** — Excellent, but would require a separate Node.js scraping service, fragmenting our scraping codebase across two languages.

**Pros**
- Reliable rendering of JS-heavy career pages
- Good auto-waiting behavior reduces flaky scraping
- Single Python codebase alongside our httpx-based scrapers

**Cons**
- Significantly heavier resource footprint (a real browser instance) than HTTP-only scraping
- Slower per-request than httpx — used only where genuinely necessary, gated by the ATS Auto-Detector identifying a JS-rendered page

---

## AI / LLM

---

### OpenAI (GPT-4o / GPT-4o-mini)

**Category:** Primary LLM Provider

**Reason for Choice**  
GPT-4o provides strong structured JSON output reliability for our highest-stakes agents (Job Extractor, Skill Extractor, JD Summarizer), where extraction errors cascade through the entire pipeline. GPT-4o-mini handles the Job Classifier — a more bounded, simpler task — at a fraction of the cost, directly supporting our `<$50/month per 1,000 users` cost target from `01_PRD.md`.

**Alternatives Considered**
- **Anthropic Claude** — Comparably strong structured output and reasoning; kept as a documented fallback/secondary provider (see below) rather than primary, mainly for the team's existing tooling familiarity with OpenAI's function-calling patterns at the time of this decision.
- **Self-hosted open-source models (Llama, Mistral)** — Would eliminate per-call API cost, but requires GPU infrastructure and operational overhead disproportionate to our team size at MVP stage; revisit if LLM costs become a larger share of spend than infrastructure costs.

**Pros**
- Strong, reliable structured JSON output
- Tiered model options (4o vs. 4o-mini) let us match cost to task complexity per agent
- Mature SDK and extensive documentation
- Function-calling / structured output features reduce parsing failures

**Cons**
- Per-call cost requires active cost management (caching, model tiering) — not "set and forget"
- Vendor dependency — mitigated by keeping the `BaseAgent` interface provider-agnostic (see `05_ARCHITECTURE.md` Section 6.2), so swapping providers doesn't require touching pipeline orchestration logic

---

### Anthropic Claude (Secondary / Fallback)

**Category:** Secondary LLM Provider

**Reason for Choice**  
Configured as a fallback for resilience — if OpenAI's API experiences extended downtime or rate-limit issues during a scrape burst, agents can fail over to Claude rather than the entire pipeline stalling. Also kept available for future A/B testing of extraction quality between providers.

**Pros**
- Resilience against single-provider outages
- Comparable structured output quality, giving genuine fallback capability rather than a degraded one
- Keeps the `BaseAgent` abstraction honest — proves the interface is actually provider-agnostic, not just in theory

**Cons**
- Maintaining prompt compatibility across two providers adds minor overhead when iterating on prompts in `20_PROMPTS.md`
- Not used as primary, so receives comparatively less production traffic and real-world validation

---

## NOTIFICATIONS

---

### python-telegram-bot

**Category:** Telegram Bot Framework

**Reason for Choice**  
The most mature and widely used Python wrapper around the Telegram Bot API, with good support for webhooks (which we use in production rather than polling, per `00_PROJECT_OVERVIEW.md`'s deployment notes), inline keyboards (needed for the Apply/Save/Not Interested buttons), and command handlers (`/start`, `/pause`, `/resume`, `/settings`).

**Alternatives Considered**
- **aiogram** — Also async-native and well-regarded; `python-telegram-bot` was chosen for its larger community and more extensive documentation at evaluation time.
- **Raw HTTP calls to the Telegram Bot API** — Full control, but reimplementing webhook handling, command parsing, and inline keyboard construction from scratch is unnecessary given mature libraries exist.

**Pros**
- Mature, well-documented, large community
- Native support for inline keyboards and webhook mode
- Async-compatible with our FastAPI backend

**Cons**
- Occasional breaking changes between major versions requiring migration effort
- Some advanced Telegram Bot API features lag slightly behind official API releases

---

### Resend / SendGrid

**Category:** Email Delivery

**Reason for Choice**  
Both are evaluated as viable providers; the system is built with an abstraction layer (`notifications/email/client.py`) so either can be used without touching business logic. Resend is favored for its modern API and generous free tier suited to MVP-stage volume; SendGrid remains a documented fallback given its longer track record at higher volume, should we need to switch as we scale.

**Alternatives Considered**
- **AWS SES** — Very cheap at scale, but requires more manual reputation/deliverability management (SPF/DKIM/DMARC setup, sending domain warmup) than a managed provider, which is more setup overhead than justified at MVP scale.
- **Postmark** — Excellent deliverability reputation, but pricing is less favorable at our current low volume compared to Resend's free tier.

**Pros**
- Simple API, fast integration
- Good deliverability out of the box (less domain warmup hassle than SES)
- Provider-agnostic abstraction layer means switching later is low-risk

**Cons**
- Free tier limits will be outgrown as user base scales — cost will need to be revisited per the KPI tracking in `01_PRD.md`
- Less control over deliverability fine-tuning than a self-managed SES setup

---

## INFRASTRUCTURE & DEVOPS

---

### Docker + Docker Compose

**Category:** Containerization

**Reason for Choice**  
Docker Compose gives every engineer an identical local development environment (PostgreSQL, Redis, backend, frontend) with a single command, eliminating "works on my machine" issues. Production Docker images ensure the same artifact tested in CI is what gets deployed.

**Alternatives Considered**
- **Manual local setup (native PostgreSQL/Redis install)** — No containerization overhead, but environment drift between engineers' machines is a real and recurring problem at any team size beyond one person.
- **Nix / direnv-based reproducible environments** — Powerful and reproducible, but a much steeper learning curve for a small team versus the now-ubiquitous Docker knowledge most engineers already have.

**Pros**
- Identical environments across all engineers' machines and CI
- Same container image tested in CI is deployed to production — no build-time surprises
- Wide hosting platform support (Railway, Render, Fly.io all support Docker deployments)

**Cons**
- Adds a layer of abstraction that occasionally complicates debugging (networking between containers, volume mounts)
- Slightly slower local iteration than running services natively, mitigated by volume-mounting source code for hot-reload

---

### GitHub Actions

**Category:** CI/CD

**Reason for Choice**  
Tightly integrated with our GitHub-hosted repository, requiring no separate CI platform account or webhook configuration. Free tier minutes are sufficient for our test/build/deploy pipeline at current scale, and the YAML-based workflow definitions are well-documented and widely understood.

**Alternatives Considered**
- **GitLab CI** — Would require migrating off GitHub or running a redundant CI system, neither of which is justified.
- **CircleCI / Jenkins** — More configuration flexibility in some respects, but adds a third-party account and integration step that GitHub Actions avoids entirely for a GitHub-native repo.

**Pros**
- Zero additional account/integration setup — native to GitHub
- Free tier sufficient for current build/test volume
- Large library of pre-built actions (Docker build/push, deployment integrations)

**Cons**
- Can become costly at very high build volume (not a near-term concern)
- Workflow YAML can become unwieldy for very complex pipelines — mitigated by keeping our pipeline straightforward per `05_ARCHITECTURE.md` Section 10.2

---

### Railway / Render (Backend Hosting)

**Category:** Backend & Scheduler Hosting

**Reason for Choice**  
Both platforms offer managed PostgreSQL and Redis add-ons, Docker-based deployments, and straightforward environment variable management — covering our entire backend hosting need without requiring a dedicated DevOps hire to manage raw cloud infrastructure (e.g., a self-managed AWS ECS/EKS setup).

**Alternatives Considered**
- **AWS (EC2/ECS) directly** — Maximum control and ultimately cheaper at large scale, but requires meaningfully more DevOps expertise and time than our `1–3 person team` constraint (per `01_PRD.md` Section 14) allows for at MVP stage.
- **Heroku** — Pioneered this hosting category, but pricing has become less competitive than Railway/Render for comparable resources in recent years.

**Pros**
- Managed database and Redis add-ons reduce operational burden
- Docker-native deployments match our containerization strategy
- Reasonable pricing at MVP-stage traffic levels
- Simple environment variable and secrets management

**Cons**
- Less raw infrastructure control than self-managed cloud — acceptable tradeoff for current team size
- Costs scale less favorably than raw cloud infrastructure at very high traffic — revisit per the scaling triggers in `05_ARCHITECTURE.md` Section 12.1

---

### Vercel (Frontend Hosting)

**Category:** Frontend Hosting

**Reason for Choice**  
Built by the creators of Next.js, with effectively zero-configuration deployment, automatic preview deployments per pull request, and a global CDN edge network that directly benefits our SEO and page-load-speed NFRs (`01_PRD.md` NFR-PERF-05).

**Alternatives Considered**
- **Netlify** — Comparable static/SSR hosting capability, but Vercel's first-party Next.js integration (especially for newer App Router features) is generally more current.
- **Self-hosting Next.js on Railway/Render alongside the backend** — Would consolidate hosting providers, but loses Vercel's CDN edge advantages and zero-config preview deployments, which are valuable for a small team's review workflow.

**Pros**
- Best-in-class Next.js integration and feature support
- Automatic preview deployments per PR — speeds up review cycles
- Global CDN improves page load times for the public jobs feed
- Generous free tier for our current scale

**Cons**
- Vendor-specific optimizations create some lock-in to Vercel's platform conventions
- Serverless function cold starts can occasionally affect API routes proxied through Next.js (mitigated by keeping the FastAPI backend as the source of truth for all real logic, with Next.js API routes used only as thin proxies per `05_ARCHITECTURE.md` Section 3.1)

---

## Technology Decisions Requiring Future Review

The following choices are intentionally provisional and have explicit revisit triggers documented elsewhere in the doc suite:

| Technology | Current Choice | Revisit Trigger | Reference |
|---|---|---|---|
| Queue system | Redis lists | >50,000 notifications/day | `05_ARCHITECTURE.md` §8.3 |
| Database | Single PostgreSQL instance | Query latency degradation, >70% sustained CPU | `05_ARCHITECTURE.md` §12.1 |
| LLM provider tiering | GPT-4o / GPT-4o-mini | Cost exceeds $50/month per 1,000 users | `01_PRD.md` NFR-COST-01 |
| Backend hosting | Railway / Render | Traffic outgrows managed platform economics | `05_ARCHITECTURE.md` §12.1 |
| Auth library | NextAuth.js | If auth requirements grow significantly more custom | This document, NextAuth section |

---

*Every technology in this stack was chosen deliberately, with documented alternatives and tradeoffs. No dependency should be added to this project without first checking whether it duplicates a capability already listed here, and no listed technology should be replaced without updating this document and recording the change in `18_DECISIONS.md`.*
# 00 — Project Overview

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Product & Engineering Lead  

---

## Table of Contents

1. [Vision](#1-vision)
2. [Mission](#2-mission)
3. [Problem Statement](#3-problem-statement)
4. [Why This Product Exists](#4-why-this-product-exists)
5. [High-Level Architecture](#5-high-level-architecture)
6. [Product Goals](#6-product-goals)
7. [Target Audience](#7-target-audience)
8. [Success Metrics](#8-success-metrics)
9. [Repository Structure](#9-repository-structure)
10. [Documentation Map](#10-documentation-map)

---

## 1. Vision

> **Every relevant job opportunity should find the student — not the other way around.**

We are building the platform that eliminates the daily manual grind of job hunting for students and freshers. Instead of students checking 8 platforms every morning and still missing roles, our system works silently in the background — discovering, processing, classifying, and delivering matched job opportunities directly to them within minutes of posting.

Job Finder AI is not a job board. It is an autonomous, AI-powered job discovery and delivery engine built specifically for students and freshers who are entering the workforce for the first time.

---

## 2. Mission

To give every student — regardless of college tier, city, or network — the same early access to job opportunities that was previously only available through referrals, paid premium subscriptions, or insider connections.

We believe that discovering a job posting 8 minutes after it goes live versus 3 days later is often the difference between an interview and a rejection. Our mission is to close that gap, permanently, for every student who uses this platform.

---

## 3. Problem Statement

### 3.1 The Fragmentation Problem

Job postings do not live in one place. A single software engineering role at a mid-size company may simultaneously appear on:

- The company's own career page (always first)
- Workday / Greenhouse / Lever / iCIMS (ATS portals, minutes later)
- LinkedIn (hours to days later, after ATS sync)
- Naukri / Indeed (aggregators, days later after further syndication)

By the time most students see a role on LinkedIn or a job board, hundreds of applications may already be in the ATS queue. Early applicants are reviewed with more care. Short application queues mean higher interview conversion rates. Students who apply in the first 24 hours of a posting going live have a measurable statistical advantage — and they almost never know it.

### 3.2 The Manual Search Problem

A typical job-hunting student in their final year spends:

| Activity | Time per day |
|---|---|
| Checking LinkedIn, Naukri, Internshala | 30–45 min |
| Visiting individual company career pages | 15–30 min |
| Reading and filtering irrelevant postings | 20–30 min |
| Tracking applications across spreadsheets | 10–15 min |
| **Total daily overhead** | **75–120 minutes** |

Over a 3-month job search, this is **75–180 hours** of low-value, repetitive effort that could be fully automated.

### 3.3 The Notification Problem

Existing job platforms offer alerts, but they are:

- **Delayed** — LinkedIn job alerts fire hours or days after posting
- **Noisy** — poor matching logic floods users with irrelevant roles
- **Easily ignored** — email alerts from Naukri are widely muted
- **Generic** — no platform delivers a student-friendly summary or skill breakdown alongside the notification

Students have trained themselves to ignore job alerts because the signal-to-noise ratio is too low.

### 3.4 The Skill Gap Problem

Students often don't know if they qualify for a role without reading the full JD — which takes 5–10 minutes per job. When searching across 20+ roles per day, this is unsustainable. No existing platform gives a fast, student-friendly summary that answers:

- *What will I actually do in this job?*
- *What skills do I need?*
- *Am I qualified for this based on my profile?*
- *Is it worth spending 30 minutes on this application?*

---

## 4. Why This Product Exists

### 4.1 The Timing Insight

Internal analysis of job posting patterns shows that companies typically:

1. Post roles on their internal career page or ATS first
2. Syndicate to LinkedIn/job boards 12–72 hours later
3. Begin reviewing applications within 24 hours of posting

This means a student who applies within the first 6–12 hours of a role going live is competing against significantly fewer candidates. Most students don't know this window exists. We are building the infrastructure to capture it for them.

### 4.2 The Infrastructure Gap

The technology to automate job discovery exists — HTTP clients, LLMs, structured output parsing, Telegram bots, cron schedulers. But no one has assembled it into a student-first product that:

- Is free and accessible to any student
- Sends alerts on Telegram (the platform students actually use)
- Provides an AI-generated, human-readable job summary
- Identifies skill matches vs. gaps at a glance
- Tracks their entire application pipeline in one place

We are building that product.

### 4.3 The Telegram Insight

Consumer behavior data from student communities shows:

- Students check Telegram an average of 15–25 times per day
- Telegram communities for placement prep have 50,000–200,000+ members
- Telegram notifications have a near-100% open rate compared to ~20% for email
- Students are already accustomed to receiving job alerts via Telegram channels

We are meeting students where they already are, rather than asking them to adopt a new habit.

---

## 5. High-Level Architecture

The platform is composed of five major subsystems that work together in a continuous pipeline:

```
╔══════════════════════════════════════════════════════════════════════╗
║                        SCHEDULER LAYER                              ║
║   APScheduler — fires every 15 minutes                              ║
╚══════════════════════════════════┬═══════════════════════════════════╝
                                   │
                                   ▼
╔══════════════════════════════════════════════════════════════════════╗
║                        SCRAPER PIPELINE                             ║
║                                                                     ║
║  Company Career Page                                                ║
║         │                                                           ║
║         ▼                                                           ║
║  ATS Detector ──────────────────────────────────────────────        ║
║         │                                                           ║
║         ├──▶ Workday Adapter                                        ║
║         ├──▶ Greenhouse Adapter                                     ║
║         ├──▶ Lever Adapter                                          ║
║         ├──▶ iCIMS Adapter                                          ║
║         ├──▶ Taleo Adapter                                          ║
║         └──▶ Generic HTML Adapter (fallback)                        ║
║                                                                     ║
║  Output: Raw job objects (title, URL, location, raw_description)    ║
╚══════════════════════════════════╦═══════════════════════════════════╝
                                   ║
                                   ▼
╔══════════════════════════════════════════════════════════════════════╗
║                      AI AGENT PIPELINE                              ║
║                                                                     ║
║  [1] Duplicate Detector   → skip if already in DB                   ║
║         │                                                           ║
║  [2] Job Extractor        → structured fields from raw HTML/JSON    ║
║         │                                                           ║
║  [3] Skill Extractor      → required_skills[], preferred_skills[]   ║
║         │                                                           ║
║  [4] JD Summarizer        → 5-point student-friendly summary        ║
║         │                                                           ║
║  [5] Job Classifier       → role_type, domain, level, remote        ║
║         │                                                           ║
║  Output: Fully structured job record → saved to PostgreSQL          ║
╚══════════════════════════════════╦═══════════════════════════════════╝
                                   ║
                                   ▼
╔══════════════════════════════════════════════════════════════════════╗
║                       DATA LAYER                                    ║
║                                                                     ║
║   PostgreSQL (primary)                   Redis                      ║
║   ─────────────────────                  ──────────────────         ║
║   • users, profiles                      • Session cache            ║
║   • jobs, job_skills                     • Notification queue       ║
║   • companies                            • Scrape job queue         ║
║   • scrape_runs                          • Rate limit counters      ║
║   • notification_logs                    • Match result cache       ║
║   • user_saved_jobs                                                 ║
║                                                                     ║
║   Object Storage (S3-compatible)                                    ║
║   ──────────────────────────────                                    ║
║   • Resume PDFs                                                     ║
║   • Raw scrape archives (for debugging)                             ║
╚══════════════════════════════════╦═══════════════════════════════════╝
                                   ║
                                   ▼
╔══════════════════════════════════════════════════════════════════════╗
║                    NOTIFICATION ENGINE                              ║
║                                                                     ║
║  Matching Service                                                   ║
║  → Find all users whose profile preferences match the new job       ║
║         │                                                           ║
║         ├──▶ Telegram Dispatcher → instant push to matched users    ║
║         └──▶ Email Queue → batched for daily digest                 ║
╚══════════════════════════════════╦═══════════════════════════════════╝
                                   ║
                                   ▼
╔══════════════════════════════════════════════════════════════════════╗
║                       CLIENT LAYER                                  ║
║                                                                     ║
║   Next.js Web App                  Telegram Bot                     ║
║   ──────────────────               ─────────────────────            ║
║   • Jobs feed with filters         • Instant job alerts             ║
║   • Profile setup                  • Quick save/apply actions       ║
║   • Application tracker            • Daily digest                   ║
║   • Admin dashboard                • /start, /pause, /settings      ║
║                                                                     ║
║   FastAPI REST API (serves both clients)                            ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Key Architectural Decisions

| Decision | Choice | Reason |
|---|---|---|
| Primary Database | PostgreSQL | JSONB support, strong indexing, relational integrity for user/job data |
| Cache & Queue | Redis | Low-latency reads, pub/sub for notifications, queue for scrape jobs |
| API Framework | FastAPI (Python) | Async support, native type hints, automatic OpenAPI docs, scraper ecosystem in Python |
| Frontend | Next.js (TypeScript) | SSR for SEO, React ecosystem, Tailwind integration |
| Notification Primary | Telegram Bot | Near-100% open rate, students already there |
| LLM Calls | OpenAI GPT-4o / Claude | Structured JSON output, high extraction accuracy |
| Job Scheduling | APScheduler | Python-native, no separate infrastructure needed for MVP |
| Object Storage | S3-compatible (Cloudflare R2) | Resume PDFs, scrape archives, low egress cost |

---

## 6. Product Goals

### 6.1 User Experience Goals

- A student should be able to complete profile setup in under **5 minutes**
- A matched job notification should arrive within **30 minutes** of company posting
- A student should be able to decide if a job is relevant within **30 seconds** of reading the notification (thanks to AI summary)
- The platform should work seamlessly on a **mobile browser and Telegram** — no native app required

### 6.2 Technical Goals

- All scraper adapters must be **detection-based**, not XPath-hardcoded, so they survive minor layout changes
- All AI agent outputs must be **structured JSON** with >95% parse success rate
- Every failure — scraper error, agent failure, notification miss — must **surface as an alert**, never fail silently
- The architecture must support **50,000 users without a rewrite** — horizontal scaling possible from day one
- **LLM costs must remain under $50/month** for the first 1,000 users through aggressive caching and prompt optimization

### 6.3 Business Goals

- Reach **500 weekly active users within 3 months** of launch
- Reach **5,000 weekly active users within 12 months**
- Achieve **<5% monthly churn rate**
- Launch recruiter-facing features in Phase 3 to generate the first revenue

---

## 7. Target Audience

### Primary Users

**Students (Final Year, Engineering / MBA / any discipline)**
- Age 20–24
- Mobile-primary behavior
- Actively searching for their first job or placement
- Comfortable with Telegram
- Frustrated by manual job searching

**Freshers (0–2 years experience)**
- Age 22–26
- Mixed mobile/desktop behavior
- Looking for growth roles, switching from non-tech to tech, or building on early experience
- Prefer email digest over constant notifications

### Secondary Users

**Admins (Internal Operations)**
- Monitor scraper health and fix failures
- Review low-confidence AI extractions
- Manage the company/career page list
- Handle user reports

### Future Users (Phase 3)

**Company Recruiters**
- Post directly to reach verified student profiles
- View anonymized match statistics
- Pay per verified application or subscription

---

## 8. Success Metrics

### Phase 1 — Foundation (Month 1–2)
These metrics validate the pipeline works reliably.

| Metric | Target |
|---|---|
| Jobs scraped per day | 500+ |
| Scraper success rate | >95% per run |
| AI extraction accuracy | >95% structured output parse rate |
| Deduplication accuracy | >98% |
| Time from posting → DB insert | <30 minutes |
| Notification delivery rate | >99% (Telegram) |

### Phase 2 — Growth (Month 3–6)
These metrics validate product-market fit.

| Metric | Target |
|---|---|
| Registered users | 500+ |
| Weekly active users | 300+ |
| Profile completion rate | >70% |
| Telegram bot connection rate | >60% of registered users |
| Day-7 retention | >40% |
| Monthly churn | <5% |

### Phase 3 — Scale (Month 6–12)
These metrics validate scalability and business viability.

| Metric | Target |
|---|---|
| Weekly active users | 5,000+ |
| Jobs processed per day | 2,000+ |
| Recruiter accounts (paying) | 10+ |
| Monthly Recurring Revenue | $2,000+ |
| LLM cost per 1,000 users/month | <$50 |

---

## 9. Repository Structure

```
job-finder-ai/
│
├── README.md                   ← Quick start, setup guide
├── LICENSE
├── .gitignore
├── .env.example                ← All required env variables listed here
│
├── docs/                       ← All documentation (primary source of truth)
│   ├── 00_PROJECT_OVERVIEW.md  ← This file
│   ├── 01_PRD.md
│   ├── 02_USER_PERSONAS.md
│   ├── 03_FEATURES.md
│   ├── 04_USER_FLOWS.md
│   ├── 05_ARCHITECTURE.md
│   ├── 06_TECH_STACK.md
│   ├── 07_DATABASE.md
│   ├── 08_API.md
│   ├── 09_SCRAPER.md
│   ├── 10_AI_AGENTS.md
│   ├── 11_NOTIFICATION_SYSTEM.md
│   ├── 12_FRONTEND.md
│   ├── 13_SECURITY.md
│   ├── 14_DEPLOYMENT.md
│   ├── 15_TESTING.md
│   ├── 16_ROADMAP.md
│   ├── 17_TASKS.md
│   ├── 18_DECISIONS.md
│   ├── 19_FILE_EXPLANATIONS.md
│   ├── 20_PROMPTS.md
│   ├── 21_GLOSSARY.md
│   ├── 22_CHANGELOG.md
│   └── AI_RULES.md
│
├── .openspec/                  ← Distilled AI assistant context
│   ├── project.md
│   ├── architecture.md
│   ├── coding-standards.md
│   ├── workflow.md
│   ├── constraints.md
│   ├── ai-guidelines.md
│   └── changelog.md
│
├── backend/                    ← FastAPI application
│   ├── api/                    ← Route handlers grouped by domain
│   ├── services/               ← Business logic layer
│   ├── models/                 ← SQLAlchemy ORM models
│   ├── schemas/                ← Pydantic request/response schemas
│   ├── middleware/             ← Auth, logging, rate limiting
│   ├── config.py               ← Settings loaded from env
│   └── main.py                 ← FastAPI app entrypoint
│
├── frontend/                   ← Next.js (TypeScript + Tailwind)
│   ├── app/                    ← App Router pages
│   ├── components/             ← Reusable UI components
│   ├── lib/                    ← API client, auth, utils
│   └── types/                  ← Shared TypeScript types
│
├── scrapers/                   ← ATS-specific scraping adapters
│   ├── base_scraper.py
│   ├── ats_detector.py
│   └── adapters/               ← One file per ATS type
│
├── agents/                     ← LLM agent definitions
│   ├── base_agent.py
│   └── [one file per agent]
│
├── notifications/              ← Telegram bot + email service
│   ├── telegram/
│   └── email/
│
├── scheduler/                  ← APScheduler cron definitions
│   ├── main.py
│   └── jobs/
│
├── database/                   ← Alembic migrations + seed data
│   ├── migrations/
│   └── seeds/
│
├── tests/                      ← Unit, integration, e2e
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── scripts/                    ← Dev utilities, one-time migrations
    ├── seed_companies.py
    ├── test_scraper.py
    └── backfill_skills.py
```

---

## 10. Documentation Map

Before writing any code, read documents in this order:

| Order | Document | What It Answers |
|---|---|---|
| 1 | `00_PROJECT_OVERVIEW.md` | What are we building and why? |
| 2 | `01_PRD.md` | What exactly does it need to do? |
| 3 | `02_USER_PERSONAS.md` | Who are we building it for? |
| 4 | `03_FEATURES.md` | What are all the features and their priorities? |
| 5 | `04_USER_FLOWS.md` | How does a user experience each workflow? |
| 6 | `05_ARCHITECTURE.md` | How is the system structured? |
| 7 | `06_TECH_STACK.md` | What technologies do we use and why? |
| 8 | `07_DATABASE.md` | What is the full database schema? |
| 9 | `08_API.md` | What are all the API endpoints? |
| 10 | `09_SCRAPER.md` | How does each scraper adapter work? |
| 11 | `10_AI_AGENTS.md` | How does each AI agent work? |
| 12 | `11_NOTIFICATION_SYSTEM.md` | How are notifications sent and tracked? |
| 13 | `12_FRONTEND.md` | How is the frontend structured? |
| 14 | `13_SECURITY.md` | How is the system secured? |
| 15 | `14_DEPLOYMENT.md` | How is the system deployed? |
| 16 | `15_TESTING.md` | How is the system tested? |
| 17 | `16_ROADMAP.md` | What's the plan and timeline? |
| 18 | `17_TASKS.md` | What is the current task status? |
| 19 | `18_DECISIONS.md` | Why were key decisions made? |
| 20 | `AI_RULES.md` | What rules must AI assistants follow? |

> **Rule:** Documentation is the single source of truth.  
> If it is not in the docs, it does not exist.  
> If it exists in code but not in docs, the docs must be updated immediately.
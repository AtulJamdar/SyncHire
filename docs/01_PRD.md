# 01 — Product Requirements Document (PRD)

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Product Lead  
**Reviewers:** Engineering Lead, Design Lead  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision](#2-product-vision)
3. [Problem Statement](#3-problem-statement)
4. [Existing Solutions & Their Failures](#4-existing-solutions--their-failures)
5. [Competitor Analysis](#5-competitor-analysis)
6. [Target Users](#6-target-users)
7. [Functional Requirements](#7-functional-requirements)
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [User Stories](#9-user-stories)
10. [MVP Scope](#10-mvp-scope)
11. [Future Scope](#11-future-scope)
12. [Risks & Mitigation](#12-risks--mitigation)
13. [Assumptions](#13-assumptions)
14. [Constraints](#14-constraints)
15. [KPIs & Success Metrics](#15-kpis--success-metrics)

---

## 1. Executive Summary

Job Finder AI is a production-grade, AI-powered job discovery and delivery platform designed specifically for students and freshers entering the workforce. The platform automates the entire process of finding, extracting, classifying, and delivering relevant job opportunities — so students receive matched roles within minutes of a company posting them, rather than hours or days later through traditional job boards.

The core pipeline runs 24/7: a scheduler triggers scraper agents every 15 minutes across a growing list of company career pages and ATS portals (Workday, Greenhouse, Lever, iCIMS, Taleo, and more). Every raw job listing is processed through a sequence of AI agents that extract structured data, identify required skills, generate a student-friendly 5-point summary, and classify the role. Matched users are then notified instantly via Telegram — the platform students already use most — or via email digest.

The result is a student experience that feels almost magical: you set your profile once, and relevant job opportunities appear in your Telegram with a concise summary, a skill match breakdown, and a direct apply link — within minutes of the role going live.

**Why now:** LLM APIs (GPT-4o, Claude) now produce reliable structured JSON output from messy HTML — making AI-based job extraction accurate enough for production. Telegram Bot API is mature and free. The tools exist. The student-first product that assembles them does not. We are building it.

---

## 2. Product Vision

> **Job hunting should be something that happens to students, not something students do.**

Today, job hunting is a second job. It requires constant manual effort — checking multiple platforms daily, reading dozens of irrelevant listings, tracking applications in spreadsheets, and still missing good opportunities because they were posted and filled before the student even saw them.

We are replacing that daily grind with an autonomous system. A student creates a profile once — their skills, preferred roles, locations, and experience level. From that moment forward, the platform works on their behalf, silently and continuously: discovering new postings, summarizing them in plain language, and delivering only the relevant ones directly to the student's phone via Telegram.

The long-term vision is a world where every student — regardless of college tier, city, personal network, or whether they know how to optimize their LinkedIn — has equal, instant access to every relevant job opportunity the moment it is posted.

### Vision Pillars

**Automation First**  
Every step of job discovery, extraction, classification, and notification is automated. No human curation. No manual posting. The pipeline runs continuously, 24/7, without operator intervention.

**AI-Powered Precision**  
Generic keyword matching is not enough. We use LLMs to understand job descriptions as a human would — extracting nuanced skills, detecting seniority level, identifying remote/hybrid status, and summarizing what the role actually involves — not just what the title says.

**Student-Centric Design**  
Everything is designed for a student's context: mobile-first, Telegram-native, low friction, fast decisions. A student should be able to read a notification and decide "apply" or "skip" within 30 seconds.

**Equal Access**  
A student at a Tier-2 college in Pune should have exactly the same early access to job postings as a student at IIT Bombay with a referral connection. Early access should not be a privilege.

**Privacy by Default**  
Student data is the minimum required for matching. We never sell it. We never share it with recruiters without explicit consent. Deletion is a one-click, permanent action.

---

## 3. Problem Statement

### 3.1 The Information Delay Problem

Job postings travel through a distribution chain before reaching students:

```
Company posts role internally
        │  (0 min)
        ▼
Career page / ATS goes live
        │  (0–30 min)
        ▼
ATS syncs to LinkedIn
        │  (12–72 hours)
        ▼
LinkedIn / Naukri / Indeed surface it
        │  (additional hours for indexing)
        ▼
Student sees it in their feed
        │  (another day, after scrolling)
        ▼
Student applies
        │  (now competing with hundreds of applicants)
```

By the time a student applies via LinkedIn, the role has often been live for 2–4 days. Recruiters report that 60–70% of applications arrive in the first 48 hours. Applications received in the first 6 hours are reviewed by humans — later ones often go through ATS keyword filtering first. Early applicants face a fundamentally different, easier screening process.

### 3.2 The Fragmentation Problem

A single company with 10 open roles may post them across:
- Their own career page (primary)
- Workday or Greenhouse (their ATS)
- LinkedIn (via ATS sync)
- Naukri or Indeed (via paid integration)
- AngelList / Wellfound (for startups)
- Company Twitter / social media

There is no single source of truth. Students must monitor all of these simultaneously or miss postings. No existing tool aggregates across ATS portals + career pages + job boards with deduplication.

### 3.3 The Noise Problem

Job alerts today are designed for volume, not relevance. LinkedIn alerts fire for:
- Roles in cities the user didn't select
- Roles requiring 5+ years when the user is a fresher
- The same role posted 3 times under different job IDs
- Roles that have been closed for weeks but not removed

Students have been conditioned to ignore job alerts. The signal-to-noise ratio is too low to act on every notification — so they stop acting on any.

### 3.4 The Comprehension Problem

Reading a full job description takes 5–10 minutes. A student actively searching may encounter 20–40 listings per day. That is 2–7 hours of reading, much of it irrelevant. There is no quick-read format that answers the two questions students actually need answered:

1. *Do I qualify for this?*
2. *Is this worth 30 minutes of my application time?*

No platform currently answers these questions at the point of discovery.

### 3.5 The Tracking Problem

Students track their applications in spreadsheets or memory. There is no lightweight, purpose-built tool that lets a student see: "I have saved 23 jobs, applied to 11, heard back from 3, and have 2 jobs closing in the next 48 hours." This tracking gap leads to missed deadlines and duplicated effort.

---

## 4. Existing Solutions & Their Failures

### 4.1 LinkedIn Jobs

**What it does well:** Large database, professional context, recruiter network.

**Where it fails for students:**
- Job alerts are delayed 12–72 hours after ATS posting
- Matching algorithm favors users with complete work history (disadvantages freshers)
- No student-friendly job summary
- Premium features (InMail, who viewed your profile) are paywalled
- Notifications are generic and high-volume → students mute them

### 4.2 Naukri

**What it does well:** India-specific, large fresher job listing inventory.

**Where it fails:**
- UI is cluttered and dated
- Email alerts are widely marked as spam
- No AI summarization or skill matching
- Scraper-quality listings with outdated postings never removed
- No Telegram integration

### 4.3 Internshala

**What it does well:** Internships and entry-level jobs, student-specific.

**Where it fails:**
- Limited to internships and small companies; misses enterprise roles
- No ATS scraping; depends on companies posting directly
- Notification quality is poor
- No skill matching or JD summarization

### 4.4 Indeed / Glassdoor

**What it does well:** Global reach, company reviews alongside listings.

**Where it fails:**
- India fresher coverage is poor
- Aggregates old listings (closed roles never removed)
- No real-time alerting
- No AI summarization

### 4.5 Telegram Job Channels (Manual)

**What it does well:** Students actually read these; near-100% open rate.

**Where it fails:**
- Entirely manual — someone must find and post every role
- No personalization — same posts go to all subscribers
- No skill matching, summarization, or tracking
- Quality is inconsistent; spam is common

### 4.6 The Gap We Fill

No existing solution provides:
- Real-time scraping of company ATS portals (not waiting for LinkedIn sync)
- AI-powered extraction + classification from raw job HTML
- Student-friendly 5-point job summary delivered at the point of notification
- Skill match overlay based on student profile
- Telegram-native delivery with instant alerts
- Lightweight application tracking
- Deduplication across sources

---

## 5. Competitor Analysis

| Feature | LinkedIn | Naukri | Internshala | Indeed | Manual Telegram | **Job Finder AI** |
|---|---|---|---|---|---|---|
| Real-time ATS scraping | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| AI job summarization | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Skill match overlay | ⚠️ partial | ❌ | ❌ | ❌ | ❌ | ✅ |
| Telegram alerts | ❌ | ❌ | ❌ | ❌ | ✅ manual | ✅ automated |
| Notification quality | ⚠️ noisy | ❌ poor | ⚠️ partial | ❌ poor | ⚠️ manual | ✅ high-signal |
| Deduplication | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Application tracking | ⚠️ basic | ⚠️ basic | ❌ | ❌ | ❌ | ✅ |
| Student-first UX | ❌ | ⚠️ | ✅ | ❌ | ⚠️ | ✅ |
| Free forever | ⚠️ freemium | ⚠️ freemium | ⚠️ freemium | ✅ | ✅ | ✅ |
| India fresher focus | ⚠️ | ✅ | ✅ | ❌ | ⚠️ | ✅ |
| Time from post → alert | 12–72 hrs | 24–72 hrs | manual | 24–48 hrs | manual | **< 30 min** |

---

## 6. Target Users

### 6.1 Primary — Students

Final-year students (B.Tech, MBA, BCA, BSc, any discipline) actively searching for placement or their first full-time role. Characteristics:

- **Device:** Mobile-primary (low-to-mid range Android)
- **Platform:** Telegram heavy user (15–25 checks/day)
- **Behavior:** Applies evenings and nights; decisions made quickly on mobile
- **Pain:** Missing early windows, irrelevant alerts, no tracking system
- **Expectation:** Zero friction. Set once, receive relevant alerts, tap to apply.

### 6.2 Primary — Freshers (0–2 YOE)

Recently graduated professionals in their first or second year of work, looking to switch or grow. Characteristics:

- **Device:** Mobile + desktop (mixed)
- **Platform:** Email + Telegram
- **Behavior:** More selective; reads full JD before applying; values skill match detail
- **Pain:** Most listings say "2+ years required"; hard to filter truly entry-level roles
- **Expectation:** Curated, high-quality matches. Email digest acceptable.

### 6.3 Secondary — Admins

Internal platform operators. One or two people responsible for:
- Keeping scrapers healthy
- Reviewing AI extraction errors
- Managing the company list
- Monitoring notification delivery

### 6.4 Future — Recruiters (Phase 3)

Company hiring managers or HR professionals who want:
- Verified student profiles to source from
- Direct posting to reach fresher candidates
- Subscription-based access to applicant pool

---

## 7. Functional Requirements

### 7.1 Authentication & Access

| Req ID | Requirement | Priority |
|---|---|---|
| FR-AUTH-01 | System must support email + password registration with email verification | P0 |
| FR-AUTH-02 | System must support Google OAuth as an alternative login method | P0 |
| FR-AUTH-03 | System must issue JWT access tokens (15 min TTL) and refresh tokens (7 days TTL) | P0 |
| FR-AUTH-04 | Refresh tokens must be stored in httpOnly cookies, not localStorage | P0 |
| FR-AUTH-05 | System must support password reset via time-limited email token (1 hour TTL) | P1 |
| FR-AUTH-06 | System must support permanent account deletion with a 30-day grace period | P1 |
| FR-AUTH-07 | Admin role must be enforced server-side on all admin endpoints | P0 |
| FR-AUTH-08 | All protected endpoints must return 401 on missing/expired token, 403 on insufficient role | P0 |

### 7.2 Student Profile

| Req ID | Requirement | Priority |
|---|---|---|
| FR-PROF-01 | User must be able to select multiple skills from a searchable canonical list | P0 |
| FR-PROF-02 | User must be able to select multiple preferred job role types | P0 |
| FR-PROF-03 | User must be able to select preferred locations (multi-city) and remote/hybrid preference | P0 |
| FR-PROF-04 | User must be able to set their experience level (Fresher / 0–1yr / 1–2yr / 2–3yr) | P0 |
| FR-PROF-05 | User must be able to enter education details (degree, branch, college, year) | P1 |
| FR-PROF-06 | User must be able to upload a resume PDF (max 5MB) | P2 |
| FR-PROF-07 | System must extract skills from uploaded resume via AI agent | P2 |
| FR-PROF-08 | User must be able to set notification channel preference (Telegram / Email / Both) | P1 |
| FR-PROF-09 | User must be able to set quiet hours (no notifications between time X and time Y) | P1 |
| FR-PROF-10 | Profile changes must take effect on the next scheduled notification run | P0 |

### 7.3 Job Discovery & Scraping

| Req ID | Requirement | Priority |
|---|---|---|
| FR-SCRP-01 | System must scrape Workday career pages and extract job listings | P0 |
| FR-SCRP-02 | System must scrape Greenhouse career pages and extract job listings | P0 |
| FR-SCRP-03 | System must scrape Lever career pages and extract job listings | P0 |
| FR-SCRP-04 | System must scrape iCIMS career pages and extract job listings | P0 |
| FR-SCRP-05 | System must scrape Taleo career pages and extract job listings | P0 |
| FR-SCRP-06 | System must auto-detect which ATS a career page uses before selecting adapter | P0 |
| FR-SCRP-07 | System must check robots.txt before scraping and skip disallowed paths | P0 |
| FR-SCRP-08 | System must rate-limit scrape requests to a maximum of 1 request per 3 seconds per domain | P0 |
| FR-SCRP-09 | System must retry failed scrape requests up to 3 times with exponential backoff | P0 |
| FR-SCRP-10 | System must detect CAPTCHA responses and skip + alert admin rather than crash | P1 |
| FR-SCRP-11 | System must log every scrape run (company, status, jobs found, jobs new, errors, duration) | P0 |
| FR-SCRP-12 | System must run scrape batches on a 15-minute schedule via APScheduler | P0 |
| FR-SCRP-13 | Scraper must update company.last_scraped_at after every run (success or failure) | P0 |
| FR-SCRP-14 | System must support a fallback generic HTML adapter for career pages with unknown ATS | P1 |

### 7.4 AI Agent Pipeline

| Req ID | Requirement | Priority |
|---|---|---|
| FR-AGNT-01 | Duplicate Detector must hash job URL + title + company and skip existing records | P0 |
| FR-AGNT-02 | Job Extractor must produce: title, company, location, salary_range, deadline, apply_url, raw_description | P0 |
| FR-AGNT-03 | Job Extractor output must be valid JSON; parse failures must be logged and retried once | P0 |
| FR-AGNT-04 | Skill Extractor must return required_skills[] and preferred_skills[] arrays | P0 |
| FR-AGNT-05 | JD Summarizer must return exactly 5 bullet points in plain student-friendly language | P0 |
| FR-AGNT-06 | Job Classifier must return: role_type, domain, experience_level, is_remote, is_internship | P0 |
| FR-AGNT-07 | All agent calls must be logged (prompt hash, model, latency, status, output) in agent_logs | P0 |
| FR-AGNT-08 | Jobs with extraction_confidence below 0.75 must be flagged for admin review | P1 |
| FR-AGNT-09 | Agents must use cached results when the same raw_description hash is seen within 24 hours | P1 |
| FR-AGNT-10 | All agent prompts must be defined in docs/20_PROMPTS.md and loaded from config, not hardcoded | P0 |

### 7.5 Job Listings Feed (Frontend)

| Req ID | Requirement | Priority |
|---|---|---|
| FR-JOBS-01 | Frontend must display paginated job listings sorted by company_posted_at descending | P0 |
| FR-JOBS-02 | Frontend must support filtering by role_type, location, experience_level, is_remote | P0 |
| FR-JOBS-03 | Frontend must support full-text keyword search across job title and description | P1 |
| FR-JOBS-04 | Each job card must display: company, title, location, time since posted, required skills chips | P0 |
| FR-JOBS-05 | Each job detail view must display the AI-generated 5-point summary prominently | P0 |
| FR-JOBS-06 | "Posted X minutes ago" must use company_posted_at, not the platform's scraped_at | P0 |
| FR-JOBS-07 | Apply button must open the original ATS application URL in a new tab | P0 |
| FR-JOBS-08 | User must be able to save a job (bookmark) from the card or detail view | P1 |
| FR-JOBS-09 | User must be able to mark a job as applied, rejected, or offer | P1 |
| FR-JOBS-10 | Jobs closing within 48 hours must display a "Closing Soon" badge | P2 |

### 7.6 Notification System

| Req ID | Requirement | Priority |
|---|---|---|
| FR-NOTIF-01 | System must send a Telegram message when a new job matches a user's profile | P0 |
| FR-NOTIF-02 | Telegram message must include: title, company, location, time posted, 5-point summary, apply link | P0 |
| FR-NOTIF-03 | Telegram message must include quick-action buttons: Apply, Save, Not Interested | P1 |
| FR-NOTIF-04 | System must respect user quiet hours when scheduling Telegram notifications | P1 |
| FR-NOTIF-05 | System must send a daily digest email with all matched jobs from the past 24 hours | P1 |
| FR-NOTIF-06 | System must log every notification attempt (user, job, channel, status, timestamp) | P0 |
| FR-NOTIF-07 | Failed notifications must be retried up to 3 times before being marked failed | P1 |
| FR-NOTIF-08 | All email notifications must include a one-click unsubscribe link | P1 |
| FR-NOTIF-09 | Telegram bot must support /start, /pause, /resume, /settings commands | P1 |

### 7.7 Admin Dashboard

| Req ID | Requirement | Priority |
|---|---|---|
| FR-ADMN-01 | Admin must see a health table: all companies, last scrape time, status, error count | P0 |
| FR-ADMN-02 | Admin must be able to add a new company with career page URL and ATS type | P0 |
| FR-ADMN-03 | Admin must be able to deactivate a company (pauses scraping) | P0 |
| FR-ADMN-04 | Admin must see a queue of jobs flagged for low-confidence extraction | P1 |
| FR-ADMN-05 | Admin must be able to approve or reject flagged jobs from the review queue | P1 |
| FR-ADMN-06 | Admin must see a list of all registered users with registration date and activity status | P1 |
| FR-ADMN-07 | Admin must be able to suspend or permanently delete a user account | P1 |
| FR-ADMN-08 | Admin must be able to trigger a manual scrape for a specific company | P2 |
| FR-ADMN-09 | Admin must receive a Telegram alert when any scraper fails 3+ consecutive runs | P1 |

---

## 8. Non-Functional Requirements

### 8.1 Performance

| Req ID | Requirement | Target |
|---|---|---|
| NFR-PERF-01 | API response time for job listing endpoints | p95 < 500ms |
| NFR-PERF-02 | API response time for job detail endpoint | p95 < 300ms |
| NFR-PERF-03 | Time from job posting on career page to DB insert | < 30 minutes |
| NFR-PERF-04 | Time from DB insert to Telegram notification sent | < 2 minutes |
| NFR-PERF-05 | Frontend initial page load (LCP) | < 2.5 seconds on 4G |
| NFR-PERF-06 | Database query time for paginated job feed | < 100ms with index |

### 8.2 Reliability

| Req ID | Requirement | Target |
|---|---|---|
| NFR-REL-01 | API uptime | > 99.5% monthly |
| NFR-REL-02 | Scraper pipeline success rate per run | > 95% |
| NFR-REL-03 | Notification delivery success rate | > 99% (Telegram) |
| NFR-REL-04 | AI agent structured output parse success rate | > 95% |
| NFR-REL-05 | No silent failures — all errors must be logged and alerted | Mandatory |

### 8.3 Scalability

| Req ID | Requirement |
|---|---|
| NFR-SCAL-01 | Architecture must support 50,000 users without a structural rewrite |
| NFR-SCAL-02 | Scraper workers must be horizontally scalable (stateless, queue-driven) |
| NFR-SCAL-03 | Database queries must be index-optimized for the expected query patterns |
| NFR-SCAL-04 | Redis queues must handle notification bursts of 10,000+ messages in a single batch |

### 8.4 Security

| Req ID | Requirement |
|---|---|
| NFR-SEC-01 | All passwords must be hashed with bcrypt (min cost factor 12) |
| NFR-SEC-02 | All API endpoints must validate input with Pydantic schemas |
| NFR-SEC-03 | Rate limiting must be applied to all auth endpoints (5 req/min per IP) |
| NFR-SEC-04 | All sensitive data (passwords, tokens) must never appear in logs |
| NFR-SEC-05 | HTTPS must be enforced in production; HTTP requests must redirect |
| NFR-SEC-06 | CORS must be restricted to the frontend origin in production |
| NFR-SEC-07 | Student resume files must be stored in private object storage (no public URLs) |
| NFR-SEC-08 | LLM API keys and database credentials must be environment variables, never in code |

### 8.5 Maintainability

| Req ID | Requirement |
|---|---|
| NFR-MAINT-01 | Every AI prompt must be defined in docs/20_PROMPTS.md, versioned, and loaded from config |
| NFR-MAINT-02 | All database changes must be applied via Alembic migrations, never manual edits |
| NFR-MAINT-03 | Every scraper adapter must implement the BaseScraper interface |
| NFR-MAINT-04 | Every AI agent must implement the BaseAgent interface |
| NFR-MAINT-05 | Code coverage must stay above 70% for all service-layer code |
| NFR-MAINT-06 | All environment variables must be documented in .env.example |

### 8.6 Cost

| Req ID | Requirement | Target |
|---|---|---|
| NFR-COST-01 | LLM API cost per 1,000 active users per month | < $50 |
| NFR-COST-02 | LLM calls for identical raw_description must be cached for 24 hours | Mandatory |
| NFR-COST-03 | Cheapest model capable of the task must be used per agent (not defaulting to GPT-4o everywhere) | Mandatory |

---

## 9. User Stories

### 9.1 Student / Fresher Stories

#### Onboarding

| ID | Story | Acceptance Criteria | Priority |
|---|---|---|---|
| US-01 | As a student, I want to create an account with my email and password so that I can access the platform. | Registration form works. Verification email sent. Account inactive until verified. | P0 |
| US-02 | As a student, I want to sign up using Google so that I don't have to create another password. | Google OAuth flow completes. Account created. Redirected to profile setup. | P0 |
| US-03 | As a student, I want to set up my skill profile so that the platform can match jobs to me. | Skill multi-select works. Minimum 1 skill required. Saved to DB on submit. | P0 |
| US-04 | As a student, I want to set my preferred job roles and locations so that I only receive relevant alerts. | Role type and location multi-select works. At least 1 of each required. | P0 |
| US-05 | As a student, I want to connect my Telegram account so that I receive instant job alerts. | Bot link generated. /start command in bot links Telegram ID to account. Confirmation message sent. | P0 |

#### Job Discovery

| ID | Story | Acceptance Criteria | Priority |
|---|---|---|---|
| US-06 | As a student, I want to receive a Telegram message when a matching job is posted so that I can apply early. | Message arrives within 30 min of posting. Includes title, company, location, summary, apply link. | P0 |
| US-07 | As a student, I want to see a 5-point plain-English summary in the notification so that I can decide in 30 seconds. | Summary present in both Telegram message and job detail page. Max 5 bullets, plain language. | P0 |
| US-08 | As a student, I want to see "Posted 8 minutes ago" on a job so that I know I'm applying early. | Timestamp uses company_posted_at, not scraped_at. Displays relative time. | P0 |
| US-09 | As a student, I want to browse a filtered job feed on the website so that I can search manually too. | Filter by role, location, experience level, remote works. Results update without page reload. | P0 |
| US-10 | As a student, I want to see which of my skills match the job so that I can quickly assess fit. | Required skills chips displayed. Skills matching user profile highlighted differently. | P1 |

#### Application Tracking

| ID | Story | Acceptance Criteria | Priority |
|---|---|---|---|
| US-11 | As a student, I want to save a job so that I can apply to it later. | Save button works. Job appears in "My Jobs" → Saved tab. | P1 |
| US-12 | As a student, I want to mark a job as applied so that I don't lose track. | Status updates to "Applied". Visible in My Jobs tracker. | P1 |
| US-13 | As a student, I want to see all my saved and applied jobs in one place so that I have a pipeline view. | My Jobs page shows Saved / Applied / Interviewing / Rejected / Offer states. | P1 |
| US-14 | As a student, I want to get a reminder before a saved job closes so that I don't miss the deadline. | Reminder sent via Telegram/email 48h before deadline if job is saved. | P2 |

#### Preferences

| ID | Story | Acceptance Criteria | Priority |
|---|---|---|---|
| US-15 | As a student, I want to set quiet hours so that I'm not notified at 2 AM. | Quiet hours stored. No notifications sent between those hours. Queued and sent after window. | P1 |
| US-16 | As a student, I want to pause all notifications when I'm in exams so that I'm not distracted. | /pause Telegram command works. Notifications resume on /resume or after set date. | P1 |
| US-17 | As a student, I want to receive a weekly email digest so that I can review the week's best matches. | Digest email sent every Monday. Contains top 10 matches from the past 7 days. | P2 |

### 9.2 Admin Stories

| ID | Story | Acceptance Criteria | Priority |
|---|---|---|---|
| UA-01 | As an admin, I want to see the health of all scrapers so that I know if anything is broken. | Dashboard table shows company name, last run time, status (success/fail), error count. | P0 |
| UA-02 | As an admin, I want to add a new company to the scrape list so that we cover more job sources. | Form accepts company name, career URL, ATS type. System validates URL and runs ATS detection. | P0 |
| UA-03 | As an admin, I want to receive a Telegram alert when a scraper fails 3 times in a row so that I can fix it quickly. | Alert sent automatically after 3 consecutive failures. Includes company name and error reason. | P1 |
| UA-04 | As an admin, I want to review jobs the AI wasn't confident about so that no bad data reaches students. | Flagged jobs queue shows raw extraction + AI output. One-click approve/reject. | P1 |
| UA-05 | As an admin, I want to trigger a manual scrape for a specific company so that I can test changes. | "Run now" button per company in admin. Run starts within 30 seconds. Result shown in health table. | P2 |

---

## 10. MVP Scope

The MVP is the minimum set of features that proves the core value proposition: **a student sets up a profile once and receives matched job alerts on Telegram within 30 minutes of posting.**

### MVP Includes (Phase 1 + Phase 2)

**Infrastructure**
- PostgreSQL database with full schema
- Redis for caching and notification queue
- FastAPI backend with all P0 endpoints
- Next.js frontend with jobs feed and profile setup
- Docker-based local development environment

**Authentication**
- Email + password registration with verification
- Google OAuth
- JWT session management
- Admin role

**Student Profile**
- Skills multi-select
- Preferred roles + locations
- Experience level
- Telegram bot connection
- Notification preferences

**Scraper Pipeline**
- ATS auto-detector
- Workday adapter
- Greenhouse adapter
- Lever adapter
- iCIMS adapter
- Taleo adapter
- APScheduler running every 15 minutes
- Scrape run logging

**AI Agent Pipeline**
- Duplicate Detector
- Job Extractor
- Skill Extractor
- JD Summarizer (5 points)
- Job Classifier
- Agent logging

**Jobs Feed**
- Paginated, filterable job listings
- Job detail with AI summary
- "Posted X ago" using company timestamp
- Direct apply link (external)

**Notifications**
- Telegram instant alert with summary + apply link
- Daily email digest
- Notification delivery logging

**Admin Dashboard**
- Scraper health table
- Add/remove companies
- Low-confidence job review queue (basic)
- Telegram admin alert on scraper failure

### MVP Excludes (Explicitly)

- Resume upload and AI skill extraction
- Match score percentage
- Application tracker (save/apply/track)
- Recruiter portal
- Weekly email digest
- SmartRecruiters, BreezyHR, JazzHR, Ashby adapters
- Mobile native app
- Chrome extension

---

## 11. Future Scope

### Phase 3 (Month 6–9)

**Resume Intelligence**
- Upload PDF resume → AI extracts skills, education, experience
- Auto-populate profile on upload
- "Your resume vs. job requirements" gap analysis

**Match Score**
- Per-job match percentage based on skill overlap, experience level, location
- Displayed on job cards and in Telegram notifications
- "Why this matched you" explanation

**Advanced Tracking**
- Kanban-style application pipeline (Saved → Applied → Interview → Offer/Rejected)
- Interview date tracking with calendar reminder
- Offer comparison view

**More ATS Adapters**
- SmartRecruiters
- BreezyHR
- JazzHR
- Ashby
- SAP SuccessFactors
- Oracle HCM

### Phase 4 (Month 9–12)

**Recruiter Portal**
- Company accounts to post directly
- Reach verified student profiles
- Subscription billing (Stripe)
- Applicant pool analytics (anonymized)

**College Integration**
- Placement officer dashboard
- Batch notifications to specific college cohorts
- Company-college relationship management

### Phase 5 (Month 12+)

**AI Career Coach**
- Interview prep questions generated from JD
- Resume tailoring suggestions per job
- Cover letter draft based on user profile + JD

**Browser Extension**
- One-click save from any career page
- Auto-detect and extract job data from current page
- Push to Job Finder AI pipeline

---

## 12. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation Strategy |
|---|---|---|---|
| ATS layout changes break scraper adapters | High | High | Detection-based adapters (not XPath-hardcoded). Weekly automated health checks. Admin alert on failure. Manual fallback. |
| LLM API produces invalid JSON output | Medium | Medium | Retry once on parse failure. Log all failures. Flag for admin review if 2nd attempt fails. Confidence scoring. |
| CAPTCHA blocks scrapers | Medium | High | Detect CAPTCHA response codes. Skip and alert admin. Do not crash pipeline. Consider Playwright for JS-heavy pages. |
| LLM cost exceeds budget | Medium | Medium | Cache results by raw_description hash (24h TTL). Use GPT-4o-mini for classification; GPT-4o only for extraction. Monitor cost per 1k users weekly. |
| False positive matches (wrong users notified) | Medium | Medium | Require minimum 2 matching preferences (role type + skill or location). Add "Not Interested" feedback loop. A/B test matching thresholds. |
| Student data breach | Low | Critical | Encrypt at rest (PostgreSQL). Private object storage for resumes. Minimal data collection. RBAC. Audit logs. Pen test before launch. |
| Telegram Bot API downtime | Low | Medium | Log all queued notifications. Retry queue. Email as fallback for P0 matches. |
| robots.txt violations causing legal issues | Low | High | Check robots.txt before every scrape run. Skip disallowed paths. Log compliance check results. |
| Scraper runs silently fail (no alert) | Medium | High | Mandatory: all errors logged and surfaced. Scraper health dashboard. Telegram alert after 3 consecutive failures. |
| User acquisition slower than projected | Medium | Medium | Focus on organic Telegram community distribution. Referral incentive in Phase 2. College ambassador program. |

---

## 13. Assumptions

| ID | Assumption |
|---|---|
| A-01 | The majority of target companies use one of the 5 supported ATS types (Workday, Greenhouse, Lever, iCIMS, Taleo) — covering estimated 70–80% of the target company list |
| A-02 | Telegram Bot API will remain free and available at current rate limits throughout the MVP phase |
| A-03 | LLM APIs (OpenAI / Anthropic) will remain accessible at current pricing for the first 12 months |
| A-04 | Company career pages do not aggressively block scrapers operating within rate limits and robots.txt compliance |
| A-05 | Students are willing to connect their Telegram account and grant the bot message permissions |
| A-06 | A single VPS or managed platform (Railway / Render) will be sufficient infrastructure for the first 1,000 users |
| A-07 | PostgreSQL JSONB columns will be sufficient for structured job data without requiring a separate document store |
| A-08 | The initial company list (100–200 companies) can be seeded manually before launching to users |
| A-09 | GPT-4o produces >95% valid structured JSON when given the extraction prompts in docs/20_PROMPTS.md |
| A-10 | The engineering team is 1–3 people during Phase 1 and 2 |

---

## 14. Constraints

### Technical Constraints

| Constraint | Detail |
|---|---|
| Language | Backend: Python. Frontend: TypeScript. No exceptions without a decision record in docs/18_DECISIONS.md. |
| Database | PostgreSQL only. No MongoDB. No other primary DB without a decision record. |
| Scraping ethics | Must comply with robots.txt. Must rate-limit to 1 req/3s per domain. No storing personally identifiable recruiter data. |
| AI prompts | All prompts must live in docs/20_PROMPTS.md. Zero hardcoded prompts in application code. |
| Migrations | All schema changes via Alembic. No direct DB edits in production. Ever. |

### Legal Constraints

| Constraint | Detail |
|---|---|
| GDPR alignment | User data must be deletable on request. No data retention beyond what's needed for the service. |
| robots.txt compliance | All scrapers must fetch and parse robots.txt before scraping. Disallowed paths must be skipped and logged. |
| No PII of recruiters | Job data may include recruiter names from JD text. These must not be stored as searchable/indexed fields. |
| No unauthorized apply | The platform links to external apply pages. It never submits applications on a user's behalf without explicit action. |

### Business Constraints

| Constraint | Detail |
|---|---|
| Cost ceiling | Total infrastructure + LLM API cost must remain under $200/month for the first 1,000 users. |
| Team size | Phase 1 and 2 are built by a team of 1–3. No architecture that requires a dedicated DevOps engineer to operate. |
| Timeline | MVP (Phase 1 + 2) must be completable in 8–10 weeks by a small team. |

---

## 15. KPIs & Success Metrics

### 15.1 Pipeline Health KPIs (Technical)

These are monitored continuously via the admin dashboard and automated alerts.

| KPI | Target | Measurement |
|---|---|---|
| Jobs scraped per day | 500+ | scrape_runs table aggregate |
| Scraper success rate per run | >95% | scrape_runs.status = 'success' / total |
| AI extraction parse success rate | >95% | agent_logs.status = 'success' / total |
| Deduplication catch rate | >98% | Duplicate Detector skip count / repeat URL count |
| Time from posting → DB insert | <30 minutes | jobs.scraped_at - jobs.company_posted_at |
| Time from DB insert → notification | <2 minutes | notification_logs.sent_at - jobs.scraped_at |
| Notification delivery success | >99% | notification_logs.status = 'delivered' / total |
| LLM cost per 1,000 users/month | <$50 | OpenAI usage dashboard |

### 15.2 User Growth KPIs (Product)

Reviewed weekly.

| KPI | Month 1 Target | Month 3 Target | Month 6 Target |
|---|---|---|---|
| Total registered users | 50+ | 500+ | 2,000+ |
| Weekly active users | 30+ | 300+ | 1,500+ |
| Profile completion rate | >60% | >70% | >75% |
| Telegram bot connection rate | >50% | >60% | >65% |
| Day-1 retention | >60% | >65% | >70% |
| Day-7 retention | >30% | >40% | >45% |
| Monthly churn | <10% | <5% | <4% |

### 15.3 Engagement KPIs (Behavior)

Reviewed monthly.

| KPI | Target | Notes |
|---|---|---|
| Notification open rate (Telegram) | >70% | Telegram read receipts (where available) |
| Notification click-through rate | >30% | Apply link taps per notification |
| Jobs saved per active user per week | >3 | user_saved_jobs aggregate |
| "Not Interested" rate per notification | <20% | Signal for matching quality |

### 15.4 Business KPIs (Phase 3+)

| KPI | Month 9 Target | Month 12 Target |
|---|---|---|
| Recruiter accounts (paying) | 5+ | 15+ |
| Monthly Recurring Revenue | $500+ | $2,000+ |
| Average Revenue Per Account | $100/mo | $150/mo |

---

*This document is the source of truth for what Job Finder AI must do and why. All feature decisions, architecture decisions, and prioritization calls must be traceable back to a requirement or user story in this document. If a requirement changes, this document is updated first.*
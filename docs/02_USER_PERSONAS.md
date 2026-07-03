# 02 — User Personas

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Product Lead  

---

## Purpose of This Document

User personas are the human anchor for every product, design, and engineering decision. Every feature we build, every notification we send, every loading state we choose — there is a real person on the other side of it. This document defines who that person is.

Personas are not marketing archetypes. They are grounded in the actual behaviors, frustrations, goals, and technical realities of the people we are building for. Before making any product decision, ask: *Which persona does this serve, and does it genuinely make their life easier?*

---

## Persona Index

| # | Persona | Type | Priority |
|---|---|---|---|
| 1 | [Aarav Shah](#persona-1--aarav-shah) | Final-Year Engineering Student | Primary |
| 2 | [Priya Menon](#persona-2--priya-menon) | MBA Fresher | Primary |
| 3 | [Rahul Verma](#persona-3--rahul-verma) | Self-Taught Developer (0 YOE) | Primary |
| 4 | [Sneha Kulkarni](#persona-4--sneha-kulkarni) | Experienced Developer (1–2 YOE) | Primary |
| 5 | [Karan Mehta](#persona-5--karan-mehta) | Internal Admin / Ops | Secondary |
| 6 | [Divya Nair](#persona-6--divya-nair) | Company Recruiter | Future (Phase 3) |

---

## Persona 1 — Aarav Shah

### The Placement-Hungry CS Student

```
Name         : Aarav Shah
Age          : 21
Location     : Nagpur, Maharashtra
Education    : B.Tech Computer Science, Final Year — Tier-2 Engineering College
GPA          : 7.8 / 10
Experience   : 1 internship (Django + PostgreSQL, 2 months, startup)
Device       : Redmi Note 12 (Android) — primary | College lab Windows PC — secondary
Internet     : 4G mobile data at home, college WiFi in labs
Monthly data : 2–3 GB/month on the phone
```

---

### Background

Aarav is 8 months away from graduation and genuinely anxious about placement. His college has a placement cell, but it only invites companies in October — and many of the best roles go to IIT/NIT candidates via referrals before campus drives even happen. Aarav knows he needs to apply directly through company career pages, but he doesn't know where to start.

He has built 3 portfolio projects: a task manager in Django, a REST API with FastAPI, and a React frontend for a college fest. He knows Python well, has touched React, and is comfortable with SQL. He is not strong in data structures and algorithms by competitive programming standards, but he can solve most LeetCode medium problems with time.

He checks LinkedIn every morning. He has applied to 40+ jobs in the past 2 months. He has heard back from 3. He doesn't know if his resume is being rejected by ATS filters or if he's simply applying too late.

---

### Goals

| Priority | Goal | Why It Matters |
|---|---|---|
| 1 | Get a full-time software engineering job before graduation | Financial pressure. First in family to work in tech. |
| 2 | Apply to roles within the first 24 hours of posting | Suspects (correctly) that early applicants get more attention |
| 3 | Know which companies are actively hiring freshers right now | Most companies he finds are not hiring; filters need to be better |
| 4 | Understand quickly if a role fits his skill set | Doesn't want to waste 45 minutes applying to a role he doesn't qualify for |
| 5 | Track where he has applied so he doesn't duplicate effort | Currently doing this in a Google Sheet; losing track |

---

### Pain Points

**Pain 1 — The Discovery Lag**
Aarav gets LinkedIn job alerts. By the time he reads them — usually the next morning — the role has been live for 18–36 hours and already has 200+ applicants. He has no idea there is a 6–12 hour early window on the company's career page before LinkedIn even indexes the role.

**Pain 2 — The Irrelevance Flood**
LinkedIn alerts send him roles requiring 3+ years of experience, roles in cities he didn't select, and the same role posted 4 times with different job IDs. He has muted most alert emails. He still checks manually, but it's exhausting.

**Pain 3 — The Comprehension Bottleneck**
He opens a job posting. It's 800 words. He reads the first paragraph, skims the requirements, and spends 5–7 minutes trying to decide if he qualifies. At 20 listings per day, that's 100–140 minutes of reading, much of it to reach the conclusion "not for me."

**Pain 4 — The Tracking Mess**
He tracks applications in a Google Sheet. He has 47 rows. He has forgotten which ones he already applied to, which ones he skipped, and which ones have upcoming deadlines. He has missed 2 application deadlines because he forgot.

**Pain 5 — The Confidence Uncertainty**
He doesn't know if his resume passes ATS filters. He doesn't know if a "Python required" role wants basic scripting or deep async frameworks. The job descriptions don't clearly say, and he has no tool to help him parse that.

---

### Technical Skill Level

| Area | Level | Notes |
|---|---|---|
| Python | Intermediate | Django, FastAPI, basic async |
| JavaScript / React | Beginner-Intermediate | Built 1 project; not production-level |
| SQL / PostgreSQL | Intermediate | Can write joins, basic indexing |
| Git | Basic | Commits, branches; no advanced workflows |
| Linux / Terminal | Basic | Can navigate, run commands |
| System Design | Beginner | Not studied formally |
| DSA / LeetCode | Beginner-Intermediate | ~60–70% Medium success rate |
| Cloud / AWS | None | Has heard of it; never used |

---

### Behavior Patterns

**Morning (8–9 AM):** Opens LinkedIn on the toilet. Skims job feed for 10 minutes. Opens 2–3 roles in browser tabs. Forgets about them by the time he sits down to study.

**Afternoon (2–4 PM):** College labs. Occasionally checks Naukri or company websites when not in class. Mostly distracted.

**Evening (6–9 PM):** Most productive job search time. Applies to 1–3 jobs per evening. Reads JDs more carefully. Writes cover letters when required (rarely).

**Night (10 PM – 1 AM):** Active on Telegram — developer communities, meme groups, placement prep channels. Reads messages from Telegram job channels but finds them generic and often outdated.

**Telegram usage:** 20–30 opens per day. Has notifications on for most groups. Reads quickly and responds fast.

**Decision style:** Fast. If a notification tells him what he needs to know in 10 lines, he will decide and act. If he has to open a browser, scroll, and read for 5 minutes, he will "do it later" — which usually means never.

---

### Journey with Job Finder AI

```
Week 1 — Discovery
Aarav sees a post in a Telegram placement prep group:
"This bot sent me a Google SWE role 9 minutes after it was posted.
 I applied same day. Got an interview."
He clicks the link.

Week 1 — Onboarding (Day 1)
Signs up with Google (one click). Sets skills: Python, FastAPI, React, PostgreSQL.
Preferred roles: Software Engineer, Backend Developer.
Location: Pune, Bengaluru, Remote.
Experience: Fresher.
Connects Telegram bot: scans QR, clicks /start, receives confirmation.
Total time: 4 minutes.

Week 1 — First Notification (Day 2, 7:43 AM)
Telegram message arrives while he's brushing his teeth:

  🚀 New Match — Software Engineer (Backend)
  Razorpay · Bengaluru · Hybrid
  Posted 11 minutes ago

  📋 What you'll do:
  • Build payment APIs used by 10M+ merchants
  • Own backend services in Python + Go
  • Work on high-throughput distributed systems
  • 0–2 years experience required
  • Strong Python fundamentals needed

  Skills: Python ✅  PostgreSQL ✅  Go ❌  Redis ❌

  [Apply Now]  [Save]  [Not Interested]

He reads it in 25 seconds. Taps "Apply Now."
Opens career page directly. Applies before 8 AM.

Week 2 — Habit Formed
He stops checking LinkedIn in the morning.
He opens Telegram and his matches are already waiting.
Applied to 9 jobs in 7 days. All within 30 minutes of posting.

Week 6 — Result
Razorpay schedules a phone screen.
It is the role he applied to on Day 2.
```

---

### Expected Experience

| Moment | Expectation |
|---|---|
| Onboarding | Under 5 minutes. No lengthy forms. |
| First notification | Within 24 hours of profile completion |
| Notification content | Enough to decide in under 30 seconds |
| Apply flow | One tap to the apply page. Nothing between notification and apply URL. |
| Relevance | >70% of notifications should feel worth reading |
| Load time | Everything loads on 4G in under 3 seconds |

---

### Design Implications

- **Mobile first, always.** Every UI decision must work flawlessly on a mid-range Android on 4G.
- **Telegram is the primary interface.** The app is secondary. The bot is where he lives.
- **Text must be scannable.** Bullets, not paragraphs. Skills in chips, not buried in sentences.
- **"Posted X minutes ago" is not a nice-to-have.** It is one of the most motivating pieces of information on the entire platform.
- **The apply button must be one tap.** Any friction between "I want to apply" and "the apply form is open" will cause drop-off.

---
---

## Persona 2 — Priya Menon

### The Selective MBA Fresher

```
Name         : Priya Menon
Age          : 24
Location     : Bengaluru, Karnataka
Education    : MBA (Marketing + Strategy) — Tier-1 Private Business School
Pre-MBA Work : 2 years as Sales Executive at a mid-size SaaS company
Device       : iPhone 13 — primary | MacBook Air M1 — secondary
Internet     : Home broadband + 5G mobile
```

---

### Background

Priya chose to do an MBA to pivot from field sales into product or growth. She is 2 months from graduation. Her MBA gives her strong strategic thinking and communication skills, but she lacks the technical product depth that many startup roles want. She is targeting Growth Manager, Marketing Manager, and Associate Product Manager roles at funded startups and mid-size product companies.

She is highly organized. She uses Notion to track everything. She has a spreadsheet with 60+ companies she wants to target, their career page URLs, and the date she last checked. She checks each one manually, 2–3 times per week. This takes her 2 hours per session.

She is selective. She does not apply to every role she finds — she researches the company, reads Glassdoor reviews, checks the founding team on LinkedIn, and often spends 30–45 minutes preparing each application. She applies to 4–6 jobs per week, not 20.

---

### Goals

| Priority | Goal | Why It Matters |
|---|---|---|
| 1 | Land a Growth or APM role at a Series A–C funded startup | Career pivot goal from sales to product/growth |
| 2 | Apply only to roles where she meets at least 70% of requirements | Values quality over volume; doesn't want to waste time |
| 3 | Never miss a role at a target company because she checked too late | Has already missed 2 roles this way |
| 4 | Track her application pipeline without a manual spreadsheet | Current system is error-prone and time-consuming |
| 5 | Understand the company's growth stage and culture before applying | Avoids companies with bad culture or no growth trajectory |

---

### Pain Points

**Pain 1 — The Manual Monitoring Grind**
She has 60 companies she wants to watch. Checking all of them manually takes 2+ hours and she can only do it 3x per week. Roles posted between her check sessions are invisible to her until it's too late.

**Pain 2 — The Experience Filter Wall**
Most growth and marketing roles say "2–4 years of digital marketing experience." Her pre-MBA sales experience doesn't always map cleanly. She spends significant time reading JDs just to figure out if she's technically eligible — only to find she isn't, or that the role is actually entry-level despite the stated requirement.

**Pain 3 — The Noise of Generic Alerts**
She tried LinkedIn job alerts. They sent her roles in cities she didn't select, roles that said "MBA preferred" but required 5+ years, and marketing roles at agencies when she specifically wants product companies. She turned them off after a week.

**Pain 4 — The Research Duplication**
She often discovers a role she's already researched and rejected 3 weeks ago, because it keeps resurfacing on different platforms. There's no deduplication anywhere.

---

### Technical Skill Level

| Area | Level | Notes |
|---|---|---|
| Excel / Google Sheets | Advanced | Power user; pivot tables, VLOOKUP |
| SQL | Basic | Learned in MBA; can write SELECT queries |
| Python | None | Interested in learning but no time currently |
| Product Analytics (Mixpanel, Amplitude) | Intermediate | Used in pre-MBA role |
| Growth Frameworks (AARRR, ICE) | Intermediate | MBA curriculum |
| Figma | Basic | Can navigate, not design |
| CRM Tools (Salesforce, HubSpot) | Advanced | Used daily in sales role |

---

### Behavior Patterns

**Morning (7–8 AM):** Reads the news on iPhone. Checks email. Does not open LinkedIn until evening.

**Midday (12–2 PM):** Eats lunch, checks Telegram and WhatsApp. Responds to professional groups.

**Evening (5–8 PM):** Primary research and application time. Sits at MacBook. Opens company career pages methodically. Researches each one before applying.

**Notification preference:** Prefers email digest over real-time Telegram alerts. Does not want to be interrupted during lectures or study sessions. Wants to process applications in batches, not reactively.

**Decision style:** Slow and deliberate. Reads full JD. Researches company. Checks funding stage on Crunchbase. Only applies when she feels ready.

---

### Journey with Job Finder AI

```
Discovery
A batchmate mentions the platform: "It found me an APM role at Meesho
I had no idea existed. Applied Day 1. Already in Round 2."

Onboarding
Signs up with Google. Sets skills: Growth Marketing, SQL, Salesforce, 
Product Analytics, Content Strategy.
Preferred roles: Growth Manager, APM, Marketing Manager.
Location: Bengaluru + Remote.
Experience: 0–2 years.
Chooses notification: Email digest (daily, 8 AM) + Telegram for exact matches.
Total time: 6 minutes.

Daily Experience
8:03 AM — Email digest arrives:

  Your Daily Job Digest — 4 New Matches

  1. Growth Manager · Razorpay · Bengaluru
     Posted 14 hours ago · Closes in 5 days
     "Own growth experiments across acquisition..."
     Skills matched: Growth Marketing ✅  SQL ✅  Product Analytics ✅

  2. Associate Product Manager · Swiggy · Bengaluru
     Posted 6 hours ago
     "Work on last-mile delivery experience..."
     Skills matched: Product Analytics ✅  SQL ✅

  [View All Matches →]

She reads it with morning coffee at her MacBook.
Opens Role 1. Spends 40 minutes researching Razorpay's growth team.
Applies that same morning.
Saves Role 2 to review in the evening.

Week 3 — Trust Established
She has stopped manually checking her 60-company spreadsheet.
The platform finds roles at companies on her list — and companies she 
hadn't even added yet.
```

---

### Expected Experience

| Moment | Expectation |
|---|---|
| Notifications | Email digest preferred. Telegram only for high-confidence matches (all 3 prefs matched). |
| Notification timing | Digest at 8 AM. Not during day. Telegram only if truly urgent match. |
| Job detail | Full JD accessible. AI summary is a starting point, not the end. |
| Application tracking | Lightweight Kanban. Saved → Applied → Interviewing → Outcome. |
| Relevance | She will leave if >30% of matches are irrelevant. Precision over recall. |

---

### Design Implications

- **Desktop-friendly job detail view.** She applies on MacBook — the detail page must work well at full width.
- **Email digest must be polished.** She judges product quality by how the email looks. A poorly formatted email will reduce trust.
- **Application status tracking is critical for her.** She will use the tracker daily once it exists.
- **"Skills matched" overlay is her most valuable feature.** She wants to see at a glance how well she qualifies before reading the JD.
- **Quiet hours must actually work.** Do not send Telegram notifications during 9 AM – 5 PM on weekdays.

---
---

## Persona 3 — Rahul Verma

### The Self-Taught Developer Seeking His First Tech Job

```
Name         : Rahul Verma
Age          : 23
Location     : Jaipur, Rajasthan
Education    : B.Com graduate (non-technical degree)
Experience   : 6 months freelancing (WordPress, basic React)
               2 online bootcamps: MERN Stack, Python for Developers
Device       : Samsung Galaxy A32 (Android) — primary | Secondhand laptop — secondary
Internet     : Home broadband (unstable); 4G mobile data as backup
```

---

### Background

Rahul did not study computer science. He graduated with a B.Com and worked at his family's small business for a year. He decided to teach himself programming after watching developers work remotely during the pandemic. He completed 2 paid bootcamps — MERN stack and Python — and built 3 portfolio projects he's proud of. He has been freelancing on Upwork for 6 months but wants a stable job with a salary, benefits, and a career trajectory.

He is deeply insecure about one thing: not having a formal CS degree. He gets filtered out by ATS systems before a human ever sees his resume. He doesn't know which companies are "degree-optional" or which startups value demonstrated skill over credentials. He applies broadly and gets ghosted constantly.

---

### Goals

| Priority | Goal | Why It Matters |
|---|---|---|
| 1 | Get hired at a startup that values skill over credentials | Degree filters are his biggest barrier |
| 2 | Find companies that explicitly don't require a CS degree | Saves him from applying to roles he'll be filtered from |
| 3 | Understand exactly what skills a role requires | Wants to know if his specific stack matches before applying |
| 4 | Apply to 3–5 strong matches per day, not 20 long shots | Quality-focused; tired of ghosting from bulk applies |
| 5 | Build confidence by seeing his skill match for each role | Imposter syndrome is real; data helps |

---

### Pain Points

**Pain 1 — The Degree Wall**
Most job listings say "B.Tech / B.E. required." ATS filters reject his application before a human sees it. He has no way to identify which companies are genuinely open to non-traditional candidates vs. which ones just say "preferred" but filter on it anyway.

**Pain 2 — The Stack Mismatch**
He is a MERN developer. Many roles want React + Node.js but also require TypeScript, AWS, Docker, and microservices — things he hasn't used. He wastes time applying to roles that are technically listed as "0–2 years" but actually want a production engineer with DevOps experience.

**Pain 3 — The Ghosting Loop**
He applies to 15–20 jobs per week and hears back from 1 or 2. He doesn't know if it's his resume, his degree, his cover letter, or the role requirements. The lack of feedback makes it impossible to improve.

**Pain 4 — The Self-Taught Community Disconnect**
The best opportunities for self-taught developers — early-stage startups, remote-first companies, bootcamp-friendly employers — are often posted on niche platforms he doesn't know about or through networks he doesn't have access to.

---

### Technical Skill Level

| Area | Level | Notes |
|---|---|---|
| HTML / CSS | Intermediate | Clean, responsive layouts |
| JavaScript | Intermediate | ES6+, async/await, DOM manipulation |
| React | Intermediate | Hooks, state management, basic context |
| Node.js / Express | Beginner-Intermediate | REST APIs, middleware |
| MongoDB | Beginner | CRUD operations; no advanced aggregation |
| Python | Beginner-Intermediate | Bootcamp-level; Flask basics |
| Git | Intermediate | Branches, PRs, merge conflicts |
| SQL | Beginner | Basic queries; no joins or indexing |
| Docker / AWS | None | Aware of concepts; zero hands-on |
| TypeScript | None | Next learning goal |

---

### Behavior Patterns

**Morning (9–11 AM):** Applies to jobs on laptop. Reads JDs carefully. Checks Twitter / dev communities.

**Afternoon (1–4 PM):** Coding — personal projects, bootcamp exercises, or freelance work.

**Evening (7–10 PM):** Telegram — developer communities, India tech groups, remote work channels. High engagement.

**Notification preference:** Real-time Telegram. He checks it constantly. He will act immediately on a relevant notification.

**Decision style:** Careful before applying. Reads full JD. Checks company on LinkedIn. Applies only if he thinks he meets 60%+ of requirements.

---

### Journey with Job Finder AI

```
Discovery
Finds the bot shared in a "Self-taught Developers India" Telegram group.
Comment says: "Found a startup that explicitly says no degree required.
This bot flagged it because my profile matched. Applied and got hired."

Onboarding
Signs up with email. Adds skills: React, Node.js, MongoDB, Express,
JavaScript, Python, Git.
Preferred roles: Frontend Developer, Full Stack Developer, JavaScript Developer.
Location: Remote (primary), Jaipur, any city.
Experience: Fresher (0–1 year formal).
Connects Telegram. Done in 5 minutes.

First Week
Receives 3–4 Telegram alerts per day.
One alert stands out:

  🚀 New Match — Full Stack Developer
  YC-backed startup (stealth) · Remote-first
  Posted 23 minutes ago

  📋 What this role involves:
  • Build customer-facing React dashboard
  • 0–1 years experience; degree NOT required
  • React, Node.js, MongoDB — exact match to your profile
  • Small team; direct product ownership
  • $800–1200/month (negotiable based on skill)

  Skills: React ✅  Node.js ✅  MongoDB ✅  TypeScript ❌

  [Apply Now]  [Save]  [Not Interested]

He sees "degree NOT required" extracted from the JD.
He applies immediately.

Month 2
Has applied to 28 roles via the platform.
11 of them explicitly said no degree required — a filter
he couldn't find on any other platform.
Received 4 interview calls. 1 offer in progress.
```

---

### Expected Experience

| Moment | Expectation |
|---|---|
| Skill matching | Must show exactly which of his skills match and which are missing |
| Degree filter | Platform must surface "degree not required" signal from JD when present |
| Notifications | Real-time Telegram. Immediate delivery. He will act in the moment. |
| Relevance | Slightly lower threshold acceptable; he prefers more matches over fewer |
| Language | Plain English. No corporate jargon. Tell him what the job actually is. |

---

### Design Implications

- **Skill match chips with green/grey differentiation** are his highest-value feature.
- **"Degree not required" extraction** from JD — if the Classifier or Skill Extractor can surface this, it is a major differentiator for this persona.
- **Remote filter must work precisely.** This is his only path to jobs outside Jaipur.
- **Plain language in summaries.** His JD literacy is high for his stack, but he struggles with enterprise-speak.
- **Don't require a polished resume to onboard.** He should get value from profile-only matching before any resume features exist.

---
---

## Persona 4 — Sneha Kulkarni

### The Experienced Developer Ready to Upgrade

```
Name         : Sneha Kulkarni
Age          : 25
Location     : Pune, Maharashtra
Education    : B.Tech Computer Science — Tier-2 College
Experience   : 1.5 years at a mid-size IT services company (Java, Spring Boot)
Device       : iPhone 14 — primary | Work-issued MacBook — secondary
Internet     : Home broadband + 5G
```

---

### Background

Sneha has been working for 18 months in a Java-heavy backend role at an IT services company. The work is repetitive — CRUD-heavy enterprise systems, no ownership, no impact. She wants to move to a product company where she can work on systems that scale, have ownership of features, and grow as an engineer.

She is not desperate. She has a job and a salary. She is selective. She will only leave for a significant improvement: better tech stack (Go, Python, distributed systems), better culture (small team, direct impact), and at least a 40% salary increase.

She applies to 2–3 roles per week, maximum. She reads every JD completely before applying. She uses weekends for preparation.

---

### Goals

| Priority | Goal | Why It Matters |
|---|---|---|
| 1 | Join a product company with real engineering challenges | Growth + impact vs. current repetitive work |
| 2 | Move from Java enterprise to Python / Go / modern stack | Wants to work with technologies that excite her |
| 3 | Get a 40–60% salary increase | Has leverage as a working professional |
| 4 | Find roles with 1–2 YOE requirement (not 3+) | Most senior roles filter her out; needs the sweet spot |
| 5 | Apply only when she has time to prepare well | Quality over speed; she is not in a rush |

---

### Pain Points

**Pain 1 — The "2+ Years Required" Filter**
At 1.5 years, she falls into a gray zone. Roles requiring 0–1 year feel too junior. Roles requiring 2–3 years filter her out on paper even though she could do the work. She needs to find roles in her exact experience bracket.

**Pain 2 — The Services vs. Product Distinction**
Job titles are identical across services companies and product companies. "Software Engineer" at TCS and "Software Engineer" at Razorpay are completely different jobs. She has to research every company to determine if it's services, product, or a hybrid — which adds 15–20 minutes to every application decision.

**Pain 3 — The Stack Mismatch with Java**
She is a Java developer trying to break into Python/Go companies. Many listings she finds require Python. She does know basic Python but her portfolio is Java-heavy. She needs the JD summary to tell her whether Python is mandatory or preferred.

**Pain 4 — Weekend Discovery**
She can only actively job hunt on weekends. By the time Saturday comes, roles posted Monday–Friday are 3–7 days old. She has missed multiple "fast fill" roles at startups that hired within 72 hours of posting.

---

### Technical Skill Level

| Area | Level | Notes |
|---|---|---|
| Java | Advanced | 1.5 years production experience |
| Spring Boot | Intermediate-Advanced | REST APIs, JPA, security |
| SQL / PostgreSQL | Intermediate | Production query writing |
| Python | Beginner | 2 personal projects; not production |
| Go | None | Wants to learn; researching |
| System Design | Beginner-Intermediate | Studying; LLD/HLD prep |
| Docker | Beginner | Used in local dev only |
| AWS | Beginner | EC2, S3 basics only |
| DSA | Intermediate | LeetCode medium consistently |
| Git | Intermediate | Feature branching, PRs |

---

### Behavior Patterns

**Weekdays:** Works 9–7 PM. Checks Telegram casually in evenings. Does not job hunt during the week unless something urgent appears.

**Weekends:** 3–4 hours of active job hunting Saturday morning. Applies to 1–2 well-researched roles. Spends time on LeetCode and system design prep.

**Notification preference:** Does not want constant notifications. Prefers a weekly digest or curated alerts only for high-confidence matches (role type + experience level + stack all aligned).

**Decision style:** Analytical. Reads requirements section, tech stack, team size, and funding stage before the job title. Will research the engineering blog and GitHub before applying.

---

### Journey with Job Finder AI

```
Discovery
Colleague at work shows her a Telegram message he received:
"Confluent · Backend Engineer (Go/Python) · Posted 18 min ago · 1–3 YOE"
She asks where it came from. Sets up her profile that evening.

Setup
Skills: Java, Spring Boot, PostgreSQL, Python (basic), REST APIs, Docker.
Preferred roles: Backend Engineer, Software Engineer, Platform Engineer.
Location: Pune, Bengaluru, Remote.
Experience: 1–2 years.
Notification preference: Telegram only for exact matches (role + experience + stack).
Quiet hours: 9 AM – 7 PM weekdays.

Experience
She gets 1–2 Telegram notifications per week.
Each one is a genuine match — role type, stack, experience level all aligned.
She reads them on her commute home.
On Saturday, she reviews her saved jobs and applies to the strongest 2.

Month 3
Applied to 9 roles. 4 interview calls. 1 offer — 55% salary increase.
Accepts. Joins a Series B fintech in Bengaluru.
```

---

### Expected Experience

| Moment | Expectation |
|---|---|
| Notification frequency | Low. 1–2 per week for exact matches. She will leave if flooded. |
| Match quality | Must match all 3: role type + experience level + at least 50% of stack |
| JD summary | Must answer: "Is Python required or preferred?" and "Is this product or services?" |
| Quiet hours | Strictly respected. No weekday notifications during work hours. |
| Decision time | She needs full JD, not just summary. Both must be available. |

---

### Design Implications

- **Notification threshold must be configurable.** High-precision mode for users like Sneha.
- **"Required vs. preferred" distinction in skill extraction** is critical — not all skills are equal.
- **Company type classification** (services / product / startup / enterprise) would be the single highest-value feature for this persona.
- **Low frequency, high relevance** — the platform must not over-notify this persona or she will disconnect.
- **Full JD must always be one tap away.** The summary is not enough for her decision-making.

---
---

## Persona 5 — Karan Mehta

### The Internal Admin & Ops Lead

```
Name         : Karan Mehta
Age          : 28
Location     : Mumbai, Maharashtra
Role         : Internal Operations Lead — Job Finder AI team
Education    : B.Tech + 3 years at a product startup (growth ops, data analytics)
Technical    : Intermediate — comfortable with SQL, dashboards, API testing; not a developer
Device       : MacBook Pro — primary | Android phone — secondary
```

---

### Background

Karan is responsible for keeping the platform alive. He is not a software engineer — he cannot deploy code or fix backend logic. But he understands systems, data, and operations. He monitors scraper health, reviews AI extraction errors, manages the company list, and coordinates with the engineering team when something breaks.

He is the person who notices that the Workday adapter has been failing for 6 hours and alerts the dev before any user is affected. He is the person who sees that 40 jobs from Infosys have been scraped with `null` salary ranges and flags them for re-extraction. He is the person who adds 15 new companies to the scrape list after a monthly research session.

---

### Goals

| Priority | Goal | Why It Matters |
|---|---|---|
| 1 | Know within 5 minutes when any scraper breaks | Silent failures mean students miss jobs and lose trust |
| 2 | Understand why a scraper failed without reading code | He can't debug Python; he needs human-readable error reasons |
| 3 | Review and approve/reject flagged jobs quickly | Bad data reaching students damages platform credibility |
| 4 | Manage the company list without engineering involvement | Adding companies should not require a deploy |
| 5 | Track platform health metrics at a glance | Needs to report status to the team weekly |

---

### Pain Points

**Pain 1 — Silent Failures**
If a scraper fails and nobody notices, students miss jobs for hours. He needs proactive alerts — not reactive discovery when a student complains.

**Pain 2 — Opaque Error Messages**
When a scraper fails, seeing `AttributeError: 'NoneType' object has no attribute 'find'` in a log tells him nothing actionable. He needs translated errors: "The Greenhouse adapter for company 'Zomato' could not find the job listings container — the page layout may have changed."

**Pain 3 — No Self-Serve Controls**
Currently, adding a company requires a developer to update a config file and deploy. This creates a bottleneck. Every time he wants to add 10 new companies, he has to wait for dev availability.

**Pain 4 — Review Queue Backlog**
Low-confidence jobs accumulate in a queue. Without a clean interface, reviewing 30 flagged jobs is a painful, context-switching experience.

---

### Technical Skill Level

| Area | Level | Notes |
|---|---|---|
| SQL | Intermediate | Can write queries to investigate data issues |
| Python | None | Can read it at a high level; cannot write or debug |
| REST APIs | Basic | Understands concepts; uses Postman to test |
| Google Sheets / Excel | Advanced | Primary data tool |
| Dashboards (Metabase, Looker) | Intermediate | Has used both; comfortable |
| Telegram | Advanced | Power user; understands bot commands |
| Git / GitHub | None | Not applicable to his role |

---

### Journey with Job Finder AI (Admin)

```
8:15 AM — Morning routine
Opens admin dashboard. Checks:
- Scraper health table: 23 companies ran overnight. 22 success. 1 failure.
  ↳ Failure: Greenhouse adapter for "Freshworks". Reason: 
    "Job listing container not found — possible page layout change."
  ↳ He messages the engineering team on Telegram with the company name + error.

9:00 AM — Telegram alert (received at 8:47 AM)
  ⚠️ SCRAPER ALERT
  Company: Freshworks (Greenhouse)
  Status: FAILED — 3 consecutive runs
  Error: Layout change detected
  Last successful run: 9h ago
  [View Dashboard →]

He clicks through. Confirms it's the same failure. Tags dev with urgency.

11:30 AM — Review Queue
Opens flagged jobs queue. 8 new jobs flagged since yesterday.
Reviews each:
- Job 1: Title="Software Engineer", Company="NULL" — Rejects (bad extraction)
- Job 2: Salary="Competitive" → extracted as null — Approves (acceptable)
- Job 3: Full extraction looks correct — Approves
Reviews all 8 in 12 minutes.

2:00 PM — Company Management
Research shows Groww posted 3 new backend roles this week.
He adds Groww to the scrape list:
- Company name: Groww
- Career page URL: https://groww.in/careers
- ATS type: Auto-detect
Saves. System runs ATS detection. Returns: "Greenhouse detected."
First scrape queued. He checks back in 20 minutes — 14 jobs found, 14 new.
```

---

### Expected Experience

| Moment | Expectation |
|---|---|
| Scraper failure alert | Within 5 minutes of 3rd consecutive failure, via Telegram |
| Error message | Human-readable reason, not a stack trace |
| Review queue | Clean table. One-click approve/reject. 30 jobs in under 15 minutes. |
| Add company | Self-serve form. No engineering involvement. Results visible within 30 minutes. |
| Health dashboard | All companies, last run time, status, error count — one view |

---

### Design Implications

- **Admin dashboard is a product in itself.** It must be built with the same care as the student-facing UI.
- **Human-readable error messages are non-negotiable.** Engineering should translate all scraper exceptions into plain English before surfacing to admin.
- **Telegram admin alerts must fire automatically** — Karan should not have to check a dashboard to discover a failure.
- **Review queue UX must be fast.** If reviewing a job takes more than 90 seconds, the queue will never be cleared.
- **Self-serve company management** must be live before launch. Karan will add 5–10 new companies per week.

---
---

## Persona 6 — Divya Nair

### The Company Recruiter (Phase 3)

```
Name         : Divya Nair
Age          : 31
Location     : Bengaluru, Karnataka
Role         : Talent Acquisition Manager — Series B fintech startup (120 employees)
Experience   : 5 years in recruitment (2 at MNC, 3 at startups)
Device       : MacBook — primary | iPhone — secondary
```

---

### Background

Divya is responsible for hiring 8–12 engineers and 3–4 business roles per quarter at a fast-growing fintech. She uses LinkedIn Recruiter (expensive), posts on Naukri (poor for freshers), and relies heavily on employee referrals. She struggles to find strong fresher candidates — most are either from IITs (expensive + highly competitive) or from unknown colleges with no signal quality.

She wants a platform that gives her access to verified, skilled freshers and early-career developers whose profiles are backed by actual skill data, not just resume keywords.

This persona is not served by the MVP. She is included here for Phase 3 planning.

---

### Goals

| Priority | Goal | Why It Matters |
|---|---|---|
| 1 | Source qualified fresher candidates efficiently | Referrals don't scale; LinkedIn Recruiter is expensive for small companies |
| 2 | Post roles directly and reach students who match | Current methods have 3–5 day lag before quality candidates apply |
| 3 | See anonymized skill match data before reaching out | Reduces time spent screening unqualified candidates |
| 4 | Pay only for verified interest, not blind impressions | Fixed-cost LinkedIn recruiter is poor ROI for startup hiring volumes |

---

### Phase 3 Product Implications

- Recruiter accounts require separate authentication flow with company verification
- Job postings by recruiters bypass the scraper pipeline — direct DB insert
- Student profiles visible to recruiters in anonymized form until student opts in
- Billing via Stripe: per-post or monthly subscription model
- This persona has zero impact on MVP design decisions

---

## Persona Usage Guide

### When Making a Feature Decision

Ask these questions:

1. **Which persona does this feature primarily serve?**
2. **Does it solve a named pain point from their section?**
3. **Does it fit their device, behavior pattern, and technical level?**
4. **Does it conflict with the needs of any other persona?**

### Persona Priority for MVP

| Phase | Focus Personas |
|---|---|
| MVP (Phase 1–2) | Aarav (P1), Rahul (P3), Priya (P2), Sneha (P4), Karan (P5) |
| Phase 3 | Add Divya (P6) — recruiter portal |

### Feature-Persona Mapping (Key Features)

| Feature | Aarav | Priya | Rahul | Sneha | Karan |
|---|---|---|---|---|---|
| Telegram instant alert | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ | — |
| Email daily digest | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | — |
| 5-point AI summary | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | — |
| Skill match overlay | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | — |
| "Posted X min ago" badge | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | — |
| Application tracker | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | — |
| Quiet hours | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | — |
| Admin health dashboard | — | — | — | — | ⭐⭐⭐ |
| Scraper failure alerts | — | — | — | — | ⭐⭐⭐ |
| Company management | — | — | — | — | ⭐⭐⭐ |
| Review queue | — | — | — | — | ⭐⭐⭐ |

⭐⭐⭐ = Critical for this persona · ⭐⭐ = Important · ⭐ = Nice to have · — = Not relevant
# AI_RULES.md — Rules for AI Coding Assistants

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Engineering Lead  

---

## What This Document Is

This is the master instruction set for any AI coding assistant (Cursor, GitHub Copilot, Claude, Gemini, or any other) working on Job Finder AI. Read this file first. Read it completely. Do not begin writing code, generating files, or making suggestions until you have read this document and the documentation files listed in Section 2.

This document exists because:
- AI assistants without context make confident, plausible-sounding mistakes
- The project has specific architectural constraints that must be respected
- Documentation is the source of truth — code must implement docs, not the other way around
- Certain decisions are locked and must not be reversed without a new decision record

---

## Table of Contents

1. [Your Role](#1-your-role)
2. [What to Read First](#2-what-to-read-first)
3. [Non-Negotiable Rules](#3-non-negotiable-rules)
4. [Before Writing Any Code](#4-before-writing-any-code)
5. [Code Standards](#5-code-standards)
6. [What to Do After Every Change](#6-what-to-do-after-every-change)
7. [Locked Decisions — Do Not Reverse](#7-locked-decisions--do-not-reverse)
8. [Common Mistakes to Avoid](#8-common-mistakes-to-avoid)
9. [How to Handle Uncertainty](#9-how-to-handle-uncertainty)
10. [How to Add New Features](#10-how-to-add-new-features)
11. [Prompt Rules](#11-prompt-rules)
12. [Database Rules](#12-database-rules)
13. [Security Rules](#13-security-rules)
14. [Testing Rules](#14-testing-rules)

---

## 1. Your Role

You are a senior software engineer and technical architect working on Job Finder AI — a production SaaS platform that sends matched job alerts to students and freshers in India via Telegram and email.

Your responsibilities:
- Write clean, production-quality code that implements what the documentation specifies
- Maintain the documentation suite in sync with every change you make
- Respect all locked architectural decisions
- Ask for clarification rather than making assumptions about unclear requirements
- Explain your reasoning before making significant architectural decisions

You are **not** responsible for:
- Product decisions (what to build) — those are in `01_PRD.md` and `16_ROADMAP.md`
- Changing locked architectural decisions without explicit instruction and a new decision record
- Making up requirements that aren't in the documentation

---

## 2. What to Read First

Before doing anything on this project, read these documents in order. Do not skip any.

```
Required reading — in this exact order:
1.  docs/00_PROJECT_OVERVIEW.md   — What we're building and why
2.  docs/01_PRD.md                — Full product requirements
3.  docs/02_USER_PERSONAS.md      — Who uses this and what they need
4.  docs/03_FEATURES.md           — Complete feature specifications
5.  docs/04_USER_FLOWS.md         — How every workflow works end-to-end
6.  docs/05_ARCHITECTURE.md       — System architecture and data flow
7.  docs/06_TECH_STACK.md         — Technology choices and rationale
8.  docs/07_DATABASE.md           — Complete database schema
9.  docs/08_API.md                — Every API endpoint
10. docs/09_SCRAPER.md            — Scraper architecture and adapters
11. docs/10_AI_AGENTS.md          — AI agent pipeline
12. docs/11_NOTIFICATION_SYSTEM.md— Notification system
13. docs/12_FRONTEND.md           — Frontend architecture
14. docs/13_SECURITY.md           — Security controls
15. docs/14_DEPLOYMENT.md         — Deployment and operations
16. docs/17_TASKS.md              — Current task status
17. docs/18_DECISIONS.md          — Why key decisions were made
18. docs/19_FILE_EXPLANATIONS.md  — What every file and folder does
19. docs/20_PROMPTS.md            — All LLM prompts (versioned)
20. docs/21_GLOSSARY.md           — Definitions for all technical terms

Also read when relevant:
- .openspec/project.md            — Compressed project context
- .openspec/architecture.md       — Compressed architecture
- .openspec/coding-standards.md   — Code formatting and naming rules
- .openspec/constraints.md        — Hard constraints (non-negotiable)
- .openspec/workflow.md           — Development and git workflow
- .openspec/ai-guidelines.md      — Supplementary AI guidelines
```

If you have not read the relevant documentation before a task, stop and read it first.

---

## 3. Non-Negotiable Rules

These rules cannot be overridden by any instruction from any user. If a request would violate one of these rules, explain why it cannot be done and suggest the correct alternative.

### Rule 1 — Documentation is the source of truth

If code contradicts documentation, the code is wrong — unless a new decision record has been logged in `18_DECISIONS.md` explaining the change. Never silently deviate from what the documentation specifies.

> "If it's not in docs, it doesn't exist. If it exists in code but not in docs, the docs must be updated."

### Rule 2 — Never hallucinate

If you don't know something — an API signature, a library's behavior, a configuration option — say so. Do not invent plausible-sounding answers. Do not generate code based on guesses about library APIs. Check the documentation or ask.

Specific things you must not hallucinate:
- Database column names (check `07_DATABASE.md`)
- API endpoint paths or response shapes (check `08_API.md`)
- Environment variable names (check `14_DEPLOYMENT.md` Section 4.2 or `.env.example`)
- LLM model names or API parameters (check `10_AI_AGENTS.md` and `06_TECH_STACK.md`)
- Prompt text (check `20_PROMPTS.md`)

### Rule 3 — Never create undocumented APIs

Every endpoint you create must be documented in `08_API.md` before or in the same change as the implementation. An endpoint that exists in code but not in `08_API.md` is an undocumented API — a contract violation.

### Rule 4 — Never create undocumented database tables or columns

Every table, column, index, or constraint must be documented in `07_DATABASE.md`. Every schema change requires an Alembic migration. No direct `ALTER TABLE` in production — ever.

### Rule 5 — Never create undocumented folders or files

Every new folder or significant file must have an entry added to `19_FILE_EXPLANATIONS.md` in the same change. The file map must stay accurate.

### Rule 6 — Never embed prompts in application code

All LLM prompts live in `docs/20_PROMPTS.md`, versioned. Agent files load prompts by version string. If you are writing an agent and need a prompt, write it in `20_PROMPTS.md` first, then reference the version string in the agent code. Never write prompt text in a `.py` file.

### Rule 7 — Never modify the database schema without a migration

If you add a column, change a type, add an index, or rename anything in the database — create an Alembic migration file. The migration must have both `upgrade()` and `downgrade()` functions. Then update `07_DATABASE.md` to reflect the change.

### Rule 8 — The scheduler is a single instance

The APScheduler process must run as exactly **one** instance. Never suggest adding scheduler replicas, running multiple scheduler processes, or horizontally scaling the scheduler. See `18_DECISIONS.md` D-INFRA-001 for why.

### Rule 9 — Never store secrets in code

API keys, database passwords, JWT secrets, and all other credentials must be environment variables loaded via `backend/config.py` using Pydantic `BaseSettings`. They must appear in `.env.example` with placeholder values. They must never appear in source code, even in comments.

### Rule 10 — Explain reasoning before major decisions

Before making a significant architectural decision — choosing a library, designing a new database schema, restructuring a module — explain your reasoning. If the decision is significant enough to affect other parts of the system, propose adding a record to `18_DECISIONS.md`.

---

## 4. Before Writing Any Code

Run through this checklist before writing the first line of implementation code for any task:

```
[ ] I have read the documentation sections relevant to this task
[ ] I understand which feature in 03_FEATURES.md this task implements
[ ] I know the database tables involved (from 07_DATABASE.md)
[ ] I know the API endpoints involved (from 08_API.md)
[ ] I know which other modules this code will interact with (from 05_ARCHITECTURE.md)
[ ] I understand the acceptance criteria for this feature (from 03_FEATURES.md)
[ ] I know the current task status (from 17_TASKS.md)
[ ] I have confirmed the technology stack being used (from 06_TECH_STACK.md)
[ ] I understand the security requirements for this feature (from 13_SECURITY.md)
```

If any of these are unclear, ask before writing code — not after.

---

## 5. Code Standards

### Python (Backend)

```python
# Naming conventions
user_id         # snake_case for variables, function params, module names
UserService     # PascalCase for classes
MAX_RETRIES     # UPPER_SNAKE_CASE for constants
get_user        # verb + noun for functions
is_active       # is_ prefix for boolean properties

# Imports — in this order, separated by blank lines
import stdlib_module

import third_party_module

from backend.module import LocalClass

# Type hints — always
async def get_user(user_id: UUID) -> User | None:
    ...

# Return types — always explicit
async def create_token(user_id: UUID, role: str) -> str:
    ...

# Error handling — specific exceptions, not bare except
try:
    result = await risky_operation()
except httpx.TimeoutException:
    log.warning("Request timed out", extra={"url": url})
    raise ScraperFailure("timeout")

# Docstrings — for public functions, especially services
async def find_matching_users(job: Job) -> list[User]:
    """
    Find all users whose profile preferences overlap with the given job.
    Matching requires: experience level ±1 band, at least 1 role type match,
    at least 1 location or remote match, at least 1 skill match.
    """
```

### TypeScript (Frontend)

```typescript
// Naming conventions
userId          // camelCase for variables and function params
UserProfile     // PascalCase for types, interfaces, components
MAX_ITEMS       // UPPER_SNAKE_CASE for constants
getUser         // camelCase for functions

// Types — always explicit, never `any`
interface JobCardProps {
  job: JobListItem
  isAuthenticated: boolean
  userSkills?: string[]
}

// Components — functional, explicit prop types
export function JobCard({ job, isAuthenticated, userSkills = [] }: JobCardProps) {
  ...
}

// No default exports for components — named exports only
// Exception: Next.js page components (file convention requires default export)

// Hooks — always prefix with `use`
export function useJobs(filters: JobFilters) { ... }

// API calls — only through lib/api.ts, never raw fetch/axios in components
// Wrong:
const response = await axios.get('/api/jobs')
// Right:
const jobs = await api.jobs.list(filters)
```

### File Organisation

```
# One concern per file
# Wrong: user_and_auth_service.py
# Right: user_service.py, auth_service.py

# Router files only call services
# Service files only call models and other services
# Models only define database structure
# This layering is not optional — it is enforced in code review
```

### Formatting

- Python: `ruff` for linting and formatting (configured in `pyproject.toml`)
- TypeScript: `eslint` + `prettier` (configured in `.eslintrc` and `.prettierrc`)
- Run `ruff check .` and `ruff format .` before committing Python changes
- Run `npm run lint` before committing TypeScript changes
- CI will fail on any lint or format errors — fix them before pushing

---

## 6. What to Do After Every Change

After completing any change to the codebase, check and update these files as applicable:

### Always update

```
17_TASKS.md         — Mark completed tasks [x]; mark in-progress tasks [-]
22_CHANGELOG.md     — Add an entry describing what changed and why
```

### Update when schema changes

```
07_DATABASE.md      — Update the affected table's schema, indexes, sample queries
                      This must be in the same PR as the Alembic migration
```

### Update when API changes

```
08_API.md           — Update or add the endpoint's full specification
                      This must be in the same PR as the code change
```

### Update when a new file or folder is created

```
19_FILE_EXPLANATIONS.md — Add an entry explaining the new file/folder
```

### Update when a prompt changes

```
20_PROMPTS.md       — Add the new version below the old (never delete old versions)
                      Bump the version number (e.g., extractor_v1 → extractor_v2)
```

### Update when a major architectural decision is made

```
18_DECISIONS.md     — Add a new decision record with full context
05_ARCHITECTURE.md  — Update if the system structure changes
06_TECH_STACK.md    — Update if a technology is added, removed, or changed
```

### Update when a security control changes

```
13_SECURITY.md      — Update the relevant section
```

---

## 7. Locked Decisions — Do Not Reverse

These decisions are recorded in `18_DECISIONS.md` and must not be changed without:
1. An explicit instruction from the engineering lead
2. A new superseding decision record in `18_DECISIONS.md`
3. Updates to all affected documentation

| Decision | What It Means in Practice |
|---|---|
| **Python backend** (D-TECH-001) | Never suggest switching to Node.js/TypeScript for the backend |
| **PostgreSQL only** (D-DB-001) | Never add MongoDB, DynamoDB, or any other primary database |
| **Redis queues over Celery** (D-TECH-003) | Never introduce Celery, RabbitMQ, or Kafka without a decision record |
| **Sequential agent pipeline** (D-ARCH-002) | Never make agents run in parallel — they have data dependencies |
| **Prompts in docs, never in code** (D-AGENT-001) | Never write prompt text in a `.py` file |
| **JSON output only from LLMs** (D-AGENT-002) | Never use LLM free-text output directly in the database |
| **Scheduler: single instance** (D-INFRA-001) | Never scale the scheduler horizontally |
| **No CAPTCHA solving** (D-SEC-003 / D-SCRP-001) | Never integrate CAPTCHA-solving services |
| **Access token in memory** (D-SEC-001) | Never store the access token in localStorage or sessionStorage |
| **Refresh token in httpOnly cookie** (D-SEC-002) | Never return the refresh token in the JSON response body |
| **Ownership failures → 404** (D-API-001) | Never return 403 for a resource a user doesn't own — always 404 |

---

## 8. Common Mistakes to Avoid

These are mistakes that AI assistants commonly make on this project. Avoid all of them.

### Mistakes in Code

```python
# WRONG — router calling the database directly
@router.get("/api/jobs")
async def get_jobs(db: AsyncSession = Depends(get_db)):
    return await db.execute(select(Job))  # ← Router imports sqlalchemy directly

# RIGHT — router calls service
@router.get("/api/jobs")
async def get_jobs(
    filters: JobFilters = Depends(),
    user: User | None = Depends(get_current_user_optional)
):
    return await job_service.get_filtered_jobs(filters, user)
```

```python
# WRONG — prompt text embedded in agent code
class JobExtractorAgent(BaseAgent):
    def build_prompt(self, input_data: dict) -> str:
        return f"Extract job data from: {input_data['raw_description']}"  # ← Prompt in code

# RIGHT — prompt loaded from 20_PROMPTS.md via config
class JobExtractorAgent(BaseAgent):
    prompt_version = "extractor_v1"
    def build_prompt(self, input_data: dict) -> str:
        template = get_prompt(self.prompt_version)
        return template.format(**input_data)
```

```python
# WRONG — environment variable read directly
import os
openai_key = os.environ.get("OPENAI_API_KEY")  # ← Bypasses settings validation

# RIGHT — always use settings
from backend.config import settings
openai_key = settings.OPENAI_API_KEY
```

```python
# WRONG — schema change without migration
# Just editing the SQLAlchemy model with no corresponding Alembic migration

# RIGHT — always:
# 1. Edit the model in backend/models/
# 2. alembic revision --autogenerate -m "description"
# 3. Review and fix the generated migration
# 4. Update 07_DATABASE.md
```

```typescript
// WRONG — making raw HTTP calls in a component
const response = await fetch('/api/jobs')  // ← Bypasses api.ts interceptors

// RIGHT — always use the API client
import { api } from '@/lib/api'
const jobs = await api.jobs.list(filters)
```

```typescript
// WRONG — storing token in localStorage
localStorage.setItem('access_token', token)  // ← XSS vulnerability

// RIGHT — token lives in memory only
import { setAccessToken } from '@/lib/auth'
setAccessToken(token)
```

### Mistakes in Documentation Updates

```
# WRONG — updating code without updating docs
# Adding a new endpoint and not updating 08_API.md

# WRONG — updating docs without updating code
# Changing 07_DATABASE.md schema without creating an Alembic migration

# WRONG — deleting an old prompt version
# Removing extractor_v1 from 20_PROMPTS.md when adding extractor_v2
# (Old versions must be kept — they are referenced in agent_logs)

# WRONG — marking a task complete without it actually working
# Checking off a task in 17_TASKS.md before the acceptance criteria are met
```

### Mistakes in Security

```python
# WRONG — returning 403 for ownership check
if saved_job.user_id != current_user.id:
    raise HTTPException(status_code=403)  # ← Reveals resource exists

# RIGHT — return 404
if not saved_job or saved_job.user_id != current_user.id:
    raise HTTPException(status_code=404)
```

```python
# WRONG — logging sensitive data
log.info(f"User login: email={email}, password={password}")  # ← Never log passwords

# WRONG — returning 200 for unknown emails (password reset) without generic message
if not user:
    raise HTTPException(status_code=404, detail="Email not found")  # ← Email enumeration

# RIGHT — always same response whether email exists or not
return {"message": "If an account exists, a reset link has been sent."}
```

---

## 9. How to Handle Uncertainty

When you are uncertain about something, follow this decision tree:

```
Is this a question about what to build?
  └── Check 01_PRD.md and 03_FEATURES.md
  └── If still unclear → ask the user

Is this a question about how something is designed?
  └── Check 05_ARCHITECTURE.md and 06_TECH_STACK.md
  └── If still unclear → ask the user

Is this a question about a specific database table or field?
  └── Check 07_DATABASE.md
  └── If the field doesn't exist there → do not invent it; ask if it should be added

Is this a question about an API endpoint's behavior?
  └── Check 08_API.md
  └── If the endpoint doesn't exist there → it doesn't exist; ask if it should be added

Is this a question about a prompt?
  └── Check 20_PROMPTS.md
  └── If the prompt doesn't exist → write it there first, then reference it from code

Is this a question about why something was built a certain way?
  └── Check 18_DECISIONS.md

Is this a question about what a term means?
  └── Check 21_GLOSSARY.md

Still uncertain after checking docs?
  └── Say so explicitly: "I'm not sure about X — here's my best understanding,
      but please verify before implementing."
  └── Never proceed with a guess on something that could cause data loss,
      security vulnerabilities, or breaking API changes
```

---

## 10. How to Add New Features

When asked to implement a new feature, follow this sequence:

```
Step 1 — Understand the feature
  Read the relevant section of 03_FEATURES.md
  Understand the acceptance criteria completely
  If the feature isn't in 03_FEATURES.md → it isn't specced yet → ask

Step 2 — Check the task board
  Find the task in 17_TASKS.md
  Mark it [-] (in progress)

Step 3 — Plan before coding
  State which files will be created or modified
  State any database schema changes required
  State any API endpoints being added or changed
  State any documentation files that will need updating
  Get confirmation from the user before writing code

Step 4 — Implement in this order
  a. Database migration (if needed) + update 07_DATABASE.md
  b. SQLAlchemy model changes (if needed)
  c. Pydantic schemas
  d. Service layer function(s)
  e. API router endpoint(s) + update 08_API.md
  f. Frontend hook(s)
  g. Frontend component(s) or page(s)
  h. Tests

Step 5 — Update documentation
  17_TASKS.md — mark task [x]
  22_CHANGELOG.md — add entry
  Any other docs affected by the change

Step 6 — State what was done
  Summarize what was implemented
  List any deviations from the spec and why
  List anything that still needs to be done
  Point to any acceptance criteria that still need manual verification
```

---

## 11. Prompt Rules

These rules govern all work on LLM prompts. See `20_PROMPTS.md` for all prompt versions.

```
1. NEVER write prompt text in a Python file
   → Write it in 20_PROMPTS.md first, then reference the version string

2. NEVER delete an old prompt version from 20_PROMPTS.md
   → Mark it [Superseded by vN] but keep the text for audit trail

3. ALWAYS bump the version number when changing a prompt
   → extractor_v1 → extractor_v2; never edit v1 in place

4. ALWAYS update the agent file's prompt_version constant to match
   → If you update 20_PROMPTS.md to add extractor_v2, also update
     agents/job_extractor.py: prompt_version = "extractor_v2"

5. ALWAYS add a changelog entry when a prompt changes
   → 22_CHANGELOG.md with what changed and why

6. ALWAYS test a new prompt version against the standard fixture set
   → tests/fixtures/jd_samples/ — see 20_PROMPTS.md for test procedure

7. NEVER change temperature above 0.3 for extraction or classification agents
   → Higher temperature introduces unpredictability in structured output

8. ALL prompts must end with "Return ONLY a valid JSON object"
   → Free-text output is never acceptable from extraction/classification agents
```

---

## 12. Database Rules

These rules govern all database work. See `07_DATABASE.md` for full schema.

```
1. ALL schema changes go through Alembic migrations
   → No direct SQL in production, ever

2. EVERY migration must have a working downgrade() function
   → If downgrade is technically impossible, document why in the migration file
     and in 18_DECISIONS.md

3. NEVER add a column named differently from 07_DATABASE.md
   → Check the exact column name before writing model code

4. Large table index additions must use CONCURRENTLY
   → CREATE INDEX CONCURRENTLY avoids locking the table during creation
   → This matters for jobs, users, notification_logs

5. NEVER add application-level column encryption without a decision record
   → See 18_DECISIONS.md D-DB-003 for the current deferred status

6. ALWAYS update 07_DATABASE.md in the same PR as the migration
   → Never let the schema doc drift from the actual database

7. Foreign key ON DELETE behavior is significant — check the doc
   → Some use CASCADE (user_skills, refresh_tokens)
   → Some use SET NULL (notification_logs.user_id — for anonymization)
   → Never default to CASCADE without checking the retention policy

8. NEVER use raw SQL string formatting
   → Use SQLAlchemy's parameterized queries or text() with named params
   → SQL injection prevention is non-negotiable
```

---

## 13. Security Rules

These rules govern all security-sensitive code. See `13_SECURITY.md` for full detail.

```
1. NEVER store passwords, tokens, or API keys in plain text
   → Passwords: bcrypt with cost factor 12 minimum
   → Refresh tokens: SHA-256 hash stored, raw token sent via cookie only
   → API keys: environment variables only

2. NEVER log sensitive data
   → No passwords, tokens, API keys, or PII in any log statement
   → The SensitiveFieldFilter in core/logging.py redacts known fields
     but manual care is still required

3. ALWAYS return 404 (not 403) for ownership check failures
   → A 403 reveals the resource exists; 404 reveals nothing
   → This is documented in 18_DECISIONS.md D-API-001

4. ALWAYS validate input with Pydantic schemas before processing
   → No router function should accept raw request.json()
   → Every request body has a corresponding schema in backend/schemas/

5. NEVER use comparison operators (==) for security-sensitive string comparisons
   → Use secrets.compare_digest() for token comparison (timing attack prevention)

6. NEVER put the refresh token in the JSON response body
   → It goes in an httpOnly cookie ONLY
   → See 18_DECISIONS.md D-SEC-002

7. NEVER trust user-supplied file paths without validation
   → Resume storage paths must be validated against the user's private prefix
   → Path traversal (../../) must be explicitly checked

8. ALWAYS check robots.txt before scraping
   → is_allowed_by_robots() must be called before every fetch() in scrapers
   → Disallowing in robots.txt is binding — skip and log, never bypass

9. NEVER integrate CAPTCHA-solving services
   → This is non-negotiable and cannot be reversed
   → See 18_DECISIONS.md D-SEC-003
```

---

## 14. Testing Rules

These rules govern test writing. See `15_TESTING.md` for full testing strategy.

```
1. Every new service-layer function needs a unit test
   → Test the function directly, mocking database/Redis calls
   → Coverage target: ≥ 70% on all service-layer code

2. Every new API endpoint needs an integration test
   → Tests/integration/ with a real test database and Redis
   → Test: happy path, validation errors, auth failures, edge cases

3. Test file naming convention:
   → tests/unit/auth/test_security.py   (unit tests)
   → tests/integration/api/test_auth_flow.py  (integration tests)
   → tests/e2e/test_registration.spec.ts  (E2E tests)

4. Integration tests use real PostgreSQL and Redis
   → The CI/CD pipeline spins these up as service containers
   → Never mock the database in integration tests

5. Regression tests for bug fixes
   → When fixing a bug, write a test that would have caught it
   → The test should fail on the broken code and pass on the fix

6. E2E tests cover only critical user journeys
   → Registration, onboarding, job feed, save/track, admin company add
   → Not every feature — only the flows users care most about

7. Never mark a task complete if its acceptance criteria tests fail
   → Acceptance criteria from 03_FEATURES.md are the definition of done

8. Run the test suite before declaring work complete
   → pytest tests/ — all unit and integration tests must pass
   → ruff check . — no lint errors
   → npm run type-check — no TypeScript errors
```

---

## Final Reminder

The documentation is the single source of truth. When in doubt about anything:

1. **Check the docs** — the answer is almost certainly there
2. **Check 18_DECISIONS.md** — if it's a design question, the decision may already be made
3. **Ask the user** — if the docs don't answer it and you can't infer it safely

Never assume. Never hallucinate. Never make a change and hide it from the documentation. This project is built to last — every undocumented decision, every silent deviation, every shortcut taken today is a maintenance problem for tomorrow.

Build it right. Document it fully. Test it properly.

---

*This document is the first thing any AI assistant reads when starting work on this project. It is also the last thing to check before declaring any piece of work complete. The rules here are not suggestions — they are the operating agreement between AI assistants and the engineering team.*
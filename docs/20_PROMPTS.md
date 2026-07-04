# 20 — Prompts

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Engineering Lead  

---

## Purpose of This Document

This is the canonical, versioned repository of every LLM prompt used in Job Finder AI. No prompt text exists anywhere in application code. Agent files load prompt templates by referencing a version string (e.g., `extractor_v1`) — the actual text lives here.

This separation exists because:
- Prompts need to be iterated on by non-engineers (product, operations) without code deploys
- Every prompt change must be auditable via version history in this document
- `agent_logs.prompt_version` references entries here — a logged version string is meaningless without this document
- AI coding assistants reading the codebase can see what every agent is actually asking the LLM

---

## Prompt ID Convention

```
{agent_name}_v{version_number}

Examples:
  extractor_v1       — Job Extractor agent, version 1
  extractor_v2       — Job Extractor agent, version 2 (supersedes v1)
  skill_extractor_v1 — Skill Extractor agent, version 1
```

When a prompt is updated:
1. The new version is added below the old one (old version is never deleted)
2. The `Current Version` field in the agent's entry is updated
3. The agent file's `prompt_version` constant is updated to match
4. A changelog entry is added to `22_CHANGELOG.md`
5. The old version is marked `[Superseded by vN]`

---

## Prompt Index

| Prompt ID | Agent | Model | Status | Agent File |
|---|---|---|---|---|
| [extractor_v1](#extractor_v1) | Job Extractor | GPT-4o | ✅ Active | `agents/job_extractor.py` |
| [skill_extractor_v1](#skill_extractor_v1) | Skill Extractor | GPT-4o | ✅ Active | `agents/skill_extractor.py` |
| [summarizer_v1](#summarizer_v1) | JD Summarizer | GPT-4o | ✅ Active | `agents/jd_summarizer.py` |
| [classifier_v1](#classifier_v1) | Job Classifier | GPT-4o-mini | ✅ Active | `agents/job_classifier.py` |
| [notif_generator_v1](#notif_generator_v1) | Notification Generator | GPT-4o-mini | ✅ Active | `agents/notification_generator.py` |
| [resume_extractor_v1](#resume_extractor_v1) | Resume Skill Extractor | GPT-4o | ✅ Active (Phase 2) | `agents/resume_skill_extractor.py` |

---

## How Prompts Are Loaded in Code

```python
# agents/config.py
import tomllib

# Prompts are stored in a TOML config file generated from this document
# at build time, OR loaded directly from this Markdown by parsing version blocks.
# For MVP: prompts are stored as string constants in agents/prompts.py,
# which is generated from this document. Never edit agents/prompts.py directly —
# always edit here, then regenerate.

PROMPTS = {
    "extractor_v1": """...""",
    "skill_extractor_v1": """...""",
    # ... all versions
}

def get_prompt(version: str) -> str:
    if version not in PROMPTS:
        raise ValueError(f"Unknown prompt version: {version}. Check docs/20_PROMPTS.md")
    return PROMPTS[version]
```

```python
# agents/job_extractor.py
from agents.config import get_prompt

class JobExtractorAgent(BaseAgent):
    agent_name = "job_extractor"
    prompt_version = "extractor_v1"   # Must match an entry in 20_PROMPTS.md
    model = settings.STRONG_MODEL

    def build_prompt(self, input_data: dict) -> str:
        template = get_prompt(self.prompt_version)
        return template.format(
            company=input_data["company"],
            source_ats=input_data["source_ats"],
            title=input_data["title"],
            raw_description=input_data["raw_description"],
        )
```

---

## Prompt Design Principles

These principles apply to every prompt in this document. Violations should be flagged in code review.

**1. JSON output only — always**  
Every prompt ends with `Return ONLY a JSON object`. The LLM is called with `response_format: {"type": "json_object"}`. Free-text output is never used in production. See `18_DECISIONS.md` D-AGENT-002.

**2. User content is always last and always delimited**  
Job description text (user-derived, potential injection vector) is placed after all instructions and wrapped in `---` delimiters. This structural position makes prompt injection harder to exploit. See `13_SECURITY.md` Section 16.1.

**3. Rules are numbered and specific, not vague**  
"Be accurate" is not a rule. "If the salary is not mentioned in the JD, return null — never invent a value" is a rule. Every rule addresses a known failure mode.

**4. Output schema is explicit in the prompt**  
The exact JSON structure is shown in the prompt, with field names, types, and allowed enum values. This reduces parse failures.

**5. Examples are included where failure modes are subtle**  
For fields where the LLM commonly makes mistakes (e.g., `deadline` vs. `start date`, `required` vs. `preferred` skills), the prompt includes a clear example showing the correct vs. incorrect interpretation.

**6. Temperature = 0.1 for all structured extraction**  
Low temperature reduces output variance for classification and extraction tasks. Higher temperature is only appropriate for generation tasks (Notification Generator uses 0.2 for slightly more varied phrasing).

---

## PROMPT: extractor_v1

**Agent:** Job Extractor  
**Model:** GPT-4o  
**Version:** 1 (current)  
**Agent file:** `agents/job_extractor.py`  
**Input variables:** `{company}`, `{source_ats}`, `{title}`, `{raw_description}`  
**Output schema:** `title`, `location`, `location_type`, `salary_range`, `deadline`, `extraction_confidence`

### Purpose

Transform raw job description text (HTML-stripped, possibly messy ATS output) into a clean, structured record. This is the most critical prompt in the system — extraction errors cascade downstream to every other agent and to students.

### Known Failure Modes This Prompt Addresses

| Failure | How the Prompt Handles It |
|---|---|
| LLM re-extracts company name (sometimes wrong) | Company is provided as a trusted input — prompt says "already known, do not re-extract" |
| Job title contains ATS codes like `[REQ-12345]` | Rule 1 explicitly tells LLM to strip requisition codes |
| LLM invents a salary not in the JD | Rule 4 says "Never invent a salary. If no salary is mentioned, return null." |
| LLM confuses start date with application deadline | Rule 5 distinguishes "application close date" from "expected joining / start date" |
| JD in non-English language | Confidence scored low (< 0.5); flagged for admin review automatically |
| JD too short or garbled to extract from | Low confidence returned; Rule 6 handles |

### Prompt Text

```
You are a job data extraction specialist. Your only job is to extract
structured information from a job description with high accuracy.

Company (trusted source — do not re-extract): {company}
ATS Source: {source_ats}
Raw Title from ATS (may contain codes): {title}
Raw Job Description:
---
{raw_description}
---

Return ONLY a valid JSON object with exactly these fields:

{{
  "title": "string",
  "location": "string or null",
  "location_type": "remote | hybrid | onsite | null",
  "salary_range": "string or null",
  "deadline": "YYYY-MM-DD or null",
  "extraction_confidence": 0.0
}}

Field-by-field rules:

1. title
   - Remove job requisition codes, tracking IDs, and internal identifiers.
     Examples of what to remove: [REQ-12345], #45678, (IC3), - New, ::Backend
   - Keep the human-readable job title only.
   - Correct: "Software Engineer — Backend"
   - Wrong:   "Software Engineer — Backend [REQ-12345]"

2. location
   - Format: "City, State" for Indian cities (e.g., "Bengaluru, Karnataka")
   - Format: "City, Country" for international (e.g., "Singapore")
   - If multiple locations listed: use the first or primary location
   - If fully remote with no base city: return null (set location_type to "remote")
   - Never invent a location not stated in the JD

3. location_type
   - "remote"  — role can be done 100% remotely, no office requirement
   - "hybrid"  — mix of remote and office (any ratio)
   - "onsite"  — must be in office full-time
   - null      — not mentioned in the JD
   - If the JD says "flexible" without specifics, return null

4. salary_range
   - Copy the salary string verbatim from the JD (e.g., "₹12–18 LPA", "$120k–$150k")
   - Do NOT convert to numbers, normalize the format, or estimate
   - If salary is not mentioned anywhere in the JD: return null
   - Never invent a salary. A null is always correct when salary is unstated.

5. deadline
   - Extract application close dates ONLY (e.g., "Apply by July 15", "Position open until filled")
   - Do NOT extract: expected joining dates, project deadlines, probation end dates
   - Format: YYYY-MM-DD (e.g., "2025-07-15")
   - If no application deadline stated: return null

6. extraction_confidence
   - Rate your confidence in the accuracy of all fields combined: 0.0 to 1.0
   - 0.90–1.00: All fields clearly present; JD is well-structured English
   - 0.75–0.89: Most fields present; some inference required
   - 0.50–0.74: JD is sparse, vague, or partially non-English
   - Below 0.50: JD appears garbled, non-English, or not a job description at all
   - Be honest — a low score flags for human review; that is the correct behavior
```

### Example Input / Output

**Input:**
```
company: Razorpay
source_ats: greenhouse
title: SDE II - Backend (Payments) [REQ-78234]
raw_description: We are looking for a Senior Backend Engineer to join our
payments infrastructure team in Bengaluru (hybrid - 3 days/week in office).
The ideal candidate has 3-5 years of experience with Python and distributed
systems. CTC: ₹24–32 LPA. Applications close July 30, 2025.
```

**Expected Output:**
```json
{
  "title": "Senior Backend Engineer",
  "location": "Bengaluru, Karnataka",
  "location_type": "hybrid",
  "salary_range": "₹24–32 LPA",
  "deadline": "2025-07-30",
  "extraction_confidence": 0.95
}
```

### Version History

| Version | Date | Changes |
|---|---|---|
| v1 | 2025-06-22 | Initial version |

---

## PROMPT: skill_extractor_v1

**Agent:** Skill Extractor  
**Model:** GPT-4o  
**Version:** 1 (current)  
**Agent file:** `agents/skill_extractor.py`  
**Input variables:** `{title}`, `{company}`, `{raw_description}`  
**Output schema:** `required_skills[]`, `preferred_skills[]`, `degree_required`, `degree_note`

### Purpose

Extract two distinct skill lists from the JD — skills the candidate must have and skills that are a bonus. Also extract whether a formal degree is required. The `degree_required` field is critical for Persona 3 (self-taught developers without a CS degree) — see `02_USER_PERSONAS.md`.

### Known Failure Modes This Prompt Addresses

| Failure | How the Prompt Handles It |
|---|---|
| Soft skills included in skill list | Rule 3 explicitly excludes "communication, teamwork, problem-solving, leadership" |
| Domain knowledge included as skills | Rule 4 excludes "fintech domain knowledge, healthcare experience" |
| Version numbers included in skill names | Rule 5 strips versions ("Python 3.10" → "Python") |
| All skills treated as required when qualifier is ambiguous | Rule 7 says unlabeled skills default to required |
| `degree_required` = false when JD just doesn't mention it | Three-way: true / false / null (unknown) |

### Prompt Text

```
You are a technical recruiter extracting skills and education requirements
from a job description.

Job Title: {title}
Company: {company}
Job Description:
---
{raw_description}
---

Return ONLY a valid JSON object with exactly these fields:

{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill3", "skill4"],
  "degree_required": true | false | null,
  "degree_note": "verbatim phrase or null"
}}

Rules for required_skills and preferred_skills:

1. Use canonical technology names only:
   - "JavaScript" not "JS" or "Javascript"
   - "TypeScript" not "TS"
   - "PostgreSQL" not "Postgres" or "psql"
   - "Kubernetes" not "K8s"
   - "Amazon Web Services" not "AWS" (exception: use "AWS" — it is the canonical name)
   - "Google Cloud Platform" not "GCP"
   - "Node.js" not "NodeJS" or "node"
   - "React" not "ReactJS" or "React.js"

2. Include only technical and tool skills:
   - YES: programming languages, frameworks, databases, cloud platforms,
          DevOps tools, data tools, testing frameworks, protocols (REST, GraphQL)
   - NO: soft skills (communication, teamwork, attention to detail, problem-solving)
   - NO: domain knowledge (fintech experience, healthcare background, e-commerce)
   - NO: certifications (AWS Certified Solutions Architect — but "AWS" itself is fine)

3. Do not include skill versions in the name:
   - "Python 3.10+" → "Python"
   - "React 18" → "React"
   - "Node.js >= 16" → "Node.js"

4. Classification — required vs. preferred:
   - REQUIRED: "must have", "required", "mandatory", "you have", "we need",
               "strong proficiency in", "experience with X is a must"
   - PREFERRED: "nice to have", "preferred", "a plus", "bonus", "ideally",
               "familiarity with", "exposure to", "working knowledge of"
   - UNLABELED (no qualifier stated): classify as required — it is safer to
               over-report required skills than to hide them

5. If the same skill appears in both required and preferred:
   - Place it in required_skills only (do not duplicate)

6. If no required skills are stated, return an empty array: []
   Do not return null for required_skills or preferred_skills.

Rules for degree_required:

7. Return true if the JD explicitly states a degree is required:
   Examples: "B.Tech required", "Must have a CS degree",
             "Bachelor's degree in Computer Science mandatory"

8. Return false if the JD explicitly states a degree is NOT required:
   Examples: "No degree required", "Equivalent experience accepted",
             "We don't require a formal degree", "Skills matter more than credentials"

9. Return null if the JD does not mention educational requirements at all.
   null means "unknown" — not the same as false.
   Do not assume a role is degree-optional just because it is not mentioned.

10. degree_note: Copy the exact phrase from the JD that informed your
    degree_required value. If degree_required is null, return null here too.
```

### Example Input / Output

**Input:**
```
title: Backend Engineer
company: Razorpay
raw_description: We're looking for a Backend Engineer who is proficient in
Python and FastAPI. PostgreSQL experience is required. Docker and Kubernetes
are preferred. Familiarity with Go would be a nice bonus. No CS degree
required — we care about what you can build, not your credentials.
```

**Expected Output:**
```json
{
  "required_skills": ["Python", "FastAPI", "PostgreSQL"],
  "preferred_skills": ["Docker", "Kubernetes", "Go"],
  "degree_required": false,
  "degree_note": "No CS degree required — we care about what you can build, not your credentials"
}
```

### Version History

| Version | Date | Changes |
|---|---|---|
| v1 | 2025-06-22 | Initial version |

---

## PROMPT: summarizer_v1

**Agent:** JD Summarizer  
**Model:** GPT-4o  
**Version:** 1 (current)  
**Agent file:** `agents/jd_summarizer.py`  
**Input variables:** `{title}`, `{company}`, `{location}`, `{experience_level}`, `{salary_range}`, `{raw_description}`  
**Output schema:** `summary[]` (exactly 5 strings)

### Purpose

The highest user-facing impact prompt in the entire pipeline. These 5 bullets appear in every Telegram notification and at the top of every job detail page. They answer the question a student actually asks: *"Is this job worth 30 minutes of my time?"*

Quality bar: a student should be able to read all 5 bullets in under 20 seconds and have enough information to decide "apply" or "skip" with confidence.

### Known Failure Modes This Prompt Addresses

| Failure | How the Prompt Handles It |
|---|---|
| Vague company-speak ("join our innovative team") | Rule 2 says "describe actual work" with a specific bad vs. good example |
| Experience requirement buried or omitted | Rule 3 mandates bullet 2 always states years if mentioned |
| Location/remote status missing | Rule 4 mandates bullet 3 always states the arrangement explicitly |
| Salary invented or omitted without disclosure | Rule 5 requires verbatim copy OR explicit "not disclosed" statement |
| Generic "fast-growing startup" filler | Rule 6 requires something genuinely distinctive |
| Bullets repeat the same information | Rule 8 enforces no repetition |
| Bullet too long to read at a glance | Hard limit: max 25 words per bullet (enforced in parse_output) |

### Prompt Text

```
You are writing a 5-point job summary for a student or fresh graduate
deciding in 30 seconds whether to apply. Write for a busy person reading
on their phone.

Job Title: {title}
Company: {company}
Location: {location}
Experience Level (from JD, if stated): {experience_level}
Salary (from JD, if stated): {salary_range}
Job Description:
---
{raw_description}
---

Return ONLY a valid JSON object with exactly this structure:

{{
  "summary": [
    "Bullet 1: The actual day-to-day work",
    "Bullet 2: Experience and key skills required",
    "Bullet 3: Location and work arrangement",
    "Bullet 4: Compensation",
    "Bullet 5: One genuinely distinctive fact"
  ]
}}

Rules for every bullet:

1. Length: each bullet must be a single complete sentence, 8–25 words.
   Shorter is better if it conveys the information clearly.
   The parser will reject any bullet over 30 words — write concisely.

2. Bullet 1 — What you will actually do (not who the company is):
   WRONG: "Join our fast-growing fintech team building the future of payments."
   RIGHT: "Build the real-time payment routing engine handling 10M+ daily transactions."
   Focus on the engineer's or analyst's actual work, not the company pitch.

3. Bullet 2 — Experience and skills required:
   - Always state the required years of experience if mentioned in the JD.
   - Include the 2–3 most critical required skills (not all of them).
   - Example: "Python and FastAPI required; 0–2 years of experience accepted."
   - If experience is not mentioned: write "No specific experience level stated."

4. Bullet 3 — Location and work arrangement:
   - Be specific. Never write "flexible" or "as per company policy."
   - WRONG: "Flexible work arrangement available."
   - RIGHT: "Hybrid role in Bengaluru — 3 days office, 2 days remote per week."
   - RIGHT: "Fully remote; must be available in IST timezone."
   - RIGHT: "Onsite in Pune; relocation support provided."
   - If fully remote with no location constraint: "Fully remote; no location restriction stated."

5. Bullet 4 — Compensation:
   - If salary is provided in the JD: copy it verbatim.
     RIGHT: "Salary ₹12–18 LPA with equity; exact breakdown not disclosed."
   - If salary is not in the JD: write exactly this:
     "Salary not disclosed in the job description."
   - NEVER invent, estimate, or omit salary information.

6. Bullet 5 — Something genuinely distinctive:
   - Team size, product scale, growth stage, technology depth, ownership model,
     unusual benefit, well-known engineering culture, notable company milestone.
   - WRONG: "Competitive compensation and great work culture." (generic, meaningless)
   - RIGHT: "Team of 5 engineers; you own features end-to-end from day one."
   - RIGHT: "Series C startup with $200M raised; product used by 30M Indians."
   - RIGHT: "Engineering blog is widely respected; open-source contributions expected."

7. Plain English only:
   - No corporate jargon: do not use "synergize", "leverage", "ecosystem",
     "disruptive", "scalable solutions", "results-driven", "passionate"
   - Write the way a smart colleague would explain the job to a friend

8. No repetition:
   - Each bullet must contain information not already stated in another bullet
   - If salary was mentioned in bullet 2, do not repeat it in bullet 4
```

### Example Input / Output

**Input:**
```
title: Backend Engineer
company: Razorpay
location: Bengaluru, Karnataka
experience_level: 0-2 years
salary_range: ₹12–18 LPA
raw_description: We're building the payment infrastructure that powers
India's digital economy. You'll own microservices in our core payment
routing stack (Python, FastAPI, PostgreSQL). Hybrid: 3 days Bengaluru office,
2 days WFH. 0–2 years experience. CTC ₹12–18 LPA. Team of 6 engineers.
```

**Expected Output:**
```json
{
  "summary": [
    "Own Python microservices in the payment routing stack handling millions of daily transactions.",
    "Python and FastAPI required; 0–2 years of experience accepted with strong fundamentals.",
    "Hybrid role in Bengaluru — 3 days in office, 2 days work from home each week.",
    "Salary ₹12–18 LPA; equity details not disclosed in the job description.",
    "Small team of 6 engineers with direct ownership of features from day one."
  ]
}
```

### Version History

| Version | Date | Changes |
|---|---|---|
| v1 | 2025-06-22 | Initial version |

---

## PROMPT: classifier_v1

**Agent:** Job Classifier  
**Model:** GPT-4o-mini  
**Version:** 1 (current)  
**Agent file:** `agents/job_classifier.py`  
**Input variables:** `{title}`, `{company}`, `{location}`, `{location_type}`, `{required_skills}`, `{raw_description_excerpt}`  
**Output schema:** `role_type`, `domain`, `experience_level`, `is_remote`, `is_hybrid`, `is_internship`, `company_type`, `classification_confidence`

### Purpose

Tag the job with metadata for the matching engine and filter system. Uses only the first 1,500 characters of the job description because classification is a coarser task than extraction — the opening section of a JD contains the most classification-relevant information.

GPT-4o-mini is used here (not GPT-4o) because classification against a fixed taxonomy is a bounded task that does not require the deeper language understanding needed for extraction or summarization. See `18_DECISIONS.md` D-AGENT-003.

### Known Failure Modes This Prompt Addresses

| Failure | How the Prompt Handles It |
|---|---|
| LLM returns value outside taxonomy | Rule 2 lists exact allowed values; `parse_output()` rejects any value not in the list |
| `is_remote` and `is_hybrid` both true | Rule 3 makes them mutually exclusive (hybrid implies partial remote, not full) |
| `is_internship` missed when title doesn't say "intern" | Rule 4 checks JD body too, not just title |
| Services company misclassified as product | Rule 6 gives explicit examples of each `company_type` |
| Experience level not stated, defaults to wrong value | Rule 7 requires inference from skills complexity, not a guess |

### Prompt Text

```
You are classifying a job posting using fixed taxonomies.
Use ONLY the exact values listed below — no variations, synonyms, or typos.

Job Title: {title}
Company: {company}
Location: {location}
Location Type (from JD): {location_type}
Required Skills: {required_skills}
Job Description (first 1500 chars):
---
{raw_description_excerpt}
---

Return ONLY a valid JSON object with exactly these fields:

{{
  "role_type": "...",
  "domain": "...",
  "experience_level": "...",
  "is_remote": true | false,
  "is_hybrid": true | false,
  "is_internship": true | false,
  "company_type": "...",
  "classification_confidence": 0.0
}}

1. role_type — choose exactly one:
   software_engineer, data_analyst, data_scientist, product_manager,
   devops_engineer, ml_engineer, frontend_developer, backend_developer,
   fullstack_developer, marketing_manager, growth_manager, business_analyst,
   ux_designer, qa_engineer, technical_writer, other

2. domain — choose exactly one:
   fintech, edtech, healthtech, ecommerce, saas, gaming, media,
   logistics, enterprise, startup, other

3. experience_level — choose exactly one:
   fresher, 0-1yr, 1-2yr, 2-3yr, 3-5yr, 5+yr

4. is_remote:
   - true ONLY if the role can be done 100% remotely with no required office days
   - false if any office presence is required (even 1 day/week)

5. is_hybrid:
   - true if the role specifies a mix of remote + in-office days
   - is_remote and is_hybrid cannot both be true
   - both can be false (fully onsite role)

6. is_internship:
   - true if "intern", "internship", "trainee", or "apprentice" appears in the
     job title OR the JD description
   - false otherwise

7. company_type — choose exactly one:
   - product    : Company builds and sells its own software product or platform
                  Examples: Razorpay, Swiggy, Zepto, Freshworks
   - services   : Company provides development services to external clients (IT services)
                  Examples: TCS, Infosys, Wipro, Accenture, HCL
   - startup    : Early-stage company, likely Series A or earlier, small team
   - enterprise : Large established non-tech company with an in-house tech team
                  Examples: HDFC Bank tech team, Tata Group digital
   - agency     : Creative or marketing agency with tech roles
   - unknown    : Cannot determine from available information — use this freely

8. experience_level inference:
   - If explicitly stated in the JD (e.g., "0-2 years required"): use the
     matching enum value
   - If not stated: infer from the complexity and seniority of required skills
     and responsibilities. A role requiring system design and team leadership
     is likely 3-5yr+. A role requiring "basic Python" is likely fresher/0-1yr.
   - When genuinely unclear: use "fresher" as a conservative default

9. classification_confidence:
   - 0.90+: All fields clearly determinable from the JD
   - 0.75–0.89: Most fields clear; one or two required inference
   - Below 0.75: Multiple fields required significant inference or guessing
```

### Example Input / Output

**Input:**
```
title: Growth Manager
company: Zepto
location: Mumbai, Maharashtra
location_type: onsite
required_skills: ["SQL", "Product Analytics", "Growth Marketing", "Mixpanel"]
raw_description_excerpt: Zepto is a 10-minute grocery delivery platform (Series D,
$900M raised). We're looking for a Growth Manager to own acquisition and retention
experiments. 2–4 years experience in growth or product marketing at a consumer
internet company. MBA preferred but not required. Onsite Mumbai.
```

**Expected Output:**
```json
{
  "role_type": "growth_manager",
  "domain": "ecommerce",
  "experience_level": "2-3yr",
  "is_remote": false,
  "is_hybrid": false,
  "is_internship": false,
  "company_type": "product",
  "classification_confidence": 0.91
}
```

### Version History

| Version | Date | Changes |
|---|---|---|
| v1 | 2025-06-22 | Initial version |

---

## PROMPT: notif_generator_v1

**Agent:** Notification Generator  
**Model:** GPT-4o-mini  
**Version:** 1 (current)  
**Agent file:** `agents/notification_generator.py`  
**Temperature:** 0.2 (slightly higher than other agents — allows natural phrasing variation)  
**Input variables:** `{title}`, `{company}`, `{location}`, `{location_type_emoji}`, `{posted_label}`, `{bullet_1}` through `{bullet_5}`, `{skills_line}`  
**Output schema:** `message_body` (a single formatted string)

### Purpose

Write the body of the Telegram notification message. By the time this agent runs, all structured data is already extracted and validated. This agent's only job is to assemble it into natural, scannable Telegram-formatted text.

**Important:** Skill match icons (✅/❌) are computed deterministically in application code before this prompt runs — they are not generated by the LLM. The `{skills_line}` variable is pre-assembled. See `agents/notification_generator.py`.

### When This Prompt Runs

Unlike the 5 pipeline agents that run once per job, this agent runs once per user-job pair at notification dispatch time. It is called by the notification dispatcher immediately before `bot.send_message()` is called.

### Known Failure Modes This Prompt Addresses

| Failure | How the Prompt Handles It |
|---|---|
| Overly formal tone | Rule 2 instructs conversational, mobile-native tone |
| Redundant header text | Rule 3 prohibits repeating the title or company in the body |
| HTML tags broken in Telegram | Rule 4 restricts to Telegram-supported HTML subset |
| Message too long for mobile scan | Rule 5 sets the length target |

### Prompt Text

```
You are formatting a job alert message for Telegram. The message will be
read on a phone by a student in under 20 seconds. Format for scannability.

Data to format:
- Title: {title}
- Company: {company}
- Location: {location}
- Work mode emoji: {location_type_emoji}
- Posted: {posted_label}
- Summary bullet 1: {bullet_1}
- Summary bullet 2: {bullet_2}
- Summary bullet 3: {bullet_3}
- Summary bullet 4: {bullet_4}
- Summary bullet 5: {bullet_5}
- Skills line (pre-formatted, do not modify): {skills_line}

Return ONLY a valid JSON object with this field:

{{
  "message_body": "the full formatted Telegram message as a single string"
}}

Format rules:

1. Use this exact structure:

🚀 <b>New Job Match</b>

<b>{title}</b>
{company} · {location} · {location_type_emoji}
📅 Posted {posted_label}

📋 <b>What this involves:</b>
• {bullet_1}
• {bullet_2}
• {bullet_3}
• {bullet_4}
• {bullet_5}

{skills_line}

2. Tone: conversational and direct. This is a notification, not a press release.
   The student has 20 seconds to decide. Every word must earn its place.

3. Do not add any text beyond the structure above:
   - No "Hope this helps!" or sign-off
   - No re-stating the company name or title in the body
   - No commentary on the role ("This looks like a great opportunity")
   - The structure IS the message — no introduction needed

4. Telegram HTML formatting only — these tags work, all others are ignored:
   <b>bold</b>, <i>italic</i>, <a href="url">link</a>, <code>code</code>
   Never use: <h1>, <h2>, <strong>, <em>, <br>, <p>, <div>, or markdown

5. Target message length: 200–350 characters (excluding the skills line).
   Long messages get collapsed in Telegram — the student only sees the first
   few lines before tapping "expand". The title, company, and posted time
   must appear before any collapse cutoff.

6. Newlines: use literal \n characters in the JSON string value.
   The structure above shows where newlines belong.
```

### Static Fallback Template

When the Notification Generator agent fails (LLM unavailable, parse error after repair), the dispatcher falls back to this static Python template — no LLM involved:

```python
# agents/notification_generator.py

STATIC_FALLBACK = (
    "🚀 <b>New Job Match</b>\n\n"
    "<b>{title}</b>\n"
    "{company} · {location}\n"
    "📅 Posted {posted_label}\n\n"
    "{skills_line}"
)
```

The fallback omits the 5-bullet summary (since the Summarizer may have also failed or its output may be unavailable at dispatch time). The notification still delivers the critical information (title, company, location, posted time, skill match icons) and the Apply button is attached as an inline keyboard regardless of which template is used.

### Version History

| Version | Date | Changes |
|---|---|---|
| v1 | 2025-06-22 | Initial version |

---

## PROMPT: resume_extractor_v1

**Agent:** Resume Skill Extractor  
**Model:** GPT-4o  
**Version:** 1 (current)  
**Agent file:** `agents/resume_skill_extractor.py`  
**Phase:** 2  
**Input variables:** `{user_name}`, `{resume_text}`  
**Output schema:** `skills[]`, `unrecognized_terms[]`

### Purpose

Extract technical skills from a user's resume PDF text. The extracted skills are presented to the user for confirmation before being written to their profile. This is distinct from the job-side Skill Extractor — it reads a person's resume rather than a company's job description.

### Key Differences from skill_extractor_v1

| Dimension | skill_extractor_v1 (JD) | resume_extractor_v1 (Resume) |
|---|---|---|
| Input | Job description | Resume text |
| Output | required + preferred split | Single skills list |
| Canonical mapping | Strict | Strict + unrecognized bucket |
| Context | What a company wants | What a person has |
| Error tolerance | Low (production job data) | Higher (user can correct) |

### Known Failure Modes This Prompt Addresses

| Failure | How the Prompt Handles It |
|---|---|
| User's name extracted as a skill | Rule 1 provides `{user_name}` as context to ignore |
| Company names extracted as skills | Rule 2 explicitly excludes employer names |
| Job titles extracted as skills | Rule 3 excludes role names |
| Proprietary internal tools incorrectly mapped | Rule 6 routes unrecognized terms to `unrecognized_terms[]` |
| University or degree names treated as skills | Rule 4 excludes education-related terms |

### Prompt Text

```
You are extracting technical skills from a resume. Your goal is to find
every technology, tool, language, and framework the person has used —
and nothing else.

Candidate Name (for context — do not extract this as a skill): {user_name}
Resume Text:
---
{resume_text}
---

Return ONLY a valid JSON object with exactly these fields:

{{
  "skills": ["canonical skill name 1", "canonical skill name 2"],
  "unrecognized_terms": ["tool or term you saw but could not map to a canonical skill"]
}}

Inclusion rules — extract these:
1. Programming languages: Python, JavaScript, Java, Go, Rust, C++, etc.
2. Frameworks and libraries: React, FastAPI, Spring Boot, TensorFlow, etc.
3. Databases: PostgreSQL, MongoDB, Redis, MySQL, Elasticsearch, etc.
4. Cloud platforms and services: AWS, Google Cloud, Azure, S3, Lambda, etc.
5. DevOps and infrastructure tools: Docker, Kubernetes, Terraform, Ansible, etc.
6. Development tools: Git, GitHub, Jira, Postman, VS Code (only if notable)
7. Methodologies (use sparingly): "Machine Learning", "Deep Learning",
   "REST API", "GraphQL", "Microservices", "Agile" — only if clearly
   demonstrated through projects or experience, not just mentioned in passing

Exclusion rules — do NOT extract these:
8. The candidate's name: {user_name}
9. Employer/company names: "Google", "Infosys", "my previous startup"
10. Job titles and roles: "Software Engineer", "Team Lead", "Intern"
11. Universities and degrees: "IIT Bombay", "B.Tech", "MBA"
12. Certifications (the cert name, not the technology):
    "AWS Certified Solutions Architect" → extract "AWS", not the cert name
13. Soft skills: communication, leadership, teamwork, problem-solving
14. Vague buzzwords without a clear technology: "cloud computing" (use specific
    cloud name instead), "data analysis" (use the specific tool)
15. Project names and product names that are not tools

Canonicalization rules:
16. Use canonical names: "JavaScript" not "JS", "PostgreSQL" not "Postgres",
    "Kubernetes" not "K8s", "Node.js" not "NodeJS"
17. Strip version numbers: "Python 3.9" → "Python"
18. If you see a tool name you recognize but it doesn't match a common
    canonical form: use your best judgment for the canonical name, and
    also add it to unrecognized_terms so the team can verify

unrecognized_terms:
19. Add to unrecognized_terms any tool name you saw in the resume that you
    could not confidently map to a well-known canonical skill name.
    This helps the platform team expand the canonical skills list.
    Example: a proprietary analytics tool used at a specific company.
20. Do NOT add commonly known technologies to unrecognized_terms.
21. If unrecognized_terms is empty, return an empty array: []
```

### Example Input / Output

**Input:**
```
user_name: Rahul Verma
resume_text:
RAHUL VERMA
rahul.verma@email.com

SKILLS
Languages: JavaScript (ES6+), Python, HTML5, CSS3
Frameworks: React.js, Node.js, Express.js, Flask
Databases: MongoDB, PostgreSQL (basic), Firebase
Tools: Git, GitHub, Postman, VS Code, Figma (basic)
Other: REST APIs, JSON, Agile/Scrum

PROJECTS
E-commerce Platform (React + Node.js + MongoDB)
  - Built full-stack shopping app with Stripe payment integration
  - Deployed on InternalHosting v2.3

EXPERIENCE
Freelance Developer (2023–2024)
  - Built 8 WordPress sites for small businesses
  - Used ProprietaryClientCMS for 2 enterprise clients
```

**Expected Output:**
```json
{
  "skills": [
    "JavaScript", "Python", "HTML", "CSS",
    "React", "Node.js", "Express", "Flask",
    "MongoDB", "PostgreSQL", "Firebase",
    "Git", "REST API", "Stripe"
  ],
  "unrecognized_terms": [
    "InternalHosting v2.3",
    "ProprietaryClientCMS",
    "WordPress"
  ]
}
```

**Note:** WordPress is intentionally in `unrecognized_terms` here because while it's well-known, it is not a programming skill in the traditional sense — the team should decide whether to add it to the canonical list. This is the correct conservative behavior.

### Version History

| Version | Date | Changes |
|---|---|---|
| v1 | 2025-06-22 | Initial version |

---

## Prompt Versioning Workflow

When any prompt needs to be updated (output quality issue, new failure mode discovered, model guidance changed):

### Step 1 — Write the New Version

Add the new version below the current version in this document. Do not delete the old version.

```markdown
### extractor_v2 [New version]
...new prompt text...

### extractor_v1 [Superseded by extractor_v2 — 2025-09-15]
...old prompt text (kept for audit trail)...
```

### Step 2 — Update the Agent File

```python
# agents/job_extractor.py
class JobExtractorAgent(BaseAgent):
    prompt_version = "extractor_v2"   # Was "extractor_v1"
```

### Step 3 — Update the Index Table

Update the `Status` column in the Prompt Index table at the top of this document.

### Step 4 — Test Before Deploying

Run the agent against a test set of at least 10 job descriptions and verify:
- Output quality is equal to or better than the old version
- Parse success rate is still ≥ 95%
- No new failure modes introduced

```bash
python scripts/test_prompt.py --prompt extractor_v2 --test-set tests/fixtures/jd_samples/
```

### Step 5 — Document in Changelog

Add an entry to `22_CHANGELOG.md`:
```
## 2025-09-15
- Updated extractor_v1 → extractor_v2: improved deadline extraction to
  correctly exclude start dates (regression found in 3% of JDs)
```

### Step 6 — Monitor After Deploy

After deploying the new version, check `agent_logs` for:
- `prompt_version = 'extractor_v2'` records appearing
- `status = 'failed'` rate for the new version vs. old version
- `extraction_confidence` distribution — should not significantly decrease

```sql
-- Compare failure rates between versions
SELECT prompt_version,
       COUNT(*) FILTER (WHERE status = 'failed') AS failures,
       COUNT(*) AS total,
       ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'failed') / COUNT(*), 2)
           AS failure_pct
FROM agent_logs
WHERE agent_name = 'job_extractor'
  AND created_at > now() - interval '7 days'
GROUP BY prompt_version
ORDER BY prompt_version;
```

---

## Prompt Testing Fixtures

Test prompts against these standard fixtures before deploying any update.

### Standard JD Test Set (10 samples)

Located at `tests/fixtures/jd_samples/`:

| File | ATS Source | Type | Tests For |
|---|---|---|---|
| `greenhouse_swe_bengaluru.txt` | Greenhouse | SWE, India | Standard extraction |
| `workday_data_analyst_remote.txt` | Workday | Data Analyst, Remote | Remote detection |
| `lever_pm_hybrid_mumbai.txt` | Lever | Product Manager, Hybrid | Hybrid detection |
| `icims_mba_growth_no_degree.txt` | iCIMS | Growth, "no degree required" | degree_required=false |
| `taleo_services_company.txt` | Taleo | SWE, Services company | company_type=services |
| `generic_startup_ashby.txt` | Ashby | Fullstack, Startup | company_type=startup |
| `sparse_jd_low_confidence.txt` | Unknown | Any | Low confidence handling |
| `salary_not_disclosed.txt` | Greenhouse | SWE | salary_range=null |
| `internship_jd.txt` | Lever | Internship | is_internship=true |
| `non_english_partial.txt` | Workday | SWE | Low confidence, non-English |

Run all test fixtures:
```bash
python scripts/test_prompt.py --all-agents --test-set tests/fixtures/jd_samples/
```

---

*This document is the single source of truth for all LLM prompts used in production. A prompt that exists only in application code is invisible, unversioned, and unauditable. Every prompt change starts here.*
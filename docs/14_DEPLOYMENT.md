# 14 — Deployment

**Document Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-06-22  
**Owner:** Engineering Lead  

---

## Purpose of This Document

This document is the complete reference for deploying, operating, and maintaining Job Finder AI in production. It covers the production topology, Docker configuration, CI/CD pipeline, environment management, database migration strategy, monitoring, logging, backup procedures, rollback strategy, and scaling plan. Any engineer or AI assistant performing a deployment must read this document first. If a deployment procedure contradicts this document, this document is the authority.

---

## Table of Contents

1. [Production Topology](#1-production-topology)
2. [Local Development Setup](#2-local-development-setup)
3. [Docker Configuration](#3-docker-configuration)
4. [Environment Management](#4-environment-management)
5. [CI/CD Pipeline](#5-cicd-pipeline)
6. [Database Migrations](#6-database-migrations)
7. [Service Startup Order](#7-service-startup-order)
8. [Monitoring & Alerting](#8-monitoring--alerting)
9. [Logging](#9-logging)
10. [Backup Strategy](#10-backup-strategy)
11. [Rollback Procedures](#11-rollback-procedures)
12. [Scaling](#12-scaling)
13. [Secrets Rotation in Production](#13-secrets-rotation-in-production)
14. [Release Checklist](#14-release-checklist)
15. [Runbooks](#15-runbooks)

---

## 1. Production Topology

### 1.1 Service Map

```mermaid
flowchart TB
    subgraph Internet
        U[Users / Browsers]
        TG[Telegram]
    end

    subgraph Edge["Cloudflare (CDN + DDoS)"]
        CF[Cloudflare Proxy\nTLS termination\nDDoS protection]
    end

    subgraph Frontend["Vercel (Frontend)"]
        NEXT[Next.js App\nSSR + Static\nauto-scaled]
    end

    subgraph Backend["Railway / Render (Backend)"]
        API[FastAPI\nUvicorn 2 workers\nPort 8000]
        SCHED[Scheduler Process\nAPScheduler\nSingle instance]
    end

    subgraph Data["Managed Data Services"]
        PG[(PostgreSQL\nSupabase / Railway\nManaged + backups)]
        REDIS[(Redis\nUpstash\nManaged)]
        R2[(Cloudflare R2\nObject Storage\nPrivate bucket)]
    end

    subgraph External["Third-Party APIs"]
        TGAPI[Telegram Bot API]
        OAI[OpenAI API]
        ANT[Anthropic API]
        EMAIL[Resend]
        GOOGLE[Google OAuth]
    end

    U --> CF
    TG --> CF
    CF --> NEXT
    CF --> API
    NEXT --> API
    API --> PG
    API --> REDIS
    API --> R2
    SCHED --> PG
    SCHED --> REDIS
    SCHED --> OAI
    SCHED --> ANT
    API --> TGAPI
    API --> EMAIL
    API --> GOOGLE
    TGAPI -.->|webhook| API
```

### 1.2 Service Responsibilities

| Service | Host | Process | Replicas | Notes |
|---|---|---|---|---|
| Next.js Frontend | Vercel | Node.js (managed) | Auto | Stateless; Vercel handles scaling |
| FastAPI Backend | Railway | Uvicorn + Gunicorn (2 workers) | 1 initially | Scale to 2+ on traffic growth |
| APScheduler | Railway | Python (single worker) | **1 always** | Must never run more than one instance — would duplicate scrape batches |
| PostgreSQL | Supabase or Railway | Managed | 1 primary | Read replicas added at Phase 3+ |
| Redis | Upstash | Managed | 1 | Upgrade tier as queue volume grows |
| Object Storage | Cloudflare R2 | Managed | N/A | |

### 1.3 Domain Configuration

| Domain | Points To | Purpose |
|---|---|---|
| `jobfinderai.com` | Vercel | Marketing + frontend app |
| `www.jobfinderai.com` | Vercel | Redirect to apex |
| `api.jobfinderai.com` | Railway/Render backend | FastAPI REST API |
| `staging.jobfinderai.com` | Vercel staging | Pre-production frontend |
| `api-staging.jobfinderai.com` | Railway/Render staging | Pre-production API |

All domains are proxied through Cloudflare for DDoS protection and CDN caching of static assets.

---

## 2. Local Development Setup

### 2.1 Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Docker Desktop | ≥ 4.20 | Required for `docker compose` |
| Python | 3.12 | For running backend outside Docker (optional) |
| Node.js | 20 LTS | For running frontend outside Docker (optional) |
| Git | Any | |

### 2.2 First-Time Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/job-finder-ai.git
cd job-finder-ai

# 2. Copy environment file and fill in values
cp .env.example .env
# Edit .env with your API keys (see Section 4)

# 3. Start all services
docker compose up -d

# 4. Run database migrations
docker compose exec backend alembic upgrade head

# 5. Seed reference data (skills, role types, cities)
docker compose exec backend python scripts/seed_db.py

# 6. Verify everything is running
docker compose ps
# Expected: backend, frontend, postgres, redis — all "Up"

# 7. Open the app
open http://localhost:3000   # Frontend
open http://localhost:8000/docs  # FastAPI auto-generated API docs
```

### 2.3 Common Development Commands

```bash
# Start all services
docker compose up -d

# Stop all services (data preserved)
docker compose down

# Stop and wipe all data volumes (full reset)
docker compose down -v

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f backend

# Run a one-off command in the backend container
docker compose exec backend python scripts/test_scraper.py --company-id 1

# Open a PostgreSQL shell
docker compose exec postgres psql -U jobfinderai -d jobfinderai

# Open a Redis CLI
docker compose exec redis redis-cli

# Run backend tests
docker compose exec backend pytest tests/

# Run frontend tests
docker compose exec frontend npm test

# Create a new Alembic migration after changing a model
docker compose exec backend alembic revision --autogenerate -m "add my_new_column"

# Apply pending migrations
docker compose exec backend alembic upgrade head

# Rollback one migration
docker compose exec backend alembic downgrade -1
```

### 2.4 Hot Reload

Both services support hot reload during development via volume mounts:

- **Backend:** Uvicorn runs with `--reload` in development mode; any change to `backend/` restarts the server.
- **Frontend:** Next.js Fast Refresh automatically updates the browser on any change to `frontend/`.

---

## 3. Docker Configuration

### 3.1 Directory Structure

```
job-finder-ai/
├── docker-compose.yml          # Local development
├── docker-compose.prod.yml     # Production overrides (used in CI/CD)
├── backend/
│   └── Dockerfile
├── frontend/
│   └── Dockerfile
└── .dockerignore
```

### 3.2 `docker-compose.yml` (Local Development)

```yaml
# docker-compose.yml
version: "3.9"

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: jobfinderai
      POSTGRES_USER: jobfinderai
      POSTGRES_PASSWORD: localpassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U jobfinderai"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app         # Hot reload via volume mount
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      DATABASE_URL: postgresql+asyncpg://jobfinderai:localpassword@postgres:5432/jobfinderai
      REDIS_URL: redis://redis:6379/0
      ENVIRONMENT: local
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  scheduler:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: python -m scheduler.main
    volumes:
      - ./backend:/app
    env_file: .env
    environment:
      DATABASE_URL: postgresql+asyncpg://jobfinderai:localpassword@postgres:5432/jobfinderai
      REDIS_URL: redis://redis:6379/0
      ENVIRONMENT: local
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development      # Uses dev stage for hot reload
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules      # Prevent host node_modules from overriding container's
      - /app/.next
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 3.3 `backend/Dockerfile`

```dockerfile
# backend/Dockerfile
FROM python:3.12.4-slim@sha256:abc123def456...   # Pinned digest

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies (for generic HTML adapter)
RUN pip install playwright==1.44.0 && playwright install chromium --with-deps

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Production: run with Gunicorn process manager
# Development: override with uvicorn --reload (see docker-compose.yml)
CMD ["gunicorn", "main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]

EXPOSE 8000

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser
USER appuser
```

### 3.4 `frontend/Dockerfile`

```dockerfile
# frontend/Dockerfile

# --- Development stage ---
FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 3000

# --- Build stage ---
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# --- Production stage ---
FROM node:20-alpine AS production
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 3000
CMD ["node", "server.js"]
```

The production stage uses Next.js's `output: "standalone"` mode (configured in `next.config.ts`) to produce a minimal self-contained server without the full `node_modules` directory — significantly reducing the image size.

### 3.5 `.dockerignore`

```
# .dockerignore (root)
.git
.github
docs
**/.env
**/.env.*
**/node_modules
**/__pycache__
**/*.pyc
**/.pytest_cache
**/.mypy_cache
**/dist
**/.next
```

---

## 4. Environment Management

### 4.1 Environment Matrix

| Variable | Local | Staging | Production | Notes |
|---|---|---|---|---|
| `ENVIRONMENT` | `local` | `staging` | `production` | Controls CORS origins, debug mode |
| `DATABASE_URL` | Docker Compose postgres | Managed staging DB | Managed production DB | |
| `REDIS_URL` | Docker Compose redis | Upstash staging | Upstash production | |
| `JWT_SECRET_KEY` | Any dev value | Unique secret | Unique secret — never same as staging |
| `OPENAI_API_KEY` | Real key (test carefully) | Real key (spending limit) | Real key (production limit) | |
| `TELEGRAM_BOT_TOKEN` | Test bot token | Test bot token | Production bot token | Never use production bot locally |
| `DEBUG` | `true` | `false` | `false` | Never true in production |

### 4.2 All Required Environment Variables

```bash
# .env.example — copy this to .env for local development

# ── Application ──────────────────────────────────
ENVIRONMENT=local                          # local | staging | production
DEBUG=true                                 # true only in local

# ── Database ─────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://jobfinderai:localpassword@postgres:5432/jobfinderai

# ── Redis ────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── Security ─────────────────────────────────────
JWT_SECRET_KEY=generate-with-secrets.token_hex-32    # python -c "import secrets; print(secrets.token_hex(32))"

# ── Google OAuth ─────────────────────────────────
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...

# ── AI / LLM ─────────────────────────────────────
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
STRONG_MODEL=gpt-4o
FAST_MODEL=gpt-4o-mini

# ── Telegram ─────────────────────────────────────
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...         # Use a test bot for local dev
TELEGRAM_WEBHOOK_SECRET=generate-with-secrets.token_hex-32
ADMIN_TELEGRAM_CHAT_ID=-1001234567890         # Admin alerts channel

# ── Email ────────────────────────────────────────
RESEND_API_KEY=re_...
EMAIL_FROM_ADDRESS=alerts@jobfinderai.com
EMAIL_FROM_NAME=Job Finder AI

# ── Object Storage (Cloudflare R2) ───────────────
R2_ENDPOINT_URL=https://accountid.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=jobfinderai-resumes

# ── Frontend (Next.js) ───────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8000    # In production: https://api.jobfinderai.com
NEXTAUTH_URL=http://localhost:3000           # In production: https://jobfinderai.com
NEXTAUTH_SECRET=generate-with-secrets.token_hex-32

# ── Scraper ──────────────────────────────────────
SCRAPE_BATCH_SIZE=20
MAX_JOBS_PER_COMPANY=50
SCRAPE_INTERVAL_MINUTES=15

# ── Monitoring ───────────────────────────────────
SENTRY_DSN=                                  # Optional; add for error tracking
```

### 4.3 Secret Generation Commands

```bash
# Generate JWT_SECRET_KEY, NEXTAUTH_SECRET, TELEGRAM_WEBHOOK_SECRET:
python -c "import secrets; print(secrets.token_hex(32))"

# Generate a strong random password for local PostgreSQL:
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

### 4.4 Staging vs. Production Separation

**Hard rules:**
- Production `JWT_SECRET_KEY` must never match staging — a staging compromise must not give access to production sessions
- Production `TELEGRAM_BOT_TOKEN` must be a different bot from the test/staging bot — production user Telegram IDs must never be exposed to test environments
- Production database credentials are stored only in the hosting platform's secrets vault, never in any file or document accessible to developers

---

## 5. CI/CD Pipeline

**File:** `.github/workflows/deploy.yml`

### 5.1 Pipeline Overview

```mermaid
flowchart TD
    A[Push to any branch] --> B[Lint & Format Check]
    B --> C[Run Tests\npytest + jest]
    C --> D{Tests pass?}
    D -->|No| E[Block merge\nNotify author]
    D -->|Yes| F{Which branch?}
    F -->|Feature branch| G[PR checks complete\nMerge when ready]
    F -->|main| H[Build Docker Images]
    H --> I[Push to GitHub\nContainer Registry]
    I --> J[Deploy to Staging]
    J --> K[Run DB Migrations\non staging]
    K --> L[Run Smoke Tests\nagainst staging API]
    L --> M{Smoke tests pass?}
    M -->|No| N[Rollback staging\nAlert team]
    M -->|Yes| O[Manual Approval Gate\nor auto-promote]
    O --> P[Deploy to Production]
    P --> Q[Run DB Migrations\non production]
    Q --> R[Health Check\n/health endpoint]
    R --> S{Healthy?}
    S -->|Yes| T[Deploy Complete]
    S -->|No| U[Auto-Rollback\nAlert team]
```

### 5.2 Full Pipeline Definition

```yaml
# .github/workflows/deploy.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  BACKEND_IMAGE: ghcr.io/${{ github.repository }}/backend
  FRONTEND_IMAGE: ghcr.io/${{ github.repository }}/frontend

jobs:
  # ── Job 1: Lint ──────────────────────────────────────────────────────
  lint:
    name: Lint & Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Python linting tools
        run: pip install ruff mypy

      - name: Run ruff (lint + format check)
        run: ruff check backend/ && ruff format --check backend/

      - name: Run mypy (type check)
        run: mypy backend/ --ignore-missing-imports

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Install frontend deps
        run: npm ci
        working-directory: frontend

      - name: Run ESLint
        run: npm run lint
        working-directory: frontend

      - name: Run TypeScript check
        run: npm run type-check
        working-directory: frontend

  # ── Job 2: Tests ─────────────────────────────────────────────────────
  test:
    name: Tests
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: jobfinderai_test
          POSTGRES_USER: jobfinderai
          POSTGRES_PASSWORD: testpassword
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 3
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Python dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
        working-directory: backend

      - name: Run Alembic migrations on test DB
        env:
          DATABASE_URL: postgresql+asyncpg://jobfinderai:testpassword@localhost:5432/jobfinderai_test
        run: alembic upgrade head
        working-directory: backend

      - name: Run pytest
        env:
          DATABASE_URL: postgresql+asyncpg://jobfinderai:testpassword@localhost:5432/jobfinderai_test
          REDIS_URL: redis://localhost:6379/0
          JWT_SECRET_KEY: test-secret-key-do-not-use-in-production
          ENVIRONMENT: test
        run: pytest tests/ -v --cov=. --cov-report=xml --cov-fail-under=70
        working-directory: backend

      - name: Upload coverage report
        uses: codecov/codecov-action@v4
        with:
          file: backend/coverage.xml

      - name: Run frontend tests
        run: npm test -- --coverage --watchAll=false
        working-directory: frontend

  # ── Job 3: Build & Push Docker Images ────────────────────────────────
  build:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    outputs:
      backend-tag: ${{ steps.meta-backend.outputs.tags }}
      frontend-tag: ${{ steps.meta-frontend.outputs.tags }}

    steps:
      - uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Docker meta — backend
        id: meta-backend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.BACKEND_IMAGE }}
          tags: |
            type=sha,prefix=sha-
            type=raw,value=latest

      - name: Docker meta — frontend
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.FRONTEND_IMAGE }}
          tags: |
            type=sha,prefix=sha-
            type=raw,value=latest

      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta-backend.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          target: production
          push: true
          tags: ${{ steps.meta-frontend.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            NEXT_PUBLIC_API_URL=${{ secrets.NEXT_PUBLIC_API_URL }}

  # ── Job 4: Deploy to Staging ──────────────────────────────────────────
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    environment: staging

    steps:
      - name: Deploy backend to Railway (staging)
        run: |
          curl -X POST "${{ secrets.RAILWAY_STAGING_DEPLOY_WEBHOOK }}" \
               -H "Authorization: Bearer ${{ secrets.RAILWAY_API_KEY }}"

      - name: Wait for staging to be healthy
        run: |
          for i in $(seq 1 20); do
            STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
              https://api-staging.jobfinderai.com/health)
            if [ "$STATUS" = "200" ]; then
              echo "Staging is healthy"
              exit 0
            fi
            echo "Attempt $i: Status $STATUS — waiting 15s"
            sleep 15
          done
          echo "Staging health check failed after 5 minutes"
          exit 1

      - name: Run smoke tests against staging
        run: |
          # Test critical endpoints
          curl -f https://api-staging.jobfinderai.com/health
          curl -f "https://api-staging.jobfinderai.com/api/jobs?limit=1"
          curl -f "https://api-staging.jobfinderai.com/api/preferences/role-types"
          echo "Smoke tests passed"

  # ── Job 5: Deploy to Production ───────────────────────────────────────
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production    # Requires manual approval in GitHub Environments

    steps:
      - name: Deploy backend to Railway (production)
        run: |
          curl -X POST "${{ secrets.RAILWAY_PRODUCTION_DEPLOY_WEBHOOK }}" \
               -H "Authorization: Bearer ${{ secrets.RAILWAY_API_KEY }}"

      - name: Wait for production health
        run: |
          for i in $(seq 1 20); do
            STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
              https://api.jobfinderai.com/health)
            if [ "$STATUS" = "200" ]; then
              echo "Production is healthy"
              exit 0
            fi
            echo "Attempt $i: Status $STATUS — waiting 15s"
            sleep 15
          done
          echo "Production health check failed — initiating rollback"
          exit 1

      - name: Notify team on success
        if: success()
        run: |
          curl -s -X POST "https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage" \
            -d "chat_id=${{ secrets.ADMIN_TELEGRAM_CHAT_ID }}" \
            -d "text=✅ Production deployment successful — commit ${{ github.sha }}"

      - name: Notify team on failure
        if: failure()
        run: |
          curl -s -X POST "https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage" \
            -d "chat_id=${{ secrets.ADMIN_TELEGRAM_CHAT_ID }}" \
            -d "text=🔴 Production deployment FAILED — commit ${{ github.sha }} — manual intervention required"
```

### 5.3 GitHub Actions Secrets Required

```
# Repository secrets (Settings → Secrets and variables → Actions)
RAILWAY_API_KEY
RAILWAY_STAGING_DEPLOY_WEBHOOK
RAILWAY_PRODUCTION_DEPLOY_WEBHOOK
NEXT_PUBLIC_API_URL              # https://api.jobfinderai.com
TELEGRAM_BOT_TOKEN               # For deployment notifications
ADMIN_TELEGRAM_CHAT_ID           # Admin channel for deployment alerts
```

Production environment variables are stored in Railway's platform UI — not in GitHub secrets — so they are never transmitted through the CI pipeline.

### 5.4 GitHub Environments

| Environment | Approval Required | Allowed Branches |
|---|---|---|
| `staging` | None (auto-deploy) | `main` |
| `production` | Manual approval from Engineering Lead | `main` |

The production environment gate ensures no accidental production deployment happens without human sign-off.

---

## 6. Database Migrations

### 6.1 Migration Rules (Non-Negotiable)

These rules are defined in `07_DATABASE.md` and `01_PRD.md` and are reproduced here for completeness:

1. **All schema changes via Alembic only** — no direct `ALTER TABLE` or `CREATE TABLE` in production, ever
2. **Every migration must have a working `downgrade()`** where technically feasible
3. **Migrations are reviewed in pull requests** — not rubber-stamped
4. **Data migrations are separate from schema migrations** — a column add and its data backfill are two separate Alembic revisions
5. **This document and `07_DATABASE.md` are updated in the same PR** as any migration

### 6.2 Migration Workflow

```bash
# 1. Make changes to SQLAlchemy models in backend/models/

# 2. Generate migration
alembic revision --autogenerate -m "add skill_category_index"

# 3. Review the generated file carefully
# Common issues to fix manually:
#   - Enum changes (autogenerate doesn't handle these well)
#   - Index changes on large tables (add CONCURRENTLY to avoid locks)
#   - Data migrations (not auto-generated at all)

# 4. Test upgrade
alembic upgrade head

# 5. Test downgrade
alembic downgrade -1

# 6. Re-apply
alembic upgrade head

# 7. Commit migration file with the model changes
```

### 6.3 Production Migration Execution

Migrations run **as part of the deployment pipeline**, not as a separate manual step. This ensures the running code and the database schema are always in sync:

```bash
# In the CI/CD pipeline, after the new image is deployed:
railway run --service backend alembic upgrade head
```

If the migration fails, the deployment is considered failed and the rollback procedure (Section 11) is triggered.

### 6.4 Zero-Downtime Migration Strategy

For tables with live traffic (especially `jobs`, `users`), schema changes that would lock the table must use PostgreSQL's concurrent operations:

```python
# alembic/versions/add_index_concurrently.py
from alembic import op

def upgrade():
    # CONCURRENTLY — does not lock the table during index creation
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_deadline
        ON jobs(deadline)
        WHERE deadline IS NOT NULL
    """)

def downgrade():
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_jobs_deadline")
```

**Changes that are generally safe (no lock required):**
- Adding a nullable column
- Adding an index with `CONCURRENTLY`
- Adding a new table

**Changes that require a maintenance window or special handling:**
- Renaming a column (requires two-phase: add column → backfill → drop old column)
- Changing a column type
- Adding a NOT NULL constraint to an existing column with data
- Dropping a column referenced by application code (requires code deployment first)

---

## 7. Service Startup Order

Services must start in a specific order to avoid connection errors on fresh boot.

```mermaid
flowchart LR
    A[(PostgreSQL)] --> B[(Redis)]
    B --> C[FastAPI Backend]
    C --> D[APScheduler]
    C --> E[Next.js Frontend]
```

In Docker Compose, this is enforced via `depends_on` with health checks (see Section 3.2). In production (Railway), services are deployed independently — the backend has a startup retry loop that waits for the database to be available:

```python
# backend/core/database.py

async def wait_for_db(max_attempts: int = 30):
    for attempt in range(max_attempts):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            log.info("Database connection established")
            return
        except Exception as e:
            log.warning(f"DB not ready (attempt {attempt + 1}/{max_attempts}): {e}")
            await asyncio.sleep(2)
    raise RuntimeError("Could not connect to database after 60 seconds")

# Called at application startup
@app.on_event("startup")
async def startup():
    await wait_for_db()
    await run_migrations()   # Apply any pending Alembic migrations on startup
```

The scheduler process will not start if the backend is unavailable — it shares the same database connection pool and will log and exit if the DB is unreachable.

---

## 8. Monitoring & Alerting

### 8.1 Health Check Endpoint

```python
# backend/api/health.py

@router.get("/health")
async def health_check():
    checks = {
        "database": "unknown",
        "redis": "unknown",
    }

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception:
        checks["database"] = "disconnected"

    # Redis check
    try:
        await redis.ping()
        checks["redis"] = "connected"
    except Exception:
        checks["redis"] = "disconnected"

    status = "ok" if all(v == "connected" for v in checks.values()) else "degraded"
    status_code = 200 if status == "ok" else 503

    return JSONResponse(
        content={
            "status": status,
            **checks,
            "timestamp": datetime.utcnow().isoformat()
        },
        status_code=status_code
    )
```

### 8.2 Uptime Monitoring

| Service | Monitor URL | Tool | Alert When |
|---|---|---|---|
| Production API | `https://api.jobfinderai.com/health` | UptimeRobot | Status ≠ 200 for 3 consecutive checks (every 1 min) |
| Production Frontend | `https://jobfinderai.com` | UptimeRobot | Status ≠ 200 for 3 consecutive checks |
| Staging API | `https://api-staging.jobfinderai.com/health` | UptimeRobot | Status ≠ 200 for 5 consecutive checks |
| TLS Certificate | `api.jobfinderai.com` | UptimeRobot SSL | Expiry < 14 days |

Alert destination: **Admin Telegram channel** for critical (P0/P1), **email** for warnings.

### 8.3 Application-Level Alerts

These are triggered by the application itself via the admin Telegram channel (see `11_NOTIFICATION_SYSTEM.md` Section 16):

| Condition | Threshold | Alert |
|---|---|---|
| Scraper consecutive failures | ≥ 3 per company | Admin Telegram immediately |
| API error rate | > 5% over 5 minutes | Admin Telegram |
| LLM agent parse failure rate | > 10% over 1 hour | Admin Telegram |
| Notification delivery rate | < 95% over 1 hour | Admin Telegram |
| Queue backlog | > 1,000 items in `agent:queue` | Admin Telegram |

### 8.4 Metrics Queries (Admin Dashboard)

The admin dashboard surfaces key operational metrics using queries on `scrape_runs`, `agent_logs`, and `notification_logs`. See `11_NOTIFICATION_SYSTEM.md` Section 11.4 for the specific SQL queries. These run on a 60-second auto-refresh cycle and are cached in Redis.

---

## 9. Logging

### 9.1 Log Format

All services emit structured JSON logs. Every log line includes:

```json
{
  "timestamp": "2025-06-22T08:30:00.000Z",
  "level": "INFO",
  "service": "backend",
  "environment": "production",
  "trace_id": "a1b2c3d4e5f6",
  "message": "Job scraped successfully",
  "company_id": 42,
  "jobs_found": 14,
  "duration_ms": 3214
}
```

### 9.2 Logging Configuration

```python
# backend/core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "backend",
            "environment": settings.ENVIRONMENT,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        # Merge any extra fields passed via logger.info("msg", extra={...})
        for key in vars(record):
            if key not in ("message", "levelname", "msg", "args", "exc_info",
                           "exc_text", "stack_info", "name", "pathname",
                           "filename", "module", "lineno", "funcName",
                           "created", "msecs", "relativeCreated", "thread",
                           "threadName", "processName", "process"):
                log_data[key] = getattr(record, key)
        return json.dumps(log_data)

def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(handler)
    # Suppress noisy library loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

### 9.3 Log Levels

| Level | Use for |
|---|---|
| `DEBUG` | Detailed per-request data; only in local development (`DEBUG=true`) |
| `INFO` | Normal operation events (scrape completed, notification sent) |
| `WARNING` | Retryable failures, rate limit hits, CAPTCHA detected |
| `ERROR` | Non-retryable failures that need investigation |
| `CRITICAL` | Service-threatening events that require immediate human response |

**Rule:** `DEBUG` logs must never contain sensitive data (passwords, tokens, API keys). `INFO` and above are written in production — they must also be clean per `13_SECURITY.md` Section 11.4.

### 9.4 Log Aggregation

Production logs from Railway/Render are forwarded to **Better Stack** (or equivalent hosted log viewer) via the platform's log drain feature. Engineers can:
- Search logs by `trace_id`, `company_id`, `user_id`, `level`
- Set log-based alerts (e.g., alert on `level = CRITICAL`)
- Retain logs for 30 days in the log viewer (full logs retained per the platform's storage limits)

### 9.5 Request Tracing

Every HTTP request generates a `trace_id` (UUID) that propagates through the request lifecycle and appears in all log lines generated during that request:

```python
# backend/middleware/logging_middleware.py
import uuid

@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    # Make trace_id available in logging context
    with trace_context(trace_id):
        response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response
```

The `X-Trace-ID` header is returned to the client — if a user reports a bug with a timestamp, the frontend includes this ID in error reports so the corresponding backend logs can be found instantly.

---

## 10. Backup Strategy

### 10.1 PostgreSQL Backups

| Backup Type | Frequency | Retention | Managed By |
|---|---|---|---|
| Automated snapshot | Daily | 7 daily + 4 weekly | Supabase/Railway managed backup |
| Point-in-time recovery | Continuous WAL | 7-day recovery window | Supabase/Railway |

### 10.2 Backup Verification

Backups are tested monthly via a restore drill:
1. Restore the latest daily snapshot to a temporary database
2. Run the full test suite against the restored DB
3. Verify row counts for critical tables match production (within expected range)
4. Drop the temporary database

The restore drill result is documented in a monthly ops log entry. If restore takes > 4 hours (our RTO target), the backup strategy is reviewed.

### 10.3 Redis Backup

Redis data is ephemeral by design — caches and queues can be rebuilt from PostgreSQL. RDB snapshots are enabled on Upstash by default (every 60 seconds for the most recent changes). A Redis restart causes:
- Cache misses → rebuilt automatically from the API (latency spike, not data loss)
- Queue items in-flight → may be re-processed (idempotent by design via DB dedup)
- Rate limit state → reset (brief window of less-strict rate limiting, acceptable)

### 10.4 Object Storage (R2) Backup

Resume PDFs in the `jobfinderai-resumes` bucket are versioned (Cloudflare R2 versioning enabled). Accidental overwrites can be recovered from the previous version. Deletion is logged in audit_logs and is irreversible by design (GDPR compliance).

---

## 11. Rollback Procedures

### 11.1 Application Rollback (Code Only)

If a deployment introduces a bug that doesn't involve a database schema change:

```bash
# Railway: redeploy the previous deployment
railway rollback --service backend --deployment {previous_deployment_id}

# Or via the Railway dashboard:
# Services → Backend → Deployments → Select previous → Redeploy

# Verify the rollback is healthy
curl https://api.jobfinderai.com/health
```

Application-level rollback is fast (< 2 minutes) and is the preferred first response to a production issue.

### 11.2 Database Migration Rollback

If a migration introduced a data problem:

```bash
# Check current migration version
alembic current

# Roll back one migration
alembic downgrade -1

# Roll back to a specific revision
alembic downgrade {revision_id}

# Verify the rollback
alembic current
```

**After rolling back the migration**, the application code must also be rolled back to the version that worked with the previous schema. Rolling back the migration without rolling back the code will cause the app to fail.

### 11.3 Full Rollback Decision Tree

```mermaid
flowchart TD
    A[Issue detected in production] --> B{Database schema\nchange in this release?}
    B -->|No| C[Roll back application code\nvia Railway]
    C --> D{Issue resolved?}
    D -->|Yes| E[Incident closed\nPost-mortem within 1 week]
    D -->|No| F[Escalate — investigate DB data]
    B -->|Yes| G{Is the migration\nreversible?}
    G -->|Yes| H[Roll back migration\nThen roll back application code]
    H --> D
    G -->|No| I[Do NOT roll back migration\nRoll back application code only\nFix forward with a new migration]
    I --> D
```

### 11.4 What "Roll Back Application Code" Means

1. Identify the previous stable deployment SHA in Railway's deployment history
2. Redeploy that SHA via Railway's dashboard or CLI
3. Verify the `/health` endpoint returns 200
4. Verify the key user-facing flows work (browse jobs, login)
5. Send notification to admin Telegram channel: "Rolled back to {previous SHA} — investigating"

---

## 12. Scaling

### 12.1 Current Limits and Scaling Triggers

| Component | Current Configuration | Trigger to Scale | Action |
|---|---|---|---|
| FastAPI | 2 Uvicorn workers, 1 instance | p95 API latency > 500ms sustained | Add Railway replicas; enable load balancing |
| PostgreSQL | 1 managed instance | Query latency > 100ms, CPU > 70% sustained | Upgrade instance tier; add read replica for jobs feed |
| Redis | 256MB Upstash | Memory > 80%, queue backlog > 1,000 | Upgrade Upstash tier |
| Scheduler | 1 instance | N/A — cannot scale horizontally | Increase batch size; optimize adapter speed |
| Scraper Workers | In-process | Scrape batch duration > 12 min | Separate scraper into dedicated worker containers |

### 12.2 Horizontal Scaling of the API

When adding API replicas, session affinity is not required (the application is fully stateless — all state in PostgreSQL/Redis):

```
Railway configuration:
  - Replicas: 2 (up from 1)
  - Load balancing: Round-robin
  - Health check path: /health
  - Drain timeout: 30 seconds (allows in-flight requests to complete)
```

### 12.3 Database Connection Pooling

As API replicas increase, direct PostgreSQL connections become a bottleneck. PgBouncer connection pooling is introduced when API replicas exceed 3:

```
PgBouncer (transaction pooling mode):
  - Pool size: 20 connections per database
  - Max client connections: 100
  - Pool mode: transaction (most efficient; each query gets a connection)
  - Deployed as: sidecar container alongside the API
```

This allows 100 concurrent API workers to share 20 database connections, preventing the PostgreSQL connection limit from being reached.

### 12.4 The 50,000-User Scaling Path

Per `05_ARCHITECTURE.md` Section 12, the current architecture supports 50,000 users without a rewrite. The sequence of changes needed as we grow:

```
0 → 1,000 users:     Current configuration (single API, single DB)
1,000 → 5,000 users:  Add 1 API replica; upgrade Upstash tier
5,000 → 20,000 users: Add PgBouncer; separate scraper workers; read replica for jobs feed
20,000 → 50,000 users: CDN caching for public job pages; Redis Cluster; second API region
```

---

## 13. Secrets Rotation in Production

### 13.1 Rotating JWT_SECRET_KEY

Rotating the JWT secret invalidates all active access tokens. Refresh tokens use a separate mechanism and are NOT invalidated by this rotation.

```
1. Generate new key: python -c "import secrets; print(secrets.token_hex(32))"
2. Update JWT_SECRET_KEY in Railway's environment variables
3. Trigger a new deployment (Railway restarts the service with the new key)
4. Active access tokens (15-min TTL) expire naturally
5. Users transparently get new tokens via the refresh-token cookie
6. No user-facing disruption — refresh happens automatically
```

### 13.2 Rotating Database Password

```
1. In Supabase/Railway: generate a new database password
2. Update DATABASE_URL in Railway's environment variables
3. Trigger a new deployment
4. Old password is invalidated by the database provider
5. Brief connection pool reset on restart — < 5 seconds of elevated error rate
```

### 13.3 Rotating LLM API Keys

```
1. In OpenAI/Anthropic dashboard: generate a new API key
2. Update OPENAI_API_KEY / ANTHROPIC_API_KEY in Railway
3. Trigger deployment
4. Immediately revoke the old key in the dashboard
5. Verify new key works by checking agent_logs for successful calls
```

### 13.4 Rotating Telegram Webhook Secret

```
1. Generate new secret: python -c "import secrets; print(secrets.token_hex(32))"
2. Update TELEGRAM_WEBHOOK_SECRET in Railway
3. Trigger deployment (new secret takes effect)
4. Re-register the webhook with the new secret:
   curl "https://api.telegram.org/bot{TOKEN}/setWebhook" \
     -d "url=https://api.jobfinderai.com/api/webhooks/telegram" \
     -d "secret_token={NEW_SECRET}"
5. Verify incoming webhook events are being processed
```

---

## 14. Release Checklist

This checklist must be completed before every production deployment.

### Pre-Deployment

- [ ] All CI checks pass (lint, types, tests, coverage ≥ 70%)
- [ ] PR has been reviewed and approved by at least one other engineer
- [ ] Any new environment variables are added to `.env.example` and documented in Section 4.2
- [ ] If this release includes a DB migration:
  - [ ] Migration file reviewed (not just autogenerated output)
  - [ ] `downgrade()` function is complete and tested
  - [ ] `07_DATABASE.md` updated in the same PR
  - [ ] Large table changes use `CONCURRENTLY`
- [ ] If this release changes an API endpoint:
  - [ ] `08_API.md` updated
  - [ ] Frontend changes are backward-compatible or deployed simultaneously
- [ ] Security checklist items relevant to this change reviewed (see `13_SECURITY.md` Section 19)
- [ ] CHANGELOG updated in `22_CHANGELOG.md`

### Deployment

- [ ] Deploy to staging via CI/CD pipeline
- [ ] Smoke tests pass against staging
- [ ] Manually test the key changed feature on staging
- [ ] Manual approval granted for production deployment
- [ ] Monitor production logs for 15 minutes after deployment:
  - No spike in error-level log entries
  - `/health` returning 200
  - Scraper health dashboard shows normal activity
  - Notification delivery rate normal

### Post-Deployment

- [ ] Send deployment notification to admin Telegram channel (automated)
- [ ] Update `17_TASKS.md` for completed items
- [ ] Add entry to `22_CHANGELOG.md` with the version tag
- [ ] If anything unexpected happened during deployment: write it up in `18_DECISIONS.md`

---

## 15. Runbooks

Runbooks are step-by-step guides for common operational tasks. They are written to be followed by anyone with production access — including in the middle of a 2 AM incident.

### Runbook 1 — Restart the Backend Service

**When:** API is returning 5xx errors; health check is failing; memory leak suspected.

```bash
# Via Railway CLI
railway restart --service backend

# Via Railway dashboard
# Services → Backend → Settings → Restart

# Verify
curl https://api.jobfinderai.com/health
# Expected: {"status": "ok", "database": "connected", "redis": "connected"}
```

### Runbook 2 — Clear the Agent Queue Backlog

**When:** `agent:queue` in Redis has > 1,000 items; jobs are not being processed.

```bash
# Check queue length
redis-cli -u $REDIS_URL LLEN agent:queue

# If the scheduler is healthy but the queue is stuck,
# the agent pipeline worker has likely crashed.

# Check scheduler logs
railway logs --service scheduler --tail 100

# Restart the scheduler
railway restart --service scheduler

# After restart, verify queue is draining
redis-cli -u $REDIS_URL LLEN agent:queue  # Should decrease over the next few minutes
```

### Runbook 3 — Manually Trigger a Scrape for One Company

**When:** A company's scraper shows failed status; want to test after fixing an adapter.

```bash
# Via the admin dashboard
# Admin → Scraper Health → Company row → "Run Now" button

# Via API (admin authenticated)
curl -X POST https://api.jobfinderai.com/api/admin/companies/{company_id}/run-now \
  -H "Authorization: Bearer {admin_access_token}"

# Via CLI (scripts/test_scraper.py)
docker compose exec backend python scripts/test_scraper.py --company-id 42 --run-now
```

### Runbook 4 — Revoke All User Sessions (Security Incident)

**When:** JWT_SECRET_KEY has been compromised; all sessions must be invalidated immediately.

```bash
# Step 1: Rotate the secret (generates new key, deploys automatically)
# [Follow Section 13.1]

# Step 2: Additionally, wipe all refresh tokens
# This forces everyone to log in again, even after the new key is deployed
railway run --service backend python -c "
import asyncio
from backend.core.database import get_db

async def revoke_all():
    async for db in get_db():
        await db.execute('DELETE FROM refresh_tokens')
        await db.commit()
        print('All refresh tokens revoked')

asyncio.run(revoke_all())
"

# Step 3: Notify users via email if PII may have been exposed
# [Follow 13_SECURITY.md Section 20.2 — P0 procedure]
```

### Runbook 5 — Disable Notifications During Incident

**When:** Notification system is sending bad data; need to stop all outbound messages immediately.

```bash
# Option A: Stop the scheduler (stops matching + dispatch)
railway stop --service scheduler

# Option B: If only Telegram is affected, temporarily disable Telegram dispatch
# Set TELEGRAM_ENABLED=false in Railway environment variables
# New deployments will respect this flag immediately (no restart needed if using env watchers)

# To re-enable
railway restart --service scheduler   # or remove the env flag
```

### Runbook 6 — Database Emergency Read-Only Mode

**When:** A bug is writing corrupt data; need to stop writes while investigating.

```bash
# Revoke write permissions from the application user
# Connect to PostgreSQL as the admin user (via Supabase/Railway dashboard):
REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM jobfinderai_app;

# Application will continue to serve reads (jobs feed, etc.) but all writes will fail
# This gives time to investigate without causing further data corruption

# Re-grant write permissions when the issue is resolved:
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO jobfinderai_app;
```

---

*This document governs how the platform is built, deployed, and operated. Deployment procedures not described here have not been reviewed for safety. When in doubt about a production operation, stop and consult this document or a senior engineer before proceeding.*
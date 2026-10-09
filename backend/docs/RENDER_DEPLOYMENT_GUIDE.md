# Render Deployment Guide
## Abundance Zone Youth Management Platform v2.0

**Complete Step-by-Step Guide for Production Deployment**

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Database Setup (Neon PostgreSQL)](#2-database-setup-neon-postgresql)
3. [Redis Setup (Upstash)](#3-redis-setup-upstash-redis)
4. [Celery Configuration](#4-celery-configuration)
5. [Render Web Service Setup](#5-render-web-service-setup)
6. [Render Background Workers](#6-render-background-workers)
7. [Environment Variables](#7-environment-variables)
8. [Database Migrations](#8-database-migrations)
9. [Health Checks & Monitoring](#9-health-checks--monitoring)
10. [Post-Deployment Verification](#10-post-deployment-verification)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Prerequisites

### Required Accounts
- ✅ GitHub account (for code repository)
- ✅ Render account (https://render.com)
- ✅ Neon account (https://neon.tech) 
- ✅ Upstash account (https://upstash.com)
- ✅ Firebase account (https://firebase.google.com)
- ✅ Google AI Studio (for Gemini API key)
- ✅ OpenAI account (for GPT-4o Vision)
- ✅ Cloudinary account (for file storage)
- ✅ Resend account (for email)

### Local Setup
```bash
git clone <your-repo-url>
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. Database Setup (Neon PostgreSQL)

### Step 2.1: Create Neon Database

1. Go to [Neon Console](https://console.neon.tech)
2. Click **"New Project"**
3. Configure:
   - **Name**: `abundance-zone-production`
   - **PostgreSQL Version**: `16`
   - **Region**: `US East (Ohio)` (aws-us-east-2)
   - **Compute**: `Autoscaling` (0.25 - 1 vCPU)
4. Click **"Create Project"**

### Step 2.2: Get Connection Strings

After creation, navigate to **Connection Details** tab:

**Pooled Connection (for FastAPI):**
```
postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Important**: Convert to asyncpg format for FastAPI:
```
postgresql+asyncpg://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Direct Connection (for Alembic migrations):**
```
postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### Step 2.3: Configure Connection Pooling

In Neon Console → **Settings** → **Connection pooling**:
- Enable **PgBouncer**
- Max connections: `100`
- Pool mode: `Transaction`

### Step 2.4: Enable Extensions

Connect to your database and run:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For full-text search
```

---

## 3. Redis Setup (Upstash Redis)

### Step 3.1: Create Upstash Redis Database

1. Go to [Upstash Console](https://console.upstash.com/redis)
2. Click **"Create Database"**
3. Configure:
   - **Name**: `abundance-zone-cache`
   - **Type**: `Regional`
   - **Region**: `us-east-1` (closest to Render US East)
   - **TLS**: `Enabled`
   - **Eviction**: `allkeys-lru`
4. Click **"Create"**

### Step 3.2: Get Redis Connection String

From the database details page, copy the **REST URL** or **Redis URL**:

**Redis URL (for Python redis client):**
```
rediss://default:<password>@us1-xxx.upstash.io:6379
```

**For Celery, we need TWO Redis databases:**

**Option 1: Use URL suffixes (recommended)**
- Broker: `rediss://default:<password>@us1-xxx.upstash.io:6379/0`
- Backend: `rediss://default:<password>@us1-xxx.upstash.io:6379/1`

**Option 2: Create separate databases**
1. Create second database: `abundance-zone-celery`
2. Use different URLs for broker and backend

### Step 3.3: Configure Redis Settings

In Upstash Console → Database → **Configuration**:
- **Max Memory**: `1 GB` (adjust based on plan)
- **Persistence**: Enable **AOF** (Append-Only File)
- **Eviction Policy**: `allkeys-lru`

---

## 4. Celery Configuration

### Step 4.1: Review Celery Setup

The project already has Celery configured. Verify these files exist:

**`app/celery_app.py`** (should exist or create):
```python
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "abundance_zone_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)
```

**`app/tasks.py`** (background tasks):
```python
from app.celery_app import celery_app
from app.core.database import get_db

@celery_app.task(name="sync_attendance_to_firestore")
def sync_attendance_to_firestore():
    """Sync attendance data to Firestore every 5 minutes"""
    # Implementation
    pass

@celery_app.task(name="send_event_reminders")
def send_event_reminders():
    """Send event reminders daily at 8 AM"""
    # Implementation
    pass

@celery_app.task(name="generate_daily_analytics")
def generate_daily_analytics():
    """Generate analytics reports daily at 2 AM"""
    # Implementation
    pass
```

### Step 4.2: Test Celery Locally

```bash
# Terminal 1: Start Celery Worker
celery -A app.celery_app worker --loglevel=info

# Terminal 2: Start Celery Beat (scheduler)
celery -A app.celery_app beat --loglevel=info

# Terminal 3: Test task
python
>>> from app.tasks import sync_attendance_to_firestore
>>> result = sync_attendance_to_firestore.delay()
>>> result.get(timeout=10)
```

---

## 5. Render Web Service Setup

### Step 5.1: Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. **Connect Repository**:
   - Authorize GitHub
   - Select your repository
   - Branch: `main`

### Step 5.2: Configure Service

**Basic Configuration:**
- **Name**: `abundance-zone-backend`
- **Region**: `Ohio (US East)`
- **Branch**: `main`
- **Root Directory**: `backend` (if monorepo, leave blank if backend is root)

**Build & Deploy:**
- **Runtime**: `Docker`
- **Dockerfile Path**: `Dockerfile` (or `backend/Dockerfile` if monorepo)

### Step 5.3: Create Dockerfile (if not exists)

Create `backend/Dockerfile`:
```dockerfile
# Use Python 3.12.9 slim image
FROM python:3.12.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application with Gunicorn + Uvicorn workers
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

### Step 5.4: Configure Instance

**Instance Type:**
- **Plan**: `Standard` ($25/month per instance)
- **CPU**: 2 vCPU
- **RAM**: 4 GB
- **Instances**: 3 (for high availability)

**Auto-Deploy:**
- ✅ Enable **Auto-Deploy** from `main` branch

**Scaling:**
- **Auto-Scaling**: Enable
- **Min Instances**: 1
- **Max Instances**: 3
- **CPU Threshold**: 70%

---

## 6. Render Background Workers

### Step 6.1: Create Celery Worker Service

1. In Render Dashboard, click **"New +"** → **"Background Worker"**
2. Select same repository
3. Configure:
   - **Name**: `abundance-zone-celery-worker`
   - **Region**: `Ohio (US East)` (same as web service)
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `Dockerfile.worker`

### Step 6.2: Create Worker Dockerfile

Create `backend/Dockerfile.worker`:
```dockerfile
FROM python:3.12.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Start Celery Worker
CMD ["celery", "-A", "app.celery_app", "worker", \
     "--loglevel=info", \
     "--concurrency=4", \
     "--max-tasks-per-child=1000"]
```

### Step 6.3: Create Celery Beat Service (Scheduler)

1. Create another Background Worker: `abundance-zone-celery-beat`
2. Use same Dockerfile but different command

Create `Dockerfile.beat`:
```dockerfile
FROM python:3.12.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Start Celery Beat (only ONE instance should run!)
CMD ["celery", "-A", "app.celery_app", "beat", "--loglevel=info"]
```

**⚠️ IMPORTANT**: Only run **ONE** Celery Beat instance!

---

## 7. Environment Variables

### Step 7.1: Add Environment Variables to Render

In Render Dashboard → Your Web Service → **Environment** tab:

Click **"Add Environment Variable"** and add ALL these:

```bash
# ─── Application ─────────────────────────────────────────────────────────
ENVIRONMENT=production
APP_NAME=Abundance Zone Youth Platform v2.0
APP_VERSION=2.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8000
WORKERS=4
ALLOWED_HOSTS=["abundancezone.onrender.com","abundancezone.org","www.abundancezone.org"]
CORS_ORIGINS=["https://abundancezone.org","https://www.abundancezone.org"]

# ─── Database (Neon PostgreSQL) ──────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
DATABASE_URL_SYNC=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# ─── Redis (Upstash) ─────────────────────────────────────────────────────
REDIS_URL=rediss://default:password@us1-xxx.upstash.io:6379
CELERY_BROKER_URL=rediss://default:password@us1-xxx.upstash.io:6379/0
CELERY_RESULT_BACKEND=rediss://default:password@us1-xxx.upstash.io:6379/1

# ─── JWT Secrets ─────────────────────────────────────────────────────────
# Generate with: openssl rand -hex 32
JWT_SECRET_KEY=<generate-64-char-hex-string>
JWT_REFRESH_SECRET_KEY=<generate-different-64-char-hex-string>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ─── AI Services ─────────────────────────────────────────────────────────
GOOGLE_API_KEY=AIzaSy...
OPENROUTER_API_KEY=sk-or-v1-...
OPENAI_API_KEY=sk-proj-...

# ─── File Storage (Cloudinary) ───────────────────────────────────────────
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=123456789
CLOUDINARY_API_SECRET=abc...

# ─── Email (Resend) ──────────────────────────────────────────────────────
RESEND_API_KEY=re_...
EMAIL_FROM=noreply@abundancezone.org
EMAIL_FROM_NAME=Abundance Zone Youth Platform

# ─── WhatsApp (Twilio) - Optional ────────────────────────────────────────
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# ─── Firebase ────────────────────────────────────────────────────────────
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=abc...
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@your-project.iam.gserviceaccount.com

# ─── Frontend URL ────────────────────────────────────────────────────────
FRONTEND_URL=https://abundancezone.org
EMAIL_VERIFICATION_EXPIRE_HOURS=24
PASSWORD_RESET_EXPIRE_HOURS=2

# ─── Rate Limiting ───────────────────────────────────────────────────────
RATE_LIMIT_PER_MINUTE=100
AUTH_RATE_LIMIT_PER_MINUTE=20

# ─── Cache TTL ───────────────────────────────────────────────────────────
AI_CACHE_TTL_SECONDS=86400
ANALYTICS_CACHE_TTL_SECONDS=2592000

# ─── Database Seed ───────────────────────────────────────────────────────
SEED_ADMIN_EMAIL=admin@abundancezone.org
SEED_ADMIN_PASSWORD=<generate-strong-password>
SEED_BRANCH_NAME=Oke-Afa 2 Branch

# ─── Error Monitoring (Sentry) ───────────────────────────────────────────
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Step 7.2: Copy Same Variables to Background Workers

1. Go to **Celery Worker** service → Environment
2. Copy **ALL** environment variables from Web Service
3. Go to **Celery Beat** service → Environment
4. Copy **ALL** environment variables from Web Service

**⚠️ All three services (Web, Worker, Beat) need SAME environment variables!**

---

## 8. Database Migrations

### Step 8.1: Create Build Script

Create `backend/bin/build.sh`:
```bash
#!/usr/bin/env bash
set -e

echo "=== Running Database Migrations ==="
python -m alembic upgrade head

echo "=== Migrations Complete ==="
```

Make it executable:
```bash
chmod +x bin/build.sh
```

### Step 8.2: Configure Build Command in Render

In Render Dashboard → Web Service → **Settings** → **Build & Deploy**:

**Build Command:**
```bash
pip install -r requirements.txt && chmod +x bin/build.sh && ./bin/build.sh
```

**OR** add to Dockerfile:
```dockerfile
# Add before CMD
RUN python -m alembic upgrade head
```

**⚠️ Note**: Running migrations in Dockerfile means they run EVERY time a new container starts. Better to run manually:

### Step 8.3: Manual Migration (Recommended)

After first deployment:

1. Go to Render Dashboard → Web Service → **Shell**
2. Run:
```bash
python -m alembic upgrade head
```

3. Verify:
```bash
python -m alembic current
```

---

## 9. Health Checks & Monitoring

### Step 9.1: Configure Health Check in Render

Render automatically uses `/health` endpoint.

**Verify in:**
- Render Dashboard → Web Service → **Settings** → **Health Check Path**: `/health`
- **Health Check Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

### Step 9.2: Test Health Endpoint

After deployment:
```bash
curl https://your-service.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "environment": "production"
}
```

### Step 9.3: Setup External Monitoring

**UptimeRobot:**
1. Go to [UptimeRobot](https://uptimerobot.com)
2. Add New Monitor:
   - Type: HTTPS
   - URL: `https://your-service.onrender.com/health`
   - Interval: 5 minutes
   - Alert: Email + SMS

**Sentry (Error Tracking):**
1. Go to [Sentry.io](https://sentry.io)
2. Create new Python project
3. Copy DSN
4. Add to Render environment: `SENTRY_DSN=https://xxx@sentry.io/xxx`

**LogTail (Log Aggregation):**
1. Go to [LogTail](https://logtail.com)
2. Create source
3. Configure in code (already in project)

---

## 10. Post-Deployment Verification

### Step 10.1: Verify Services

**Web Service:**
```bash
# Check health
curl https://your-service.onrender.com/health

# Check API docs
curl https://your-service.onrender.com/docs

# Test auth endpoint
curl -X POST https://your-service.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "Password123!",
    "role": "YOUTH_MEMBER",
    "branch_id": "your-branch-id"
  }'
```

**Database Connection:**
```bash
# In Render Shell
python
>>> from app.core.database import engine
>>> from sqlalchemy import text
>>> async def test():
...     async with engine.begin() as conn:
...         result = await conn.execute(text("SELECT 1"))
...         print(result.scalar())
>>> import asyncio
>>> asyncio.run(test())
```

**Redis Connection:**
```bash
python
>>> from app.core.redis import redis_client
>>> await redis_client.ping()
True
```

**Celery Worker:**
```bash
# Check worker logs in Render Dashboard
# Look for: "[2024-10-09 00:00:00,000: INFO/MainProcess] celery@hostname ready"
```

### Step 10.2: Seed Initial Data

Run seed script:
```bash
# In Render Shell
python scripts/seed_database.py
```

Or create admin user manually:
```bash
python
>>> from app.infrastructure.security.password_hasher import PasswordHasher
>>> from app.infrastructure.repositories.user_repository import UserRepository
>>> from app.core.database import get_db
>>> 
>>> hasher = PasswordHasher()
>>> hashed = hasher.hash_password("SecurePassword123!")
>>> 
>>> # Create admin user (pseudo-code, adjust to your repo)
>>> async def create_admin():
...     async for db in get_db():
...         repo = UserRepository()
...         await repo.create({
...             "name": "Admin",
...             "email": "admin@abundancezone.org",
...             "password": hashed,
...             "role": "SUPER_ADMIN"
...         }, db)
>>> 
>>> import asyncio
>>> asyncio.run(create_admin())
```

### Step 10.3: Performance Testing

**Load Test:**
```bash
# Install locust locally
pip install locust

# Create locustfile.py (test script)
# Run load test
locust -f locustfile.py --host=https://your-service.onrender.com
```

**Response Time Test:**
```bash
# Using curl
for i in {1..10}; do
  curl -o /dev/null -s -w "Response time: %{time_total}s\n" \
    https://your-service.onrender.com/health
done
```

---

## 11. Troubleshooting

### Issue 1: Database Connection Failed

**Symptoms:**
- Error: `connection refused` or `timeout`

**Solutions:**
1. Check DATABASE_URL format includes `?sslmode=require`
2. Verify asyncpg driver: `postgresql+asyncpg://...`
3. Check Neon status: https://neon.tech/status
4. Verify IP whitelisting disabled (Neon allows all by default)
5. Test connection:
```bash
psql "postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

### Issue 2: Redis Connection Failed

**Symptoms:**
- Error: `Connection refused` or `SSL required`

**Solutions:**
1. Use `rediss://` (with double 's' for TLS)
2. Check Upstash Redis status
3. Verify password is correct (no special char escaping needed in URL)
4. Test with redis-cli:
```bash
redis-cli -u "rediss://default:password@us1-xxx.upstash.io:6379" PING
```

### Issue 3: Celery Worker Not Processing Tasks

**Symptoms:**
- Tasks stuck in PENDING state
- No worker logs

**Solutions:**
1. Check worker logs in Render Dashboard
2. Verify CELERY_BROKER_URL matches web service
3. Ensure Redis database index differs (0 vs 1)
4. Restart worker service
5. Test manually:
```python
from app.celery_app import celery_app
celery_app.control.inspect().active()
```

### Issue 4: Database Migrations Failed

**Symptoms:**
- Error during deployment
- Tables not created

**Solutions:**
1. Check alembic version:
```bash
python -m alembic current
```
2. If empty, initialize:
```bash
python -m alembic stamp head
python -m alembic upgrade head
```
3. Check DATABASE_URL_SYNC is correct (without +asyncpg)
4. Manual fix:
```bash
# In Render Shell
python -m alembic upgrade head --sql > migration.sql
psql $DATABASE_URL_SYNC < migration.sql
```

### Issue 5: High Memory Usage

**Symptoms:**
- OOM (Out of Memory) errors
- Slow response times

**Solutions:**
1. Reduce DATABASE_POOL_SIZE (default: 20 → 10)
2. Reduce Gunicorn workers (4 → 2)
3. Enable connection pooling in Neon
4. Monitor with:
```python
import psutil
print(f"Memory: {psutil.virtual_memory().percent}%")
```
5. Upgrade Render plan (4GB → 8GB)

### Issue 6: Slow API Response

**Symptoms:**
- High latency (> 1 second)

**Solutions:**
1. Enable Redis caching for frequently accessed data
2. Add database indexes:
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_youths_branch_id ON youths(branch_id);
CREATE INDEX idx_events_date ON events(event_date);
```
3. Use `selectinload` for relationships (already implemented)
4. Check slow queries:
```sql
SELECT query, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

### Issue 7: CORS Errors

**Symptoms:**
- Browser console: `CORS policy blocked`

**Solutions:**
1. Verify CORS_ORIGINS includes your frontend domain
2. Ensure protocol matches (https://)
3. Check ALLOWED_HOSTS
4. Test with curl:
```bash
curl -H "Origin: https://your-frontend.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS \
  https://your-api.onrender.com/api/v1/auth/login -v
```

---

## 12. Custom Domain Setup

### Step 12.1: Configure Custom Domain in Render

1. Go to Render Dashboard → Web Service → **Settings**
2. Scroll to **Custom Domain**
3. Click **"Add Custom Domain"**
4. Enter: `api.abundancezone.org`

### Step 12.2: Update DNS Records

In your domain registrar (Cloudflare, Namecheap, etc.):

**Add CNAME record:**
```
Type: CNAME
Name: api
Value: your-service.onrender.com
TTL: Auto
```

### Step 12.3: Wait for SSL Certificate

Render automatically provisions SSL certificate via Let's Encrypt. Wait 5-10 minutes.

### Step 12.4: Update Environment Variables

```bash
ALLOWED_HOSTS=["api.abundancezone.org","abundancezone.org"]
CORS_ORIGINS=["https://abundancezone.org"]
```

---

## 13. Scaling & Performance

### Horizontal Scaling

In Render Dashboard → Web Service → **Scaling**:

**Manual Scaling:**
- Min Instances: 1
- Max Instances: 5

**Auto-Scaling:**
- Enable auto-scale
- CPU Threshold: 70%
- Memory Threshold: 80%

### Vertical Scaling

Upgrade plan:
- Standard: 2 vCPU, 4 GB RAM ($25/month)
- Pro: 4 vCPU, 8 GB RAM ($85/month)
- Pro Plus: 8 vCPU, 16 GB RAM ($200/month)

### Database Scaling

**Neon Autoscaling:**
- Automatically scales compute (0.25 - 4 vCPU)
- Storage: Auto-scales up to plan limit

**Read Replicas:**
1. Go to Neon Console → Branches
2. Create branch for read replica
3. Update code to route reads to replica

---

## 14. Backup & Disaster Recovery

### Database Backups

**Neon Automatic Backups:**
- Daily snapshots (30-day retention)
- Point-in-time recovery (up to 30 days)

**Manual Backup:**
```bash
# Backup
pg_dump $DATABASE_URL_SYNC > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL_SYNC < backup_20241009.sql
```

### Redis Backups

Upstash automatically creates snapshots every 24 hours.

**Manual Redis backup:**
```bash
redis-cli -u $REDIS_URL --rdb dump.rdb
```

### Application Rollback

In Render Dashboard → Web Service → **Events**:
- Click **"Rollback to Previous Deploy"**

---

## 15. Monitoring Dashboard

Create monitoring dashboard:

**Sentry:**
- Error rate
- Response time
- User sessions

**Render Metrics (builtin):**
- CPU usage
- Memory usage
- Request rate
- Response time

**Custom Prometheus Metrics:**
```python
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Database created (Neon)
- [ ] Redis created (Upstash)
- [ ] All environment variables configured
- [ ] Dockerfile created
- [ ] Alembic migrations ready
- [ ] Dependencies in requirements.txt

### Deployment
- [ ] Render Web Service deployed
- [ ] Render Celery Worker deployed
- [ ] Render Celery Beat deployed
- [ ] Database migrations run
- [ ] Health check passing
- [ ] Custom domain configured

### Post-Deployment
- [ ] Initial admin user created
- [ ] Seed data loaded
- [ ] API endpoints tested
- [ ] Celery tasks executing
- [ ] Monitoring configured
- [ ] Backups verified
- [ ] Load tested

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Neon Docs**: https://neon.tech/docs
- **Upstash Docs**: https://upstash.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Celery Docs**: https://docs.celeryq.dev

---

**Deployment Guide Version**: 1.0
**Last Updated**: October 9, 2026
**Project**: Abundance Zone Youth Management Platform v2.0

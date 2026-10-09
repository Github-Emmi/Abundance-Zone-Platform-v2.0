# 🚀 Abundance Zone Platform v2.0 — Render Deployment Checklist

## Pre-Deployment Requirements

### ✅ External Services Setup (Complete These First)

#### 1. Neon PostgreSQL Database

- [ ] Sign up at https://neon.tech
- [ ] Create new project: "abundance-zone-production"
- [ ] Enable Connection Pooling in Settings
- [ ] Copy **Pooled Connection** string → `DATABASE_URL`
- [ ] Copy **Direct Connection** string → `DATABASE_URL_SYNC`
- [ ] Enable pgvector extension (for AI features)

**Example URLs:**

```
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
DATABASE_URL_SYNC=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

#### 2. Upstash Redis Database

- [ ] Sign up at https://upstash.com
- [ ] Create new Redis database (choose nearest region)
- [ ] Enable TLS
- [ ] Set eviction policy: `allkeys-lru`
- [ ] Copy Redis URL → use for all 3 Redis variables

**Format:**

```
REDIS_URL=rediss://default:YOUR_PASSWORD@YOUR_HOST:6379
CELERY_BROKER_URL=rediss://default:YOUR_PASSWORD@YOUR_HOST:6379/0
CELERY_RESULT_BACKEND=rediss://default:YOUR_PASSWORD@YOUR_HOST:6379/1
```

#### 3. Google AI (Gemini)

- [ ] Get API key from https://makersuite.google.com/app/apikey
- [ ] Copy key → `GOOGLE_API_KEY`

#### 4. Firebase (Push Notifications)

- [ ] Create project at https://console.firebase.google.com
- [ ] Generate service account key (Settings → Service Accounts)
- [ ] Extract values for:
  - `FIREBASE_PROJECT_ID`
  - `FIREBASE_PRIVATE_KEY` (keep `\n` newlines!)
  - `FIREBASE_CLIENT_EMAIL`

#### 5. Cloudinary (File Storage)

- [ ] Sign up at https://cloudinary.com
- [ ] Get credentials from Dashboard
- [ ] Copy → `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`

#### 6. Resend (Email)

- [ ] Sign up at https://resend.com
- [ ] Create API key
- [ ] Verify domain: `abundancezone.org`
- [ ] Copy key → `RESEND_API_KEY`

#### 7. Twilio (WhatsApp - Optional)

- [ ] Sign up at https://www.twilio.com
- [ ] Set up WhatsApp sandbox
- [ ] Copy credentials → `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`

---

## Render Deployment Steps

### Step 1: Push Code to GitHub

```bash
cd "/Volumes/EmmiDev256G/Projects/abundance-zone-platform v2.0"
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Create Render Account

- [ ] Sign up at https://render.com
- [ ] Connect your GitHub account
- [ ] Authorize access to your repository

### Step 3: Deploy Using Blueprint (Automated)

1. Go to Render Dashboard
2. Click **"New" → "Blueprint"**
3. Connect your GitHub repository
4. Select branch: `main`
5. Render will detect `render.yaml` automatically
6. Click **"Apply"**

Render will create 3 services:

- ✅ `abundance-zone-backend` (Web Service)
- ✅ `abundance-zone-celery-worker` (Background Worker)
- ✅ `abundance-zone-celery-beat` (Task Scheduler)

### Step 4: Add Environment Variables

For **EACH SERVICE**, add these variables in Render Dashboard:

#### Required Secrets (mark as "Secret" in Render):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://...
DATABASE_URL_SYNC=postgresql://...

# Redis
REDIS_URL=rediss://...
CELERY_BROKER_URL=rediss://.../0
CELERY_RESULT_BACKEND=rediss://.../1

# AI
GOOGLE_API_KEY=AIza...
OPENAI_API_KEY=sk-proj-...
OPENROUTER_API_KEY=sk-or-v1-...

# File Storage
CLOUDINARY_CLOUD_NAME=your_cloud
CLOUDINARY_API_KEY=123456789
CLOUDINARY_API_SECRET=abc123xyz

# Email
RESEND_API_KEY=re_123...

# WhatsApp
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=key-id-here
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@...

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
```

#### Auto-Generated (Render creates these):

- ✅ `JWT_SECRET_KEY` (Render will generate)
- ✅ `JWT_REFRESH_SECRET_KEY` (Render will generate)

### Step 5: Deploy & Verify

#### Wait for Build

- [ ] Monitor build logs in Render Dashboard
- [ ] First deploy takes 5-10 minutes
- [ ] Watch for "Build succeeded" message

#### Run Database Migrations (Automatic)

Migrations run automatically via `buildCommand` in render.yaml:

```bash
python -m alembic upgrade head
```

#### Test Health Check

```bash
curl https://abundance-zone-backend.onrender.com/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "environment": "production",
  "version": "2.0.0",
  "database": "connected",
  "redis": "connected"
}
```

#### Test API Docs (Disabled in Production)

API docs are disabled in production. To test locally:

```bash
curl https://abundance-zone-backend.onrender.com/api/v1/auth/login
```

---

## Post-Deployment

### 1. Create Admin User

Run this in Render Shell (Dashboard → Service → Shell):

```bash
python -c "
from app.db.session import SessionLocal
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate
from app.models.enums import PlatformRole

db = SessionLocal()
admin = user_crud.create(db, UserCreate(
    email='emmidevcodes@gmail.com',
    password='Password1234!',
    first_name='Admin',
    last_name='User',
    phone_number='+2341234567890',
    platform_role=PlatformRole.ADMIN
))
print(f'Admin created: {admin.email}')
"
```

### 2. Seed Sample Data (Optional)

```bash
python -m app.db.seed
```

### 3. Configure Custom Domain

1. Go to Render Dashboard → Your Service → Settings
2. Add custom domain: `api.abundancezone.org`
3. Add DNS record at your domain provider:
   ```
   Type: CNAME
   Name: api
   Value: abundance-zone-backend.onrender.com
   ```
4. Wait for SSL certificate (5-10 minutes)

### 4. Set Up Monitoring

#### Sentry (Error Tracking)

1. Sign up at https://sentry.io
2. Create new project: "Abundance Zone Backend"
3. Copy DSN → add to `SENTRY_DSN` env var
4. Redeploy service

#### UptimeRobot (Uptime Monitoring)

1. Sign up at https://uptimerobot.com
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://api.abundancezone.org/health`
   - Interval: 5 minutes

---

## Troubleshooting

### Build Fails

**Problem:** Docker build fails with dependency errors

**Solution:**

```bash
# Test locally first
cd backend
docker build -t abundance-zone-test .
docker run -p 8000:8000 abundance-zone-test
```

### Database Connection Failed

**Problem:** `asyncpg.exceptions.InvalidPasswordError`

**Solution:**

- Verify `DATABASE_URL` has `postgresql+asyncpg://` prefix
- Check password doesn't contain special chars (URL-encode if needed)
- Enable SSL: add `?sslmode=require` to URL

### Redis Connection Failed

**Problem:** `redis.exceptions.ConnectionError`

**Solution:**

- Verify `REDIS_URL` has `rediss://` (with double 's' for TLS)
- Check Upstash console → Database is "Active"
- Test connection:
  ```bash
  python -c "import redis; r=redis.from_url('YOUR_REDIS_URL'); r.ping()"
  ```

### Celery Worker Not Processing Tasks

**Problem:** Tasks stay in "PENDING" state

**Solution:**

1. Check Celery worker logs in Render
2. Verify `CELERY_BROKER_URL` matches `REDIS_URL`
3. Ensure only 1 Beat scheduler is running
4. Restart worker service

### 502 Bad Gateway

**Problem:** Render shows "Bad Gateway" error

**Solution:**

- Check health endpoint: `/health`
- Increase `WORKERS` env var (try 2-4)
- Check logs for startup errors
- Verify PORT=8000 in environment

---

## Scaling

### Horizontal Scaling (More Instances)

**render.yaml already configured for auto-scaling:**

- Min instances: 1
- Max instances: 3
- Triggers: CPU > 70%, Memory > 80%

### Vertical Scaling (Bigger Machines)

Upgrade plan in Render Dashboard:

- Starter: 512MB RAM, 0.5 CPU ($7/month)
- Standard: 2GB RAM, 1 CPU ($25/month)
- Pro: 4GB RAM, 2 CPU ($85/month)

### Database Scaling

**Neon PostgreSQL:**

- Enable Read Replicas (2 replicas for high availability)
- Increase compute size
- Enable autoscaling

**Upstash Redis:**

- Upgrade to higher tier for more connections
- Enable persistence if needed

---

## 🎉 Deployment Complete!

Your backend is now live at:

- **API:** https://abundance-zone-backend.onrender.com
- **Custom Domain:** https://api.abundancezone.org (after DNS setup)
- **Health Check:** https://api.abundancezone.org/health

**Next Steps:**

1. Deploy frontend to Vercel
2. Update CORS_ORIGINS with frontend URL
3. Test end-to-end user flows
4. Set up CI/CD with GitHub Actions
5. Configure backup strategy

---

## Quick Commands Reference

```bash
# Check service status
curl https://api.abundancezone.org/health

# View logs
render logs abundance-zone-backend --tail

# Run migrations manually
render shell abundance-zone-backend
python -m alembic upgrade head

# Restart service
render deploy abundance-zone-backend

# Run Celery task manually
render shell abundance-zone-celery-worker
python -c "from app.tasks.example import example_task; example_task.delay()"
```

---

**📚 Full Documentation:** `/backend/docs/RENDER_DEPLOYMENT_GUIDE.md`

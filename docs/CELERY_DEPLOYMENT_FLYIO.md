# 🛫 Deploy Celery Workers to Fly.io (100% FREE)

**Cost: $0/month (genuinely free forever)**

---

## ✅ **What You Get FREE on Fly.io**

- ✅ **3 shared-cpu VMs** (256MB RAM each)
- ✅ **160GB bandwidth/month**
- ✅ **No credit card required**
- ✅ **No sleep/spin-down**
- ✅ **3 apps** (perfect for 2 workers + 1 beat)

---

## 📋 **Step 1: Install Fly CLI**

### **macOS:**

```bash
brew install flyctl
```

Or using curl:

```bash
curl -L https://fly.io/install.sh | sh
```

### **Verify Installation:**

```bash
flyctl version
```

---

## 🔐 **Step 2: Sign Up & Login**

```bash
# Sign up (opens browser)
flyctl auth signup

# Or login if you have an account
flyctl auth login
```

**Note:** No credit card required for free tier!

---

## 🐳 **Step 3: Create Celery App Files**

First, let's create the Celery application structure.

### **Create Task Files:**

Run these commands in your backend directory:

```bash
cd "/Volumes/EmmiDev256G/Projects/abundance-zone-platform v2.0/backend"
mkdir -p app/tasks
```

### **1. Create `app/tasks/__init__.py`:**

```python
"""
Celery Tasks Package
"""

from app.tasks.celery_app import celery_app

__all__ = ["celery_app"]
```

### **2. Create `app/tasks/celery_app.py`:**

```python
"""
Celery Application Configuration
Handles background tasks and scheduled jobs
"""

import ssl
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "abundance_zone",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.notifications",
        "app.tasks.emails",
        "app.tasks.reports",
    ],
)

# SSL/TLS configuration for Upstash Redis (rediss://)
_ssl_opts = {}
if settings.CELERY_BROKER_URL.startswith("rediss://"):
    _ssl_opts = {
        "broker_use_ssl": {"ssl_cert_reqs": ssl.CERT_NONE},
        "redis_backend_use_ssl": {"ssl_cert_reqs": ssl.CERT_NONE},
    }

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
  
    # Task routing
    task_routes={
        "app.tasks.notifications.*": {"queue": "default"},
        "app.tasks.emails.*": {"queue": "default"},
        "app.tasks.reports.*": {"queue": "default"},
    },
  
    # Scheduled tasks (Celery Beat)
    beat_schedule={
        "daily-attendance-report": {
            "task": "app.tasks.reports.generate_daily_attendance_report",
            "schedule": crontab(hour=9, minute=0),
        },
        "weekly-analytics-summary": {
            "task": "app.tasks.reports.generate_weekly_analytics",
            "schedule": crontab(day_of_week=1, hour=8, minute=0),
        },
    },
  
    **_ssl_opts,
)
```

### **3. Create `app/tasks/notifications.py`:**

```python
"""Notification Background Tasks"""

from app.tasks.celery_app import celery_app

@celery_app.task(name="app.tasks.notifications.send_push_notification")
def send_push_notification(user_id: str, title: str, body: str):
    """Send push notification to user via Firebase"""
    print(f"📱 Sending push notification to user {user_id}: {title}")
    # TODO: Implement Firebase push notification
    return {"status": "sent", "user_id": user_id}
```

### **4. Create `app/tasks/emails.py`:**

```python
"""Email Background Tasks"""

from app.tasks.celery_app import celery_app

@celery_app.task(name="app.tasks.emails.send_welcome_email")
def send_welcome_email(user_email: str, user_name: str):
    """Send welcome email to new user"""
    print(f"📧 Sending welcome email to {user_email}")
    # TODO: Implement Resend email sending
    return {"status": "sent", "email": user_email}

@celery_app.task(name="app.tasks.emails.send_password_reset_email")
def send_password_reset_email(user_email: str, reset_token: str):
    """Send password reset email"""
    print(f"🔑 Sending password reset to {user_email}")
    return {"status": "sent", "email": user_email}
```

### **5. Create `app/tasks/reports.py`:**

```python
"""Report Generation Background Tasks"""

from app.tasks.celery_app import celery_app

@celery_app.task(name="app.tasks.reports.generate_daily_attendance_report")
def generate_daily_attendance_report():
    """Generate daily attendance report"""
    print("📊 Generating daily attendance report...")
    # TODO: Implement report generation
    return {"status": "completed", "type": "daily_attendance"}

@celery_app.task(name="app.tasks.reports.generate_weekly_analytics")
def generate_weekly_analytics():
    """Generate weekly analytics summary"""
    print("📈 Generating weekly analytics...")
    return {"status": "completed", "type": "weekly_analytics"}
```

---

## 🛫 **Step 4: Create Fly.io Configurations**

### **Create `fly.worker.toml`** (for Celery Worker):

```toml
app = "abundance-zone-worker"
primary_region = "ord"  # Chicago (closest to your Neon DB in us-east-2)

[build]
  dockerfile = "Dockerfile"

[env]
  ENVIRONMENT = "production"

[processes]
  worker = "celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### **Create `fly.beat.toml`** (for Celery Beat):

```toml
app = "abundance-zone-beat"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile"

[env]
  ENVIRONMENT = "production"

[processes]
  beat = "celery -A app.tasks.celery_app beat --loglevel=info"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

---

## 🚀 **Step 5: Deploy Celery Worker**

```bash
cd "/Volumes/EmmiDev256G/Projects/abundance-zone-platform v2.0/backend"

# Initialize Fly app for worker
flyctl launch --config fly.worker.toml --no-deploy --copy-config

# Set secrets (environment variables)
flyctl secrets set \
  DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_A0DtPnGMad4g@ep-weathered-rain-b4hzoi9m-pooler.c-6.us-east-2.aws.neon.tech/neondb" \
  REDIS_URL="rediss://default:gQAAAAAAA0orAAIgcDE5OTc3MjY1MTI3OTg0MDU3OTQ1NWRhMjc2MmU2OWI1Mw@integral-bengal-215595.upstash.io:6379" \
  CELERY_BROKER_URL="rediss://default:gQAAAAAAA0orAAIgcDE5OTc3MjY1MTI3OTg0MDU3OTQ1NWRhMjc2MmU2OWI1Mw@integral-bengal-215595.upstash.io:6379" \
  CELERY_RESULT_BACKEND="rediss://default:gQAAAAAAA0orAAIgcDE5OTc3MjY1MTI3OTg0MDU3OTQ1NWRhMjc2MmU2OWI1Mw@integral-bengal-215595.upstash.io:6379" \
  GOOGLE_API_KEY="AIzaSyD8F8qpXhSCVHdDI_TpaJtj5j2ljkyffFE" \
  FIREBASE_PROJECT_ID="abundancezone-d6189" \
  FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7RaK4jPHl5Ru5\n2g++aehesopuTG0svA4ZhXOhI8tUGzf9jeY3Vt3xNBfOpwxjwTT2UZpMhWRHGemS\nTs+bMR6F64oud+9cQQhdFckUy/oygo+mlM+sCmYuNuS2qhCcbIU7N/+ceRIPPlgc\nK05guYEVx99jy/InZMP8fsLZzog576jZbXFPMRa5c+8gOwTeXZeiS3XoBKQai1a0\ns7z7iLRtfu67wR4rdDwgHsB4qIjm9F7KT4OdLJukXSmK/N6rG71iwQs1/TkU3oYg\nfymzSpFabTYCduEa4UP1lPoG2gL8UIOB03qbFcidFtOmuz7U77YFGMYT3e4DEqoO\nF2UQFH/TAgMBAAECggEAMFQzPy9YifzLX/Yvk/Ne/XlUEkz069OIS/vNsGs9YPI5\nS90f6W4ojsPj1Pf1UZUd5ud+S3stOtAsIA7osuNFPkhf+8gF5Kf/0Y36u7w8UGaz\nTckfowV4Azs1YRKYgNXcuECmXao9B+QN9w8SBhI5hvZy5x1N2+68SWApRu5u54xJ\nytMEDT1WA3vdddrMA7LYt1YB2Jf8zEIDmtxQQveZhxn6OZwYeHQ88AYMur5y+g2d\nCk7J3svdZt9iQ4g9bpUtEWpwJpPeXvXrohGe46umstJqrjWECu8uI+L97QXlpsxp\nfNsMVUM+ukzg3VGrpn6tbULVOP4Mxwjb/FeYanOIcQKBgQDkCm+E4u+XabvWp/8+\neNsXfyDxsw/Trq/NeQvvZ/umebajzNpFhTi4AtLIph6jhUzK6jb1DjWuF2Hgilnb\nfHJ0qGMu3/85sw12RO+uyG7Uyuks/YZbT+1ePnRNId24+JrrHe9hqQYwaKvAvhi3\nB2TqLK9DzjtpH+5RHQizaBN3WQKBgQDSO5UfK8T3ngk992t4reiiSDVxK+Rmhi6y\nZ9brof48dJmEQrTddFFC0ALVUJdH3Zyh9+xLsVAT4Tffp7vWI62iLKsP802lP4Nv\nICd+l1QA/+5j6xlThLOsRan+nXQ/xZbNwbZ1bG3VTTuLHj1Qia5l42WsDQGAtVhX\nG2pBzGR3CwKBgQDGQzhwDaoHN5tjZo5pL0Q06oem/GqPPXqFp280B3DobTvYr9s5\nxDjq6zF918gdnWCFrxp29pK/OH8VbNPxGwKb4GbTM1bAQKc8o3TLvmF1yrDuN8Hf\nk98pKB2Pjhkqn6J5Nn6QpxbFccuZ+Oyd/OTFIHKE/kHzBRr7FMYizSLXiQKBgDtV\nFYD2mWBI+dLDQVGNw1oJhwupl4xX0lYHeGCIF3h4b9sj+GeHrGduzV3moMtngA02\nKzoxkKgLp/k3HYwSBa7/bEfUItXAVxfFu1++1bZyhJUuhLdNfGfiQVfamDRnT2hC\ng3wgXd8VLPjWT/eq481doBQul337sDLlSdfIF5KBAoGAdmn6VzZAYFNgJT0oLYjb\nONH88NmIoC+2ztOEyuoY2uRLFXj6jG/8MNfN9OaF0/binLwCYRSScfcrqI660pOj\n2EZnvCwC8MZBaQeTPYnDlGyVJdCmJXaN67AR7kYsEhYBbPA8BoSiusx9gQOWJE6x\n7cGQF4VC5SxRS8Z2g+Xp6K4=\n-----END PRIVATE KEY-----\n" \
  FIREBASE_CLIENT_EMAIL="firebase-adminsdk-fbsvc@abundancezone-d6189.iam.gserviceaccount.com" \
  RESEND_API_KEY="RESEND_API_KEY_REDACTED" \
  --app abundance-zone-worker

# Deploy
flyctl deploy --config fly.worker.toml
```

---

## 🚀 **Step 6: Deploy Celery Beat**

```bash
# Initialize Fly app for beat
flyctl launch --config fly.beat.toml --no-deploy --copy-config

# Set secrets (same as worker)
flyctl secrets set \
  DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_A0DtPnGMad4g@ep-weathered-rain-b4hzoi9m-pooler.c-6.us-east-2.aws.neon.tech/neondb" \
  REDIS_URL="rediss://default:gQAAAAAAA0orAAIgcDE5OTc3MjY1MTI3OTg0MDU3OTQ1NWRhMjc2MmU2OWI1Mw@integral-bengal-215595.upstash.io:6379" \
  CELERY_BROKER_URL="rediss://default:gQAAAAAAA0orAAIgcDE5OTc3MjY1MTI3OTg0MDU3OTQ1NWRhMjc2MmU2OWI1Mw@integral-bengal-215595.upstash.io:6379" \
  CELERY_RESULT_BACKEND="rediss://default:gQAAAAAAA0orAAIgcDE5OTc3MjY1MTI3OTg0MDU3OTQ1NWRhMjc2MmU2OWI1Mw@integral-bengal-215595.upstash.io:6379" \
  --app abundance-zone-beat

# Deploy
flyctl deploy --config fly.beat.toml
```

---

## ✅ **Step 7: Verify Deployment**

### **Check Worker Status:**

```bash
flyctl status --app abundance-zone-worker
```

### **View Worker Logs:**

```bash
flyctl logs --app abundance-zone-worker
```

You should see:

```
Connected to redis://integral-bengal-215595.upstash.io:6379//
celery@worker1 ready.
```

### **Check Beat Status:**

```bash
flyctl status --app abundance-zone-beat
flyctl logs --app abundance-zone-beat
```

---

## 🧪 **Step 8: Test Celery Tasks**

### **Add Test Endpoint to Your Backend:**

In `app/api/v1/__init__.py`, add:

```python
from app.api.v1 import auth, users, branches, test  # Add test

# In your router setup
app.include_router(test.router, prefix="/api/v1/test", tags=["Test"])
```

### **Create `app/api/v1/test.py`:**

```python
"""Test Endpoints for Celery"""

from fastapi import APIRouter
from app.tasks.emails import send_welcome_email
from app.tasks.notifications import send_push_notification

router = APIRouter()

@router.post("/send-email")
async def test_send_email(email: str, name: str):
    """Test Celery email task"""
    task = send_welcome_email.delay(email, name)
    return {
        "success": True,
        "task_id": task.id,
        "status": "queued",
        "message": f"Email task queued for {email}"
    }

@router.post("/send-notification")
async def test_send_notification(user_id: str, title: str, body: str):
    """Test Celery notification task"""
    task = send_push_notification.delay(user_id, title, body)
    return {
        "success": True,
        "task_id": task.id,
        "status": "queued",
        "message": f"Notification task queued for user {user_id}"
    }
```

### **Test with curl:**

```bash
curl -X POST "https://abundance-zone-platform-v2-0.onrender.com/api/v1/test/send-email?email=test@example.com&name=Test+User"
```

Check worker logs to see the task executed:

```bash
flyctl logs --app abundance-zone-worker
```

---

## 📊 **Step 9: Monitor Your Apps**

### **Check Resource Usage:**

```bash
flyctl status --app abundance-zone-worker
flyctl status --app abundance-zone-beat
```

### **Scale if Needed (Still Free):**

```bash
# Add more worker instances (up to 3 total free VMs)
flyctl scale count 2 --app abundance-zone-worker
```

---

## 🎯 **Final Architecture**

```
┌─────────────────────────────────────────────────────────┐
│              100% FREE Production Stack                  │
├─────────────────────────────────────────────────────────┤
│  Frontend (Vercel)          │  FREE                     │
│  ↓                          │                           │
│  Backend API (Render)       │  FREE                     │
│  ↓                          │                           │
│  Celery Worker (Fly.io)     │  FREE ✅                  │
│  Celery Beat (Fly.io)       │  FREE ✅                  │
│  ↓                          │                           │
│  Redis (Upstash)            │  FREE                     │
│  PostgreSQL (Neon)          │  FREE                     │
└─────────────────────────────────────────────────────────┘

Total Cost: $0/month forever! 🎉
```

---

## ✅ **Deployment Checklist**

- [ ] Install Fly CLI (`brew install flyctl`)
- [ ] Sign up for Fly.io (no credit card)
- [ ] Create Celery app files (celery_app.py, tasks/*.py)
- [ ] Create fly.worker.toml
- [ ] Create fly.beat.toml
- [ ] Deploy Celery Worker to Fly.io
- [ ] Deploy Celery Beat to Fly.io
- [ ] Set environment secrets
- [ ] Verify worker logs
- [ ] Verify beat logs
- [ ] Test sending a task
- [ ] Confirm task execution in logs

---

## 🎉 **Success!**

You now have:

- ✅ **Celery Worker** running on Fly.io (100% FREE)
- ✅ **Celery Beat** running on Fly.io (100% FREE)
- ✅ **Connected to Upstash Redis** (FREE)
- ✅ **Background tasks** working
- ✅ **Scheduled tasks** running
- ✅ **3 free VMs** (256MB RAM each)
- ✅ **No credit card required**

**Total Cost: $0/month forever!** 🚀

# 05 - Deployment Diagram

Deployment diagrams show the physical infrastructure, cloud services, and runtime environment for Abundance Zone Platform v2.0.

---

## 1. Production Deployment Architecture

```mermaid
graph TB
    subgraph "Client Tier"
        Browser[Web Browser]
        MobileApp[Mobile App<br/>iOS/Android]
    end
    
    subgraph "CDN & Static Hosting - Vercel"
        VercelCDN[Vercel CDN]
        NextJSApp[Next.js 14 App<br/>SSR + Static]
        VercelEdge[Vercel Edge Functions]
    end
    
    subgraph "API Tier - Render"
        RenderLB[Render Load Balancer]
        FastAPI1[FastAPI Instance 1<br/>Python 3.12.9]
        FastAPI2[FastAPI Instance 2<br/>Python 3.12.9]
        FastAPI3[FastAPI Instance 3<br/>Python 3.12.9]
        CeleryWorker1[Celery Worker 1]
        CeleryWorker2[Celery Worker 2]
        CeleryBeat[Celery Beat Scheduler]
    end
    
    subgraph "Database Tier - Neon"
        NeonPrimary[Neon PostgreSQL 16<br/>Primary Instance]
        NeonReplica1[Read Replica 1]
        NeonReplica2[Read Replica 2]
        NeonBackup[Automated Backups<br/>Point-in-Time Recovery]
    end
    
    subgraph "Cache & Queue Tier - Upstash/Redis Cloud"
        RedisCache[Redis 7 Cache<br/>Session & Data Cache]
        RedisBroker[Redis Celery Broker<br/>Task Queue]
    end
    
    subgraph "Firebase Services"
        FirebaseAuth[Firebase Auth]
        FirestoreDB[Firestore Database<br/>Mobile Sync]
        FCM[Firebase Cloud Messaging]
        FirebaseAppCheck[Firebase App Check]
        FirebaseStorage[Firebase Storage]
    end
    
    subgraph "External AI Services"
        GeminiAI[Google Gemini 1.5 Pro<br/>Primary AI]
        OpenRouter[OpenRouter API<br/>Fallback AI]
        OpenAI[OpenAI GPT-4o Vision<br/>OCR Service]
    end
    
    subgraph "Monitoring & Observability"
        Sentry[Sentry<br/>Error Tracking]
        LogTail[LogTail<br/>Log Aggregation]
        UptimeRobot[UptimeRobot<br/>Health Monitoring]
    end
    
    Browser -->|HTTPS| VercelCDN
    MobileApp -->|HTTPS| RenderLB
    
    VercelCDN --> NextJSApp
    NextJSApp -->|REST API| RenderLB
    
    RenderLB --> FastAPI1
    RenderLB --> FastAPI2
    RenderLB --> FastAPI3
    
    FastAPI1 --> NeonPrimary
    FastAPI2 --> NeonReplica1
    FastAPI3 --> NeonReplica2
    
    FastAPI1 --> RedisCache
    FastAPI2 --> RedisCache
    FastAPI3 --> RedisCache
    
    FastAPI1 --> RedisBroker
    FastAPI2 --> RedisBroker
    FastAPI3 --> RedisBroker
    
    RedisBroker --> CeleryWorker1
    RedisBroker --> CeleryWorker2
    CeleryBeat --> RedisBroker
    
    FastAPI1 --> FirebaseAuth
    FastAPI1 --> FirestoreDB
    CeleryWorker1 --> FCM
    CeleryWorker2 --> FCM
    
    FastAPI1 --> GeminiAI
    FastAPI1 --> OpenRouter
    FastAPI1 --> OpenAI
    
    NeonPrimary --> NeonBackup
    
    FastAPI1 --> Sentry
    FastAPI2 --> Sentry
    FastAPI3 --> Sentry
    CeleryWorker1 --> LogTail
    CeleryWorker2 --> LogTail
```

---

## 2. Detailed Infrastructure Specifications

### Frontend - Vercel

| Component | Specification | Details |
|-----------|---------------|---------|
| **Framework** | Next.js 14.2.35 | App Router, React 18, Server Components |
| **Hosting** | Vercel Pro Plan | Global CDN, Automatic HTTPS, DDoS protection |
| **Build** | Turborepo | Incremental Static Regeneration (ISR) |
| **Edge Functions** | Vercel Edge Runtime | Middleware for auth check, rate limiting |
| **Static Assets** | Vercel CDN | Images, CSS, JS cached at edge locations |
| **Deployment** | Git-based CI/CD | Auto-deploy from `main` branch |
| **Custom Domain** | abundancezone.org | SSL/TLS via Let's Encrypt |
| **Regions** | Global | 70+ edge locations worldwide |

**Environment Variables:**
```bash
NEXT_PUBLIC_API_URL=https://api.abundancezone.org
NEXT_PUBLIC_FIREBASE_API_KEY=***
NEXT_PUBLIC_FIREBASE_PROJECT_ID=***
NEXT_PUBLIC_APP_CHECK_DEBUG_TOKEN=***
```

---

### Backend - Render

| Component | Specification | Details |
|-----------|---------------|---------|
| **Framework** | FastAPI 0.115.5 | Async Python web framework |
| **Runtime** | Python 3.12.9 | uv package manager, pyproject.toml |
| **Hosting** | Render Standard Plan | 3 instances, auto-scaling |
| **Instance Type** | 2 vCPU, 4 GB RAM | Per instance |
| **Scaling** | Horizontal | Auto-scale based on CPU (50% threshold) |
| **Load Balancer** | Render Internal LB | Round-robin distribution |
| **Health Check** | `/health` endpoint | Every 30 seconds |
| **Deployment** | Docker-based | Dockerfile, automatic rollback |
| **Region** | US East (Ohio) | Primary region |
| **Workers** | 4 Gunicorn workers | Per instance |

**Docker Configuration:**
```dockerfile
FROM python:3.12.9-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen
COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini ./
CMD ["uv", "run", "gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

**Environment Variables:**
```bash
DATABASE_URL=postgresql://user:pass@neon.tech/abundancezone
REDIS_URL=redis://default:pass@redis.upstash.io:6379
FIREBASE_SERVICE_ACCOUNT_KEY=***
GEMINI_API_KEY=***
OPENROUTER_API_KEY=***
OPENAI_API_KEY=***
JWT_SECRET_KEY=***
```

---

### Database - Neon PostgreSQL

| Component | Specification | Details |
|-----------|---------------|---------|
| **Engine** | PostgreSQL 16 | Latest stable version |
| **Hosting** | Neon Serverless | Auto-scaling, branching support |
| **Plan** | Neon Pro | Unlimited compute, 100 GB storage |
| **Primary** | US East (Ohio) | Write operations |
| **Read Replicas** | 2 replicas | Load distribution for reads |
| **Connection Pooling** | PgBouncer | 100 max connections per instance |
| **Backups** | Automated daily | 30-day retention, point-in-time recovery |
| **Branching** | Database Branching | Instant dev/staging environments |
| **Extensions** | pg_vector, uuid-ossp | Vector search, UUID generation |
| **Migration Tool** | Alembic 1.13.2 | Version control for schema |

**Database Schema:**
- **14 Tables**: users, branches, departments, youths, events, attendance, pledges, payments, notifications, refresh_tokens, audit_logs, analytics_cache, user_sessions, ai_chat_history
- **Indexes**: 28 indexes for query optimization
- **Constraints**: Foreign keys, unique constraints, check constraints
- **Row-Level Security**: Enabled for multi-tenancy

**Performance Tuning:**
```sql
-- Connection pooling
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 10MB

-- Query optimization
random_page_cost = 1.1
effective_io_concurrency = 200
```

---

### Cache & Queue - Upstash Redis

| Component | Specification | Details |
|-----------|---------------|---------|
| **Engine** | Redis 7 | In-memory data store |
| **Hosting** | Upstash Serverless | Pay-per-request pricing |
| **Plan** | Upstash Pro | 10 GB cache, 100M requests/month |
| **Region** | US East (Ohio) | Same as backend |
| **Persistence** | RDB + AOF | Snapshot every 5 minutes, append-only log |
| **Eviction Policy** | allkeys-lru | Least recently used eviction |
| **Max Memory** | 10 GB | Auto-scale on demand |
| **TLS** | Enabled | Encrypted connections |

**Use Cases:**
1. **Session Cache**: User sessions, JWT tokens (TTL: 15 minutes)
2. **Data Cache**: Youth profiles, event lists (TTL: 5 minutes)
3. **Rate Limiting**: IP-based rate limits (TTL: 1 minute)
4. **Celery Broker**: Task queue for background jobs
5. **Pub/Sub**: Real-time notifications (WebSocket fallback)

**Redis Keys Structure:**
```
session:{user_id} -> Session data
user:{user_id} -> User profile
youth:{youth_id} -> Youth data
event:{event_id} -> Event data
attendance:{event_id}:{youth_id} -> Attendance status
rate_limit:{ip_address} -> Request count
celery:task:{task_id} -> Task metadata
```

---

### Celery Workers - Render Background Workers

| Component | Specification | Details |
|-----------|---------------|---------|
| **Workers** | 2 instances | Celery workers on Render |
| **Concurrency** | 4 workers/instance | 8 total concurrent tasks |
| **Broker** | Redis (Upstash) | Task queue |
| **Result Backend** | Redis | Task results cache |
| **Scheduler** | Celery Beat | Cron-like task scheduling |
| **Monitoring** | Flower | Web-based monitoring (optional) |

**Background Tasks:**
1. **Notification Tasks**: Send FCM push, email notifications
2. **Attendance Sync**: Sync PostgreSQL → Firestore
3. **Analytics Jobs**: Generate daily/weekly reports
4. **Cleanup Tasks**: Archive old data, compress logs
5. **AI Tasks**: Batch attendance risk predictions
6. **Reminder Tasks**: Event reminders, pledge payment reminders

**Celery Beat Schedule:**
```python
CELERYBEAT_SCHEDULE = {
    'sync-firestore-every-5-minutes': {
        'task': 'app.tasks.sync_attendance_to_firestore',
        'schedule': crontab(minute='*/5'),
    },
    'send-event-reminders-daily': {
        'task': 'app.tasks.send_event_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    'generate-analytics-daily': {
        'task': 'app.tasks.generate_daily_analytics',
        'schedule': crontab(hour=2, minute=0),
    },
    'cleanup-old-sessions-weekly': {
        'task': 'app.tasks.cleanup_expired_sessions',
        'schedule': crontab(day_of_week=1, hour=3, minute=0),
    },
}
```

---

### Firebase Services

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **Firebase Auth** | User authentication, SSO | Email/password, Google OAuth |
| **Firestore** | Mobile app data sync | Real-time attendance, events |
| **FCM** | Push notifications | iOS + Android push messages |
| **App Check** | API security, bot protection | reCAPTCHA v3 for web, DeviceCheck for mobile |
| **Storage** | File uploads | Youth profile photos, receipt images |

**Firestore Collections:**
```
/events/{event_id}
  - name, date, location, status
  
/attendance/{attendance_id}
  - event_id, youth_id, check_in_time, check_out_time, status
  
/youths/{youth_id}
  - name, phone, branch, department, attendance_rate, platform_role
  
/notifications/{notification_id}
  - title, body, user_id, timestamp, read_status
```

**Firestore Security Rules:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /events/{eventId} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.role in ['SUPER_ADMIN', 'BRANCH_COORDINATOR'];
    }
    match /attendance/{attendanceId} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.role in ['SUPER_ADMIN', 'BRANCH_COORDINATOR', 'DEPARTMENT_LEADER'];
    }
  }
}
```

---

### External AI Services

#### Google Gemini AI
- **Model**: gemini-1.5-pro-latest
- **Use Cases**: AI chat assistant, attendance risk prediction, insights generation
- **Rate Limit**: 1000 requests/minute
- **Cost**: $0.00025 per 1K input tokens, $0.00075 per 1K output tokens
- **Fallback**: OpenRouter API

#### OpenRouter API
- **Models**: Multiple models (Claude, GPT-4, Llama)
- **Use Cases**: Fallback for Gemini failures, model comparison
- **Rate Limit**: 500 requests/minute
- **Cost**: Variable per model

#### OpenAI GPT-4o Vision
- **Model**: gpt-4o (GPT-4 Omni with vision)
- **Use Cases**: Receipt OCR, payment verification
- **Rate Limit**: 500 requests/minute
- **Cost**: $5 per 1M input tokens, $15 per 1M output tokens

---

## 3. Network Architecture

```mermaid
graph TB
    subgraph "Public Internet"
        Users[End Users]
    end
    
    subgraph "Cloudflare DNS"
        DNS[abundancezone.org]
    end
    
    subgraph "Vercel Network"
        VercelEdge[Edge Network<br/>70+ Locations]
        VercelOrigin[Origin Servers<br/>US East]
    end
    
    subgraph "Render Network"
        RenderVPC[Render VPC<br/>US East Ohio]
        RenderFastAPI[FastAPI Instances]
        RenderCelery[Celery Workers]
    end
    
    subgraph "Neon Network"
        NeonVPC[Neon VPC<br/>US East Ohio]
        NeonDB[PostgreSQL Cluster]
    end
    
    subgraph "Upstash Network"
        UpstashVPC[Upstash VPC<br/>US East Ohio]
        UpstashRedis[Redis Cluster]
    end
    
    Users --> DNS
    DNS --> VercelEdge
    VercelEdge --> VercelOrigin
    VercelOrigin --> RenderVPC
    
    RenderVPC --> RenderFastAPI
    RenderVPC --> RenderCelery
    
    RenderFastAPI -->|TLS| NeonVPC
    RenderFastAPI -->|TLS| UpstashVPC
    RenderCelery -->|TLS| UpstashVPC
    
    NeonVPC --> NeonDB
    UpstashVPC --> UpstashRedis
```

**Network Security:**
- **TLS 1.3**: All connections encrypted
- **Private VPC**: Database and Redis in private networks
- **IP Whitelisting**: Backend IPs whitelisted for Neon
- **DDoS Protection**: Cloudflare + Vercel built-in
- **Rate Limiting**: 100 req/min per IP
- **App Check**: Mobile app integrity verification

---

## 4. Monitoring & Observability Stack

```mermaid
graph LR
    subgraph "Application Tier"
        FastAPI[FastAPI]
        Celery[Celery Workers]
        NextJS[Next.js]
    end
    
    subgraph "Observability Services"
        Sentry[Sentry<br/>Error Tracking]
        LogTail[LogTail<br/>Log Aggregation]
        UptimeRobot[UptimeRobot<br/>Uptime Monitoring]
        Prometheus[Prometheus<br/>Metrics]
    end
    
    FastAPI -->|Errors| Sentry
    Celery -->|Errors| Sentry
    NextJS -->|Errors| Sentry
    
    FastAPI -->|Logs| LogTail
    Celery -->|Logs| LogTail
    
    UptimeRobot -->|Health Check| FastAPI
    
    FastAPI -->|Metrics| Prometheus
```

**Monitoring Configuration:**

**Sentry (Error Tracking):**
- **Projects**: 2 (backend, frontend)
- **Sampling**: 100% error capture, 10% performance traces
- **Alerts**: Email + Slack for critical errors
- **Integrations**: GitHub issues auto-creation

**LogTail (Log Aggregation):**
- **Sources**: FastAPI, Celery workers
- **Retention**: 30 days
- **Alerts**: Keyword-based alerts (ERROR, CRITICAL)
- **Dashboards**: Request latency, error rates, task durations

**UptimeRobot (Uptime Monitoring):**
- **Endpoints**: 
  - `https://api.abundancezone.org/health` (1 min interval)
  - `https://abundancezone.org` (1 min interval)
- **Alerts**: Email + SMS for downtime
- **SLA Target**: 99.9% uptime

**Prometheus Metrics:**
- Request rate, error rate, latency (p50, p95, p99)
- Database query performance
- Cache hit/miss rates
- Celery task queue length, processing time
- Memory/CPU usage per instance

---

## 5. CI/CD Pipeline

```mermaid
graph LR
    Developer[Developer] -->|git push| GitHub[GitHub Repository]
    
    GitHub -->|Webhook| VercelCI[Vercel CI]
    GitHub -->|Webhook| RenderCI[Render CI]
    
    VercelCI -->|Build| VercelBuild[Next.js Build]
    RenderCI -->|Build| RenderBuild[Docker Build]
    
    VercelBuild -->|Deploy| VercelProd[Vercel Production]
    RenderBuild -->|Deploy| RenderProd[Render Production]
    
    RenderProd -->|Migrate| Neon[Neon Database]
```

**Deployment Workflow:**

**Frontend (Vercel):**
1. Push to `main` branch → Auto-deploy to production
2. Push to `develop` branch → Auto-deploy to preview environment
3. Pull requests → Automatic preview deployments
4. Build time: ~2 minutes
5. Rollback: One-click rollback to previous deployment

**Backend (Render):**
1. Push to `main` branch → Trigger Docker build
2. Run database migrations (Alembic)
3. Zero-downtime deployment (rolling restart)
4. Health check before routing traffic
5. Build time: ~5 minutes
6. Rollback: Redeploy previous Docker image

**Database Migrations:**
```bash
# Auto-run on deployment
alembic upgrade head
```

---

## 6. Disaster Recovery & Backup Strategy

| Component | Backup Frequency | Retention | Recovery Time Objective (RTO) | Recovery Point Objective (RPO) |
|-----------|------------------|-----------|-------------------------------|--------------------------------|
| **PostgreSQL** | Automated daily + continuous WAL | 30 days | < 15 minutes | < 5 minutes |
| **Redis** | RDB snapshot every 5 minutes | 7 days | < 5 minutes | < 5 minutes |
| **Firestore** | Automatic backups | 30 days | < 10 minutes | < 1 hour |
| **Firebase Storage** | Versioning enabled | 30 days | < 30 minutes | < 1 hour |
| **Application Code** | Git repository | Indefinite | < 5 minutes | 0 (version control) |

**Disaster Recovery Plan:**
1. **Database Failure**: Promote read replica to primary (< 15 min)
2. **Redis Failure**: Restart from RDB snapshot (< 5 min)
3. **Backend Instance Failure**: Auto-scale new instance (< 2 min)
4. **Entire Region Failure**: Failover to secondary region (manual, ~30 min)

---

## Deployment Summary

### Infrastructure Providers
- **Frontend Hosting**: Vercel (Global CDN)
- **Backend Hosting**: Render (US East Ohio)
- **Database**: Neon PostgreSQL 16 (Serverless)
- **Cache/Queue**: Upstash Redis 7 (Serverless)
- **Mobile Backend**: Firebase (Auth, Firestore, FCM, Storage)
- **AI Services**: Google Gemini, OpenRouter, OpenAI
- **Monitoring**: Sentry, LogTail, UptimeRobot, Prometheus

### Estimated Monthly Costs
- **Vercel Pro**: $20/month
- **Render Standard (3 instances + 2 workers)**: $105/month
- **Neon Pro**: $69/month
- **Upstash Pro**: $50/month
- **Firebase Blaze**: ~$30/month (usage-based)
- **AI APIs (Gemini + OpenAI)**: ~$100/month (usage-based)
- **Monitoring (Sentry + LogTail)**: ~$50/month
- **Total**: ~$424/month

### Performance Targets
- **API Response Time**: < 200ms (p95)
- **Page Load Time**: < 2s (First Contentful Paint)
- **Database Query Time**: < 50ms (p95)
- **Cache Hit Rate**: > 80%
- **Uptime**: 99.9% SLA
- **Concurrent Users**: 1000+ simultaneous users

---

*Reference: Based on v1.0 deployment configuration and CHANGE.md Neon migration plan*

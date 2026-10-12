# 🎉 Post-Deployment Guide

**Abundance Zone Youth Platform v2.0 - Successfully Deployed to Render!**

---

## ✅ Deployment Status

Your backend is **LIVE** and operational:

- **URL:** https://abundance-zone-platform-v2-0.onrender.com
- **Health Check:** ✅ Passing (HTTP 200)
- **Database:** ✅ Neon PostgreSQL Connected
- **Redis:** ✅ Upstash Redis Connected
- **Workers:** 4 Gunicorn workers running

---

## 🚀 Required: Create Admin User

### Step 1: Access Render Shell

1. Go to Render Dashboard
2. Select your service: `abundance-zone-platform-v2-0`
3. Click **"Shell"** tab on the left
4. Wait for shell to connect

### Step 2: Run Admin Creation Script

```bash
python scripts/create_admin.py
```

**Expected Output:**

```
🔗 Connecting to database...
🔍 Checking for existing admin...
👤 Creating admin user...
============================================================
🎉 Admin user created successfully!
============================================================
   📧 Email: admin@abundancezone.org
   🔑 Password: ChangeMe123!
   👤 User ID: [generated-uuid]
   🛡️  Role: ADMIN
============================================================
⚠️  IMPORTANT: Change the password immediately after first login!
============================================================
```

### Step 3: Test Admin Login

```bash
# Test login endpoint
curl -X POST https://abundance-zone-platform-v2-0.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@abundancezone.org",
    "password": "ChangeMe123!"
  }'
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "user": {
      "id": "uuid",
      "email": "admin@abundancezone.org",
      "platform_role": "ADMIN"
    }
  }
}
```

---

## 📝 Next Steps

### 1. Change Admin Password

```bash
curl -X PUT https://abundance-zone-platform-v2-0.onrender.com/api/v1/users/me/password \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "ChangeMe123!",
    "new_password": "YourSecurePassword123!"
  }'
```

### 2. Create Organization Structure

#### Create Branch

```bash
curl -X POST https://abundance-zone-platform-v2-0.onrender.com/api/v1/branches \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Oke-Afa 2 Branch",
    "address": "Lagos, Nigeria",
    "phone_number": "+2341234567890"
  }'
```

#### Create Department

```bash
curl -X POST https://abundance-zone-platform-v2-0.onrender.com/api/v1/departments \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Youth Ministry",
    "description": "Main youth department",
    "branch_id": "BRANCH_UUID_FROM_PREVIOUS_STEP"
  }'
```

### 3. Deploy Celery Workers (Background Tasks)

You have 2 more services to deploy for full functionality:

#### Option A: Use render.yaml Blueprint (Already Configured)

The `render.yaml` file in your repo root includes Celery worker and beat configurations. If you deployed via Blueprint, they should already be running.

Check in Render Dashboard:

- ✅ `abundance-zone-celery-worker` (should be running)
- ✅ `abundance-zone-celery-beat` (should be running)

#### Option B: Deploy Manually

If not deployed yet:

1. **Render Dashboard** → **New** → **Background Worker**
2. Connect repository
3. **Name:** `abundance-zone-celery-worker`
4. **Docker Command:**
   ```bash
   celery -A app.celery_app worker --loglevel=info --concurrency=4
   ```
5. Add same environment variables as web service
6. Deploy

Repeat for Celery Beat scheduler:

- **Name:** `abundance-zone-celery-beat`
- **Docker Command:**
  ```bash
  celery -A app.celery_app beat --loglevel=info
  ```
- ⚠️ **IMPORTANT:** Only run **1 instance** of Beat scheduler

### 4. Configure Custom Domain (Optional)

1. **Render Dashboard** → Your Service → **Settings**
2. **Custom Domain** section → Add: `api.abundancezone.org`
3. Update DNS at your domain provider:

   ```
   Type: CNAME
   Name: api
   Value: abundance-zone-platform-v2-0.onrender.com
   TTL: 3600
   ```
4. Wait 5-10 minutes for SSL certificate
5. Update environment variables:

   ```
   ALLOWED_HOSTS=["localhost","127.0.0.1","abundance-zone-platform-v2-0.onrender.com","api.abundancezone.org","*.onrender.com"]
   CORS_ORIGINS=["https://abundancezone.org","https://www.abundancezone.org"]
   ```

### 5. Set Up Monitoring

#### Sentry (Error Tracking)

1. Sign up at https://sentry.io
2. Create project: "Abundance Zone Backend"
3. Copy DSN
4. Add to Render environment: `SENTRY_DSN=https://...@sentry.io/...`
5. Redeploy

#### UptimeRobot (Uptime Monitoring)

1. Sign up at https://uptimerobot.com
2. Add new monitor:
   - Type: HTTP(s)
   - URL: `https://abundance-zone-platform-v2-0.onrender.com/health`
   - Interval: 5 minutes
3. Add alert email

#### Render Metrics (Built-in)

- **Dashboard** → Your Service → **Metrics**
- Monitor: CPU, Memory, Response Time, Request Rate

### 6. Frontend Integration

Update your frontend environment variables:

```env
NEXT_PUBLIC_API_URL=https://abundance-zone-platform-v2-0.onrender.com
# or
NEXT_PUBLIC_API_URL=https://api.abundancezone.org
```

Test API connectivity from frontend:

```typescript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`);
console.log(await response.json());
// Should print: { status: "healthy", version: "2.0.0", environment: "production" }
```

---

## 🔍 Troubleshooting

### Service Not Responding

```bash
# Check service status
curl https://abundance-zone-platform-v2-0.onrender.com/health

# View logs in Render Dashboard
# Dashboard → Service → Logs
```

### Database Connection Issues

```bash
# Test in Render Shell
python -c "from app.core.database import engine; print('DB Connected!')"
```

### Redis Connection Issues

```bash
# Test in Render Shell
python -c "from app.core.redis import redis_client; redis_client.ping(); print('Redis Connected!')"
```

### Celery Tasks Not Running

1. Check worker logs in Render Dashboard
2. Verify `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` are set
3. Ensure Redis is accessible
4. Only ONE Beat scheduler should be running

---

## 📊 API Endpoints

Your backend has **44 production endpoints** across 8 modules:

### Authentication (`/api/v1/auth`)

- `POST /login` - User login
- `POST /register` - User registration
- `POST /refresh` - Refresh access token
- `POST /verify-email` - Email verification
- `POST /forgot-password` - Password reset request
- `POST /reset-password` - Password reset

### Users (`/api/v1/users`)

- `GET /me` - Get current user
- `PUT /me` - Update profile
- `PUT /me/password` - Change password
- `GET /users` - List users (Admin only)

### Branches (`/api/v1/branches`)

- `GET /branches` - List all branches
- `POST /branches` - Create branch
- `GET /branches/{id}` - Get branch details
- `PUT /branches/{id}` - Update branch
- `DELETE /branches/{id}` - Delete branch

### Departments (`/api/v1/departments`)

- Similar CRUD operations

### Youths (`/api/v1/youths`)

- Full youth profile management
- Search and filtering
- Document uploads

### Events (`/api/v1/events`)

- Event creation and management
- RSVP tracking

### Attendance (`/api/v1/attendance`)

- Check-in/check-out
- Attendance reports
- Analytics

### Notifications (`/api/v1/notifications`)

- Push notifications
- Email notifications
- WhatsApp notifications

---

## 🔐 Security Checklist

- ✅ HTTPS enabled (automatic via Render)
- ✅ JWT authentication configured
- ✅ CORS properly configured
- ✅ Rate limiting enabled
- ✅ Environment variables secured
- ⚠️ Change default admin password
- ⚠️ Rotate JWT secrets periodically
- ⚠️ Enable Sentry for error monitoring
- ⚠️ Set up database backups (Neon automatic)

---

## 📈 Scaling

### Current Setup

- **Plan:** Starter (512MB RAM, 0.5 CPU)
- **Workers:** 4 Gunicorn workers
- **Instances:** 1 (auto-scales to 3 under load)

### When to Scale

**Vertical Scaling (Bigger Machine):**

- Upgrade to Standard plan ($25/month) if CPU > 70%
- 2GB RAM, 1 CPU, better for AI workloads

**Horizontal Scaling (More Instances):**

- Already configured for auto-scaling (1-3 instances)
- Render will automatically add instances when CPU > 70%

**Database Scaling:**

- Neon PostgreSQL: Enable read replicas
- Increase compute units in Neon dashboard

**Redis Scaling:**

- Upstash: Upgrade tier for more connections
- Enable persistence if needed

---

## 🎊 Congratulations!

Your **Abundance Zone Youth Platform v2.0** backend is now running in production!

**Quick Stats:**

- 🚀 44 API endpoints live
- 🗄️ Neon PostgreSQL database connected
- ⚡ Upstash Redis caching active
- 🔒 JWT authentication secured
- 📊 65.81% test coverage (262 tests passing)
- 🐳 Docker-based deployment
- 🔄 Auto-scaling configured

**What's Next?**

1. Create admin user ✅ (Do this first!)
2. Test all API endpoints
3. Deploy Celery workers
4. Integrate with frontend
5. Set up monitoring
6. Configure custom domain

---

**Need Help?**

- 📚 Full Documentation: `/backend/docs/RENDER_DEPLOYMENT_GUIDE.md`
- 📋 Deployment Checklist: `/DEPLOYMENT_CHECKLIST.md`
- 🔍 Troubleshooting: Check Render logs and health endpoint

**Support:**

- Render Status: https://status.render.com
- Neon Status: https://status.neon.tech
- Upstash Status: https://status.upstash.com

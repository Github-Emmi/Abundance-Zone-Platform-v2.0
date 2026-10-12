# Sequence Diagrams - Behavioral UML

## Abundance Zone Youth Management Platform v2.0

**Diagram Type:** UML Behavioral Diagram (Interaction Diagram)
**Purpose:** Show how objects interact over time for key use cases
**Notation:** UML 2.5 Sequence Diagram

---

## 1. User Authentication Flow (JWT + Firebase SSO)

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Next.js Frontend
    participant API as FastAPI Router
    participant AuthMW as Auth Middleware
    participant AuthSvc as Auth Service
    participant UserRepo as User Repository
    participant DB as PostgreSQL
    participant JWT as JWT Handler
    participant Redis as Redis Cache

    User->>Frontend: Enter email & password
    Frontend->>API: POST /api/v1/auth/login
    API->>AuthSvc: login(email, password)
    AuthSvc->>UserRepo: get_by_email(email)
    UserRepo->>DB: SELECT * FROM users WHERE email=?
    DB-->>UserRepo: User record
    UserRepo-->>AuthSvc: User entity
    AuthSvc->>AuthSvc: verify_password(password)
  
    alt Password Valid
        AuthSvc->>JWT: create_access_token(user_id, role, branch_id)
        JWT-->>AuthSvc: access_token (15 min TTL)
        AuthSvc->>JWT: create_refresh_token(user_id)
        JWT-->>AuthSvc: refresh_token (7 days TTL)
        AuthSvc->>DB: INSERT INTO refresh_tokens (hash, user_id)
        AuthSvc-->>API: {access_token, refresh_token, user}
        API-->>Frontend: 200 OK + Set-Cookie (httpOnly)
        Frontend-->>User: Redirect to Dashboard
    else Password Invalid
        AuthSvc-->>API: AuthenticationError
        API-->>Frontend: 401 Unauthorized
        Frontend-->>User: Show error message
    end
```

---

## 2. Youth Registration Flow (with Domain Events)

```mermaid
sequenceDiagram
    actor Coordinator as Branch Coordinator
    participant FE as Frontend
    participant API as FastAPI Router
    participant RBAC as RBAC Middleware
    participant YouthSvc as Youth Service
    participant YouthRepo as Youth Repository
    participant DB as PostgreSQL
    participant EventBus as Event Bus
    participant NotifSvc as Notification Service
    participant Cache as Redis Cache

    Coordinator->>FE: Fill youth registration form
    FE->>API: POST /api/v1/youths {fullname, branch_id, ...}
    API->>RBAC: Check role & branch access
    RBAC->>RBAC: Verify BRANCH_COORDINATOR role
    RBAC->>RBAC: Verify branch_id matches user.branch_id
  
    alt Authorized
        RBAC->>YouthSvc: create_youth(data, created_by)
        YouthSvc->>YouthSvc: Validate business rules
        YouthSvc->>YouthRepo: get_by_phone(phone, branch_id)
        YouthRepo->>DB: SELECT for duplicate check
        DB-->>YouthRepo: null (no duplicate)
        YouthRepo-->>YouthSvc: No existing youth
      
        YouthSvc->>YouthRepo: create(youth_data)
        YouthRepo->>DB: INSERT INTO youths
        DB-->>YouthRepo: youth_id
        YouthRepo-->>YouthSvc: Created Youth entity
      
        YouthSvc->>EventBus: publish(YouthRegistered event)
        EventBus->>NotifSvc: YouthRegistered handler
        NotifSvc->>NotifSvc: send_welcome_notification(youth_id)
      
        YouthSvc->>Cache: DELETE analytics:branch:*
        YouthSvc-->>API: YouthDTO
        API-->>FE: 201 Created {youth}
        FE-->>Coordinator: Success message
    else Not Authorized
        RBAC-->>API: 403 Forbidden
        API-->>FE: Authorization error
        FE-->>Coordinator: Permission denied
    end
```

---

## 3. Bulk Attendance Marking Flow

```mermaid
sequenceDiagram
    actor Leader as Department Leader
    participant FE as Frontend
    participant API as FastAPI Router
    participant AttSvc as Attendance Service
    participant AttRepo as Attendance Repository
    participant DB as PostgreSQL
    participant Firestore as Firestore Service
    participant EventBus as Event Bus
    participant Analytics as Analytics Service

    Leader->>FE: Select 50 youths, mark as PRESENT
    FE->>API: POST /api/v1/attendance/bulk
    Note over FE,API: {event_id, records: [{youth_id, status}...]}
  
    API->>AttSvc: bulk_mark_attendance(event_id, records)
    AttSvc->>AttRepo: validate_youths_in_branch(youth_ids, branch_id)
    AttRepo->>DB: SELECT youth_id FROM youths WHERE branch_id=?
    DB-->>AttRepo: Valid youth_ids
    AttRepo-->>AttSvc: Validation passed
  
    loop For each record (50 records)
        AttSvc->>AttRepo: upsert_attendance(youth_id, event_id, status)
        AttRepo->>DB: INSERT ... ON CONFLICT UPDATE
        DB-->>AttRepo: attendance_id
        AttRepo-->>AttSvc: Attendance entity
      
        AttSvc->>Firestore: sync_attendance_to_firestore(event_id, youth_id)
        Note over Firestore: Fire-and-forget, async
        Firestore-->>AttSvc: Acknowledged (doesn't block)
    end
  
    AttSvc->>DB: COMMIT transaction (atomic)
    AttSvc->>EventBus: publish(AttendanceRecorded event)
    EventBus->>Analytics: Update attendance cache
  
    AttSvc-->>API: Attendance[] (50 records)
    API-->>FE: 201 Created
    FE-->>Leader: Attendance marked successfully
```

---

## 4. AI Chat with Context Injection

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant API as FastAPI Router
    participant AISvc as AI Service
    participant Cache as Redis Cache
    participant DB as PostgreSQL
    participant Gemini as Google Gemini API
    participant OpenRouter as OpenRouter API

    User->>FE: Ask: "What's my branch attendance rate?"
    FE->>API: POST /api/v1/ai/chat {message, history}
    API->>AISvc: chat_with_assistant(message, user_context)
  
    AISvc->>Cache: GET ai_context:{user_id}
    Cache-->>AISvc: Cache miss
  
    AISvc->>DB: Build context: SELECT branch stats, youths, events
    DB-->>AISvc: {branch_id, total_youths: 120, attendance_rate: 78%}
  
    AISvc->>AISvc: Construct system prompt with live data
    Note over AISvc: "You are AZYMP Intelligence.<br/>Branch: Lagos Central<br/>Youths: 120<br/>Attendance: 78%"
  
    AISvc->>Gemini: POST /generateContent {prompt, message}
  
    alt Gemini Success
        Gemini-->>AISvc: AI response
        AISvc->>Cache: SETEX ai_context:{user_id} 300 {context}
        AISvc-->>API: {reply, cached: false}
        API-->>FE: 200 OK {reply}
        FE-->>User: "Your branch has 78% attendance..."
    else Gemini Failure
        Gemini-->>AISvc: APIError
        AISvc->>OpenRouter: POST /chat/completions (fallback)
        OpenRouter-->>AISvc: AI response
        AISvc-->>API: {reply, fallback_used: true}
        API-->>FE: 200 OK {reply}
        FE-->>User: Response from fallback AI
    end
```

---

## 5. Payment with Receipt OCR Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant API as FastAPI Router
    participant FinSvc as Finance Service
    participant OCR as Receipt OCR Service
    participant Storage as Cloudinary
    participant OpenAI as OpenAI Vision API
    participant DB as PostgreSQL
    participant NotifSvc as Notification Service

    User->>FE: Upload receipt image
    FE->>Storage: Upload image
    Storage-->>FE: receipt_url
  
    FE->>API: POST /api/v1/finance/payments/ocr
    Note over FE,API: {pledge_id, receipt_url}
  
    API->>FinSvc: record_payment_with_ocr(pledge_id, receipt_url)
    FinSvc->>OCR: extract_receipt_data(receipt_url)
  
    OCR->>OpenAI: POST /chat/completions (GPT-4o Vision)
    Note over OCR,OpenAI: Prompt: "Extract amount, date,<br/>reference from receipt"
    OpenAI-->>OCR: {amount: 5000, date: "2026-10-05", ...}
    OCR-->>FinSvc: Parsed receipt data
  
    FinSvc->>DB: BEGIN TRANSACTION
    FinSvc->>DB: INSERT INTO payments (amount, receipt_url, receipt_data)
    FinSvc->>DB: UPDATE pledges SET amount_paid = amount_paid + ?
    FinSvc->>DB: COMMIT
  
    FinSvc->>NotifSvc: send_payment_confirmation(user_id)
    FinSvc-->>API: Payment entity
    API-->>FE: 201 Created {payment}
    FE-->>User: Payment recorded successfully
```

---

## 6. Token Refresh Flow (Silent Refresh)

```mermaid
sequenceDiagram
    participant FE as Frontend (Axios Interceptor)
    participant API as FastAPI Router
    participant AuthSvc as Auth Service
    participant DB as PostgreSQL
    participant JWT as JWT Handler

    FE->>API: GET /api/v1/youths (with expired token)
    API->>API: Verify JWT
    API-->>FE: 401 Unauthorized

    FE->>FE: Intercept 401, queue original request
    FE->>API: POST /api/v1/auth/refresh (with refresh_token cookie)
    API->>AuthSvc: refresh_token(refresh_token)
  
    AuthSvc->>JWT: verify_refresh_token(token)
    JWT-->>AuthSvc: Valid, extract user_id
  
    AuthSvc->>DB: SELECT * FROM refresh_tokens WHERE token_hash=?
    DB-->>AuthSvc: Token record
  
    AuthSvc->>AuthSvc: Check is_revoked, check expiry
  
    alt Token Valid & Not Revoked
        AuthSvc->>DB: UPDATE refresh_tokens SET is_revoked=true (old token)
        AuthSvc->>JWT: create_access_token(user_id, role)
        JWT-->>AuthSvc: new_access_token
        AuthSvc->>JWT: create_refresh_token(user_id)
        JWT-->>AuthSvc: new_refresh_token
        AuthSvc->>DB: INSERT INTO refresh_tokens (new token hash)
      
        AuthSvc-->>API: {access_token, refresh_token}
        API-->>FE: 200 OK + Set-Cookie
        FE->>FE: Update token in memory
        FE->>API: Retry original request (GET /api/v1/youths)
        API-->>FE: 200 OK {youths}
    else Token Revoked or Expired
        AuthSvc-->>API: Unauthorized
        API-->>FE: 401 Unauthorized
        FE->>FE: Clear tokens, redirect to /login
    end
```

---

## 7. Event Creation with Notifications

```mermaid
sequenceDiagram
    actor Coordinator
    participant FE as Frontend
    participant API as FastAPI Router
    participant EventSvc as Event Service
    participant EventRepo as Event Repository
    participant DB as PostgreSQL
    participant BgTasks as Background Tasks
    participant NotifSvc as Notification Service
    participant Email as Email Service
    participant Push as FCM Service

    Coordinator->>FE: Create event: "Youth Vigil - Friday 8PM"
    FE->>API: POST /api/v1/events
  
    API->>EventSvc: create_event(data, created_by)
    EventSvc->>EventRepo: create(event_data)
    EventRepo->>DB: INSERT INTO events
    DB-->>EventRepo: event_id
    EventRepo-->>EventSvc: Event entity
  
    EventSvc->>BgTasks: dispatch_event_notifications(event)
    EventSvc-->>API: Event entity
    API-->>FE: 201 Created
    FE-->>Coordinator: Event created
  
    Note over BgTasks: Async execution (doesn't block response)
  
    BgTasks->>DB: SELECT users WHERE branch_id=?
    DB-->>BgTasks: User[] (150 users)
  
    par Parallel Notification Dispatch
        BgTasks->>NotifSvc: create_notifications(users, event)
        NotifSvc->>DB: INSERT INTO notifications (IN_APP channel)
      
        and
        BgTasks->>Email: send_event_invite_emails(users, event)
        Email->>Email: Queue Celery task
      
        and
        BgTasks->>Push: broadcast_to_topic("branch-{id}", event)
        Push->>Push: Firebase FCM topic broadcast
    end
  
    BgTasks-->>BgTasks: Notifications dispatched
```

---

## 8. Attendance Risk Prediction Flow

```mermaid
sequenceDiagram
    actor Leader
    participant FE as Frontend
    participant API as FastAPI Router
    participant AttSvc as Attendance Service
    participant Predictor as ML Predictor
    participant Model as RandomForest Model
    participant RuleBased as Rule-Based Fallback

    Leader->>FE: View youth attendance history
    FE->>API: GET /api/v1/attendance/predict/{youth_id}
  
    API->>AttSvc: predict_attendance_risk(youth_id, features)
    AttSvc->>Predictor: predict_risk(features)
  
    Predictor->>Predictor: Check if model loaded
  
    alt ML Model Available
        Predictor->>Model: predict(features)
        Note over Model: RandomForest with<br/>5 features
        Model-->>Predictor: probabilities [0.2, 0.5, 0.3]
        Predictor->>Predictor: Map to risk levels
        Predictor-->>AttSvc: {risk_level: "MEDIUM", model_available: true}
    else ML Model Not Loaded
        Predictor->>RuleBased: calculate_risk(attendance_rate, consecutive_absences)
        RuleBased->>RuleBased: if rate >= 0.75 → LOW
        RuleBased->>RuleBased: else if rate >= 0.5 → MEDIUM
        RuleBased->>RuleBased: else → HIGH
        RuleBased-->>Predictor: {risk_level: "MEDIUM", model_available: false}
        Predictor-->>AttSvc: Risk prediction with fallback flag
    end
  
    AttSvc-->>API: {risk_level, attendance_rate, model_available}
    API-->>FE: 200 OK
    FE-->>Leader: Display risk badge (MEDIUM)
```

---

## Key Behavioral Patterns Demonstrated

### 1. **Synchronous Communication**

- Request-Response pattern (HTTP REST)
- Direct method calls between objects

### 2. **Asynchronous Communication**

- Background tasks (FastAPI BackgroundTasks)
- Event Bus (publish-subscribe pattern)
- Fire-and-forget Firestore sync

### 3. **Error Handling**

- Try-catch with fallbacks (AI services)
- Graceful degradation (Firestore optional)
- Token refresh on 401

### 4. **Transaction Management**

- Database transactions (BEGIN/COMMIT)
- Atomic bulk operations
- Rollback on errors

### 5. **Caching Strategy**

- Check cache first, then database
- Write-through cache invalidation
- TTL-based expiry

### 6. **Authentication & Authorization**

- JWT token validation
- Role-based access control (RBAC)
- Branch isolation checks

---

## Time Complexity Analysis

| Sequence                      | Average Time | Notes                               |
| ----------------------------- | ------------ | ----------------------------------- |
| Login                         | 200-400ms    | Database query + JWT generation     |
| Youth Registration            | 100-200ms    | Single INSERT + event dispatch      |
| Bulk Attendance (500 records) | 2-5 seconds  | Sequential inserts + Firestore sync |
| AI Chat (first request)       | 3-8 seconds  | Context building + LLM API call     |
| AI Chat (cached)              | 50-100ms     | Redis cache hit                     |
| Token Refresh                 | 100-150ms    | Token rotation + database update    |
| Event Creation                | 150-300ms    | INSERT + background task dispatch   |
| Risk Prediction (ML)          | 50-100ms     | Model inference                     |

---

**Document Purpose:** These sequence diagrams show the dynamic behavior of the system - how objects interact over time to accomplish specific use cases.

**For Kiro:** Use these diagrams to understand:

- The exact order of method calls for each feature
- Which objects communicate with each other
- Where errors can occur and how they're handled
- Async vs sync operations
- Performance bottlenecks

**Reference:** Phase 05 Auth Flow + Phase 06 Core Modules

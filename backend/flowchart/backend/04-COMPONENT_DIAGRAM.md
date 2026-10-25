# 04 - Component Diagram

Component diagrams show the modular architecture, dependencies, and Clean Architecture layers of the Abundance Zone Platform v2.0.

---

## 1. High-Level Component Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        NextJS[Next.js 14 Frontend]
        MobileApp[React Native Mobile App]
    end
    
    subgraph "API Gateway Layer"
        FastAPI[FastAPI Application]
        Middleware[Security Middleware]
        RateLimiter[Rate Limiter]
    end
    
    subgraph "Application Layer - 11 Feature Modules"
        AuthModule[Auth Module]
        YouthModule[Youth Module]
        EventModule[Event Module]
        AttendanceModule[Attendance Module]
        PledgeModule[Pledge Module]
        PaymentModule[Payment Module]
        NotificationModule[Notification Module]
        BranchModule[Branch Module]
        DeptModule[Department Module]
        AnalyticsModule[Analytics Module]
        AIModule[AI/ML Module]
    end
    
    subgraph "Domain Layer"
        DomainModels[Domain Models]
        DomainEvents[Domain Events]
        ValueObjects[Value Objects]
        DomainServices[Domain Services]
    end
    
    subgraph "Infrastructure Layer"
        PostgreSQL[(PostgreSQL/Neon)]
        Redis[(Redis Cache)]
        Firestore[(Firestore)]
        Celery[Celery Workers]
        FCM[Firebase Cloud Messaging]
        EmailService[Email Service]
    end
    
    subgraph "External Services"
        Firebase[Firebase Auth]
        GeminiAI[Google Gemini AI]
        OpenRouter[OpenRouter API]
        OpenAI[OpenAI GPT-4o]
        CloudStorage[Cloud Storage]
    end
    
    NextJS -->|REST API| FastAPI
    MobileApp -->|REST API| FastAPI
    
    FastAPI --> Middleware
    Middleware --> RateLimiter
    RateLimiter --> AuthModule
    RateLimiter --> YouthModule
    RateLimiter --> EventModule
    RateLimiter --> AttendanceModule
    RateLimiter --> PledgeModule
    RateLimiter --> PaymentModule
    RateLimiter --> NotificationModule
    RateLimiter --> BranchModule
    RateLimiter --> DeptModule
    RateLimiter --> AnalyticsModule
    RateLimiter --> AIModule
    
    AuthModule --> DomainModels
    YouthModule --> DomainModels
    EventModule --> DomainModels
    AttendanceModule --> DomainModels
    PledgeModule --> DomainModels
    PaymentModule --> DomainModels
    
    DomainModels --> DomainEvents
    DomainModels --> ValueObjects
    DomainServices --> DomainModels
    
    AuthModule --> PostgreSQL
    YouthModule --> PostgreSQL
    EventModule --> PostgreSQL
    AttendanceModule --> PostgreSQL
    PledgeModule --> PostgreSQL
    PaymentModule --> PostgreSQL
    
    AuthModule --> Redis
    AttendanceModule --> Firestore
    EventModule --> Firestore
    
    NotificationModule --> Celery
    Celery --> FCM
    Celery --> EmailService
    
    AuthModule --> Firebase
    AIModule --> GeminiAI
    AIModule --> OpenRouter
    PaymentModule --> OpenAI
    YouthModule --> CloudStorage
```

---

## 2. Clean Architecture Layers - Detailed Component View

```mermaid
graph LR
    subgraph "Domain Layer (Core Business Logic)"
        DE[Domain Entities]
        VO[Value Objects]
        DR[Domain Rules]
        DI[Domain Interfaces]
    end
    
    subgraph "Application Layer (Use Cases)"
        UC[Use Cases]
        DTO[DTOs/Schemas]
        AS[Application Services]
        EH[Event Handlers]
    end
    
    subgraph "Infrastructure Layer (External Concerns)"
        REPO[Repository Implementations]
        EXT[External Service Adapters]
        DB[Database Access]
        CACHE[Cache Access]
        MSG[Message Queue]
    end
    
    subgraph "Presentation Layer (API)"
        ROUTER[FastAPI Routers]
        MW[Middleware]
        VAL[Request Validation]
        RESP[Response Formatting]
    end
    
    ROUTER --> UC
    UC --> AS
    AS --> DE
    AS --> DR
    UC --> EH
    EH --> DI
    
    REPO --> DB
    REPO --> CACHE
    EXT --> DI
    AS --> REPO
    AS --> EXT
    
    DE --> VO
    DR --> DE
    
    VAL --> DTO
    RESP --> DTO
```

**Dependency Rule:** 
- Domain Layer has ZERO dependencies (pure business logic)
- Application Layer depends ONLY on Domain
- Infrastructure implements Domain interfaces
- Presentation depends on Application, never Infrastructure directly

---

## 3. 11 Feature Modules - Component Breakdown

### Module 1: Auth Module

```mermaid
graph TB
    subgraph "Auth Module Components"
        AuthRouter[Auth Router<br/>7 endpoints]
        AuthService[Auth Service]
        JWTManager[JWT Manager]
        FirebaseAdapter[Firebase Auth Adapter]
        UserRepo[User Repository]
        TokenRepo[Refresh Token Repository]
    end
    
    AuthRouter --> AuthService
    AuthService --> JWTManager
    AuthService --> FirebaseAdapter
    AuthService --> UserRepo
    AuthService --> TokenRepo
    
    JWTManager --> Redis
    FirebaseAdapter --> FirebaseAuth[Firebase Auth API]
    UserRepo --> PostgreSQL
    TokenRepo --> PostgreSQL
```

**Endpoints:** Login, Logout, Refresh Token, Verify Token, Password Reset, Register, Profile

---

### Module 2: Youth Module

```mermaid
graph TB
    subgraph "Youth Module Components"
        YouthRouter[Youth Router<br/>8 endpoints]
        YouthService[Youth Service]
        RiskPredictor[Attendance Risk Predictor]
        YouthRepo[Youth Repository]
        AttendanceCalc[Attendance Calculator]
    end
    
    YouthRouter --> YouthService
    YouthService --> RiskPredictor
    YouthService --> YouthRepo
    YouthService --> AttendanceCalc
    
    RiskPredictor --> GeminiAI[Gemini AI API]
    YouthRepo --> PostgreSQL
    AttendanceCalc --> Redis
```

**Endpoints:** Create Youth, Get Youth, Update Youth, Delete Youth, List Youths, Get Youth Stats, Predict Risk, Bulk Import

---

### Module 3: Event Module

```mermaid
graph TB
    subgraph "Event Module Components"
        EventRouter[Event Router<br/>6 endpoints]
        EventService[Event Service]
        QRGenerator[QR Code Generator]
        EventRepo[Event Repository]
        NotificationTrigger[Notification Trigger]
    end
    
    EventRouter --> EventService
    EventService --> QRGenerator
    EventService --> EventRepo
    EventService --> NotificationTrigger
    
    EventRepo --> PostgreSQL
    EventRepo --> Firestore
    NotificationTrigger --> Celery
```

**Endpoints:** Create Event, Update Event, Delete Event, Get Event, List Events, Generate QR

---

### Module 4: Attendance Module

```mermaid
graph TB
    subgraph "Attendance Module Components"
        AttendanceRouter[Attendance Router<br/>7 endpoints]
        AttendanceService[Attendance Service]
        BulkProcessor[Bulk Attendance Processor]
        QRScanner[QR Code Scanner]
        AttendanceRepo[Attendance Repository]
        FirestoreSync[Firestore Sync Handler]
    end
    
    AttendanceRouter --> AttendanceService
    AttendanceService --> BulkProcessor
    AttendanceService --> QRScanner
    AttendanceService --> AttendanceRepo
    AttendanceService --> FirestoreSync
    
    BulkProcessor --> Celery
    AttendanceRepo --> PostgreSQL
    FirestoreSync --> Firestore
```

**Endpoints:** Mark Attendance, Bulk Mark, Get Attendance, List Attendance, Get Stats, Check-in, Check-out

---

### Module 5: Pledge Module

```mermaid
graph TB
    subgraph "Pledge Module Components"
        PledgeRouter[Pledge Router<br/>6 endpoints]
        PledgeService[Pledge Service]
        PledgeValidator[Pledge Validator]
        PledgeRepo[Pledge Repository]
        ReminderScheduler[Reminder Scheduler]
    end
    
    PledgeRouter --> PledgeService
    PledgeService --> PledgeValidator
    PledgeService --> PledgeRepo
    PledgeService --> ReminderScheduler
    
    PledgeRepo --> PostgreSQL
    ReminderScheduler --> Celery
```

**Endpoints:** Create Pledge, Update Pledge, Delete Pledge, Get Pledge, List Pledges, Get Stats

---

### Module 6: Payment Module

```mermaid
graph TB
    subgraph "Payment Module Components"
        PaymentRouter[Payment Router<br/>7 endpoints]
        PaymentService[Payment Service]
        OCRProcessor[Receipt OCR Processor]
        PaymentVerifier[Payment Verifier]
        PaymentRepo[Payment Repository]
    end
    
    PaymentRouter --> PaymentService
    PaymentService --> OCRProcessor
    PaymentService --> PaymentVerifier
    PaymentService --> PaymentRepo
    
    OCRProcessor --> OpenAI[OpenAI GPT-4o Vision]
    PaymentRepo --> PostgreSQL
    PaymentService --> CloudStorage
```

**Endpoints:** Record Payment, Upload Receipt, Verify Payment, Get Payment, List Payments, Get Stats, Refund

---

### Module 7: Notification Module

```mermaid
graph TB
    subgraph "Notification Module Components"
        NotificationRouter[Notification Router<br/>5 endpoints]
        NotificationService[Notification Service]
        SegmentResolver[User Segment Resolver]
        FCMHandler[FCM Handler]
        EmailHandler[Email Handler]
        NotificationRepo[Notification Repository]
    end
    
    NotificationRouter --> NotificationService
    NotificationService --> SegmentResolver
    NotificationService --> FCMHandler
    NotificationService --> EmailHandler
    NotificationService --> NotificationRepo
    
    FCMHandler --> Celery
    EmailHandler --> Celery
    Celery --> FCM[Firebase Cloud Messaging]
    Celery --> SMTP[Email SMTP]
    NotificationRepo --> PostgreSQL
```

**Endpoints:** Send Notification, Send Bulk, Get Notification, List Notifications, Get Stats

---

### Module 8: Branch Module

```mermaid
graph TB
    subgraph "Branch Module Components"
        BranchRouter[Branch Router<br/>5 endpoints]
        BranchService[Branch Service]
        BranchRepo[Branch Repository]
    end
    
    BranchRouter --> BranchService
    BranchService --> BranchRepo
    BranchRepo --> PostgreSQL
```

**Endpoints:** Create Branch, Update Branch, Delete Branch, Get Branch, List Branches

---

### Module 9: Department Module

```mermaid
graph TB
    subgraph "Department Module Components"
        DeptRouter[Department Router<br/>5 endpoints]
        DeptService[Department Service]
        DeptRepo[Department Repository]
    end
    
    DeptRouter --> DeptService
    DeptService --> DeptRepo
    DeptRepo --> PostgreSQL
```

**Endpoints:** Create Department, Update Department, Delete Department, Get Department, List Departments

---

### Module 10: Analytics Module

```mermaid
graph TB
    subgraph "Analytics Module Components"
        AnalyticsRouter[Analytics Router<br/>4 endpoints]
        AnalyticsService[Analytics Service]
        MetricsCalculator[Metrics Calculator]
        ReportGenerator[Report Generator]
        AnalyticsCache[Analytics Cache]
    end
    
    AnalyticsRouter --> AnalyticsService
    AnalyticsService --> MetricsCalculator
    AnalyticsService --> ReportGenerator
    AnalyticsService --> AnalyticsCache
    
    MetricsCalculator --> PostgreSQL
    AnalyticsCache --> Redis
    ReportGenerator --> Celery
```

**Endpoints:** Get Dashboard Stats, Get Youth Analytics, Get Financial Analytics, Generate Report

---

### Module 11: AI/ML Module

```mermaid
graph TB
    subgraph "AI/ML Module Components"
        AIRouter[AI Router<br/>3 endpoints]
        AIService[AI Service]
        ContextBuilder[Context Builder]
        GeminiClient[Gemini Client]
        OpenRouterClient[OpenRouter Client]
        FallbackHandler[Fallback Handler]
    end
    
    AIRouter --> AIService
    AIService --> ContextBuilder
    AIService --> GeminiClient
    AIService --> OpenRouterClient
    AIService --> FallbackHandler
    
    ContextBuilder --> PostgreSQL
    GeminiClient --> Gemini[Google Gemini API]
    OpenRouterClient --> OpenRouter[OpenRouter API]
    FallbackHandler --> OpenRouterClient
```

**Endpoints:** Chat with AI, Get AI Insights, Predict Attendance Risk

---

## 4. Cross-Cutting Concerns Components

```mermaid
graph TB
    subgraph "Security Components"
        AppCheck[Firebase App Check]
        RateLimiter[Rate Limiter]
        RBAC[RBAC Handler]
        JWTVerifier[JWT Verifier]
    end
    
    subgraph "Observability Components"
        Logger[Structured Logger]
        Metrics[Prometheus Metrics]
        Tracer[Distributed Tracer]
    end
    
    subgraph "Data Sync Components"
        FirestoreSync[Firestore Sync]
        RedisCache[Redis Cache]
        EventBus[Domain Event Bus]
    end
    
    subgraph "Background Jobs"
        CeleryBeat[Celery Beat Scheduler]
        AttendanceWorker[Attendance Worker]
        NotificationWorker[Notification Worker]
        ReportWorker[Report Worker]
        CleanupWorker[Cleanup Worker]
    end
    
    AppCheck --> FastAPI
    RateLimiter --> FastAPI
    RBAC --> FastAPI
    JWTVerifier --> FastAPI
    
    Logger --> AllModules[All Modules]
    Metrics --> AllModules
    Tracer --> AllModules
    
    FirestoreSync --> AttendanceModule
    FirestoreSync --> EventModule
    RedisCache --> AllModules
    EventBus --> AllModules
    
    CeleryBeat --> AttendanceWorker
    CeleryBeat --> NotificationWorker
    CeleryBeat --> ReportWorker
    CeleryBeat --> CleanupWorker
```

---

## 5. Module Dependency Graph

```mermaid
graph LR
    Auth[Auth Module]
    Youth[Youth Module]
    Event[Event Module]
    Attendance[Attendance Module]
    Pledge[Pledge Module]
    Payment[Payment Module]
    Notification[Notification Module]
    Branch[Branch Module]
    Dept[Department Module]
    Analytics[Analytics Module]
    AI[AI/ML Module]
    
    Youth --> Auth
    Youth --> Branch
    Youth --> Dept
    
    Event --> Auth
    Event --> Branch
    Event --> Notification
    
    Attendance --> Auth
    Attendance --> Youth
    Attendance --> Event
    Attendance --> Notification
    
    Pledge --> Auth
    Pledge --> Youth
    Pledge --> Notification
    
    Payment --> Auth
    Payment --> Pledge
    Payment --> Notification
    
    Analytics --> Youth
    Analytics --> Attendance
    Analytics --> Pledge
    Analytics --> Payment
    Analytics --> Event
    
    AI --> Youth
    AI --> Attendance
    AI --> Event
    
    Notification --> Auth
    Branch --> Auth
    Dept --> Auth
```

**Dependency Rules:**
- Auth module has zero internal dependencies (foundation layer)
- Branch and Department modules depend only on Auth
- Youth module depends on Auth, Branch, Department
- Event, Pledge modules depend on Auth and related entities
- Attendance module depends on Youth and Event
- Payment module depends on Pledge
- Analytics and AI modules depend on multiple data modules (read-only)
- Notification module is dependency-inverted (other modules trigger it via events)

---

## 6. API Gateway Component Details

```mermaid
graph TB
    subgraph "API Gateway Pipeline"
        Request[HTTP Request]
        
        Request --> AppCheckMiddleware[App Check Middleware]
        AppCheckMiddleware --> RateLimitMiddleware[Rate Limit Middleware]
        RateLimitMiddleware --> LoggingMiddleware[Logging Middleware]
        LoggingMiddleware --> CORSMiddleware[CORS Middleware]
        CORSMiddleware --> SecurityHeadersMiddleware[Security Headers]
        SecurityHeadersMiddleware --> Router[Route Handler]
        
        Router --> RBACCheck{RBAC Check}
        RBACCheck -->|Authorized| Controller[Controller Logic]
        RBACCheck -->|Denied| Error403[403 Forbidden]
        
        Controller --> Service[Service Layer]
        Service --> Response[HTTP Response]
        
        Error403 --> Response
    end
```

**Middleware Stack Order:**
1. **App Check Middleware**: Verifies Firebase App Check token
2. **Rate Limit Middleware**: Redis-based rate limiting (100 req/min per IP)
3. **Logging Middleware**: Structured logging with request ID
4. **CORS Middleware**: Cross-origin resource sharing headers
5. **Security Headers**: CSP, HSTS, X-Frame-Options
6. **Route Handler**: Matches endpoint and invokes controller
7. **RBAC Check**: Role-based authorization at controller level

---

## Component Summary

### Total Component Count
- **11 Feature Modules**: 63 total endpoints
- **4 Architectural Layers**: Domain, Application, Infrastructure, Presentation
- **6 Cross-Cutting Concerns**: Security, Observability, Data Sync, Background Jobs, Error Handling, Validation
- **8 External Service Integrations**: Firebase, Gemini AI, OpenRouter, OpenAI, FCM, Email, Neon PostgreSQL, Firestore

### Key Architectural Principles
1. **Clean Architecture**: Strict layer separation with dependency inversion
2. **Domain-Driven Design**: Rich domain models with business logic encapsulation
3. **Modular Monolith**: 11 independent feature modules, ready for microservices migration
4. **Event-Driven**: Domain events for cross-module communication
5. **Async Processing**: Celery for background jobs and notifications
6. **Multi-Database**: PostgreSQL (source of truth), Redis (cache), Firestore (mobile sync)

---

*Reference: Based on v1.0 backend architecture in `app/api/v1/` and Clean Architecture implementation*

# 07 - Data Flow Diagrams

Data Flow Diagrams (DFD) show how data moves through the Abundance Zone Platform v2.0 using structured design methodology.

---

## 1. Context Diagram (Level 0 DFD)

```mermaid
graph TB
    subgraph "External Entities"
        Admin[Super Admin]
        Coordinator[Branch Coordinator]
        Leader[Department Leader]
        Youth[Youth Member]
        Mobile[Mobile App Users]
    end
    
    subgraph "Abundance Zone Platform v2.0"
        System[Abundance Zone<br/>Youth Management System]
    end
    
    subgraph "External Systems"
        Firebase[Firebase Auth]
        Gemini[Google Gemini AI]
        FCM[Firebase Cloud Messaging]
        Email[Email Service]
    end
    
    Admin -->|User credentials, System config| System
    System -->|Dashboard data, Reports| Admin
    
    Coordinator -->|Youth data, Event data| System
    System -->|Analytics, Attendance reports| Coordinator
    
    Leader -->|Attendance records, Pledge data| System
    System -->|Department stats, Youth lists| Leader
    
    Youth -->|Profile updates, Payment receipts| System
    System -->|Event notifications, Attendance status| Youth
    
    Mobile -->|Check-in/out requests| System
    System -->|Real-time attendance updates| Mobile
    
    System -->|Auth requests| Firebase
    Firebase -->|JWT tokens| System
    
    System -->|AI prompts| Gemini
    Gemini -->|AI responses| System
    
    System -->|Push notifications| FCM
    System -->|Email notifications| Email
    
    style System fill:#FFD700
```

**Key Insights:**
- 4 user roles with distinct data flows
- 4 external system integrations
- Bidirectional data flow for all interactive users

---

## 2. Level 1 DFD - Major Processes

```mermaid
graph TB
    subgraph "Users"
        U[Users]
    end
    
    subgraph "Abundance Zone Platform Processes"
        P1[1.0<br/>User Authentication<br/>& Authorization]
        P2[2.0<br/>Youth<br/>Management]
        P3[3.0<br/>Event<br/>Management]
        P4[4.0<br/>Attendance<br/>Tracking]
        P5[5.0<br/>Financial<br/>Management]
        P6[6.0<br/>Notification<br/>System]
        P7[7.0<br/>Analytics &<br/>Reporting]
        P8[8.0<br/>AI Assistant]
    end
    
    subgraph "Data Stores"
        DS1[(D1: Users DB)]
        DS2[(D2: Youths DB)]
        DS3[(D3: Events DB)]
        DS4[(D4: Attendance DB)]
        DS5[(D5: Financial DB)]
        DS6[(D6: Cache)]
    end
    
    subgraph "External Systems"
        EXT1[Firebase]
        EXT2[Gemini AI]
        EXT3[FCM]
    end
    
    U -->|Login credentials| P1
    P1 -->|JWT token| U
    P1 <-->|User data| DS1
    P1 <-->|Auth requests| EXT1
    
    U -->|Youth data| P2
    P2 -->|Youth profiles| U
    P2 <-->|Youth records| DS2
    P2 -->|Cache youth data| DS6
    
    U -->|Event data| P3
    P3 -->|Event schedules| U
    P3 <-->|Event records| DS3
    P3 -->|Notify users| P6
    
    U -->|Attendance data| P4
    P4 -->|Attendance status| U
    P4 <-->|Attendance records| DS4
    P4 -->|Read youth data| DS2
    P4 -->|Read event data| DS3
    
    U -->|Payment data| P5
    P5 -->|Financial reports| U
    P5 <-->|Financial records| DS5
    
    P6 -->|Notifications| U
    P6 -->|Send push| EXT3
    P6 -->|Cache notifications| DS6
    
    P7 -->|Reports & insights| U
    P7 -->|Read all data| DS2
    P7 -->|Read all data| DS3
    P7 -->|Read all data| DS4
    P7 -->|Read all data| DS5
    
    U -->|AI queries| P8
    P8 -->|AI responses| U
    P8 <-->|AI requests| EXT2
    P8 -->|Read context data| DS2
    
    style P1 fill:#FFB6C1
    style P2 fill:#87CEEB
    style P3 fill:#90EE90
    style P4 fill:#FFD700
    style P5 fill:#DDA0DD
    style P6 fill:#F0E68C
    style P7 fill:#FFA07A
    style P8 fill:#98FB98
```

---

## 3. Level 2 DFD - Authentication & Authorization Process

```mermaid
graph TB
    U[User] -->|Login request| P1_1[1.1<br/>Validate<br/>Credentials]
    
    P1_1 <-->|Verify credentials| DS1[(D1: Users DB)]
    P1_1 <-->|Firebase SSO| EXT1[Firebase Auth]
    
    P1_1 -->|Valid credentials| P1_2[1.2<br/>Generate<br/>JWT Tokens]
    P1_1 -->|Invalid credentials| U
    
    P1_2 -->|Store refresh token| DS1
    P1_2 -->|Cache access token| DS6[(D6: Cache)]
    P1_2 -->|Access + Refresh tokens| U
    
    U -->|Access token| P1_3[1.3<br/>Verify<br/>Token]
    P1_3 <-->|Check cache| DS6
    P1_3 <-->|Verify signature| DS1
    
    P1_3 -->|Valid token| P1_4[1.4<br/>Check<br/>RBAC]
    P1_3 -->|Invalid token| U
    
    P1_4 <-->|Load user roles| DS1
    P1_4 -->|Authorized| P_Next[Next Process]
    P1_4 -->|Forbidden| U
    
    U -->|Refresh token| P1_5[1.5<br/>Refresh<br/>Token]
    P1_5 <-->|Verify refresh token| DS1
    P1_5 -->|Rotate tokens| P1_2
    
    style P1_1 fill:#FFB6C1
    style P1_2 fill:#FFB6C1
    style P1_3 fill:#FFB6C1
    style P1_4 fill:#FFB6C1
    style P1_5 fill:#FFB6C1
```

**Data Elements:**
- **Input**: email, password, firebase_token
- **Output**: access_token (JWT, 15 min), refresh_token (30 days)
- **Storage**: users table, refresh_tokens table, Redis cache

---

## 4. Level 2 DFD - Youth Management Process

```mermaid
graph TB
    U[User] -->|Youth data| P2_1[2.1<br/>Validate<br/>Youth Data]
    
    P2_1 -->|Valid data| P2_2[2.2<br/>Check<br/>Duplicates]
    P2_1 -->|Invalid data| U
    
    P2_2 <-->|Query existing| DS2[(D2: Youths DB)]
    P2_2 -->|Duplicate found| U
    P2_2 -->|No duplicate| P2_3[2.3<br/>Create/Update<br/>Youth Record]
    
    P2_3 -->|Store youth| DS2
    P2_3 -->|Emit YouthRegistered event| P2_4[2.4<br/>Domain<br/>Event Handler]
    
    P2_4 -->|Notify coordinator| P6[6.0 Notification System]
    P2_4 -->|Cache youth profile| DS6[(D6: Cache)]
    P2_4 -->|Success response| U
    
    U -->|Youth ID| P2_5[2.5<br/>Get Youth<br/>Details]
    P2_5 -->|Check cache| DS6
    P2_5 -->|Cache hit| U
    P2_5 -->|Cache miss| P2_6[2.6<br/>Query<br/>Database]
    
    P2_6 <-->|Fetch youth| DS2
    P2_6 -->|Calculate attendance rate| DS4[(D4: Attendance DB)]
    P2_6 -->|Cache result| DS6
    P2_6 -->|Youth profile| U
    
    U -->|Youth ID| P2_7[2.7<br/>Predict<br/>Attendance Risk]
    P2_7 <-->|Fetch history| DS4
    P2_7 -->|AI prediction request| EXT2[Gemini AI]
    EXT2 -->|Risk score| P2_7
    P2_7 -->|Risk prediction| U
    
    style P2_1 fill:#87CEEB
    style P2_2 fill:#87CEEB
    style P2_3 fill:#87CEEB
    style P2_4 fill:#87CEEB
    style P2_5 fill:#87CEEB
    style P2_6 fill:#87CEEB
    style P2_7 fill:#87CEEB
```

**Data Elements:**
- **Input**: first_name, last_name, phone, email, branch_id, department_id, date_of_birth
- **Output**: youth_id, platform_role, attendance_rate, risk_score
- **Storage**: youths table, Redis cache (5 min TTL)
- **Events**: YouthRegistered, YouthUpdated, YouthStatusChanged

---

## 5. Level 2 DFD - Attendance Tracking Process

```mermaid
graph TB
    U[User] -->|Check-in request| P4_1[4.1<br/>Validate<br/>QR Code]
    
    P4_1 <-->|Verify event| DS3[(D3: Events DB)]
    P4_1 -->|Invalid QR| U
    P4_1 -->|Valid QR| P4_2[4.2<br/>Check<br/>Existing Record]
    
    P4_2 <-->|Query attendance| DS4[(D4: Attendance DB)]
    P4_2 -->|Already checked in| U
    P4_2 -->|New check-in| P4_3[4.3<br/>Record<br/>Check-in]
    
    P4_3 -->|Create attendance record| DS4
    P4_3 -->|Update status: CheckedIn| DS4
    P4_3 -->|Emit AttendanceRecorded event| P4_4[4.4<br/>Sync<br/>Firestore]
    
    P4_4 -->|Real-time sync| EXT1[Firestore]
    P4_4 -->|Success| U
    
    U -->|Check-out request| P4_5[4.5<br/>Record<br/>Check-out]
    P4_5 <-->|Find check-in record| DS4
    P4_5 -->|Update checkout time| DS4
    P4_5 -->|Calculate duration| P4_6[4.6<br/>Determine<br/>Status]
    
    P4_6 -->|Duration >= threshold| P4_7[4.7<br/>Mark Present]
    P4_6 -->|Duration < threshold| P4_8[4.8<br/>Mark Early<br/>Departure]
    
    P4_7 -->|Update status: Present| DS4
    P4_7 -->|Recalculate attendance rate| P4_9[4.9<br/>Update<br/>Youth Stats]
    
    P4_8 -->|Update status: EarlyDeparture| DS4
    P4_8 -->|Flag for review| P4_9
    
    P4_9 <-->|Update youth record| DS2[(D2: Youths DB)]
    P4_9 -->|Invalidate cache| DS6[(D6: Cache)]
    P4_9 -->|Sync to Firestore| EXT1
    P4_9 -->|Success| U
    
    Coordinator[Coordinator] -->|Bulk attendance data| P4_10[4.10<br/>Bulk<br/>Processing]
    P4_10 -->|Validate batch| P4_11[4.11<br/>Queue<br/>Celery Task]
    P4_11 -->|Process async| P4_3
    P4_11 -->|Task ID| Coordinator
    
    style P4_1 fill:#FFD700
    style P4_2 fill:#FFD700
    style P4_3 fill:#FFD700
    style P4_4 fill:#FFD700
    style P4_5 fill:#FFD700
    style P4_6 fill:#FFD700
    style P4_7 fill:#FFD700
    style P4_8 fill:#FFD700
    style P4_9 fill:#FFD700
    style P4_10 fill:#FFD700
    style P4_11 fill:#FFD700
```

**Data Elements:**
- **Input**: qr_code_data, youth_id, event_id, check_in_time, check_out_time
- **Output**: attendance_id, status (Present/Absent/EarlyDeparture), duration
- **Storage**: attendance table, Firestore collection, Redis cache
- **Events**: AttendanceRecorded, AttendanceUpdated, YouthStatsChanged
- **Async**: Bulk operations via Celery (500 records per batch)

---

## 6. Level 2 DFD - Financial Management Process

```mermaid
graph TB
    U[Youth] -->|Pledge commitment| P5_1[5.1<br/>Create<br/>Pledge]
    
    P5_1 -->|Validate amount| P5_2[5.2<br/>Store<br/>Pledge]
    P5_2 -->|Create pledge record| DS5[(D5: Financial DB)]
    P5_2 -->|Schedule reminder| P5_3[5.3<br/>Schedule<br/>Notifications]
    
    P5_3 -->|Queue Celery task| Queue[Task Queue]
    P5_3 -->|Success| U
    
    U -->|Payment + Receipt image| P5_4[5.4<br/>Upload<br/>Receipt]
    P5_4 -->|Store image| EXT1[Cloud Storage]
    P5_4 -->|Image URL| P5_5[5.5<br/>OCR<br/>Processing]
    
    P5_5 -->|Send to GPT-4o Vision| EXT2[OpenAI API]
    EXT2 -->|Extracted data| P5_5
    P5_5 -->|amount, date, merchant| P5_6[5.6<br/>Validate<br/>Payment]
    
    P5_6 -->|Validate against pledge| DS5
    P5_6 -->|Valid payment| P5_7[5.7<br/>Record<br/>Payment]
    P5_6 -->|Invalid/mismatch| U
    
    P5_7 -->|Create payment record| DS5
    P5_7 -->|Update pledge progress| P5_8[5.8<br/>Update<br/>Pledge Status]
    
    P5_8 <-->|Calculate total paid| DS5
    P5_8 -->|amount_paid >= pledge_amount| P5_9[5.9<br/>Mark<br/>Fully Paid]
    P5_8 -->|amount_paid < pledge_amount| P5_10[5.10<br/>Mark<br/>Partially Paid]
    
    P5_9 -->|Update status: FullyPaid| DS5
    P5_9 -->|Cancel reminders| Queue
    P5_9 -->|Notify youth| P6[6.0 Notification System]
    P5_9 -->|Success| U
    
    P5_10 -->|Update status: PartiallyPaid| DS5
    P5_10 -->|Success| U
    
    Coordinator[Coordinator] -->|Query payments| P5_11[5.11<br/>Generate<br/>Financial Report]
    P5_11 <-->|Aggregate data| DS5
    P5_11 -->|Format report| Coordinator
    
    style P5_1 fill:#DDA0DD
    style P5_2 fill:#DDA0DD
    style P5_3 fill:#DDA0DD
    style P5_4 fill:#DDA0DD
    style P5_5 fill:#DDA0DD
    style P5_6 fill:#DDA0DD
    style P5_7 fill:#DDA0DD
    style P5_8 fill:#DDA0DD
    style P5_9 fill:#DDA0DD
    style P5_10 fill:#DDA0DD
    style P5_11 fill:#DDA0DD
```

**Data Elements:**
- **Input**: pledge_amount, due_date, receipt_image, payment_amount
- **Output**: pledge_id, payment_id, ocr_extracted_data, pledge_status
- **Storage**: pledges table, payments table, Cloud Storage (images)
- **External**: OpenAI GPT-4o Vision for OCR
- **Async**: Scheduled reminders via Celery Beat

---

## 7. Level 2 DFD - Notification System Process

```mermaid
graph TB
    Source[Event Source] -->|Notification trigger| P6_1[6.1<br/>Create<br/>Notification]
    
    P6_1 -->|notification_data| P6_2[6.2<br/>Resolve<br/>User Segment]
    
    P6_2 <-->|Query users| DS1[(D1: Users DB)]
    P6_2 -->|Filter by role/branch| P6_3[6.3<br/>Build<br/>Recipient List]
    
    P6_3 -->|recipient_list| P6_4[6.4<br/>Queue<br/>Notification Task]
    
    P6_4 -->|Enqueue to Redis| Queue[Celery Queue]
    P6_4 -->|Task ID| Source
    
    Queue -->|Pick task| Worker[Celery Worker]
    Worker -->|Process notification| P6_5[6.5<br/>Prepare<br/>Messages]
    
    P6_5 -->|Split by channel| P6_6[6.6<br/>Send Push<br/>Notification]
    P6_5 -->|Split by channel| P6_7[6.7<br/>Send Email<br/>Notification]
    
    P6_6 -->|Batch 500 users| EXT1[FCM]
    EXT1 -->|Delivery status| P6_8[6.8<br/>Track<br/>Delivery]
    
    P6_7 -->|SMTP| EXT2[Email Service]
    EXT2 -->|Delivery status| P6_8
    
    P6_8 -->|Log delivery| DS_Notif[(D6: Notifications DB)]
    P6_8 -->|Update metrics| DS6[(D6: Cache)]
    
    P6_8 -->|Retry on failure| P6_9{Max<br/>Retries?}
    P6_9 -->|No| Queue
    P6_9 -->|Yes| P6_10[6.10<br/>Mark<br/>Failed]
    
    P6_10 -->|Store failure| DS_Notif
    
    style P6_1 fill:#F0E68C
    style P6_2 fill:#F0E68C
    style P6_3 fill:#F0E68C
    style P6_4 fill:#F0E68C
    style P6_5 fill:#F0E68C
    style P6_6 fill:#F0E68C
    style P6_7 fill:#F0E68C
    style P6_8 fill:#F0E68C
    style P6_9 fill:#F0E68C
    style P6_10 fill:#F0E68C
```

**Data Elements:**
- **Input**: title, body, user_segment, priority, channel (push/email)
- **Output**: notification_id, delivery_status, recipients_count, failed_count
- **Storage**: notifications table, Redis queue
- **External**: Firebase FCM, Email SMTP
- **Retry Logic**: Max 3 retries with exponential backoff (30s, 5m, 30m)

---

## 8. Module Hierarchy (Structured Design)

```mermaid
graph TB
    Main[Main Application<br/>FastAPI App] --> Auth[Auth Module]
    Main --> Youth[Youth Module]
    Main --> Event[Event Module]
    Main --> Attendance[Attendance Module]
    Main --> Pledge[Pledge Module]
    Main --> Payment[Payment Module]
    Main --> Notification[Notification Module]
    Main --> Branch[Branch Module]
    Main --> Dept[Department Module]
    Main --> Analytics[Analytics Module]
    Main --> AI[AI Module]
    
    Auth --> AuthService[Auth Service]
    Auth --> JWTManager[JWT Manager]
    Auth --> UserRepo[User Repository]
    
    Youth --> YouthService[Youth Service]
    Youth --> YouthRepo[Youth Repository]
    Youth --> RiskPredictor[Risk Predictor]
    
    Attendance --> AttendanceService[Attendance Service]
    Attendance --> BulkProcessor[Bulk Processor]
    Attendance --> FirestoreSync[Firestore Sync]
    Attendance --> AttendanceRepo[Attendance Repository]
    
    Payment --> PaymentService[Payment Service]
    Payment --> OCRProcessor[OCR Processor]
    Payment --> PaymentRepo[Payment Repository]
    
    Notification --> NotificationService[Notification Service]
    Notification --> FCMHandler[FCM Handler]
    Notification --> EmailHandler[Email Handler]
    
    Analytics --> AnalyticsService[Analytics Service]
    Analytics --> MetricsCalc[Metrics Calculator]
    Analytics --> ReportGen[Report Generator]
    
    AI --> AIService[AI Service]
    AI --> GeminiClient[Gemini Client]
    AI --> OpenRouterClient[OpenRouter Client]
    
    style Main fill:#FFD700
    style Auth fill:#FFB6C1
    style Youth fill:#87CEEB
    style Attendance fill:#FFD700
    style Payment fill:#DDA0DD
    style Notification fill:#F0E68C
    style Analytics fill:#FFA07A
    style AI fill:#98FB98
```

**Module Coupling:**
- **Low coupling**: Modules communicate via domain events
- **High cohesion**: Each module encapsulates related functionality
- **Dependency direction**: Always toward domain layer (Clean Architecture)

---

## 9. Data Dictionary

### Key Data Entities

| Entity | Primary Key | Foreign Keys | Description |
|--------|-------------|--------------|-------------|
| **User** | user_id (UUID) | branch_id, department_id | Platform users (all roles) |
| **Youth** | youth_id (UUID) | user_id, branch_id, department_id | Youth members |
| **Event** | event_id (UUID) | branch_id, created_by (user_id) | Events/activities |
| **Attendance** | attendance_id (UUID) | youth_id, event_id | Attendance records |
| **Pledge** | pledge_id (UUID) | youth_id | Financial pledges |
| **Payment** | payment_id (UUID) | pledge_id | Pledge payments |
| **Notification** | notification_id (UUID) | user_id | Sent notifications |
| **Branch** | branch_id (UUID) | None | Organization branches |
| **Department** | department_id (UUID) | branch_id | Branch departments |

### Key Data Flows

| Flow | Source | Destination | Frequency | Volume |
|------|--------|-------------|-----------|--------|
| **User Login** | User → System → Firebase | JWT tokens | Per session | ~100/day |
| **Youth Registration** | Coordinator → System → DB | Youth record | Daily | ~10/day |
| **Attendance Check-in** | Youth → System → DB + Firestore | Attendance record | Per event | ~500/event |
| **Bulk Attendance** | Coordinator → System → Celery → DB | Batch attendance | Weekly | ~500 records/batch |
| **Payment Receipt** | Youth → System → OpenAI → DB | Payment + OCR data | Weekly | ~50/week |
| **Push Notification** | System → Celery → FCM → Users | Push message | Daily | ~1000/day |
| **Analytics Query** | Coordinator → System → DB | Report data | Daily | ~20/day |
| **AI Chat** | User → System → Gemini | AI response | Hourly | ~100/day |

---

## Data Flow Summary

### Key Insights
1. **Clean Architecture**: All data flows respect layer boundaries
2. **Async Processing**: Heavy operations (bulk attendance, notifications, OCR) use Celery
3. **Caching Strategy**: Redis caches frequently accessed data (users, youth profiles, attendance rates)
4. **Real-time Sync**: Firestore mirrors critical data for mobile app
5. **External Integrations**: 4 external services (Firebase, Gemini, OpenAI, FCM)
6. **Event-Driven**: Domain events trigger cross-module communication

### Performance Optimizations
- **Cache-first reads**: Check Redis before database
- **Bulk operations**: Batch processing for attendance (500 records)
- **Async tasks**: Background workers for notifications and sync
- **Read replicas**: Database read scaling via Neon replicas
- **CDN delivery**: Static assets via Vercel CDN

---

*Reference: Based on v1.0 data flow patterns and structured design principles*

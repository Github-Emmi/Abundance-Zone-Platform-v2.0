# Class Diagram - Object-Oriented Analysis & Design (OOAD)

## Abundance Zone Youth Management Platform v2.0

**Diagram Type:** UML Structural Diagram
**Purpose:** Show all domain entities, their properties, methods, and relationships
**Notation:** UML 2.5 Class Diagram

---

## 1. Complete Domain Model Class Diagram

```mermaid
classDiagram
    class User {
        +UUID id
        +String name
        +String email
        +String password_hash
        +RoleEnum role
        +UUID branch_id
        +UUID department_id
        +Boolean is_active
        +Boolean is_email_verified
        +DateTime created_at
        +DateTime updated_at
        +login(email, password) Token
        +logout() Boolean
        +reset_password(token, new_password) Boolean
        +update_profile(data) User
        +register_fcm_token(token) Boolean
    }

    class RoleEnum {
        <<enumeration>>
        SUPER_ADMIN
        BRANCH_COORDINATOR
        DEPARTMENT_LEADER
        YOUTH_MEMBER
    }

    class Branch {
        +UUID id
        +String name
        +String location
        +String address
        +String phone
        +UUID coordinator_id
        +Boolean is_active
        +DateTime created_at
        +create(data) Branch
        +update(data) Branch
        +get_statistics() BranchStats
        +list_youths(filters) Youth[]
        +list_departments() Department[]
    }

    class Department {
        +UUID id
        +String name
        +String description
        +UUID branch_id
        +UUID leader_id
        +Boolean is_default
        +Boolean is_active
        +DateTime created_at
        +create(data) Department
        +update(data) Department
        +assign_leader(user_id) Boolean
        +get_members() User[]
        +get_health_metrics() DepartmentHealth
    }

    class Youth {
        +UUID id
        +String fullname
        +String email
        +String phone
        +GenderEnum gender
        +Date date_of_birth
        +String address
        +UUID branch_id
        +UUID department_id
        +UUID user_id
        +PlatformRoleEnum platform_role
        +MembershipStatusEnum status
        +String profile_image_url
        +DateTime created_at
        +DateTime updated_at
        +register(data) Youth
        +update_profile(data) Youth
        +assign_department(dept_id) Boolean
        +link_user_account(user_id) Boolean
        +get_attendance_history() Attendance[]
        +calculate_attendance_rate() Float
    }

    class GenderEnum {
        <<enumeration>>
        MALE
        FEMALE
    }

    class MembershipStatusEnum {
        <<enumeration>>
        ACTIVE
        INACTIVE
        SUSPENDED
        TRANSFERRED
    }

    class Event {
        +UUID id
        +String title
        +String description
        +EventTypeEnum event_type
        +DateTime start_time
        +DateTime end_time
        +String venue
        +UUID branch_id
        +UUID created_by
        +Boolean is_recurring
        +Boolean is_regional
        +Boolean rsvp_required
        +Int max_attendees
        +DateTime created_at
        +create(data) Event
        +update(data) Event
        +cancel() Boolean
        +notify_participants() Boolean
        +bulk_mark_attendance(records) Attendance[]
    }

    class EventTypeEnum {
        <<enumeration>>
        SUNDAY_SERVICE
        BIBLE_STUDY
        WORKERS_MEETING
        REVIVAL_HOUR
        YOUTH_VIGIL
        SPECIAL_EVENT
        REGIONAL_MEETING
    }

    class Attendance {
        +UUID id
        +UUID youth_id
        +UUID event_id
        +AttendanceStatusEnum status
        +String notes
        +UUID marked_by
        +DateTime marked_at
        +DateTime created_at
        +mark_attendance(youth_id, event_id, status) Attendance
        +bulk_mark(records) Attendance[]
        +sync_to_firestore() Boolean
        +get_event_summary(event_id) AttendanceSummary
    }

    class AttendanceStatusEnum {
        <<enumeration>>
        PRESENT
        ABSENT
        EXCUSED
        LATE
    }

    class Pledge {
        +UUID id
        +UUID user_id
        +PledgeTypeEnum pledge_type
        +Decimal amount
        +Decimal amount_paid
        +PledgeStatusEnum status
        +String project
        +String description
        +Date due_date
        +DateTime created_at
        +create(data) Pledge
        +record_payment(amount, receipt) Payment
        +calculate_balance() Decimal
        +send_reminder() Boolean
    }

    class PledgeTypeEnum {
        <<enumeration>>
        MONTHLY
        PROJECT
        PROGRAM
        SPECIAL
    }

    class Payment {
        +UUID id
        +UUID pledge_id
        +Decimal amount
        +String receipt_url
        +JSON receipt_data
        +DateTime paid_at
        +UUID verified_by
        +DateTime verified_at
        +record_payment(data) Payment
        +extract_receipt_ocr(url) JSON
        +verify_payment(user_id) Boolean
    }

    class Notification {
        +UUID id
        +UUID user_id
        +NotificationTypeEnum type
        +NotificationChannelEnum channel
        +String title
        +String content
        +JSON metadata
        +DateTime read_at
        +DateTime sent_at
        +Boolean is_delivered
        +create(data) Notification
        +mark_read() Boolean
        +dispatch() Boolean
        +broadcast_to_topic(topic, message) Boolean
    }

    class NotificationTypeEnum {
        <<enumeration>>
        ANNOUNCEMENT
        REMINDER
        ATTENDANCE_ALERT
        PLEDGE_REMINDER
        EVENT_INVITE
        SYSTEM
    }

    class NotificationChannelEnum {
        <<enumeration>>
        IN_APP
        EMAIL
        WHATSAPP
        PUSH
    }

    class RefreshToken {
        +UUID id
        +UUID user_id
        +String token_hash
        +DateTime expires_at
        +Boolean is_revoked
        +String device_info
        +DateTime created_at
        +create(user_id) RefreshToken
        +rotate(old_token) RefreshToken
        +revoke() Boolean
        +revoke_all_user_tokens(user_id) Boolean
    }

    %% Relationships

    User "1" --> "0..1" Branch : belongs_to
    User "1" --> "0..1" Department : belongs_to
    User "1" --> "0..*" RefreshToken : has_many
    User "1" --> "0..*" Notification : receives
    User "1" --> "0..*" Pledge : creates

    Branch "1" --> "0..*" User : has_members
    Branch "1" --> "0..*" Department : contains
    Branch "1" --> "0..*" Youth : manages
    Branch "1" --> "0..*" Event : hosts
    Branch "1" <-- "1" User : coordinated_by

    Department "1" --> "0..*" User : has_members
    Department "1" --> "0..*" Youth : contains
    Department "1" <-- "0..1" User : led_by
    Department "*" --> "1" Branch : belongs_to

    Youth "1" --> "1" Branch : belongs_to
    Youth "1" --> "0..1" Department : assigned_to
    Youth "1" --> "0..1" User : linked_to_account
    Youth "1" --> "0..*" Attendance : has_records

    Event "1" --> "0..1" Branch : hosted_by
    Event "1" --> "0..*" Attendance : tracks
    Event "1" <-- "1" User : created_by

    Attendance "*" --> "1" Youth : for_youth
    Attendance "*" --> "1" Event : at_event
    Attendance "1" <-- "0..1" User : marked_by

    Pledge "1" --> "1" User : pledged_by
    Pledge "1" --> "0..*" Payment : receives

    Payment "*" --> "1" Pledge : for_pledge
    Payment "1" <-- "0..1" User : verified_by

    Notification "*" --> "1" User : sent_to

    RefreshToken "*" --> "1" User : belongs_to

    User -- RoleEnum
    Youth -- GenderEnum
    Youth -- MembershipStatusEnum
    Event -- EventTypeEnum
    Attendance -- AttendanceStatusEnum
    Pledge -- PledgeTypeEnum
    Notification -- NotificationTypeEnum
    Notification -- NotificationChannelEnum
```

---

## 2. Repository Pattern Interfaces

```mermaid
classDiagram
    class IRepository~T~ {
        <<interface>>
        +get_by_id(id: UUID) T
        +create(entity: T) T
        +update(id: UUID, data: Dict) T
        +delete(id: UUID) Boolean
        +list(filters: Dict) List~T~
    }

    class IUserRepository {
        <<interface>>
        +get_by_email(email: String) User
        +get_by_branch(branch_id: UUID) User[]
        +update_role(user_id: UUID, role: RoleEnum) Boolean
        +verify_email(token: String) Boolean
    }

    class IYouthRepository {
        <<interface>>
        +get_by_branch(branch_id: UUID) Youth[]
        +get_by_department(dept_id: UUID) Youth[]
        +search_by_name(query: String) Youth[]
        +get_upcoming_birthdays(days: Int) Youth[]
        +soft_delete(id: UUID) Boolean
    }

    class IAttendanceRepository {
        <<interface>>
        +get_by_event(event_id: UUID) Attendance[]
        +get_by_youth(youth_id: UUID) Attendance[]
        +bulk_create(records: List) Attendance[]
        +get_summary(event_id: UUID) AttendanceSummary
    }

    class UserRepository {
        -db: AsyncSession
        +get_by_id(id: UUID) User
        +get_by_email(email: String) User
        +create(user: User) User
        +update_role(user_id: UUID, role: RoleEnum) Boolean
    }

    class YouthRepository {
        -db: AsyncSession
        +get_by_branch(branch_id: UUID) Youth[]
        +search_by_name(query: String) Youth[]
        +get_upcoming_birthdays(days: Int) Youth[]
    }

    class AttendanceRepository {
        -db: AsyncSession
        +bulk_create(records: List) Attendance[]
        +get_summary(event_id: UUID) AttendanceSummary
    }

    IRepository <|.. IUserRepository
    IRepository <|.. IYouthRepository
    IRepository <|.. IAttendanceRepository

    IUserRepository <|.. UserRepository
    IYouthRepository <|.. YouthRepository
    IAttendanceRepository <|.. AttendanceRepository
```

---

## 3. Service Layer Pattern

```mermaid
classDiagram
    class AuthService {
        -user_repo: IUserRepository
        -jwt_handler: JWTHandler
        -email_service: EmailService
        +login(email, password) LoginResponse
        +register(data) User
        +refresh_token(refresh_token) TokenPair
        +logout(refresh_token) Boolean
        +forgot_password(email) Boolean
        +reset_password(token, new_password) Boolean
        +firebase_signin(firebase_token) LoginResponse
    }

    class YouthService {
        -youth_repo: IYouthRepository
        -storage_service: StorageService
        -event_bus: EventBus
        +create_youth(data) Youth
        +list_youths(filters) Tuple~Youth[], Int~
        +update_youth(id, data) Youth
        +remove_youth(id) Boolean
        +upload_profile_image(id, file) String
        +get_upcoming_birthdays(days) Youth[]
    }

    class AttendanceService {
        -attendance_repo: IAttendanceRepository
        -firestore_service: FirestoreService
        -event_bus: EventBus
        +mark_attendance(youth_id, event_id, status) Attendance
        +bulk_mark_attendance(event_id, records) Attendance[]
        +get_event_attendance(event_id) Attendance[]
        +get_youth_history(youth_id) Attendance[]
        +predict_risk(youth_id, features) RiskPrediction
    }

    class FinanceService {
        -pledge_repo: IPledgeRepository
        -payment_repo: IPaymentRepository
        -ocr_service: ReceiptOCRService
        -notification_service: NotificationService
        +create_pledge(data) Pledge
        +record_payment(pledge_id, amount, receipt) Payment
        +extract_receipt_data(image_url) JSON
        +send_pledge_reminder(user_id) Boolean
        +get_financial_summary(branch_id) FinancialSummary
    }

    class NotificationService {
        -notification_repo: INotificationRepository
        -email_service: EmailService
        -push_service: PushService
        -whatsapp_service: WhatsAppService
        +create_notification(data) Notification
        +dispatch_notification(notification_id) Boolean
        +broadcast_to_branch(branch_id, message) Boolean
        +send_to_topic(topic, message) Boolean
        +mark_read(notification_id) Boolean
    }

    class AIService {
        -gemini_client: GeminiClient
        -openai_client: OpenAIClient
        -cache: RedisCache
        +chat_with_assistant(message, context) String
        +generate_analytics_insight(data) String
        +get_bible_guidance(query) BibleResponse
        +get_daily_verses() VerseResponse
        +extract_receipt_data(image_url) JSON
    }

    class AnalyticsService {
        -analytics_repo: IAnalyticsRepository
        -cache: RedisCache
        +get_branch_overview(branch_id) BranchStats
        +get_attendance_trend(branch_id, months) TrendData
        +get_global_overview() GlobalStats
        +generate_department_leaderboard() LeaderboardData
    }

    AuthService ..> IUserRepository
    YouthService ..> IYouthRepository
    AttendanceService ..> IAttendanceRepository
    FinanceService ..> IPledgeRepository
    NotificationService ..> INotificationRepository
```

---

## 4. Domain Events (Event-Driven Architecture)

```mermaid
classDiagram
    class DomainEvent {
        <<abstract>>
        +UUID event_id
        +DateTime timestamp
        +String aggregate_id
        +Dict metadata
    }

    class YouthRegistered {
        +UUID youth_id
        +UUID branch_id
        +String name
        +String email
    }

    class AttendanceRecorded {
        +UUID attendance_id
        +UUID youth_id
        +UUID event_id
        +AttendanceStatusEnum status
    }

    class PledgeSubmitted {
        +UUID pledge_id
        +UUID user_id
        +Decimal amount
        +PledgeTypeEnum type
    }

    class EventCreated {
        +UUID event_id
        +UUID branch_id
        +String title
        +DateTime event_date
        +Boolean is_regional
    }

    class ReceiptUploaded {
        +UUID payment_id
        +UUID pledge_id
        +String receipt_url
    }

    class EventBus {
        -subscribers: Dict
        +publish(event: DomainEvent) void
        +subscribe(event_type, handler) void
        +unsubscribe(event_type, handler) void
    }

    DomainEvent <|-- YouthRegistered
    DomainEvent <|-- AttendanceRecorded
    DomainEvent <|-- PledgeSubmitted
    DomainEvent <|-- EventCreated
    DomainEvent <|-- ReceiptUploaded

    EventBus ..> DomainEvent
```

---

## 5. Value Objects

```mermaid
classDiagram
    class Email {
        -String value
        +validate() Boolean
        +domain() String
        +to_string() String
    }

    class PhoneNumber {
        -String value
        -String country_code
        +validate() Boolean
        +format_international() String
        +format_national() String
    }

    class Role {
        -RoleEnum value
        +has_permission(permission) Boolean
        +is_admin() Boolean
        +is_coordinator() Boolean
        +can_access_branch(branch_id) Boolean
    }

    class AttendanceRate {
        -Int total_events
        -Int attended
        +calculate() Float
        +is_at_risk() Boolean
        +get_risk_level() RiskLevel
    }

    class Amount {
        -Decimal value
        -String currency
        +add(other: Amount) Amount
        +subtract(other: Amount) Amount
        +format() String
    }
```

---

## 6. External Service Adapters (Adapter Pattern)

```mermaid
classDiagram
    class IEmailService {
        <<interface>>
        +send_email(to, subject, body) Boolean
        +send_template(to, template_id, data) Boolean
    }

    class IPushService {
        <<interface>>
        +send_to_token(token, title, body) Boolean
        +send_to_topic(topic, title, body) Boolean
        +send_multicast(tokens, title, body) Boolean
    }

    class IAIService {
        <<interface>>
        +chat(message, context) String
        +generate_insight(data) String
    }

    class ResendEmailService {
        -api_key: String
        -from_email: String
        +send_email(to, subject, body) Boolean
    }

    class FirebasePushService {
        -firebase_app: FirebaseApp
        +send_to_token(token, title, body) Boolean
        +send_to_topic(topic, title, body) Boolean
    }

    class GeminiAIService {
        -api_key: String
        -model: String
        +chat(message, context) String
    }

    class OpenAIService {
        -api_key: String
        -base_url: String
        +chat(message, context) String
    }

    IEmailService <|.. ResendEmailService
    IPushService <|.. FirebasePushService
    IAIService <|.. GeminiAIService
    IAIService <|.. OpenAIService
```

---

## Key OOAD Principles Applied

### 1. **Encapsulation**

- All entity properties are private/protected
- Access through public methods only
- Business logic encapsulated in domain entities

### 2. **Inheritance**

- Repository pattern: specific repos inherit from IRepository~T~
- Domain events inherit from abstract DomainEvent
- Service classes inherit common service behaviors

### 3. **Polymorphism**

- Multiple AI service implementations (Gemini, OpenAI) via IAIService interface
- Repository pattern allows swapping database implementations
- Notification channels (Email, Push, WhatsApp) implement common interface

### 4. **Abstraction**

- Repository interfaces abstract data access
- Service layer abstracts business logic from presentation
- Domain layer has no dependencies on infrastructure

### 5. **Loose Coupling**

- Services depend on interfaces, not concrete implementations
- Domain events decouple modules (EventBus pattern)
- Adapter pattern decouples external services

### 6. **High Cohesion**

- Each class has single responsibility
- Related methods grouped in same class
- Domain entities contain their own business rules

---

## Object Instantiation Examples

```python
# Creating instances (objects) from classes

# User instance
admin_user = User(
    id=uuid4(),
    name="Regional Leader",
    email="admin@abundancezone.org",
    role=RoleEnum.SUPER_ADMIN,
    branch_id=None  # Super admin has no branch restriction
)

# Youth instance
youth_member = Youth(
    id=uuid4(),
    fullname="Emmanuel Oladipo",
    email="emmanuel@email.com",
    gender=GenderEnum.MALE,
    date_of_birth=date(2000, 5, 15),
    branch_id=lagos_branch.id,
    department_id=choir_dept.id,
    status=MembershipStatusEnum.ACTIVE
)

# Attendance instance
attendance_record = Attendance(
    id=uuid4(),
    youth_id=youth_member.id,
    event_id=sunday_service.id,
    status=AttendanceStatusEnum.PRESENT,
    marked_by=admin_user.id,
    marked_at=datetime.now()
)

# Service usage
youth_service = YouthService(
    youth_repo=YouthRepository(db),
    storage_service=StorageService(),
    event_bus=EventBus()
)

created_youth = await youth_service.create_youth(youth_data)
```

---

**Document Purpose:** This class diagram serves as the blueprint for the entire system's object-oriented design, showing how all domain entities, services, repositories, and value objects relate to each other.

**For Kiro:** Use this diagram to understand:

- What classes exist in the system
- What properties and methods each class has
- How classes relate to each other (composition, aggregation, inheritance)
- How to instantiate objects and call their methods

**Reference:** Phase 03 Database Schema + Phase 08 Backend Architecture

# 03 - State Diagrams

State diagrams show the lifecycle and state transitions of key domain entities in the Abundance Zone Platform v2.0.

---

## 1. Youth Membership Lifecycle State Diagram

```mermaid
stateDiagram-v2
    [*] --> Pending: Youth Registration
    
    Pending --> Active: Coordinator Approval
    Pending --> Rejected: Coordinator Rejection
    Pending --> Pending: Update Profile
    
    Active --> Suspended: Disciplinary Action
    Active --> Inactive: Prolonged Absence (>3 months)
    Active --> Active: Regular Attendance
    Active --> AtRisk: Low Attendance (<50%)
    
    AtRisk --> Active: Attendance Improved (>70%)
    AtRisk --> Inactive: Continued Low Attendance
    
    Suspended --> Active: Suspension Lifted
    Suspended --> Terminated: Permanent Ban
    
    Inactive --> Active: Return & Re-enrollment
    Inactive --> Archived: >12 months inactive
    
    Terminated --> [*]
    Rejected --> [*]
    Archived --> [*]
    
    note right of Pending
        Awaiting coordinator approval
        Can update profile fields
    end note
    
    note right of Active
        Full platform access
        Can attend events
        Can make pledges
    end note
    
    note right of AtRisk
        Triggered by ML prediction
        or <50% attendance rate
        Notifications sent
    end note
```

**State Descriptions:**

| State | Description | Triggers | Exit Conditions |
|-------|-------------|----------|-----------------|
| **Pending** | Initial registration awaiting approval | Youth submits registration form | Coordinator approves/rejects |
| **Active** | Full membership with platform access | Approval or suspension lifted | Suspension, prolonged absence, at-risk detection |
| **AtRisk** | Low engagement warning state | Attendance <50% or ML prediction | Attendance improves or continues declining |
| **Suspended** | Temporary disciplinary suspension | Coordinator action for policy violation | Suspension period ends or permanent ban |
| **Inactive** | No activity for extended period | No attendance for >3 months | Re-enrollment or archival |
| **Archived** | Historical record only | Inactive for >12 months | Final state |
| **Rejected** | Registration denied | Coordinator rejection | Final state |
| **Terminated** | Permanent ban from platform | Severe policy violation | Final state |

---

## 2. Attendance Record State Diagram

```mermaid
stateDiagram-v2
    [*] --> PendingCheckIn: Event Starts
    
    PendingCheckIn --> CheckedIn: QR Code Scan / Manual Entry
    PendingCheckIn --> Absent: Event Ends Without Check-in
    
    CheckedIn --> PendingCheckOut: Waiting for Check-out
    
    PendingCheckOut --> Present: QR Code Scan / Manual Check-out
    PendingCheckOut --> EarlyDeparture: Check-out Before Event End
    
    Present --> [*]
    EarlyDeparture --> [*]
    Absent --> [*]
    
    note right of CheckedIn
        Check-in timestamp recorded
        Synced to Firestore
    end note
    
    note right of Present
        Full attendance credited
        Attendance rate updated
    end note
    
    note right of EarlyDeparture
        Partial attendance credited
        Flag for coordinator review
    end note
```

**State Transitions:**

- **PendingCheckIn → CheckedIn**: Youth scans QR code or coordinator marks present
- **CheckedIn → Present**: Youth completes full event duration and checks out
- **CheckedIn → EarlyDeparture**: Youth leaves before event end time
- **PendingCheckIn → Absent**: Event ends without check-in record

**Business Rules:**
- Early departure flagged if checkout time < (event_end_time - 30 minutes)
- Bulk operations can skip PendingCheckIn for manual marking
- Firestore sync occurs immediately on state change
- Attendance rate recalculated on every Present/Absent/EarlyDeparture final state

---

## 3. Pledge Payment State Diagram

```mermaid
stateDiagram-v2
    [*] --> Pledged: Youth Makes Pledge
    
    Pledged --> PartiallyPaid: First Payment Recorded
    Pledged --> FullyPaid: Complete Payment Recorded
    Pledged --> Cancelled: Youth Cancels Pledge
    
    PartiallyPaid --> PartiallyPaid: Additional Payment
    PartiallyPaid --> FullyPaid: Final Payment Recorded
    PartiallyPaid --> Overdue: Payment Due Date Passed
    PartiallyPaid --> Cancelled: Youth Cancels
    
    Overdue --> PartiallyPaid: Late Payment Recorded
    Overdue --> FullyPaid: Complete Late Payment
    Overdue --> Defaulted: >60 Days Overdue
    
    FullyPaid --> Refunded: Refund Issued
    FullyPaid --> [*]
    
    Cancelled --> [*]
    Defaulted --> [*]
    Refunded --> [*]
    
    note right of Pledged
        Initial commitment recorded
        Due date set
        Notifications scheduled
    end note
    
    note right of PartiallyPaid
        Payment progress tracked
        amount_paid < pledge_amount
        Receipts attached via OCR
    end note
    
    note right of Overdue
        Automated reminders sent
        Coordinator notified
        Grace period: 7 days
    end note
```

**Payment State Logic:**

```python
def calculate_pledge_state(pledge: Pledge, payments: list[Payment]) -> PledgeState:
    total_paid = sum(p.amount for p in payments if p.status == "VERIFIED")
    
    if total_paid == 0:
        if datetime.now() > pledge.due_date + timedelta(days=60):
            return PledgeState.DEFAULTED
        elif datetime.now() > pledge.due_date:
            return PledgeState.OVERDUE
        return PledgeState.PLEDGED
    
    elif total_paid < pledge.amount:
        if datetime.now() > pledge.due_date:
            return PledgeState.OVERDUE
        return PledgeState.PARTIALLY_PAID
    
    elif total_paid >= pledge.amount:
        if any(p.is_refunded for p in payments):
            return PledgeState.REFUNDED
        return PledgeState.FULLY_PAID
```

---

## 4. Event Lifecycle State Diagram

```mermaid
stateDiagram-v2
    [*] --> Draft: Coordinator Creates Event
    
    Draft --> Scheduled: Coordinator Publishes
    Draft --> Cancelled: Coordinator Cancels
    
    Scheduled --> InProgress: Event Start Time Reached
    Scheduled --> Cancelled: Coordinator Cancels
    Scheduled --> Rescheduled: Date/Time Changed
    
    Rescheduled --> Scheduled: New Date Confirmed
    
    InProgress --> Completed: Event End Time + All Check-outs
    InProgress --> Cancelled: Emergency Cancellation
    
    Completed --> Archived: >90 Days After End
    
    Archived --> [*]
    Cancelled --> [*]
    
    note right of Draft
        Not visible to youths
        Can edit all fields
    end note
    
    note right of Scheduled
        Notifications sent to youths
        QR codes generated
        Cannot edit core fields
    end note
    
    note right of InProgress
        Check-in/out active
        Real-time attendance tracking
        Notifications paused
    end note
    
    note right of Completed
        Attendance finalized
        Analytics available
        Read-only mode
    end note
```

**Automatic State Transitions (Celery Beat Tasks):**

| Transition | Trigger | Frequency | Action |
|------------|---------|-----------|--------|
| Scheduled → InProgress | `datetime.now() >= event.start_time` | Every 5 minutes | Enable QR code scanning |
| InProgress → Completed | `datetime.now() >= event.end_time + 1 hour` | Every 15 minutes | Finalize attendance, send summary notifications |
| Completed → Archived | `datetime.now() >= event.end_time + 90 days` | Daily at 2 AM | Archive event data, compress analytics |

---

## 5. Notification State Diagram

```mermaid
stateDiagram-v2
    [*] --> Queued: Notification Created
    
    Queued --> Sending: Celery Task Picked Up
    
    Sending --> Sent: FCM/Email Success
    Sending --> Failed: FCM/Email Error
    Sending --> PartiallyDelivered: Some Recipients Failed
    
    Failed --> Retrying: Retry Logic (Max 3)
    Retrying --> Sending
    Retrying --> PermanentFailure: Max Retries Exceeded
    
    PartiallyDelivered --> [*]
    Sent --> [*]
    PermanentFailure --> [*]
    
    note right of Queued
        Redis queue entry
        Priority assigned
        User segment resolved
    end note
    
    note right of Sending
        Batch size: 500 users
        Rate limit: 100 msg/sec
        Parallel FCM + Email
    end note
    
    note right of Failed
        Exponential backoff
        Retry delays: 30s, 5m, 30m
    end note
```

**Notification Priority Levels:**

- **CRITICAL**: Security alerts, payment confirmations (immediate delivery)
- **HIGH**: Event reminders, attendance alerts (5-minute delay)
- **NORMAL**: General announcements, birthday wishes (hourly batch)
- **LOW**: Analytics reports, monthly summaries (daily batch)

---

## 6. User Session State Diagram

```mermaid
stateDiagram-v2
    [*] --> Unauthenticated: App Launch
    
    Unauthenticated --> Authenticating: Login Request
    
    Authenticating --> Authenticated: JWT Issued
    Authenticating --> Unauthenticated: Auth Failed
    
    Authenticated --> Active: API Requests
    Authenticated --> Idle: No Activity (5 mins)
    Authenticated --> TokenExpired: Access Token Expired (15 mins)
    
    Idle --> Active: User Interaction
    Idle --> TokenExpired: Continued Idle (15 mins)
    
    TokenExpired --> RefreshingToken: Refresh Token Sent
    
    RefreshingToken --> Authenticated: New Access Token
    RefreshingToken --> Unauthenticated: Refresh Token Expired/Invalid
    
    Active --> Unauthenticated: Logout
    Authenticated --> Unauthenticated: Account Suspended
    
    Unauthenticated --> [*]
    
    note right of Authenticated
        Access token valid
        Role-based permissions active
        App Check token verified
    end note
    
    note right of TokenExpired
        Access token expired (15 min)
        Refresh token still valid (30 days)
        Silent refresh attempted
    end note
```

**Token Lifetimes:**
- **Access Token**: 15 minutes
- **Refresh Token**: 30 days (rotated on use)
- **Firebase App Check Token**: 1 hour (auto-renewed)

---

## State Diagram Summary

### Key Insights

1. **Youth Membership**: 8 distinct states with automated risk detection
2. **Attendance**: 5 states supporting partial attendance and bulk operations
3. **Pledge Payments**: 7 states with overdue handling and OCR integration
4. **Events**: 6 states with automatic time-based transitions
5. **Notifications**: 6 states with retry logic and priority queues
6. **User Sessions**: 7 states with token refresh and security checks

### State Management Implementation

**Domain Events Triggered on State Changes:**
- `YouthStatusChanged(youth_id, old_state, new_state, reason)`
- `AttendanceStatusChanged(attendance_id, event_id, youth_id, status)`
- `PledgeStatusChanged(pledge_id, youth_id, old_state, new_state, amount_paid)`
- `EventStatusChanged(event_id, old_state, new_state, timestamp)`
- `NotificationStatusChanged(notification_id, status, recipients_count, failed_count)`

**State Persistence:**
- All states stored in PostgreSQL (Neon) with audit trail
- State transitions logged in `audit_logs` table
- Firestore mirrors attendance and event states for mobile app
- Redis caches current states for high-frequency reads

---

*Reference: Based on v1.0 backend state machines in `app/models/` and service layer logic*

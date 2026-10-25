# Department Leader Journey - Complete User Flow

**Document**: Department Leader User Journey  
**Version**: 2.0.0  
**Date**: October 16, 2026  
**Role**: DEPARTMENT_LEADER (Department-level management)

---

## 🎯 Department Leader Overview

**Department Leader** manages a single department with access to:
- ✅ Department youth management (assigned department only)
- ✅ Event participation for department youth
- ✅ Attendance tracking for department
- ✅ Department-level reports
- ✅ Youth engagement monitoring
- ❌ NO finance access
- ❌ NO system-wide analytics

---

## 🗺️ Complete Journey Map

```mermaid
graph TB
    START([User Visits Platform]) --> LOGIN[Login Page]
    LOGIN --> AUTH{Authenticate}
    
    AUTH -->|Valid - DEPARTMENT_LEADER| LEADER_DASH[Department Leader Dashboard]
    
    LEADER_DASH --> OVERVIEW[Department Overview]
    OVERVIEW --> DEPT_STATS[View Department Statistics]
    OVERVIEW --> YOUTH_LIST[View Department Youth]
    OVERVIEW --> UPCOMING_EVENTS[Upcoming Events]
    
    LEADER_DASH --> NAV{Choose Action}
    
    NAV --> YOUTH_MGMT[Youth Management]
    NAV --> EVENT_PARTICIPATION[Event Participation]
    NAV --> ATTENDANCE[Attendance Tracking]
    NAV --> REPORTS[Department Reports]
    
    YOUTH_MGMT --> VIEW_YOUTH[View Youth Profiles]
    YOUTH_MGMT --> REGISTER_YOUTH[Register New Youth]
    YOUTH_MGMT --> ENGAGEMENT[Monitor Engagement]
    
    EVENT_PARTICIPATION --> VIEW_EVENTS[View Assigned Events]
    EVENT_PARTICIPATION --> MANAGE_RSVP[Manage RSVPs]
    
    ATTENDANCE --> CHECKIN[Record Attendance]
    ATTENDANCE --> ATTENDANCE_REPORTS[View Reports]
    
    style LEADER_DASH fill:#2196F3,stroke:#1976D2,stroke-width:3px
    style YOUTH_MGMT fill:#4CAF50,stroke:#388E3C,stroke-width:2px
```

---

## 📊 Dashboard Components

### Quick Stats
- Total department youth
- Active youth count
- This month's attendance rate
- Upcoming events

### Recent Activity
- Recent youth registrations
- Recent event participation
- Recent attendance records

---

## 🔄 Key Features

### 1. Youth Management (Department-Scoped)
- View youth in assigned department only
- Register new youth to department
- View youth profiles and history
- Monitor engagement scores

### 2. Event Participation
- View events assigned to department
- Track RSVP responses
- Encourage participation

### 3. Attendance Tracking
- Record attendance for department youth
- View attendance history
- Generate department reports

### 4. Engagement Monitoring
- Track youth participation trends
- Identify at-risk youth
- View engagement metrics

---

## 🔐 Permission Matrix

| Feature | Create | Read | Update | Delete | Export | Scope |
|---------|--------|------|--------|--------|--------|-------|
| **Youth** | ✅ | ✅ | ✅ | ❌ | ✅ | Department only |
| **Events** | ❌ | ✅ | ❌ | ❌ | ❌ | View only |
| **Attendance** | ✅ | ✅ | ✅ | ❌ | ✅ | Department only |
| **Reports** | ❌ | ✅ | ❌ | ❌ | ✅ | Department only |
| **Finance** | ❌ | ❌ | ❌ | ❌ | ❌ | No access |
| **Analytics** | ❌ | ✅ | ❌ | ❌ | ❌ | Department only |

---

## 🎯 Success Metrics

1. **Department Youth Growth**: New registrations per month
2. **Attendance Rate**: Average attendance percentage
3. **Event Participation**: Percentage of youth attending events
4. **Engagement Score**: Department-wide average
5. **At-Risk Youth**: Number identified and interventions

---

**Next Document**: 09-YOUTH-MEMBER-JOURNEY.md

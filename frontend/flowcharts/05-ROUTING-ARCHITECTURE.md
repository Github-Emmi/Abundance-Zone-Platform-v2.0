# Routing Architecture - Next.js App Router

**Document**: Routing Architecture  
**Version**: 2.0.0  
**Date**: October 16, 2026  
**Purpose**: Complete Next.js 15 App Router structure with role-based access

---

## 🎯 Overview

The Abundance Zone Platform uses **Next.js 15 App Router** with route groups for role-based access control, parallel routes for modals, and intercepting routes for seamless UX.

---

## 📁 Complete Route Structure

```
src/app/
├── layout.tsx                    # Root layout
├── page.tsx                      # Landing → redirects to dashboard
├── providers.tsx                 # Query + Zustand providers
│
├── (auth)/                       # PUBLIC routes
│   ├── layout.tsx
│   ├── login/page.tsx
│   ├── register/page.tsx
│   ├── forgot-password/page.tsx
│   └── reset-password/page.tsx
│
└── (dashboard)/                  # PROTECTED routes
    ├── layout.tsx                # Sidebar + Header
    ├── dashboard/
    │   ├── admin/page.tsx
    │   ├── coordinator/page.tsx
    │   ├── leader/page.tsx
    │   └── member/page.tsx
    ├── youths/
    │   ├── page.tsx              # List
    │   ├── new/page.tsx
    │   └── [id]/
    │       ├── page.tsx
    │       └── edit/page.tsx
    ├── events/
    │   ├── page.tsx
    │   ├── new/page.tsx
    │   └── [id]/page.tsx
    ├── attendance/
    │   ├── page.tsx
    │   ├── check-in/page.tsx
    │   └── reports/page.tsx
    ├── finance/
    │   ├── page.tsx
    │   └── reports/page.tsx
    ├── analytics/
    │   └── page.tsx
    └── settings/
        └── page.tsx
```

---

## 🛡️ Middleware Protection

```typescript
// src/middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('az_session')?.value;
  
  // Public paths
  if (publicPaths.includes(pathname)) return NextResponse.next();
  
  // Require auth
  if (!token) return NextResponse.redirect(new URL('/login', request.url));
  
  // Role-based access
  const decoded = jwtDecode<{ role: string }>(token);
  if (!hasAccess(pathname, decoded.role)) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  
  return NextResponse.next();
}
```

---

## 🔐 Role Access Matrix

| Route | SUPER_ADMIN | BRANCH_COORDINATOR | DEPARTMENT_LEADER | YOUTH_MEMBER |
|-------|-------------|-------------------|-------------------|--------------|
| /dashboard | ✅ | ✅ | ✅ | ✅ |
| /youths | ✅ | ✅ | ✅ | ❌ |
| /events | ✅ | ✅ | ✅ | ✅ |
| /attendance | ✅ | ✅ | ✅ | ❌ |
| /finance | ✅ | ✅ | ❌ | ❌ |
| /analytics | ✅ | ✅ | ❌ | ❌ |

---

**Backend Integration**: Maps to 78 API endpoints

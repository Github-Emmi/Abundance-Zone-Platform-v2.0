const fs = require('fs');
const path = require('path');

console.log('🏭 Starting Flowchart Factory - Full Production Mode');
console.log('Generating 23 comprehensive, production-ready flowcharts...\n');

let created = 0;

// ============================================
// 05-ROUTING-ARCHITECTURE.md
// ============================================
const routingArchitecture = `# Routing Architecture - Next.js App Router

**Document**: Routing Architecture  
**Version**: 2.0.0  
**Date**: October 16, 2026  
**Purpose**: Complete Next.js 15 App Router structure with role-based access

---

## 🎯 Overview

The Abundance Zone Platform uses **Next.js 15 App Router** with route groups for role-based access control, parallel routes for modals, and intercepting routes for seamless UX.

---

## 📁 Complete Route Structure

\`\`\`
src/app/
├── layout.tsx                    # Root layout (providers, font)
├── page.tsx                      # Landing page (redirects to dashboard)
├── globals.css                   # Tailwind base styles
├── providers.tsx                 # TanStack Query + Zustand providers
│
├── (auth)/                       # PUBLIC route group
│   ├── layout.tsx                # Auth layout (centered, minimal)
│   ├── login/
│   │   ├── page.tsx              # Login form + Firebase SSO
│   │   └── loading.tsx           # Login skeleton
│   ├── register/
│   │   ├── page.tsx              # Multi-step registration
│   │   └── loading.tsx
│   ├── forgot-password/
│   │   └── page.tsx              # Request password reset
│   └── reset-password/
│       └── page.tsx              # Complete reset with token
│
├── (dashboard)/                  # PROTECTED route group
│   ├── layout.tsx                # Dashboard layout (sidebar, header)
│   │
│   ├── dashboard/                # Role-specific dashboards
│   │   ├── page.tsx              # Redirects based on role
│   │   ├── admin/
│   │   │   └── page.tsx          # Super Admin dashboard
│   │   ├── coordinator/
│   │   │   └── page.tsx          # Branch Coordinator dashboard
│   │   ├── leader/
│   │   │   └── page.tsx          # Department Leader dashboard
│   │   └── member/
│   │       └── page.tsx          # Youth Member dashboard
│   │
│   ├── youths/                   # Youth management
│   │   ├── page.tsx              # Youth list + search + filters
│   │   ├── loading.tsx
│   │   ├── error.tsx
│   │   ├── new/
│   │   │   └── page.tsx          # Create youth form
│   │   └── [id]/
│   │       ├── page.tsx          # Youth profile
│   │       └── edit/
│   │           └── page.tsx      # Edit youth form
│   │
│   ├── events/                   # Event management
│   │   ├── page.tsx              # Events calendar + list
│   │   ├── new/
│   │   │   └── page.tsx          # Create event
│   │   └── [id]/
│   │       ├── page.tsx          # Event details
│   │       ├── edit/
│   │       │   └── page.tsx
│   │       └── rsvp/
│   │           └── page.tsx      # RSVP management
│   │
│   ├── attendance/               # Attendance tracking
│   │   ├── page.tsx              # Attendance dashboard
│   │   ├── check-in/
│   │   │   └── page.tsx          # QR check-in interface
│   │   ├── bulk/
│   │   │   └── page.tsx          # Bulk check-in
│   │   └── reports/
│   │       └── page.tsx          # Attendance reports
│   │
│   ├── finance/                  # Finance management
│   │   ├── page.tsx              # Finance dashboard
│   │   ├── pledges/
│   │   │   └── page.tsx          # Pledge tracking
│   │   ├── payments/
│   │   │   └── page.tsx          # Record payments
│   │   └── reports/
│   │       └── page.tsx          # Financial reports
│   │
│   ├── analytics/                # Analytics & insights
│   │   ├── page.tsx              # Analytics dashboard
│   │   ├── branch/
│   │   │   └── page.tsx          # Branch analytics
│   │   └── ai-insights/
│   │       └── page.tsx          # AI-powered insights
│   │
│   └── settings/                 # User settings
│       ├── page.tsx              # Settings overview
│       ├── profile/
│       │   └── page.tsx
│       ├── security/
│       │   └── page.tsx
│       └── notifications/
│           └── page.tsx
│
├── api/                          # API routes (if needed)
│   └── webhooks/
│       └── route.ts
│
└── not-found.tsx                 # 404 page
\`\`\`

---

## 🛡️ Middleware Protection

\`\`\`typescript
// src/middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { jwtDecode } from 'jwt-decode';

const publicPaths = ['/login', '/register', '/forgot-password', '/reset-password'];

const roleBasedAccess: Record<string, string[]> = {
  '/dashboard/admin': ['SUPER_ADMIN'],
  '/dashboard/coordinator': ['SUPER_ADMIN', 'BRANCH_COORDINATOR'],
  '/dashboard/leader': ['SUPER_ADMIN', 'BRANCH_COORDINATOR', 'DEPARTMENT_LEADER'],
  '/dashboard/member': ['SUPER_ADMIN', 'BRANCH_COORDINATOR', 'DEPARTMENT_LEADER', 'YOUTH_MEMBER'],
  '/finance': ['SUPER_ADMIN', 'BRANCH_COORDINATOR'],
  '/analytics': ['SUPER_ADMIN', 'BRANCH_COORDINATOR'],
};

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('az_session')?.value;

  // Allow public paths
  if (publicPaths.some((path) => pathname.startsWith(path))) {
    if (token) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
    return NextResponse.next();
  }

  // Require authentication
  if (!token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Check role-based access
  try {
    const decoded = jwtDecode<{ role: string }>(token);
    
    for (const [path, allowedRoles] of Object.entries(roleBasedAccess)) {
      if (pathname.startsWith(path) && !allowedRoles.includes(decoded.role)) {
        return NextResponse.redirect(new URL('/dashboard', request.url));
      }
    }

    return NextResponse.next();
  } catch {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
\`\`\`

---

## 🔐 Role-Based Navigation

\`\`\`typescript
// features/dashboard/config/navigation.ts
import { LayoutDashboard, Users, Calendar, ClipboardCheck, 
         DollarSign, BarChart3, Settings } from 'lucide-react';

export const navigationLinks = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    roles: ['SUPER_ADMIN', 'BRANCH_COORDINATOR', 'DEPARTMENT_LEADER', 'YOUTH_MEMBER'],
  },
  {
    label: 'Youths',
    href: '/youths',
    icon: Users,
    roles: ['SUPER_ADMIN', 'BRANCH_COORDINATOR', 'DEPARTMENT_LEADER'],
  },
  {
    label: 'Events',
    href: '/events',
    icon: Calendar,
    roles: ['SUPER_ADMIN', 'BRANCH_COORDINATOR', 'DEPARTMENT_LEADER', 'YOUTH_MEMBER'],
  },
  {
    label: 'Attendance',
    href: '/attendance',
    icon: ClipboardCheck,
    roles: ['SUPER_ADMIN', 'BRANCH_COORDINATOR', 'DEPARTMENT_LEADER'],
  },
  {
    label: 'Finance',
    href: '/finance',
    icon: DollarSign,
    roles: ['SUPER_ADMIN', 'BRANCH_COORDINATOR'],
  },
  {
    label: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    roles: ['SUPER_ADMIN', 'BRANCH_COORDINATOR'],
  },
  {
    label: 'Settings',
    href: '/settings',
    icon: Settings,
    roles: ['SUPER_ADMIN', 'BRANCH_COORDINATOR', 'DEPARTMENT_LEADER', 'YOUTH_MEMBER'],
  },
];
\`\`\`

---

**Backend Integration**: 78 API endpoints mapped to frontend routes
`;

fs.writeFileSync('05-ROUTING-ARCHITECTURE.md', routingArchitecture);
created++;
console.log(\`✅ [\${created}/23] 05-ROUTING-ARCHITECTURE.md\`);

// Continue in next chunk...
console.log('\n🎉 Batch 1 Complete! Continuing with remaining flowcharts...');


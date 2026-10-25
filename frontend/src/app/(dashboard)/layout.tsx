"use client"

import * as React from "react"
import { useRouter, usePathname } from "next/navigation"
import { useAuthStore, UserRole } from "@/features/auth/stores/authStore"
import { DashboardNav } from "@/shared/ui/dashboard-nav"
import { DashboardHeader } from "@/shared/ui/dashboard-header"

/**
 * Get role-specific dashboard path
 */
function getRoleDashboard(role: UserRole): string {
  const dashboards = {
    [UserRole.SUPER_ADMIN]: '/dashboard/admin',
    [UserRole.BRANCH_COORDINATOR]: '/dashboard/coordinator',
    [UserRole.DEPARTMENT_LEADER]: '/dashboard/leader',
    [UserRole.YOUTH_MEMBER]: '/dashboard/member',
  }
  return dashboards[role] || '/dashboard'
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  const { isAuthenticated, isHydrated, user } = useAuthStore()

  // Redirect to login if not authenticated
  React.useEffect(() => {
    if (isHydrated && !isAuthenticated) {
      router.push("/login")
    }
  }, [isAuthenticated, isHydrated, router])

  // Redirect to role-specific dashboard if accessing /dashboard root
  React.useEffect(() => {
    if (isHydrated && isAuthenticated && user && pathname === '/dashboard') {
      const roleDashboard = getRoleDashboard(user.role)
      router.push(roleDashboard)
    }
  }, [isAuthenticated, isHydrated, user, pathname, router])

  // Show loading while hydrating or if not authenticated
  if (!isHydrated || !isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen">
      <DashboardNav />
      <div className="flex-1 flex flex-col">
        <DashboardHeader />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { 
  LayoutDashboard, 
  Users, 
  Calendar, 
  UserCheck, 
  DollarSign, 
  BarChart3, 
  Bell, 
  Settings,
  Building2,
  Folders
} from "lucide-react"
import { cn } from "@/shared/lib/utils"
import { useUserRole } from "@/features/auth/hooks/useAuth"
import { UserRole } from "@/features/auth/stores/authStore"

interface NavItem {
  label: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  roles?: UserRole[]
}

const navigationItems: NavItem[] = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Youth Management",
    href: "/youths",
    icon: Users,
  },
  {
    label: "Events",
    href: "/events",
    icon: Calendar,
  },
  {
    label: "Attendance",
    href: "/attendance",
    icon: UserCheck,
  },
  {
    label: "Finance",
    href: "/finance",
    icon: DollarSign,
  },
  {
    label: "Analytics",
    href: "/analytics",
    icon: BarChart3,
  },
  {
    label: "Branches",
    href: "/branches",
    icon: Building2,
    roles: [UserRole.SUPER_ADMIN],
  },
  {
    label: "Departments",
    href: "/departments",
    icon: Folders,
    roles: [UserRole.SUPER_ADMIN, UserRole.BRANCH_COORDINATOR],
  },
  {
    label: "Notifications",
    href: "/notifications",
    icon: Bell,
  },
  {
    label: "Settings",
    href: "/settings",
    icon: Settings,
  },
]

export function DashboardNav() {
  const pathname = usePathname()
  const userRole = useUserRole()

  const filteredNav = React.useMemo(() => {
    return navigationItems.filter((item) => {
      if (!item.roles) return true
      return item.roles.includes(userRole as UserRole)
    })
  }, [userRole])

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="h-16 flex items-center px-6 border-b border-gray-200">
        <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white text-lg font-bold">
          AZ
        </div>
        <span className="ml-3 font-semibold text-lg">Abundance Zone</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-3">
          {filteredNav.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
            
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-white"
                      : "text-gray-700 hover:bg-gray-100"
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {item.label}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </aside>
  )
}

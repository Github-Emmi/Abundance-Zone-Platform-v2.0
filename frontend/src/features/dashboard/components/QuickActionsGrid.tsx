import * as React from "react"
import Link from "next/link"
import { LucideIcon, UserPlus, Calendar, CheckCircle, DollarSign, BarChart3, Building } from "lucide-react"
import { Card, CardContent } from "@/shared/ui/card"
import { cn } from "@/shared/lib/utils"

interface QuickAction {
  id: string
  label: string
  description: string
  href: string
  icon: LucideIcon
  iconColor: string
  iconBgColor: string
}

const defaultActions: QuickAction[] = [
  {
    id: "add-youth",
    label: "Add Youth",
    description: "Register new youth member",
    href: "/youths/new",
    icon: UserPlus,
    iconColor: "text-blue-600",
    iconBgColor: "bg-blue-100",
  },
  {
    id: "create-event",
    label: "Create Event",
    description: "Schedule new event",
    href: "/events/new",
    icon: Calendar,
    iconColor: "text-purple-600",
    iconBgColor: "bg-purple-100",
  },
  {
    id: "record-attendance",
    label: "Record Attendance",
    description: "Mark attendance",
    href: "/attendance",
    icon: CheckCircle,
    iconColor: "text-green-600",
    iconBgColor: "bg-green-100",
  },
  {
    id: "record-payment",
    label: "Record Payment",
    description: "Log payment received",
    href: "/finance/payments/new",
    icon: DollarSign,
    iconColor: "text-emerald-600",
    iconBgColor: "bg-emerald-100",
  },
  {
    id: "view-analytics",
    label: "View Analytics",
    description: "Detailed insights",
    href: "/analytics",
    icon: BarChart3,
    iconColor: "text-orange-600",
    iconBgColor: "bg-orange-100",
  },
  {
    id: "manage-branches",
    label: "Manage Branches",
    description: "Branch settings",
    href: "/branches",
    icon: Building,
    iconColor: "text-indigo-600",
    iconBgColor: "bg-indigo-100",
  },
]

interface QuickActionsGridProps {
  actions?: QuickAction[]
  className?: string
}

export function QuickActionsGrid({ actions = defaultActions, className }: QuickActionsGridProps) {
  return (
    <div className={cn("grid grid-cols-2 md:grid-cols-3 gap-4", className)}>
      {actions.map((action) => {
        const Icon = action.icon
        return (
          <Link key={action.id} href={action.href}>
            <Card className="transition-all hover:shadow-md hover:scale-[1.02] cursor-pointer">
              <CardContent className="p-4">
                <div className="flex flex-col items-center text-center space-y-2">
                  <div className={cn(
                    "flex items-center justify-center h-12 w-12 rounded-lg",
                    action.iconBgColor
                  )}>
                    <Icon className={cn("h-6 w-6", action.iconColor)} />
                  </div>
                  <div>
                    <p className="font-semibold text-sm">{action.label}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {action.description}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        )
      })}
    </div>
  )
}

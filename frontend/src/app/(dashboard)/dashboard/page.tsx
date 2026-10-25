"use client"

import * as React from "react"
import { useCurrentUser } from "@/features/auth/hooks/useAuth"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { Users, Calendar, UserCheck, DollarSign } from "lucide-react"

type ChangeType = "positive" | "negative" | "neutral"

interface Stat {
  label: string
  value: string
  icon: React.ComponentType<{ className?: string }>
  change: string
  changeType: ChangeType
}

const stats: Stat[] = [
  {
    label: "Total Youth",
    value: "1,234",
    icon: Users,
    change: "+12% from last month",
    changeType: "positive",
  },
  {
    label: "Upcoming Events",
    value: "8",
    icon: Calendar,
    change: "3 this week",
    changeType: "neutral",
  },
  {
    label: "Attendance Rate",
    value: "87%",
    icon: UserCheck,
    change: "+5% from last month",
    changeType: "positive",
  },
  {
    label: "Monthly Donations",
    value: "$12,450",
    icon: DollarSign,
    change: "+8% from last month",
    changeType: "positive",
  },
]

export default function DashboardPage() {
  const { data: currentUser } = useCurrentUser()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          Welcome back, {currentUser?.name?.split(" ")[0] || "User"}!
        </h1>
        <p className="text-muted-foreground mt-2">
          Here's what's happening with your youth ministry today.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.label}>
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p
                  className={`text-xs mt-1 ${
                    stat.changeType === "positive"
                      ? "text-green-600"
                      : stat.changeType === "negative"
                      ? "text-red-600"
                      : "text-muted-foreground"
                  }`}
                >
                  {stat.change}
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                No recent activity to display
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <button className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-gray-100 transition-colors">
                Add New Youth
              </button>
              <button className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-gray-100 transition-colors">
                Create Event
              </button>
              <button className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-gray-100 transition-colors">
                Record Attendance
              </button>
              <button className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-gray-100 transition-colors">
                View Analytics
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

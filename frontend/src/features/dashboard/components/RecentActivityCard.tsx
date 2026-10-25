import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { UserPlus, Calendar, DollarSign, CheckCircle, Building, Folder } from "lucide-react"
import type { RecentActivity, ActivityType } from "../types/dashboard.types"

const activityIcons: Record<ActivityType, React.ComponentType<{ className?: string }>> = {
  youth_registered: UserPlus,
  event_created: Calendar,
  payment_received: DollarSign,
  attendance_recorded: CheckCircle,
  branch_created: Building,
  department_created: Folder,
}

const activityColors: Record<ActivityType, string> = {
  youth_registered: "text-blue-600 bg-blue-100",
  event_created: "text-purple-600 bg-purple-100",
  payment_received: "text-green-600 bg-green-100",
  attendance_recorded: "text-orange-600 bg-orange-100",
  branch_created: "text-indigo-600 bg-indigo-100",
  department_created: "text-pink-600 bg-pink-100",
}

interface RecentActivityCardProps {
  activities: RecentActivity[]
  loading?: boolean
  className?: string
}

export function RecentActivityCard({ activities, loading, className }: RecentActivityCardProps) {
  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="h-10 w-10 rounded-full bg-gray-200 animate-pulse" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-3/4 bg-gray-200 rounded animate-pulse" />
                  <div className="h-3 w-1/4 bg-gray-200 rounded animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (activities.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            No recent activity to display
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => {
            const Icon = activityIcons[activity.type]
            const colorClass = activityColors[activity.type]
            const timeAgo = new Date(activity.timestamp).toLocaleString()

            return (
              <div key={activity.id} className="flex items-start gap-3">
                <div className={`flex items-center justify-center h-10 w-10 rounded-full ${colorClass}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">
                    {activity.message}
                  </p>
                  {activity.userName && (
                    <p className="text-xs text-muted-foreground">
                      by {activity.userName}
                    </p>
                  )}
                  <p className="text-xs text-muted-foreground mt-1">
                    {timeAgo}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

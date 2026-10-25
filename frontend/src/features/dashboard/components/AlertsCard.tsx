import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card"
import { AlertCircle, AlertTriangle, Info, CheckCircle, X } from "lucide-react"
import Link from "next/link"
import { cn } from "@/shared/lib/utils"
import type { SystemAlert, AlertSeverity } from "../types/dashboard.types"

const alertIcons: Record<AlertSeverity, React.ComponentType<{ className?: string }>> = {
  info: Info,
  warning: AlertTriangle,
  error: AlertCircle,
  success: CheckCircle,
}

const alertColors: Record<AlertSeverity, { bg: string; border: string; text: string; icon: string }> = {
  info: {
    bg: "bg-blue-50",
    border: "border-blue-200",
    text: "text-blue-900",
    icon: "text-blue-600",
  },
  warning: {
    bg: "bg-yellow-50",
    border: "border-yellow-200",
    text: "text-yellow-900",
    icon: "text-yellow-600",
  },
  error: {
    bg: "bg-red-50",
    border: "border-red-200",
    text: "text-red-900",
    icon: "text-red-600",
  },
  success: {
    bg: "bg-green-50",
    border: "border-green-200",
    text: "text-green-900",
    icon: "text-green-600",
  },
}

interface AlertsCardProps {
  alerts: SystemAlert[]
  loading?: boolean
  className?: string
  onDismiss?: (alertId: string) => void
}

export function AlertsCard({ alerts, loading, className, onDismiss }: AlertsCardProps) {
  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>System Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-3 border rounded-lg">
                <div className="h-4 w-3/4 bg-gray-200 rounded animate-pulse mb-2" />
                <div className="h-3 w-full bg-gray-200 rounded animate-pulse" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const activeAlerts = alerts.filter(a => !a.dismissed)

  if (activeAlerts.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>System Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <CheckCircle className="h-12 w-12 mx-auto mb-2 text-green-500" />
            <p>All systems operational</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>System Alerts</span>
          {activeAlerts.length > 0 && (
            <span className="text-xs font-normal text-muted-foreground">
              {activeAlerts.length} active
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {activeAlerts.map((alert) => {
            const Icon = alertIcons[alert.severity]
            const colors = alertColors[alert.severity]

            return (
              <div
                key={alert.id}
                className={cn(
                  "p-3 border rounded-lg relative",
                  colors.bg,
                  colors.border
                )}
              >
                {onDismiss && (
                  <button
                    onClick={() => onDismiss(alert.id)}
                    className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
                    aria-label="Dismiss alert"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
                <div className="flex gap-3">
                  <Icon className={cn("h-5 w-5 flex-shrink-0 mt-0.5", colors.icon)} />
                  <div className="flex-1 min-w-0">
                    <h4 className={cn("text-sm font-semibold", colors.text)}>
                      {alert.title}
                    </h4>
                    <p className={cn("text-sm mt-1", colors.text)}>
                      {alert.message}
                    </p>
                    {alert.actionUrl && alert.actionLabel && (
                      <Link
                        href={alert.actionUrl}
                        className={cn(
                          "text-sm font-medium underline mt-2 inline-block",
                          colors.text
                        )}
                      >
                        {alert.actionLabel} →
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

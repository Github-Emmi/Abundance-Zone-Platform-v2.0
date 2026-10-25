import * as React from "react"
import { ArrowUp, ArrowDown, Minus } from "lucide-react"
import { cn } from "@/shared/lib/utils"

interface TrendIndicatorProps {
  value: number
  isPositive: boolean
  period?: string
  className?: string
  showIcon?: boolean
}

export function TrendIndicator({
  value,
  isPositive,
  period,
  className,
  showIcon = true,
}: TrendIndicatorProps) {
  const isNeutral = value === 0

  return (
    <div className={cn("flex items-center gap-1", className)}>
      {showIcon && (
        <span className={cn(
          "flex items-center justify-center",
          isNeutral ? "text-gray-500" : isPositive ? "text-green-600" : "text-red-600"
        )}>
          {isNeutral ? (
            <Minus className="h-3 w-3" />
          ) : isPositive ? (
            <ArrowUp className="h-3 w-3" />
          ) : (
            <ArrowDown className="h-3 w-3" />
          )}
        </span>
      )}
      <span className={cn(
        "text-sm font-medium",
        isNeutral ? "text-gray-500" : isPositive ? "text-green-600" : "text-red-600"
      )}>
        {Math.abs(value).toFixed(1)}%
      </span>
      {period && (
        <span className="text-sm text-muted-foreground">
          {period}
        </span>
      )}
    </div>
  )
}

/**
 * Event Participation Chart Component
 * 
 * Pie chart showing event participation breakdown
 * Displays participation by event type or category
 */

import * as React from "react"
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
} from "recharts"
import type { ChartDataPoint } from "../types/dashboard.types"

interface EventParticipationChartProps {
  data: ChartDataPoint[]
  height?: number
}

// Color palette for pie segments
const COLORS = [
  '#10b981', // green
  '#3b82f6', // blue
  '#8b5cf6', // purple
  '#f59e0b', // amber
  '#ef4444', // red
  '#06b6d4', // cyan
  '#ec4899', // pink
  '#84cc16', // lime
]

const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    const data = payload[0]
    return (
      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-semibold text-sm">{data.name}</p>
        <p className="text-sm" style={{ color: data.payload.fill }}>
          Participants: {data.value?.toLocaleString()}
        </p>
        <p className="text-sm text-gray-600">
          {data.payload.percentage?.toFixed(1)}%
        </p>
      </div>
    )
  }
  return null
}

const renderCustomLabel = (entry: any) => {
  const { cx, cy, midAngle, innerRadius, outerRadius, percentage } = entry
  const RADIAN = Math.PI / 180
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)

  if (percentage < 5) return null // Don't show label if slice is too small

  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor={x > cx ? 'start' : 'end'}
      dominantBaseline="central"
      fontSize={12}
      fontWeight="bold"
    >
      {`${percentage.toFixed(0)}%`}
    </text>
  )
}

export function EventParticipationChart({ data, height = 300 }: EventParticipationChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-muted-foreground">
        No participation data available
      </div>
    )
  }

  // Calculate percentages
  const total = data.reduce((sum, item) => sum + item.value, 0)
  const dataWithPercentage = data.map(item => ({
    ...item,
    percentage: (item.value / total) * 100,
  }))

  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={dataWithPercentage}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={renderCustomLabel}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
          nameKey="label"
        >
          {dataWithPercentage.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend
          verticalAlign="bottom"
          height={36}
          wrapperStyle={{ fontSize: '12px' }}
          iconType="circle"
        />
      </PieChart>
    </ResponsiveContainer>
  )
}

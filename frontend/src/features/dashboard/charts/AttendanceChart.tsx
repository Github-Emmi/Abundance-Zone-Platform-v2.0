/**
 * Attendance Chart Component
 * 
 * Bar chart showing attendance trends over time
 * Displays attendance rate, total attendees, and total events
 */

import * as React from "react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
} from "recharts"
import type { AttendanceTrendsData } from "../types/dashboard.types"

interface AttendanceChartProps {
  data: AttendanceTrendsData[]
  height?: number
}

const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-semibold text-sm mb-2">{label}</p>
        {payload.map((entry, index) => {
          const value = entry.dataKey === 'attendanceRate' 
            ? `${entry.value}%` 
            : entry.value?.toLocaleString()
          return (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {value}
            </p>
          )
        })}
      </div>
    )
  }
  return null
}

export function AttendanceChart({ data, height = 300 }: AttendanceChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-muted-foreground">
        No attendance data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="date"
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
        />
        <YAxis
          yAxisId="left"
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
          tickFormatter={(value) => value.toLocaleString()}
          label={{ value: 'Count', angle: -90, position: 'insideLeft', style: { fontSize: '12px' } }}
        />
        <YAxis
          yAxisId="right"
          orientation="right"
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
          tickFormatter={(value) => `${value}%`}
          label={{ value: 'Rate (%)', angle: 90, position: 'insideRight', style: { fontSize: '12px' } }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: '12px' }}
          iconType="rect"
        />
        <Bar
          yAxisId="left"
          dataKey="totalAttendees"
          fill="#10b981"
          name="Total Attendees"
          radius={[4, 4, 0, 0]}
        />
        <Bar
          yAxisId="left"
          dataKey="totalEvents"
          fill="#3b82f6"
          name="Total Events"
          radius={[4, 4, 0, 0]}
        />
        <Bar
          yAxisId="right"
          dataKey="attendanceRate"
          fill="#8b5cf6"
          name="Attendance Rate"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}

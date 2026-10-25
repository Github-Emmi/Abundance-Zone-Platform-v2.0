/**
 * Attendance Trends Hook
 * 
 * Wrapper hook for attendance trends with:
 * - Data transformation
 * - Average calculations
 * - Period filtering
 */

import { useState } from 'react';
import { useAttendanceTrends as useQueryAttendanceTrends } from '../api/dashboard-queries';
import type { AttendanceTrendsData } from '../types/dashboard.types';

interface UseAttendanceTrendsReturn {
  data: AttendanceTrendsData[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  isEmpty: boolean;
  days: number;
  setDays: (days: number) => void;
  averageRate: number;
  totalAttendees: number;
  totalEvents: number;
  refetch: () => void;
}

/**
 * Fetch attendance trends for charts
 * Calculates aggregate metrics automatically
 * 
 * @param initialDays - Initial number of days to fetch (default: 30)
 * 
 * @example
 * const { data, averageRate, totalAttendees } = useAttendanceTrends(30);
 * 
 * return (
 *   <>
 *     <p>Average Attendance: {averageRate}%</p>
 *     <AttendanceChart data={data} />
 *   </>
 * );
 */
export const useAttendanceTrends = (initialDays: number = 30): UseAttendanceTrendsReturn => {
  const [days, setDays] = useState(initialDays);

  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
  } = useQueryAttendanceTrends(days);

  // Calculate aggregate metrics
  const aggregates = data?.reduce(
    (acc, item) => ({
      totalRate: acc.totalRate + item.attendanceRate,
      totalAttendees: acc.totalAttendees + item.totalAttendees,
      totalEvents: acc.totalEvents + item.totalEvents,
      count: acc.count + 1,
    }),
    { totalRate: 0, totalAttendees: 0, totalEvents: 0, count: 0 }
  );

  const averageRate = aggregates && aggregates.count > 0
    ? Math.round((aggregates.totalRate / aggregates.count) * 10) / 10
    : 0;

  return {
    data: data ?? [],
    isLoading,
    isError,
    error: error as Error | null,
    isEmpty: !data || data.length === 0,
    days,
    setDays,
    averageRate,
    totalAttendees: aggregates?.totalAttendees ?? 0,
    totalEvents: aggregates?.totalEvents ?? 0,
    refetch,
  };
};

/**
 * Get attendance status (good/warning/critical)
 * Based on average attendance rate
 * 
 * @example
 * const { status, statusColor, statusLabel } = useAttendanceStatus();
 */
export const useAttendanceStatus = (days: number = 30) => {
  const { averageRate } = useAttendanceTrends(days);

  let status: 'good' | 'warning' | 'critical';
  let statusColor: string;
  let statusLabel: string;

  if (averageRate >= 80) {
    status = 'good';
    statusColor = 'text-green-600';
    statusLabel = 'Excellent Attendance';
  } else if (averageRate >= 60) {
    status = 'warning';
    statusColor = 'text-yellow-600';
    statusLabel = 'Moderate Attendance';
  } else {
    status = 'critical';
    statusColor = 'text-red-600';
    statusLabel = 'Low Attendance';
  }

  return {
    status,
    statusColor,
    statusLabel,
    averageRate,
  };
};

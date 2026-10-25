/**
 * Dashboard Stats Hook
 * 
 * Wrapper hook for dashboard statistics with:
 * - Error handling
 * - Loading states
 * - Data transformation
 * - Cache management
 */

import { useDashboardStats as useQueryStats } from '../api/dashboard-queries';
import type { DashboardStats } from '../types/dashboard.types';

interface UseDashboardStatsReturn {
  stats: DashboardStats | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  isRefetching: boolean;
  refetch: () => void;
}

/**
 * Fetch and manage dashboard statistics
 * Auto-refreshes every 60 seconds
 * 
 * @example
 * const { stats, isLoading, error, refetch } = useDashboardStats();
 * 
 * if (isLoading) return <Skeleton />;
 * if (error) return <Error message={error.message} />;
 * 
 * return <StatsGrid stats={stats} />;
 */
export const useDashboardStats = (): UseDashboardStatsReturn => {
  const {
    data: stats,
    isLoading,
    isError,
    error,
    isRefetching,
    refetch,
  } = useQueryStats();

  return {
    stats,
    isLoading,
    isError,
    error: error as Error | null,
    isRefetching,
    refetch,
  };
};

/**
 * Get individual stat values with defaults
 * Useful for displaying stats in separate components
 * 
 * @example
 * const { totalYouths, activeEvents } = useIndividualStats();
 */
export const useIndividualStats = () => {
  const { stats } = useDashboardStats();

  return {
    totalYouths: stats?.totalYouths ?? 0,
    activeEvents: stats?.activeEvents ?? 0,
    attendanceRate: stats?.attendanceRate ?? 0,
    totalRevenue: stats?.totalRevenue ?? 0,
    totalBranches: stats?.totalBranches ?? 0,
    totalDepartments: stats?.totalDepartments ?? 0,
    trends: stats?.trends ?? {
      youths: { value: 0, change: 0, isPositive: false, period: 'vs last month' },
      revenue: { value: 0, change: 0, isPositive: false, period: 'vs last month' },
      attendance: { value: 0, change: 0, isPositive: false, period: 'vs last month' },
    },
  };
};

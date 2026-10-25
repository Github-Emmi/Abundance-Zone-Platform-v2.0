/**
 * Dashboard Refresh Interval Hook
 * 
 * Custom hook for auto-refreshing dashboard data
 * Manages refresh intervals and manual refresh triggers
 */

import { useEffect, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { dashboardKeys } from '../api/dashboard-queries';
import { toast } from 'sonner';

interface UseRefreshIntervalOptions {
  intervalMs?: number;
  enabled?: boolean;
  onRefresh?: () => void;
}

/**
 * Auto-refresh dashboard data at specified intervals
 * Provides manual refresh trigger
 * 
 * @param options.intervalMs - Refresh interval in milliseconds (default: 60000 = 1 minute)
 * @param options.enabled - Whether auto-refresh is enabled (default: true)
 * @param options.onRefresh - Callback function called after each refresh
 * 
 * @example
 * const { refresh, isRefreshing, lastRefresh } = useRefreshInterval({
 *   intervalMs: 60000,
 *   enabled: true,
 *   onRefresh: () => console.log('Dashboard refreshed'),
 * });
 * 
 * return <Button onClick={refresh}>Refresh Now</Button>;
 */
export const useRefreshInterval = (options: UseRefreshIntervalOptions = {}) => {
  const {
    intervalMs = 60000, // 1 minute default
    enabled = true,
    onRefresh,
  } = options;

  const queryClient = useQueryClient();

  /**
   * Manual refresh function
   * Invalidates all dashboard queries
   */
  const refresh = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: dashboardKeys.all });
    onRefresh?.();
    toast.success('Dashboard refreshed');
  }, [queryClient, onRefresh]);

  /**
   * Auto-refresh effect
   */
  useEffect(() => {
    if (!enabled) return;

    const interval = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: dashboardKeys.all });
      onRefresh?.();
    }, intervalMs);

    return () => clearInterval(interval);
  }, [enabled, intervalMs, queryClient, onRefresh]);

  return {
    refresh,
    intervalMs,
  };
};

/**
 * Refresh specific dashboard section
 * For granular refresh control
 * 
 * @example
 * const refreshStats = useRefreshSection('stats');
 * const refreshCharts = useRefreshSection('charts');
 */
export const useRefreshSection = (section: 'stats' | 'charts' | 'activity' | 'alerts') => {
  const queryClient = useQueryClient();

  const refresh = useCallback(() => {
    switch (section) {
      case 'stats':
        queryClient.invalidateQueries({ queryKey: dashboardKeys.stats() });
        break;
      case 'charts':
        queryClient.invalidateQueries({ queryKey: dashboardKeys.youthGrowth(6) });
        queryClient.invalidateQueries({ queryKey: dashboardKeys.attendanceTrends(30) });
        queryClient.invalidateQueries({ queryKey: dashboardKeys.revenueSummary(12) });
        break;
      case 'activity':
        queryClient.invalidateQueries({ queryKey: dashboardKeys.recentActivity(10) });
        break;
      case 'alerts':
        queryClient.invalidateQueries({ queryKey: dashboardKeys.systemAlerts() });
        break;
    }
    toast.success(`${section.charAt(0).toUpperCase() + section.slice(1)} refreshed`);
  }, [section, queryClient]);

  return refresh;
};

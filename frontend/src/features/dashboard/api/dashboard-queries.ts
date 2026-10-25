/**
 * Dashboard TanStack Query Hooks
 * 
 * React Query hooks for dashboard data fetching with:
 * - Auto-refresh every 60 seconds
 * - Optimistic updates
 * - Cache management
 * - Error handling
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { dashboardApi } from './dashboard-api';
import { toast } from 'sonner';
import type { ExportReportParams } from '../types/dashboard.types';

/**
 * Query keys factory for dashboard
 * Ensures consistent cache key structure
 */
export const dashboardKeys = {
  all: ['dashboard'] as const,
  stats: () => [...dashboardKeys.all, 'stats'] as const,
  youthGrowth: (months: number) => [...dashboardKeys.all, 'youth-growth', months] as const,
  attendanceTrends: (days: number) => [...dashboardKeys.all, 'attendance-trends', days] as const,
  revenueSummary: (months: number) => [...dashboardKeys.all, 'revenue-summary', months] as const,
  recentActivity: (limit: number) => [...dashboardKeys.all, 'recent-activity', limit] as const,
  systemAlerts: () => [...dashboardKeys.all, 'system-alerts'] as const,
  branchComparison: () => [...dashboardKeys.all, 'branch-comparison'] as const,
  reportStatus: (taskId: string) => [...dashboardKeys.all, 'report-status', taskId] as const,
};

/**
 * Fetch dashboard statistics
 * Auto-refreshes every 60 seconds
 */
export const useDashboardStats = () => {
  return useQuery({
    queryKey: dashboardKeys.stats(),
    queryFn: dashboardApi.getStats,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 60 * 1000, // Auto-refresh every minute
    refetchOnWindowFocus: true,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

/**
 * Fetch youth growth data for chart
 */
export const useYouthGrowth = (months: number = 6) => {
  return useQuery({
    queryKey: dashboardKeys.youthGrowth(months),
    queryFn: () => dashboardApi.getYouthGrowth(months),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
};

/**
 * Fetch attendance trends
 */
export const useAttendanceTrends = (days: number = 30) => {
  return useQuery({
    queryKey: dashboardKeys.attendanceTrends(days),
    queryFn: () => dashboardApi.getAttendanceTrends(days),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
};

/**
 * Fetch revenue summary
 */
export const useRevenueSummary = (months: number = 12) => {
  return useQuery({
    queryKey: dashboardKeys.revenueSummary(months),
    queryFn: () => dashboardApi.getRevenueSummary(months),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
};

/**
 * Fetch recent activity
 */
export const useRecentActivity = (limit: number = 10) => {
  return useQuery({
    queryKey: dashboardKeys.recentActivity(limit),
    queryFn: () => dashboardApi.getRecentActivity(limit),
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 2 * 60 * 1000, // Refresh every 2 minutes
  });
};

/**
 * Fetch system alerts
 */
export const useSystemAlerts = () => {
  return useQuery({
    queryKey: dashboardKeys.systemAlerts(),
    queryFn: dashboardApi.getSystemAlerts,
    staleTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 1 * 60 * 1000, // Refresh every minute
  });
};

/**
 * Fetch branch comparison data
 */
export const useBranchComparison = () => {
  return useQuery({
    queryKey: dashboardKeys.branchComparison(),
    queryFn: dashboardApi.getBranchComparison,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Export report mutation
 */
export const useExportReport = () => {
  return useMutation({
    mutationFn: (params: ExportReportParams) => dashboardApi.exportReport(params),
    onSuccess: (blob, variables) => {
      // Download the file
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${variables.type}-report-${Date.now()}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success('Report exported successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to export report');
    },
  });
};

/**
 * Generate daily report mutation
 */
export const useGenerateDailyReport = () => {
  return useMutation({
    mutationFn: (date: string) => dashboardApi.generateDailyReport(date),
    onSuccess: (data) => {
      toast.success('Report generation started. You will be notified when ready.');
      return data.taskId;
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to generate report');
    },
  });
};

/**
 * Generate weekly report mutation
 */
export const useGenerateWeeklyReport = () => {
  return useMutation({
    mutationFn: ({ startDate, endDate }: { startDate: string; endDate: string }) => 
      dashboardApi.generateWeeklyReport(startDate, endDate),
    onSuccess: () => {
      toast.success('Weekly report generation started');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to generate weekly report');
    },
  });
};

/**
 * Generate monthly report mutation
 */
export const useGenerateMonthlyReport = () => {
  return useMutation({
    mutationFn: ({ month, year }: { month: number; year: number }) => 
      dashboardApi.generateMonthlyReport(month, year),
    onSuccess: () => {
      toast.success('Monthly report generation started');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to generate monthly report');
    },
  });
};

/**
 * Check report status
 * Polls every 3 seconds until complete
 */
export const useReportStatus = (taskId: string | null, enabled: boolean = false) => {
  return useQuery({
    queryKey: dashboardKeys.reportStatus(taskId || ''),
    queryFn: () => dashboardApi.getReportStatus(taskId!),
    enabled: enabled && !!taskId,
    refetchInterval: (query) => {
      // Stop polling if task is complete
      const data = query.state.data;
      if (data?.status === 'SUCCESS' || data?.status === 'FAILURE') {
        return false;
      }
      return 3000; // Poll every 3 seconds
    },
    retry: false,
  });
};

/**
 * Download report mutation
 */
export const useDownloadReport = () => {
  return useMutation({
    mutationFn: (taskId: string) => dashboardApi.downloadReport(taskId),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report-${Date.now()}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success('Report downloaded successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to download report');
    },
  });
};

/**
 * Refresh all dashboard data
 */
export const useRefreshDashboard = () => {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ queryKey: dashboardKeys.all });
    toast.success('Dashboard refreshed');
  };
};

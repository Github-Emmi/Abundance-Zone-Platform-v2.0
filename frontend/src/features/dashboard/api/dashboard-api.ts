/**
 * Dashboard API Client
 * 
 * Centralized API calls for Super Admin Dashboard
 * Integrates with multiple backend endpoints to fetch dashboard statistics
 */

import apiClient from '@/shared/api/client';
import type { 
  DashboardStats, 
  YouthGrowthData, 
  AttendanceTrendsData,
  RevenueSummaryData,
  RecentActivity,
  SystemAlert,
  BranchComparison,
  ExportReportParams
} from '../types/dashboard.types';

/**
 * Dashboard API namespace
 */
export const dashboardApi = {
  /**
   * Get comprehensive dashboard statistics
   * Fetches data from multiple endpoints in parallel
   */
  getStats: async (): Promise<DashboardStats> => {
    try {
      // Parallel requests for better performance
      const [
        youthsRes,
        eventsRes,
        attendanceRes,
        branchesRes,
        departmentsRes,
        analyticsRes
      ] = await Promise.allSettled([
        apiClient.get('youths?page=1&page_size=1'), // Just for count
        apiClient.get('events?status=SCHEDULED&page=1&page_size=1'),
        apiClient.get('attendance/stats'),
        apiClient.get('branches?page=1&page_size=1'),
        apiClient.get('departments?page=1&page_size=1'),
        apiClient.get('analytics/summary')
      ]);

      // Extract data safely
      const totalYouths = youthsRes.status === 'fulfilled' ? youthsRes.value.data.total : 0;
      const activeEvents = eventsRes.status === 'fulfilled' ? eventsRes.value.data.total : 0;
      const attendanceRate = attendanceRes.status === 'fulfilled' ? attendanceRes.value.data.rate : 0;
      const totalBranches = branchesRes.status === 'fulfilled' ? branchesRes.value.data.total : 0;
      const totalDepartments = departmentsRes.status === 'fulfilled' ? departmentsRes.value.data.total : 0;
      const analytics = analyticsRes.status === 'fulfilled' ? analyticsRes.value.data : null;

      return {
        totalYouths,
        activeEvents,
        attendanceRate,
        totalRevenue: analytics?.totalRevenue || 0,
        totalBranches,
        totalDepartments,
        trends: {
          youths: {
            value: totalYouths,
            change: analytics?.youthGrowthPercent || 0,
            isPositive: (analytics?.youthGrowthPercent || 0) >= 0,
            period: 'vs last month'
          },
          revenue: {
            value: analytics?.totalRevenue || 0,
            change: analytics?.revenueGrowthPercent || 0,
            isPositive: (analytics?.revenueGrowthPercent || 0) >= 0,
            period: 'vs last month'
          },
          attendance: {
            value: attendanceRate,
            change: analytics?.attendanceChangePercent || 0,
            isPositive: (analytics?.attendanceChangePercent || 0) >= 0,
            period: 'vs last month'
          }
        }
      };
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
      throw error;
    }
  },

  /**
   * Get youth growth data for chart
   * @param months - Number of months to fetch (default: 6)
   */
  getYouthGrowth: async (months: number = 6): Promise<YouthGrowthData[]> => {
    const response = await apiClient.get('analytics/youth-growth', {
      params: { months }
    });
    return response.data;
  },

  /**
   * Get attendance trends data
   * @param days - Number of days to fetch (default: 30)
   */
  getAttendanceTrends: async (days: number = 30): Promise<AttendanceTrendsData[]> => {
    const response = await apiClient.get('analytics/attendance-trends', {
      params: { days }
    });
    return response.data;
  },

  /**
   * Get revenue summary data
   * @param months - Number of months (default: 12)
   */
  getRevenueSummary: async (months: number = 12): Promise<RevenueSummaryData> => {
    const response = await apiClient.get('analytics/revenue-summary', {
      params: { months }
    });
    return response.data;
  },

  /**
   * Get recent activities
   * @param limit - Number of activities to fetch
   */
  getRecentActivity: async (limit: number = 10): Promise<RecentActivity[]> => {
    const response = await apiClient.get('analytics/recent-activity', {
      params: { limit }
    });
    return response.data;
  },

  /**
   * Get system alerts
   */
  getSystemAlerts: async (): Promise<SystemAlert[]> => {
    const response = await apiClient.get('analytics/alerts');
    return response.data;
  },

  /**
   * Get branch comparison data
   */
  getBranchComparison: async (): Promise<BranchComparison[]> => {
    const response = await apiClient.get('analytics/branch-comparison');
    return response.data;
  },

  /**
   * Export report
   * @param params - Export parameters
   * @returns Blob for download
   */
  exportReport: async (params: ExportReportParams): Promise<Blob> => {
    const response = await apiClient.post(
      'analytics/export',
      params,
      {
        responseType: 'blob',
        headers: {
          'Accept': 'text/csv'
        }
      }
    );
    return response.data;
  },

  /**
   * Generate daily attendance report
   */
  generateDailyReport: async (date: string): Promise<{ taskId: string }> => {
    const response = await apiClient.post('analytics/reports/daily', {
      date
    });
    return response.data;
  },

  /**
   * Generate weekly analytics report
   */
  generateWeeklyReport: async (startDate: string, endDate: string): Promise<{ taskId: string }> => {
    const response = await apiClient.post('analytics/reports/weekly', {
      start_date: startDate,
      end_date: endDate
    });
    return response.data;
  },

  /**
   * Generate monthly financial report
   */
  generateMonthlyReport: async (month: number, year: number): Promise<{ taskId: string }> => {
    const response = await apiClient.post('analytics/reports/monthly', {
      month,
      year
    });
    return response.data;
  },

  /**
   * Download report by task ID
   */
  downloadReport: async (taskId: string): Promise<Blob> => {
    const response = await apiClient.get(
      `analytics/reports/${taskId}/download`,
      {
        responseType: 'blob'
      }
    );
    return response.data;
  },

  /**
   * Check report generation status
   */
  getReportStatus: async (taskId: string): Promise<{
    status: 'PENDING' | 'SUCCESS' | 'FAILURE';
    result?: any;
  }> => {
    const response = await apiClient.get(`tasks/${taskId}`);
    return response.data;
  }
};

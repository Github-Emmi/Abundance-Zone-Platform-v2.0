/**
 * Dashboard Type Definitions
 * 
 * Type-safe interfaces for Super Admin Dashboard
 */

/**
 * Trend data for KPI cards
 */
export interface TrendData {
  value: number;
  change: number;
  isPositive: boolean;
  period: string;
}

/**
 * Main dashboard statistics
 */
export interface DashboardStats {
  totalYouths: number;
  activeEvents: number;
  attendanceRate: number;
  totalRevenue: number;
  totalBranches: number;
  totalDepartments: number;
  trends: {
    youths: TrendData;
    revenue: TrendData;
    attendance: TrendData;
  };
}

/**
 * Youth growth data point
 */
export interface YouthGrowthData {
  month: string;
  count: number;
  newRegistrations: number;
  activeMembers: number;
}

/**
 * Attendance trends data point
 */
export interface AttendanceTrendsData {
  date: string;
  attendanceRate: number;
  totalAttendees: number;
  totalEvents: number;
}

/**
 * Revenue summary data
 */
export interface RevenueSummaryData {
  totalRevenue: number;
  pledgesFulfilled: number;
  outstandingPayments: number;
  monthlyBreakdown: {
    month: string;
    revenue: number;
    pledges: number;
    payments: number;
  }[];
}

/**
 * Recent activity types
 */
export type ActivityType = 
  | 'youth_registered'
  | 'event_created'
  | 'payment_received'
  | 'attendance_recorded'
  | 'branch_created'
  | 'department_created';

/**
 * Recent activity item
 */
export interface RecentActivity {
  id: string;
  type: ActivityType;
  message: string;
  timestamp: string;
  userId?: string;
  userName?: string;
  metadata?: Record<string, any>;
}

/**
 * System alert severity
 */
export type AlertSeverity = 'info' | 'warning' | 'error' | 'success';

/**
 * System alert
 */
export interface SystemAlert {
  id: string;
  severity: AlertSeverity;
  title: string;
  message: string;
  timestamp: string;
  actionUrl?: string;
  actionLabel?: string;
  dismissed: boolean;
}

/**
 * Branch comparison data
 */
export interface BranchComparison {
  branchId: string;
  branchName: string;
  totalYouths: number;
  attendanceRate: number;
  totalRevenue: number;
  activeEvents: number;
  rank: number;
}

/**
 * Export report types
 */
export type ReportType = 
  | 'daily_attendance'
  | 'weekly_analytics'
  | 'monthly_financial'
  | 'youth_directory'
  | 'event_summary'
  | 'financial_summary';

/**
 * Export report parameters
 */
export interface ExportReportParams {
  type: ReportType;
  startDate?: string;
  endDate?: string;
  branchId?: string;
  format?: 'csv' | 'pdf' | 'xlsx';
}

/**
 * Chart data point (generic)
 */
export interface ChartDataPoint {
  label: string;
  value: number;
  [key: string]: any;
}

/**
 * Chart dataset
 */
export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string;
  fill?: boolean;
}

/**
 * Chart configuration
 */
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

/**
 * Date range filter
 */
export interface DateRangeFilter {
  startDate: string;
  endDate: string;
  preset?: 'today' | 'week' | 'month' | '3months' | '6months' | 'year' | 'custom';
}

/**
 * Dashboard filters
 */
export interface DashboardFilters {
  dateRange: DateRangeFilter;
  branchId?: string;
  departmentId?: string;
}

/**
 * Quick action item
 */
export interface QuickAction {
  id: string;
  label: string;
  icon: string;
  href: string;
  description?: string;
  badge?: number;
}

/**
 * Widget visibility preferences
 */
export interface DashboardPreferences {
  showYouthGrowthChart: boolean;
  showRevenueChart: boolean;
  showAttendanceChart: boolean;
  showEventParticipation: boolean;
  showRecentActivity: boolean;
  showSystemAlerts: boolean;
  showBranchComparison: boolean;
  refreshInterval: number; // in seconds
  defaultDateRange: DateRangeFilter['preset'];
}

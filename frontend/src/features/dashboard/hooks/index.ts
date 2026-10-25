/**
 * Dashboard Hooks - Barrel Export
 * 
 * Centralized export for all dashboard hooks
 */

export {
  useDashboardStats,
  useIndividualStats,
} from './useDashboardStats';

export {
  useYouthGrowth,
  useYouthGrowthMetrics,
} from './useYouthGrowth';

export {
  useAttendanceTrends,
  useAttendanceStatus,
} from './useAttendanceTrends';

export {
  useRevenueSummary,
  useRevenueHealth,
} from './useRevenueSummary';

export {
  useRecentActivity,
  useActivityByType,
} from './useRecentActivity';

export {
  useSystemAlerts,
  useAlertsBySeverity,
  usePriorityAlerts,
} from './useSystemAlerts';

export {
  useRefreshInterval,
  useRefreshSection,
} from './useRefreshInterval';

export { 
  useProgressiveLoading, 
  useFadeIn 
} from './useProgressiveLoading';

// Export useDashboardPreferences from component file
export { useDashboardPreferences } from '../components/DashboardPreferences';

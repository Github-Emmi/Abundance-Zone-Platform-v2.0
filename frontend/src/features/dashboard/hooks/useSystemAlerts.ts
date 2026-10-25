/**
 * System Alerts Hook
 * 
 * Wrapper hook for system alerts with:
 * - Alert filtering by severity
 * - Dismissal management
 * - Count aggregates
 */

import { useSystemAlerts as useQuerySystemAlerts } from '../api/dashboard-queries';
import type { SystemAlert, AlertSeverity } from '../types/dashboard.types';

interface UseSystemAlertsReturn {
  alerts: SystemAlert[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  isEmpty: boolean;
  activeAlerts: SystemAlert[];
  alertsBySeverity: {
    info: SystemAlert[];
    warning: SystemAlert[];
    error: SystemAlert[];
    success: SystemAlert[];
  };
  counts: {
    total: number;
    active: number;
    dismissed: number;
    byType: Record<AlertSeverity, number>;
  };
  refetch: () => void;
}

/**
 * Fetch system alerts with filtering and aggregation
 * Provides counts and severity-based grouping
 * 
 * @example
 * const { alerts, activeAlerts, counts } = useSystemAlerts();
 * 
 * return (
 *   <>
 *     <Badge>{counts.active} Active Alerts</Badge>
 *     {alertsBySeverity.error.map(alert => (
 *       <Alert key={alert.id} variant="error">
 *         {alert.message}
 *       </Alert>
 *     ))}
 *   </>
 * );
 */
export const useSystemAlerts = (): UseSystemAlertsReturn => {
  const {
    data: alerts,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuerySystemAlerts();

  const allAlerts = alerts ?? [];

  // Filter active (non-dismissed) alerts
  const activeAlerts = allAlerts.filter(alert => !alert.dismissed);

  // Group alerts by severity
  const alertsBySeverity = {
    info: allAlerts.filter(alert => alert.severity === 'info' && !alert.dismissed),
    warning: allAlerts.filter(alert => alert.severity === 'warning' && !alert.dismissed),
    error: allAlerts.filter(alert => alert.severity === 'error' && !alert.dismissed),
    success: allAlerts.filter(alert => alert.severity === 'success' && !alert.dismissed),
  };

  // Calculate counts
  const counts = {
    total: allAlerts.length,
    active: activeAlerts.length,
    dismissed: allAlerts.filter(alert => alert.dismissed).length,
    byType: {
      info: alertsBySeverity.info.length,
      warning: alertsBySeverity.warning.length,
      error: alertsBySeverity.error.length,
      success: alertsBySeverity.success.length,
    },
  };

  return {
    alerts: allAlerts,
    isLoading,
    isError,
    error: error as Error | null,
    isEmpty: allAlerts.length === 0,
    activeAlerts,
    alertsBySeverity,
    counts,
    refetch,
  };
};

/**
 * Get alerts by severity level
 * Useful for severity-specific alert lists
 * 
 * @example
 * const criticalAlerts = useAlertsBySeverity('error');
 */
export const useAlertsBySeverity = (severity: AlertSeverity) => {
  const { alertsBySeverity, isLoading } = useSystemAlerts();

  return {
    alerts: alertsBySeverity[severity],
    count: alertsBySeverity[severity].length,
    isLoading,
  };
};

/**
 * Get priority alerts (error and warning only)
 * For displaying critical alerts prominently
 * 
 * @example
 * const { priorityAlerts, hasCritical } = usePriorityAlerts();
 */
export const usePriorityAlerts = () => {
  const { alertsBySeverity, isLoading } = useSystemAlerts();

  const priorityAlerts = [
    ...alertsBySeverity.error,
    ...alertsBySeverity.warning,
  ];

  return {
    priorityAlerts,
    hasCritical: alertsBySeverity.error.length > 0,
    hasWarnings: alertsBySeverity.warning.length > 0,
    count: priorityAlerts.length,
    isLoading,
  };
};

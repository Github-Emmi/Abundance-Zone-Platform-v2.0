/**
 * Recent Activity Hook
 * 
 * Wrapper hook for recent activity with:
 * - Activity formatting
 * - Icon mapping
 * - Time formatting (relative)
 */

import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { useRecentActivity as useQueryRecentActivity } from '../api/dashboard-queries';
import type { RecentActivity, ActivityType } from '../types/dashboard.types';
import {
  UserPlus,
  Calendar,
  DollarSign,
  CheckCircle,
  Building2,
  Users,
  type LucideIcon,
} from 'lucide-react';

interface UseRecentActivityReturn {
  activities: RecentActivity[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  isEmpty: boolean;
  limit: number;
  setLimit: (limit: number) => void;
  getActivityIcon: (type: ActivityType) => LucideIcon;
  getActivityColor: (type: ActivityType) => string;
  formatTime: (timestamp: string) => string;
  refetch: () => void;
}

/**
 * Fetch recent activity with formatting helpers
 * Provides icon and color mapping for activity types
 * 
 * @param initialLimit - Initial number of activities to fetch (default: 10)
 * 
 * @example
 * const { activities, getActivityIcon, formatTime } = useRecentActivity(10);
 * 
 * return activities.map(activity => {
 *   const Icon = getActivityIcon(activity.type);
 *   return (
 *     <div key={activity.id}>
 *       <Icon />
 *       <p>{activity.message}</p>
 *       <span>{formatTime(activity.timestamp)}</span>
 *     </div>
 *   );
 * });
 */
export const useRecentActivity = (initialLimit: number = 10): UseRecentActivityReturn => {
  const [limit, setLimit] = useState(initialLimit);

  const {
    data: activities,
    isLoading,
    isError,
    error,
    refetch,
  } = useQueryRecentActivity(limit);

  /**
   * Map activity type to Lucide icon
   */
  const getActivityIcon = (type: ActivityType): LucideIcon => {
    const iconMap: Record<ActivityType, LucideIcon> = {
      youth_registered: UserPlus,
      event_created: Calendar,
      payment_received: DollarSign,
      attendance_recorded: CheckCircle,
      branch_created: Building2,
      department_created: Users,
    };
    return iconMap[type] || UserPlus;
  };

  /**
   * Map activity type to color class
   */
  const getActivityColor = (type: ActivityType): string => {
    const colorMap: Record<ActivityType, string> = {
      youth_registered: 'text-blue-600 bg-blue-100',
      event_created: 'text-purple-600 bg-purple-100',
      payment_received: 'text-green-600 bg-green-100',
      attendance_recorded: 'text-emerald-600 bg-emerald-100',
      branch_created: 'text-orange-600 bg-orange-100',
      department_created: 'text-pink-600 bg-pink-100',
    };
    return colorMap[type] || 'text-gray-600 bg-gray-100';
  };

  /**
   * Format timestamp to relative time (e.g., "5 minutes ago")
   */
  const formatTime = (timestamp: string): string => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch {
      return 'recently';
    }
  };

  return {
    activities: activities ?? [],
    isLoading,
    isError,
    error: error as Error | null,
    isEmpty: !activities || activities.length === 0,
    limit,
    setLimit,
    getActivityIcon,
    getActivityColor,
    formatTime,
    refetch,
  };
};

/**
 * Filter activities by type
 * Useful for type-specific activity feeds
 * 
 * @example
 * const youthActivities = useActivityByType('youth_registered', 20);
 */
export const useActivityByType = (type: ActivityType, limit: number = 20) => {
  const { activities, isLoading } = useRecentActivity(limit);

  const filteredActivities = activities.filter(activity => activity.type === type);

  return {
    activities: filteredActivities,
    isLoading,
    count: filteredActivities.length,
  };
};

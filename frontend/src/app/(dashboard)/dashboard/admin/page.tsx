/**
 * Super Admin Dashboard Page - Performance Optimized
 * 
 * Features:
 * - Lazy loading for charts
 * - Code splitting for modals
 * - Memoization for expensive computations
 * - Progressive loading
 */

'use client';

import * as React from 'react';
import dynamic from 'next/dynamic';
import { RefreshCw, TrendingUp } from 'lucide-react';
import {
  useDashboardStats,
  useYouthGrowth,
  useAttendanceTrends,
  useRevenueSummary,
  useRecentActivity,
  useSystemAlerts,
  useRefreshInterval,
  useDashboardPreferences,
} from '@/features/dashboard/hooks';
import {
  ChartContainer,
  StatsGrid,
  DashboardErrorBoundary,
  DashboardPreferences,
} from '@/features/dashboard/components';
import { Button } from '@/shared/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card';
import { Skeleton } from '@/shared/ui/skeleton';

// Lazy load heavy components
const YouthGrowthChart = dynamic(
  () => import('@/features/dashboard/charts').then(mod => ({ default: mod.YouthGrowthChart })),
  { loading: () => <ChartSkeleton />, ssr: false }
);

const RevenueChart = dynamic(
  () => import('@/features/dashboard/charts').then(mod => ({ default: mod.RevenueChart })),
  { loading: () => <ChartSkeleton />, ssr: false }
);

const AttendanceChart = dynamic(
  () => import('@/features/dashboard/charts').then(mod => ({ default: mod.AttendanceChart })),
  { loading: () => <ChartSkeleton />, ssr: false }
);

const EventParticipationChart = dynamic(
  () => import('@/features/dashboard/charts').then(mod => ({ default: mod.EventParticipationChart })),
  { loading: () => <ChartSkeleton />, ssr: false }
);

const DateRangeFilter = dynamic(
  () => import('@/features/dashboard/components').then(mod => ({ default: mod.DateRangeFilter })),
  { loading: () => <Skeleton className="h-10 w-[200px]" /> }
);

const ExportMenu = dynamic(
  () => import('@/features/dashboard/components').then(mod => ({ default: mod.ExportMenu })),
  { loading: () => <Skeleton className="h-9 w-[100px]" /> }
);

const QuickActionsGrid = dynamic(
  () => import('@/features/dashboard/components').then(mod => ({ default: mod.QuickActionsGrid })),
  { loading: () => <Skeleton className="h-[200px] w-full" /> }
);

function ChartSkeleton() {
  return <div className="h-[300px] flex items-center justify-center">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
  </div>;
}

export default function SuperAdminDashboard() {
  const { preferences, updatePreferences } = useDashboardPreferences();
  const { stats, isLoading: statsLoading, refetch: refetchStats } = useDashboardStats();
  const { data: youthGrowthData, isLoading: youthGrowthLoading } = useYouthGrowth(6);
  const { data: attendanceData, averageRate, isLoading: attendanceLoading } = useAttendanceTrends(30);
  const { data: revenueData, formattedRevenue, growthRate, isLoading: revenueLoading } = useRevenueSummary(12);
  const { activities, getActivityIcon, getActivityColor, formatTime, isLoading: activityLoading } = useRecentActivity(10);
  const { activeAlerts, counts: alertCounts, isLoading: alertsLoading } = useSystemAlerts();

  const { refresh } = useRefreshInterval({ 
    intervalMs: preferences.refreshInterval * 1000, 
    enabled: preferences.refreshInterval > 0 
  });

  const handleRefresh = React.useCallback(() => {
    refetchStats();
    refresh();
  }, [refetchStats, refresh]);

  // Memoize event participation data
  const eventParticipationData = React.useMemo(() => [
    { label: 'Worship Services', value: 450 },
    { label: 'Youth Conferences', value: 280 },
    { label: 'Bible Studies', value: 320 },
    { label: 'Outreach Programs', value: 195 },
    { label: 'Sports Events', value: 210 },
  ], []);

  return (
    <DashboardErrorBoundary>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Super Admin Dashboard</h1>
            <p className="text-muted-foreground mt-1">System-wide overview and analytics</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <DateRangeFilter
              value={{
                from: new Date(),
                to: new Date(),
                preset: preferences.defaultDateRange as any,
              }}
              onChange={() => {}}
            />
            <ExportMenu />
            <DashboardPreferences preferences={preferences} onPreferencesChange={updatePreferences} />
            <Button onClick={handleRefresh} variant="outline" size="sm">
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <StatsGrid
          stats={stats}
          isLoading={statsLoading}
          formattedRevenue={formattedRevenue}
        />

        {/* Charts Section */}
        {(preferences.showYouthGrowthChart || preferences.showRevenueChart || 
          preferences.showAttendanceChart || preferences.showEventParticipation) && (
          <div className="grid gap-4 md:grid-cols-2">
            {preferences.showYouthGrowthChart && (
              <ChartContainer
                title="Youth Growth Trend"
                description="Monthly registration trends over the last 6 months"
                loading={youthGrowthLoading}
              >
                <YouthGrowthChart data={youthGrowthData} height={300} />
              </ChartContainer>
            )}

            {preferences.showRevenueChart && (
              <ChartContainer
                title="Revenue Trends"
                description={`Total: ${formattedRevenue}`}
                loading={revenueLoading}
                action={
                  <div className="flex items-center text-sm text-muted-foreground">
                    <TrendingUp className="mr-1 h-4 w-4 text-green-600" />
                    {growthRate > 0 ? '+' : ''}{growthRate}%
                  </div>
                }
              >
                <RevenueChart data={revenueData!} height={300} />
              </ChartContainer>
            )}

            {preferences.showAttendanceChart && (
              <ChartContainer
                title="Attendance Trends"
                description={`Average attendance rate: ${averageRate}%`}
                loading={attendanceLoading}
              >
                <AttendanceChart data={attendanceData} height={300} />
              </ChartContainer>
            )}

            {preferences.showEventParticipation && (
              <ChartContainer
                title="Event Participation"
                description="Participation breakdown by event type"
              >
                <EventParticipationChart data={eventParticipationData} height={300} />
              </ChartContainer>
            )}
          </div>
        )}

        {/* Activity & Alerts */}
        {(preferences.showRecentActivity || preferences.showSystemAlerts) && (
          <div className="grid gap-4 md:grid-cols-2">
            {preferences.showRecentActivity && (
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>Latest platform activities</CardDescription>
                </CardHeader>
                <CardContent>
                  {activityLoading ? (
                    <div className="space-y-3">
                      {[...Array(5)].map((_, i) => (
                        <div key={i} className="flex items-start gap-3">
                          <Skeleton className="h-10 w-10 rounded-lg" />
                          <div className="flex-1 space-y-2">
                            <Skeleton className="h-4 w-3/4" />
                            <Skeleton className="h-3 w-1/2" />
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : activities.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">No recent activity</p>
                  ) : (
                    <div className="space-y-3">
                      {activities.map((activity) => {
                        const Icon = getActivityIcon(activity.type);
                        const colorClass = getActivityColor(activity.type);
                        return (
                          <div key={activity.id} className="flex items-start gap-3">
                            <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${colorClass}`}>
                              <Icon className="h-5 w-5" />
                            </div>
                            <div className="flex-1 space-y-1">
                              <p className="text-sm font-medium leading-none">{activity.message}</p>
                              <p className="text-xs text-muted-foreground">{formatTime(activity.timestamp)}</p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {preferences.showSystemAlerts && (
              <Card>
                <CardHeader>
                  <CardTitle>System Alerts</CardTitle>
                  <CardDescription>
                    {alertCounts.active} active alert{alertCounts.active !== 1 ? 's' : ''}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {alertsLoading ? (
                    <div className="space-y-3">
                      {[...Array(3)].map((_, i) => (
                        <Skeleton key={i} className="h-16 w-full" />
                      ))}
                    </div>
                  ) : activeAlerts.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">No active alerts</p>
                  ) : (
                    <div className="space-y-3">
                      {activeAlerts.slice(0, 5).map((alert) => {
                        const severityColors = {
                          error: 'bg-red-50 border-red-200 text-red-800',
                          warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
                          info: 'bg-blue-50 border-blue-200 text-blue-800',
                          success: 'bg-green-50 border-green-200 text-green-800',
                        };
                        return (
                          <div key={alert.id} className={`p-3 rounded-lg border ${severityColors[alert.severity]}`}>
                            <p className="text-sm font-medium">{alert.title}</p>
                            <p className="text-xs mt-1 opacity-90">{alert.message}</p>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common administrative tasks</CardDescription>
          </CardHeader>
          <CardContent>
            <QuickActionsGrid />
          </CardContent>
        </Card>
      </div>
    </DashboardErrorBoundary>
  );
}

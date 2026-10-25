/**
 * Stats Grid Component
 * 
 * Displays 6 KPI stat cards in a responsive grid
 * Extracted from dashboard page for reusability
 */

'use client';

import * as React from 'react';
import { StatCard } from './StatCard';
import { Users, Calendar, UserCheck, DollarSign, Building2, Briefcase } from 'lucide-react';
import type { DashboardStats } from '../types/dashboard.types';

interface StatsGridProps {
  stats?: DashboardStats;
  isLoading?: boolean;
  formattedRevenue?: string;
}

export function StatsGrid({ stats, isLoading = false, formattedRevenue = '$0' }: StatsGridProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <StatCard
        title="Total Youth"
        value={stats?.totalYouths ?? 0}
        icon={Users}
        trend={stats?.trends.youths}
        loading={isLoading}
        iconColor="text-blue-600"
        iconBgColor="bg-blue-100"
      />
      <StatCard
        title="Active Events"
        value={stats?.activeEvents ?? 0}
        icon={Calendar}
        loading={isLoading}
        iconColor="text-purple-600"
        iconBgColor="bg-purple-100"
      />
      <StatCard
        title="Attendance Rate"
        value={`${stats?.attendanceRate ?? 0}%`}
        icon={UserCheck}
        trend={stats?.trends.attendance}
        loading={isLoading}
        iconColor="text-green-600"
        iconBgColor="bg-green-100"
      />
      <StatCard
        title="Total Revenue"
        value={formattedRevenue}
        icon={DollarSign}
        trend={stats?.trends.revenue}
        loading={isLoading}
        iconColor="text-emerald-600"
        iconBgColor="bg-emerald-100"
      />
      <StatCard
        title="Total Branches"
        value={stats?.totalBranches ?? 0}
        icon={Building2}
        loading={isLoading}
        iconColor="text-orange-600"
        iconBgColor="bg-orange-100"
      />
      <StatCard
        title="Total Departments"
        value={stats?.totalDepartments ?? 0}
        icon={Briefcase}
        loading={isLoading}
        iconColor="text-pink-600"
        iconBgColor="bg-pink-100"
      />
    </div>
  );
}

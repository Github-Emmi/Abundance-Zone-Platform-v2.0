/**
 * Revenue Summary Hook
 * 
 * Wrapper hook for revenue data with:
 * - Data formatting
 * - Growth calculations
 * - Period comparisons
 */

import { useState } from 'react';
import { useRevenueSummary as useQueryRevenueSummary } from '../api/dashboard-queries';
import type { RevenueSummaryData } from '../types/dashboard.types';

interface UseRevenueSummaryReturn {
  data: RevenueSummaryData | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  isEmpty: boolean;
  months: number;
  setMonths: (months: number) => void;
  formattedRevenue: string;
  growthRate: number;
  refetch: () => void;
}

/**
 * Fetch revenue summary with formatted values
 * Calculates growth rate automatically
 * 
 * @param initialMonths - Initial number of months to fetch (default: 12)
 * 
 * @example
 * const { data, formattedRevenue, growthRate } = useRevenueSummary(12);
 * 
 * return (
 *   <>
 *     <h2>Total Revenue: {formattedRevenue}</h2>
 *     <p>Growth: {growthRate}%</p>
 *     <RevenueChart data={data} />
 *   </>
 * );
 */
export const useRevenueSummary = (initialMonths: number = 12): UseRevenueSummaryReturn => {
  const [months, setMonths] = useState(initialMonths);

  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
  } = useQueryRevenueSummary(months);

  // Format total revenue as currency
  const formattedRevenue = data
    ? new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
      }).format(data.totalRevenue)
    : '$0';

  // Calculate growth rate (comparing first half to second half)
  const growthRate = (() => {
    if (!data?.monthlyBreakdown || !Array.isArray(data.monthlyBreakdown) || data.monthlyBreakdown.length < 2) return 0;

    const breakdown = data.monthlyBreakdown;
    const midPoint = Math.floor(breakdown.length / 2);
    
    const firstHalf = breakdown.slice(0, midPoint);
    const secondHalf = breakdown.slice(midPoint);

    const firstHalfTotal = firstHalf.reduce((sum, item) => sum + item.revenue, 0);
    const secondHalfTotal = secondHalf.reduce((sum, item) => sum + item.revenue, 0);

    if (firstHalfTotal === 0) return 0;

    return Math.round(((secondHalfTotal - firstHalfTotal) / firstHalfTotal) * 100);
  })();

  return {
    data,
    isLoading,
    isError,
    error: error as Error | null,
    isEmpty: !data || !data.monthlyBreakdown || data.monthlyBreakdown.length === 0,
    months,
    setMonths,
    formattedRevenue,
    growthRate,
    refetch,
  };
};

/**
 * Calculate revenue health metrics
 * Useful for alerts and recommendations
 * 
 * @example
 * const { outstandingRatio, fulfillmentRate, healthStatus } = useRevenueHealth();
 */
export const useRevenueHealth = (months: number = 12) => {
  const { data } = useRevenueSummary(months);

  if (!data) {
    return {
      outstandingRatio: 0,
      fulfillmentRate: 0,
      healthStatus: 'unknown' as const,
      healthColor: 'text-gray-500',
      healthLabel: 'No Data',
    };
  }

  const totalExpected = data.totalRevenue + data.outstandingPayments;
  const outstandingRatio = totalExpected > 0
    ? (data.outstandingPayments / totalExpected) * 100
    : 0;

  const fulfillmentRate = data.pledgesFulfilled > 0
    ? Math.round((data.totalRevenue / data.pledgesFulfilled) * 100)
    : 0;

  let healthStatus: 'excellent' | 'good' | 'warning' | 'critical' | 'unknown';
  let healthColor: string;
  let healthLabel: string;

  if (outstandingRatio < 10 && fulfillmentRate >= 90) {
    healthStatus = 'excellent';
    healthColor = 'text-green-600';
    healthLabel = 'Excellent Revenue Health';
  } else if (outstandingRatio < 20 && fulfillmentRate >= 75) {
    healthStatus = 'good';
    healthColor = 'text-blue-600';
    healthLabel = 'Good Revenue Health';
  } else if (outstandingRatio < 35 && fulfillmentRate >= 60) {
    healthStatus = 'warning';
    healthColor = 'text-yellow-600';
    healthLabel = 'Revenue Needs Attention';
  } else {
    healthStatus = 'critical';
    healthColor = 'text-red-600';
    healthLabel = 'Critical Revenue Issues';
  }

  return {
    outstandingRatio: Math.round(outstandingRatio * 10) / 10,
    fulfillmentRate,
    healthStatus,
    healthColor,
    healthLabel,
  };
};

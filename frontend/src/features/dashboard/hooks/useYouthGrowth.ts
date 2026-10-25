/**
 * Youth Growth Hook
 * 
 * Wrapper hook for youth growth chart data with:
 * - Data transformation for charts
 * - Empty state handling
 * - Date range filtering
 */

import { useState } from 'react';
import { useYouthGrowth as useQueryYouthGrowth } from '../api/dashboard-queries';
import type { YouthGrowthData } from '../types/dashboard.types';

interface UseYouthGrowthReturn {
  data: YouthGrowthData[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  isEmpty: boolean;
  months: number;
  setMonths: (months: number) => void;
  refetch: () => void;
}

/**
 * Fetch youth growth data for charts
 * Supports dynamic month range selection
 * 
 * @param initialMonths - Initial number of months to fetch (default: 6)
 * 
 * @example
 * const { data, isLoading, months, setMonths } = useYouthGrowth(6);
 * 
 * return (
 *   <>
 *     <Select value={months} onChange={setMonths}>
 *       <option value={3}>3 months</option>
 *       <option value={6}>6 months</option>
 *       <option value={12}>12 months</option>
 *     </Select>
 *     <YouthGrowthChart data={data} />
 *   </>
 * );
 */
export const useYouthGrowth = (initialMonths: number = 6): UseYouthGrowthReturn => {
  const [months, setMonths] = useState(initialMonths);

  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
  } = useQueryYouthGrowth(months);

  return {
    data: data ?? [],
    isLoading,
    isError,
    error: error as Error | null,
    isEmpty: !data || data.length === 0,
    months,
    setMonths,
    refetch,
  };
};

/**
 * Calculate total growth metrics from youth growth data
 * Useful for summary cards
 * 
 * @example
 * const { totalGrowth, averageMonthlyGrowth } = useYouthGrowthMetrics(6);
 */
export const useYouthGrowthMetrics = (months: number = 6) => {
  const { data } = useYouthGrowth(months);

  if (!data || data.length === 0) {
    return {
      totalGrowth: 0,
      averageMonthlyGrowth: 0,
      highestMonth: null,
      lowestMonth: null,
    };
  }

  const totalNew = data.reduce((sum, item) => sum + item.newRegistrations, 0);
  const avgGrowth = totalNew / data.length;

  const sortedByNew = [...data].sort((a, b) => b.newRegistrations - a.newRegistrations);

  return {
    totalGrowth: totalNew,
    averageMonthlyGrowth: Math.round(avgGrowth * 10) / 10,
    highestMonth: sortedByNew[0]?.month ?? null,
    lowestMonth: sortedByNew[sortedByNew.length - 1]?.month ?? null,
  };
};

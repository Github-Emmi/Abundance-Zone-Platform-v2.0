/**
 * Branch Comparison Table Component
 * 
 * Displays branch performance comparison with rankings
 * Supports sorting and drill-down into branch details
 */

'use client';

import * as React from 'react';
import { ArrowUpDown, ChevronRight, Trophy, TrendingUp, TrendingDown } from 'lucide-react';
import { Button } from '@/shared/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui/table';
import { Badge } from '@/shared/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card';
import { useBranchComparison } from '../api/dashboard-queries';
import { Skeleton } from '@/shared/ui/skeleton';

type SortKey = 'rank' | 'totalYouths' | 'attendanceRate' | 'totalRevenue' | 'activeEvents';
type SortDirection = 'asc' | 'desc';

export function BranchComparisonTable() {
  const { data: branches, isLoading } = useBranchComparison();
  const [sortKey, setSortKey] = React.useState<SortKey>('rank');
  const [sortDirection, setSortDirection] = React.useState<SortDirection>('asc');

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const sortedBranches = React.useMemo(() => {
    if (!branches) return [];

    return [...branches].sort((a, b) => {
      let aValue = a[sortKey];
      let bValue = b[sortKey];

      if (sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  }, [branches, sortKey, sortDirection]);

  const getRankBadge = (rank: number) => {
    if (rank === 1) {
      return (
        <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">
          <Trophy className="mr-1 h-3 w-3" />
          #1
        </Badge>
      );
    } else if (rank === 2) {
      return (
        <Badge className="bg-gray-100 text-gray-800 border-gray-200">
          #2
        </Badge>
      );
    } else if (rank === 3) {
      return (
        <Badge className="bg-orange-100 text-orange-800 border-orange-200">
          #3
        </Badge>
      );
    }
    return <Badge variant="outline">#{rank}</Badge>;
  };

  const getAttendanceStatus = (rate: number) => {
    if (rate >= 80) {
      return (
        <span className="flex items-center text-green-600">
          <TrendingUp className="mr-1 h-4 w-4" />
          {rate}%
        </span>
      );
    } else if (rate >= 60) {
      return <span className="text-yellow-600">{rate}%</span>;
    }
    return (
      <span className="flex items-center text-red-600">
        <TrendingDown className="mr-1 h-4 w-4" />
        {rate}%
      </span>
    );
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Branch Performance Comparison</CardTitle>
          <CardDescription>Loading branch data...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!branches || branches.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Branch Performance Comparison</CardTitle>
          <CardDescription>No branch data available</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Branch Performance Comparison</CardTitle>
        <CardDescription>
          Compare performance metrics across all branches
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('rank')}
                    className="h-8 w-full justify-start"
                  >
                    Rank
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>Branch Name</TableHead>
                <TableHead className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('totalYouths')}
                    className="h-8 w-full justify-end"
                  >
                    Total Youth
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('attendanceRate')}
                    className="h-8 w-full justify-end"
                  >
                    Attendance
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('totalRevenue')}
                    className="h-8 w-full justify-end"
                  >
                    Revenue
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('activeEvents')}
                    className="h-8 w-full justify-end"
                  >
                    Events
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedBranches.map((branch) => (
                <TableRow key={branch.branchId} className="cursor-pointer hover:bg-muted/50">
                  <TableCell>{getRankBadge(branch.rank)}</TableCell>
                  <TableCell className="font-medium">{branch.branchName}</TableCell>
                  <TableCell className="text-right">{branch.totalYouths.toLocaleString()}</TableCell>
                  <TableCell className="text-right">
                    {getAttendanceStatus(branch.attendanceRate)}
                  </TableCell>
                  <TableCell className="text-right">
                    ${branch.totalRevenue.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right">{branch.activeEvents}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

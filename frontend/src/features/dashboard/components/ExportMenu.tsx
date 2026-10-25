/**
 * Export Menu Component
 * 
 * Dropdown menu for exporting dashboard data in various formats
 * Supports CSV, PDF, and XLSX exports
 */

'use client';

import * as React from 'react';
import { Download, FileSpreadsheet, FileText, File } from 'lucide-react';
import { Button } from '@/shared/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu';
import { useExportReport } from '../api/dashboard-queries';
import type { ExportReportParams } from '../types/dashboard.types';
import { toast } from 'sonner';

interface ExportMenuProps {
  dateRange?: {
    startDate: string;
    endDate: string;
  };
}

export function ExportMenu({ dateRange }: ExportMenuProps) {
  const { mutate: exportReport, isPending } = useExportReport();

  const handleExport = (format: 'csv' | 'pdf' | 'xlsx', type: ExportReportParams['type']) => {
    exportReport(
      {
        type,
        format,
        startDate: dateRange?.startDate,
        endDate: dateRange?.endDate,
      },
      {
        onSuccess: () => {
          toast.success(`Report exported successfully as ${format.toUpperCase()}`);
        },
        onError: (error: any) => {
          toast.error(error?.response?.data?.message || 'Export failed');
        },
      }
    );
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" disabled={isPending}>
          <Download className="mr-2 h-4 w-4" />
          {isPending ? 'Exporting...' : 'Export'}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>Export Dashboard Data</DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">
          Daily Reports
        </DropdownMenuLabel>
        <DropdownMenuItem onClick={() => handleExport('csv', 'daily_attendance')}>
          <FileSpreadsheet className="mr-2 h-4 w-4" />
          Daily Attendance (CSV)
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">
          Analytics Reports
        </DropdownMenuLabel>
        <DropdownMenuItem onClick={() => handleExport('xlsx', 'weekly_analytics')}>
          <File className="mr-2 h-4 w-4" />
          Weekly Analytics (XLSX)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('pdf', 'monthly_financial')}>
          <FileText className="mr-2 h-4 w-4" />
          Monthly Financial (PDF)
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">
          Directory Exports
        </DropdownMenuLabel>
        <DropdownMenuItem onClick={() => handleExport('csv', 'youth_directory')}>
          <FileSpreadsheet className="mr-2 h-4 w-4" />
          Youth Directory (CSV)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('xlsx', 'event_summary')}>
          <File className="mr-2 h-4 w-4" />
          Event Summary (XLSX)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('pdf', 'financial_summary')}>
          <FileText className="mr-2 h-4 w-4" />
          Financial Summary (PDF)
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

/**
 * Date Range Filter Component
 * 
 * Provides preset and custom date range selection for dashboard filters
 * Updates all charts and data queries dynamically
 */

'use client';

import * as React from 'react';
import { CalendarIcon } from 'lucide-react';
import { format, subDays, subMonths, startOfDay, endOfDay } from 'date-fns';
import { Button } from '@/shared/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/ui/dialog';
import { cn } from '@/shared/lib/utils';

export type DateRangePreset = 
  | 'today'
  | 'yesterday'
  | 'last7days'
  | 'last30days'
  | 'last3months'
  | 'last6months'
  | 'last12months'
  | 'custom';

export interface DateRange {
  from: Date;
  to: Date;
  preset: DateRangePreset;
}

interface DateRangeFilterProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
  className?: string;
}

const presets: { label: string; value: DateRangePreset; getDates: () => { from: Date; to: Date } }[] = [
  {
    label: 'Today',
    value: 'today',
    getDates: () => ({
      from: startOfDay(new Date()),
      to: endOfDay(new Date()),
    }),
  },
  {
    label: 'Yesterday',
    value: 'yesterday',
    getDates: () => ({
      from: startOfDay(subDays(new Date(), 1)),
      to: endOfDay(subDays(new Date(), 1)),
    }),
  },
  {
    label: 'Last 7 days',
    value: 'last7days',
    getDates: () => ({
      from: startOfDay(subDays(new Date(), 7)),
      to: endOfDay(new Date()),
    }),
  },
  {
    label: 'Last 30 days',
    value: 'last30days',
    getDates: () => ({
      from: startOfDay(subDays(new Date(), 30)),
      to: endOfDay(new Date()),
    }),
  },
  {
    label: 'Last 3 months',
    value: 'last3months',
    getDates: () => ({
      from: startOfDay(subMonths(new Date(), 3)),
      to: endOfDay(new Date()),
    }),
  },
  {
    label: 'Last 6 months',
    value: 'last6months',
    getDates: () => ({
      from: startOfDay(subMonths(new Date(), 6)),
      to: endOfDay(new Date()),
    }),
  },
  {
    label: 'Last 12 months',
    value: 'last12months',
    getDates: () => ({
      from: startOfDay(subMonths(new Date(), 12)),
      to: endOfDay(new Date()),
    }),
  },
];

export function DateRangeFilter({ value, onChange, className }: DateRangeFilterProps) {
  const [isCustomDialogOpen, setIsCustomDialogOpen] = React.useState(false);
  const [customFrom, setCustomFrom] = React.useState('');
  const [customTo, setCustomTo] = React.useState('');

  const handlePresetChange = (presetValue: string) => {
    if (presetValue === 'custom') {
      setIsCustomDialogOpen(true);
      return;
    }

    const preset = presets.find((p) => p.value === presetValue);
    if (preset) {
      const dates = preset.getDates();
      onChange({
        from: dates.from,
        to: dates.to,
        preset: preset.value,
      });
    }
  };

  const handleCustomApply = () => {
    if (customFrom && customTo) {
      const from = new Date(customFrom);
      const to = new Date(customTo);
      
      if (from <= to) {
        onChange({
          from: startOfDay(from),
          to: endOfDay(to),
          preset: 'custom',
        });
        setIsCustomDialogOpen(false);
      }
    }
  };

  const getDisplayText = () => {
    if (value.preset === 'custom') {
      return `${format(value.from, 'MMM d, yyyy')} - ${format(value.to, 'MMM d, yyyy')}`;
    }
    const preset = presets.find((p) => p.value === value.preset);
    return preset?.label || 'Select range';
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <CalendarIcon className="h-4 w-4 text-muted-foreground" />
      
      <Select value={value.preset} onValueChange={handlePresetChange}>
        <SelectTrigger className="w-[200px]">
          <SelectValue>{getDisplayText()}</SelectValue>
        </SelectTrigger>
        <SelectContent>
          {presets.map((preset) => (
            <SelectItem key={preset.value} value={preset.value}>
              {preset.label}
            </SelectItem>
          ))}
          <SelectItem value="custom">Custom Range...</SelectItem>
        </SelectContent>
      </Select>

      <Dialog open={isCustomDialogOpen} onOpenChange={setIsCustomDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Custom Date Range</DialogTitle>
            <DialogDescription>
              Select a custom date range for the dashboard
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <label htmlFor="from" className="text-sm font-medium">
                From
              </label>
              <input
                id="from"
                type="date"
                value={customFrom}
                onChange={(e) => setCustomFrom(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                max={customTo || format(new Date(), 'yyyy-MM-dd')}
              />
            </div>
            
            <div className="grid gap-2">
              <label htmlFor="to" className="text-sm font-medium">
                To
              </label>
              <input
                id="to"
                type="date"
                value={customTo}
                onChange={(e) => setCustomTo(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                min={customFrom}
                max={format(new Date(), 'yyyy-MM-dd')}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsCustomDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCustomApply}
              disabled={!customFrom || !customTo}
            >
              Apply
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

/**
 * Hook to manage date range state
 */
export function useDateRangeFilter(defaultPreset: DateRangePreset = 'last30days') {
  const [dateRange, setDateRange] = React.useState<DateRange>(() => {
    const preset = presets.find((p) => p.value === defaultPreset);
    const dates = preset?.getDates() || presets[3].getDates(); // fallback to last 30 days
    return {
      from: dates.from,
      to: dates.to,
      preset: defaultPreset,
    };
  });

  return {
    dateRange,
    setDateRange,
    // Helper to get days count
    daysCount: Math.ceil(
      (dateRange.to.getTime() - dateRange.from.getTime()) / (1000 * 60 * 60 * 24)
    ),
    // Format for API
    formatForApi: () => ({
      startDate: format(dateRange.from, 'yyyy-MM-dd'),
      endDate: format(dateRange.to, 'yyyy-MM-dd'),
    }),
  };
}

/**
 * Dashboard Preferences Component
 * 
 * Settings panel for customizing dashboard behavior
 * - Widget visibility toggles
 * - Refresh interval settings
 * - Layout customization
 */

'use client';

import * as React from 'react';
import { Settings } from 'lucide-react';
import { Button } from '@/shared/ui/button';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/shared/ui/sheet';
import { Label } from '@/shared/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui/select';
import { Separator } from '@/shared/ui/separator';
import { toast } from 'sonner';

interface DashboardPreferencesState {
  showYouthGrowthChart: boolean;
  showRevenueChart: boolean;
  showAttendanceChart: boolean;
  showEventParticipation: boolean;
  showRecentActivity: boolean;
  showSystemAlerts: boolean;
  refreshInterval: number; // in seconds
  defaultDateRange: string;
}

interface DashboardPreferencesProps {
  preferences: DashboardPreferencesState;
  onPreferencesChange: (preferences: DashboardPreferencesState) => void;
}

const REFRESH_INTERVALS = [
  { value: 30, label: '30 seconds' },
  { value: 60, label: '1 minute' },
  { value: 120, label: '2 minutes' },
  { value: 300, label: '5 minutes' },
  { value: 0, label: 'Manual only' },
];

const DATE_RANGES = [
  { value: 'last7days', label: 'Last 7 days' },
  { value: 'last30days', label: 'Last 30 days' },
  { value: 'last3months', label: 'Last 3 months' },
  { value: 'last6months', label: 'Last 6 months' },
  { value: 'last12months', label: 'Last 12 months' },
];

export function DashboardPreferences({ preferences, onPreferencesChange }: DashboardPreferencesProps) {
  const [localPreferences, setLocalPreferences] = React.useState(preferences);
  const [isOpen, setIsOpen] = React.useState(false);

  const handleToggle = (key: keyof DashboardPreferencesState) => {
    setLocalPreferences((prev) => ({
      ...prev,
      [key]: !prev[key as keyof typeof prev],
    }));
  };

  const handleRefreshIntervalChange = (value: string) => {
    setLocalPreferences((prev) => ({
      ...prev,
      refreshInterval: parseInt(value, 10),
    }));
  };

  const handleDateRangeChange = (value: string) => {
    setLocalPreferences((prev) => ({
      ...prev,
      defaultDateRange: value,
    }));
  };

  const handleSave = () => {
    onPreferencesChange(localPreferences);
    setIsOpen(false);
    toast.success('Preferences saved successfully');
  };

  const handleReset = () => {
    const defaults: DashboardPreferencesState = {
      showYouthGrowthChart: true,
      showRevenueChart: true,
      showAttendanceChart: true,
      showEventParticipation: true,
      showRecentActivity: true,
      showSystemAlerts: true,
      refreshInterval: 60,
      defaultDateRange: 'last30days',
    };
    setLocalPreferences(defaults);
    onPreferencesChange(defaults);
    toast.success('Preferences reset to defaults');
  };

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm">
          <Settings className="mr-2 h-4 w-4" />
          Preferences
        </Button>
      </SheetTrigger>
      <SheetContent className="w-[400px] sm:w-[540px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Dashboard Preferences</SheetTitle>
          <SheetDescription>
            Customize your dashboard layout and behavior
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-6 py-6">
          {/* Widget Visibility */}
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold mb-2">Widget Visibility</h3>
              <p className="text-xs text-muted-foreground mb-4">
                Show or hide dashboard widgets
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="youth-growth">Youth Growth Chart</Label>
                <input
                  type="checkbox"
                  id="youth-growth"
                  checked={localPreferences.showYouthGrowthChart}
                  onChange={() => handleToggle('showYouthGrowthChart')}
                  className="h-4 w-4"
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="revenue">Revenue Chart</Label>
                <input
                  type="checkbox"
                  id="revenue"
                  checked={localPreferences.showRevenueChart}
                  onChange={() => handleToggle('showRevenueChart')}
                  className="h-4 w-4"
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="attendance">Attendance Chart</Label>
                <input
                  type="checkbox"
                  id="attendance"
                  checked={localPreferences.showAttendanceChart}
                  onChange={() => handleToggle('showAttendanceChart')}
                  className="h-4 w-4"
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="event-participation">Event Participation</Label>
                <input
                  type="checkbox"
                  id="event-participation"
                  checked={localPreferences.showEventParticipation}
                  onChange={() => handleToggle('showEventParticipation')}
                  className="h-4 w-4"
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="recent-activity">Recent Activity</Label>
                <input
                  type="checkbox"
                  id="recent-activity"
                  checked={localPreferences.showRecentActivity}
                  onChange={() => handleToggle('showRecentActivity')}
                  className="h-4 w-4"
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="system-alerts">System Alerts</Label>
                <input
                  type="checkbox"
                  id="system-alerts"
                  checked={localPreferences.showSystemAlerts}
                  onChange={() => handleToggle('showSystemAlerts')}
                  className="h-4 w-4"
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Refresh Interval */}
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold mb-2">Auto Refresh</h3>
              <p className="text-xs text-muted-foreground mb-4">
                How often the dashboard should refresh data automatically
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="refresh-interval">Refresh Interval</Label>
              <Select
                value={localPreferences.refreshInterval.toString()}
                onValueChange={handleRefreshIntervalChange}
              >
                <SelectTrigger id="refresh-interval">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {REFRESH_INTERVALS.map((interval) => (
                    <SelectItem key={interval.value} value={interval.value.toString()}>
                      {interval.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <Separator />

          {/* Default Date Range */}
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold mb-2">Default View</h3>
              <p className="text-xs text-muted-foreground mb-4">
                Default date range when loading the dashboard
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="date-range">Default Date Range</Label>
              <Select
                value={localPreferences.defaultDateRange}
                onValueChange={handleDateRangeChange}
              >
                <SelectTrigger id="date-range">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DATE_RANGES.map((range) => (
                    <SelectItem key={range.value} value={range.value}>
                      {range.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <Separator />

        <div className="flex justify-between gap-2 pt-6">
          <Button variant="outline" onClick={handleReset}>
            Reset to Defaults
          </Button>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave}>
              Save Changes
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

/**
 * Hook to manage dashboard preferences with localStorage persistence
 */
export function useDashboardPreferences() {
  const [preferences, setPreferences] = React.useState<DashboardPreferencesState>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('dashboard-preferences');
      if (saved) {
        return JSON.parse(saved);
      }
    }
    return {
      showYouthGrowthChart: true,
      showRevenueChart: true,
      showAttendanceChart: true,
      showEventParticipation: true,
      showRecentActivity: true,
      showSystemAlerts: true,
      refreshInterval: 60,
      defaultDateRange: 'last30days',
    };
  });

  const updatePreferences = React.useCallback((newPreferences: DashboardPreferencesState) => {
    setPreferences(newPreferences);
    if (typeof window !== 'undefined') {
      localStorage.setItem('dashboard-preferences', JSON.stringify(newPreferences));
    }
  }, []);

  return {
    preferences,
    updatePreferences,
  };
}

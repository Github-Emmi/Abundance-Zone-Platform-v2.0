/**
 * Department Leader Dashboard Page
 * Department-level oversight and management
 */

'use client';

import * as React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card';
import { Users } from 'lucide-react';

export default function DepartmentLeaderDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Department Leader Dashboard</h1>
        <p className="text-muted-foreground mt-1">Department-level oversight and management</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-pink-100">
              <Users className="h-6 w-6 text-pink-600" />
            </div>
            <div>
              <CardTitle>Coming Soon</CardTitle>
              <CardDescription>Department Leader features are under development</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            This dashboard will provide department-specific analytics, team management, 
            activity coordination, and department performance tracking.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

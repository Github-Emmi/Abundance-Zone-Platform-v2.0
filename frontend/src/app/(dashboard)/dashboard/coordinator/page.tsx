/**
 * Branch Coordinator Dashboard Page
 * Branch-level management and oversight
 */

'use client';

import * as React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card';
import { Building2 } from 'lucide-react';

export default function BranchCoordinatorDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Branch Coordinator Dashboard</h1>
        <p className="text-muted-foreground mt-1">Branch-level management and oversight</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-orange-100">
              <Building2 className="h-6 w-6 text-orange-600" />
            </div>
            <div>
              <CardTitle>Coming Soon</CardTitle>
              <CardDescription>Branch Coordinator features are under development</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            This dashboard will provide branch-specific analytics, youth management, 
            event coordination, and branch performance metrics.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

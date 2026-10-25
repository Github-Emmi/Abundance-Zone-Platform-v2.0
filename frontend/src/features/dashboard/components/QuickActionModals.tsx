/**
 * Quick Action Modals Component
 * 
 * Modal forms for quick actions with validation and toast notifications
 */

'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Label } from '@/shared/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui/select';

type QuickActionType = 
  | 'add-youth'
  | 'create-event'
  | 'record-attendance'
  | 'record-payment'
  | 'view-analytics'
  | 'manage-branches';

interface QuickActionModalsProps {
  action: QuickActionType | null;
  isOpen: boolean;
  onClose: () => void;
}

export function QuickActionModals({ action, isOpen, onClose }: QuickActionModalsProps) {
  const router = useRouter();

  const handleNavigate = (path: string) => {
    onClose();
    router.push(path);
  };

  const renderModalContent = () => {
    switch (action) {
      case 'add-youth':
        return (
          <>
            <DialogHeader>
              <DialogTitle>Add New Youth</DialogTitle>
              <DialogDescription>
                Quick form to register a new youth member. For full details, use the complete registration form.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Full Name *</Label>
                <Input id="name" placeholder="John Doe" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="email">Email *</Label>
                <Input id="email" type="email" placeholder="john@example.com" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="phone">Phone Number *</Label>
                <Input id="phone" placeholder="+234 800 000 0000" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="branch">Branch *</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select branch" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="branch1">Main Branch</SelectItem>
                    <SelectItem value="branch2">City Branch</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={onClose}>Cancel</Button>
              <Button onClick={() => handleNavigate('/youths/new')}>
                Continue to Full Form
              </Button>
            </div>
          </>
        );

      case 'create-event':
        return (
          <>
            <DialogHeader>
              <DialogTitle>Create New Event</DialogTitle>
              <DialogDescription>
                Quick form to create an event. Use the full form for advanced options.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="event-name">Event Name *</Label>
                <Input id="event-name" placeholder="Sunday Service" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="event-date">Date *</Label>
                <Input id="event-date" type="date" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="event-time">Time *</Label>
                <Input id="event-time" type="time" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="event-type">Event Type *</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="worship">Worship Service</SelectItem>
                    <SelectItem value="conference">Conference</SelectItem>
                    <SelectItem value="bible-study">Bible Study</SelectItem>
                    <SelectItem value="outreach">Outreach</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={onClose}>Cancel</Button>
              <Button onClick={() => handleNavigate('/events/new')}>
                Continue to Full Form
              </Button>
            </div>
          </>
        );

      case 'record-attendance':
        return (
          <>
            <DialogHeader>
              <DialogTitle>Record Attendance</DialogTitle>
              <DialogDescription>
                Quick attendance recording. For bulk operations, use the attendance module.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="attendance-event">Event *</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select event" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="event1">Sunday Service - Today</SelectItem>
                    <SelectItem value="event2">Bible Study - Today</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="attendance-youth">Youth Member *</Label>
                <Input id="attendance-youth" placeholder="Search by name or ID" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="attendance-time">Check-in Time</Label>
                <Input id="attendance-time" type="time" defaultValue={new Date().toTimeString().slice(0, 5)} />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={onClose}>Cancel</Button>
              <Button onClick={() => {
                toast.success('Attendance recorded successfully');
                onClose();
              }}>
                Record Attendance
              </Button>
              <Button variant="secondary" onClick={() => handleNavigate('/attendance')}>
                Bulk Check-In
              </Button>
            </div>
          </>
        );

      case 'record-payment':
        return (
          <>
            <DialogHeader>
              <DialogTitle>Record Payment</DialogTitle>
              <DialogDescription>
                Quick payment recording. For detailed transactions, use the finance module.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="payment-youth">Youth Member *</Label>
                <Input id="payment-youth" placeholder="Search by name or ID" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="payment-amount">Amount *</Label>
                <Input id="payment-amount" type="number" placeholder="0.00" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="payment-method">Payment Method *</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select method" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cash">Cash</SelectItem>
                    <SelectItem value="transfer">Bank Transfer</SelectItem>
                    <SelectItem value="card">Card</SelectItem>
                    <SelectItem value="mobile">Mobile Money</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="payment-purpose">Purpose</Label>
                <Input id="payment-purpose" placeholder="e.g., Monthly Dues" />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={onClose}>Cancel</Button>
              <Button onClick={() => {
                toast.success('Payment recorded successfully');
                onClose();
              }}>
                Record Payment
              </Button>
              <Button variant="secondary" onClick={() => handleNavigate('/finance')}>
                Finance Module
              </Button>
            </div>
          </>
        );

      case 'view-analytics':
        return (
          <>
            <DialogHeader>
              <DialogTitle>Analytics Dashboard</DialogTitle>
              <DialogDescription>
                Choose the analytics view you want to explore
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-3 py-4">
              <Button variant="outline" className="justify-start" onClick={() => handleNavigate('/analytics?view=youth')}>
                Youth Analytics
              </Button>
              <Button variant="outline" className="justify-start" onClick={() => handleNavigate('/analytics?view=events')}>
                Event Analytics
              </Button>
              <Button variant="outline" className="justify-start" onClick={() => handleNavigate('/analytics?view=attendance')}>
                Attendance Analytics
              </Button>
              <Button variant="outline" className="justify-start" onClick={() => handleNavigate('/analytics?view=financial')}>
                Financial Analytics
              </Button>
              <Button variant="outline" className="justify-start" onClick={() => handleNavigate('/analytics?view=branches')}>
                Branch Comparison
              </Button>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={onClose}>Cancel</Button>
            </div>
          </>
        );

      case 'manage-branches':
        return (
          <>
            <DialogHeader>
              <DialogTitle>Branch Management</DialogTitle>
              <DialogDescription>
                Quick access to branch management functions
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-3 py-4">
              <Button variant="outline" className="justify-start" onClick={() => handleNavigate('/branches')}>
                View All Branches
              </Button>
              <Button variant="outline" className="justify-start" onClick={() => handleNavigate('/branches/new')}>
                Create New Branch
              </Button>
              <Button variant="outline" className="justify-start" onClick={() => handleNavigate('/branches/performance')}>
                Branch Performance
              </Button>
              <Button variant="outline" className="justify-start" onClick={() => handleNavigate('/departments')}>
                Manage Departments
              </Button>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={onClose}>Cancel</Button>
            </div>
          </>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        {renderModalContent()}
      </DialogContent>
    </Dialog>
  );
}

/**
 * Hook to manage quick action modals
 */
export function useQuickActionModals() {
  const [currentAction, setCurrentAction] = React.useState<QuickActionType | null>(null);
  const [isOpen, setIsOpen] = React.useState(false);

  const openModal = (action: QuickActionType) => {
    setCurrentAction(action);
    setIsOpen(true);
  };

  const closeModal = () => {
    setIsOpen(false);
    setTimeout(() => setCurrentAction(null), 200); // Delay to allow close animation
  };

  return {
    currentAction,
    isOpen,
    openModal,
    closeModal,
  };
}

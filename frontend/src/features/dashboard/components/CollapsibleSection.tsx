/**
 * Collapsible Section Component
 * 
 * Mobile-friendly collapsible sections for dashboard
 * Allows users to expand/collapse sections on mobile devices
 */

'use client';

import * as React from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/shared/lib/utils';
import { Button } from '@/shared/ui/button';

interface CollapsibleSectionProps {
  title: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
  className?: string;
  badge?: React.ReactNode;
}

export function CollapsibleSection({ 
  title, 
  defaultOpen = true, 
  children, 
  className,
  badge 
}: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = React.useState(defaultOpen);

  return (
    <div className={cn('border rounded-lg', className)}>
      <Button
        variant="ghost"
        className="w-full flex items-center justify-between p-4 hover:bg-muted/50"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-left">{title}</h3>
          {badge}
        </div>
        <ChevronDown
          className={cn(
            'h-5 w-5 transition-transform duration-200',
            isOpen && 'transform rotate-180'
          )}
        />
      </Button>
      
      <div
        className={cn(
          'overflow-hidden transition-all duration-200 ease-in-out',
          isOpen ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'
        )}
      >
        <div className="p-4 pt-0">
          {children}
        </div>
      </div>
    </div>
  );
}

/**
 * Touch-optimized button for mobile
 */
interface TouchButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

export function TouchButton({ children, className, ...props }: TouchButtonProps) {
  return (
    <button
      {...props}
      className={cn(
        'min-h-[44px] min-w-[44px] flex items-center justify-center',
        'active:scale-95 transition-transform touch-manipulation',
        className
      )}
    >
      {children}
    </button>
  );
}

/**
 * Mobile bottom sheet for quick actions
 */
interface MobileBottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
}

export function MobileBottomSheet({ 
  isOpen, 
  onClose, 
  children, 
  title 
}: MobileBottomSheetProps) {
  React.useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/50 z-40 lg:hidden"
        onClick={onClose}
      />
      
      {/* Bottom Sheet */}
      <div
        className={cn(
          'fixed bottom-0 left-0 right-0 bg-background rounded-t-2xl z-50 lg:hidden',
          'transform transition-transform duration-300 ease-out',
          'max-h-[85vh] overflow-y-auto',
          isOpen ? 'translate-y-0' : 'translate-y-full'
        )}
      >
        {/* Drag Handle */}
        <div className="flex justify-center py-3">
          <div className="w-12 h-1 bg-muted rounded-full" />
        </div>
        
        {title && (
          <div className="px-6 pb-4">
            <h3 className="font-semibold text-lg">{title}</h3>
          </div>
        )}
        
        <div className="px-6 pb-6">
          {children}
        </div>
      </div>
    </>
  );
}

/**
 * Swipeable card for mobile gestures
 */
interface SwipeableCardProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  className?: string;
}

export function SwipeableCard({ 
  children, 
  onSwipeLeft, 
  onSwipeRight,
  className 
}: SwipeableCardProps) {
  const [touchStart, setTouchStart] = React.useState(0);
  const [touchEnd, setTouchEnd] = React.useState(0);

  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(0);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe && onSwipeLeft) {
      onSwipeLeft();
    }
    if (isRightSwipe && onSwipeRight) {
      onSwipeRight();
    }
  };

  return (
    <div
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
      className={cn('touch-pan-y', className)}
    >
      {children}
    </div>
  );
}

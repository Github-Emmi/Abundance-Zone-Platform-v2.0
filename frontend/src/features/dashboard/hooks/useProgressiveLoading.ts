/**
 * Progressive Loading Hook
 * 
 * Implements progressive/staged loading for dashboard data
 * Loads critical data first, then secondary data
 */

import * as React from 'react';

type LoadingStage = 'idle' | 'stats' | 'charts' | 'activity' | 'complete';

interface UseProgressiveLoadingOptions {
  enabled?: boolean;
  onStageChange?: (stage: LoadingStage) => void;
}

export function useProgressiveLoading(options: UseProgressiveLoadingOptions = {}) {
  const { enabled = true, onStageChange } = options;
  const [stage, setStage] = React.useState<LoadingStage>('idle');
  const [loadedStages, setLoadedStages] = React.useState<Set<LoadingStage>>(new Set());

  const advanceStage = React.useCallback((nextStage: LoadingStage) => {
    setStage(nextStage);
    setLoadedStages(prev => new Set(prev).add(nextStage));
    onStageChange?.(nextStage);
  }, [onStageChange]);

  React.useEffect(() => {
    if (!enabled) return;

    // Stage 1: Load stats (immediate)
    const statsTimer = setTimeout(() => advanceStage('stats'), 0);

    // Stage 2: Load charts (after 500ms)
    const chartsTimer = setTimeout(() => advanceStage('charts'), 500);

    // Stage 3: Load activity (after 1000ms)
    const activityTimer = setTimeout(() => advanceStage('activity'), 1000);

    // Stage 4: Complete (after 1500ms)
    const completeTimer = setTimeout(() => advanceStage('complete'), 1500);

    return () => {
      clearTimeout(statsTimer);
      clearTimeout(chartsTimer);
      clearTimeout(activityTimer);
      clearTimeout(completeTimer);
    };
  }, [enabled, advanceStage]);

  return {
    stage,
    loadedStages,
    shouldLoadStats: stage !== 'idle',
    shouldLoadCharts: loadedStages.has('stats') || loadedStages.has('charts'),
    shouldLoadActivity: loadedStages.has('charts') || loadedStages.has('activity'),
    isComplete: stage === 'complete',
  };
}

/**
 * Hook for skeleton fade-out animation
 */
export function useFadeIn(isLoading: boolean, delay: number = 0) {
  const [isVisible, setIsVisible] = React.useState(true);
  const [shouldRender, setShouldRender] = React.useState(true);

  React.useEffect(() => {
    if (!isLoading) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(() => setShouldRender(false), 300); // Match CSS transition
      }, delay);
      return () => clearTimeout(timer);
    } else {
      setIsVisible(true);
      setShouldRender(true);
    }
  }, [isLoading, delay]);

  return {
    isVisible,
    shouldRender,
    className: isVisible ? 'opacity-100' : 'opacity-0 transition-opacity duration-300',
  };
}

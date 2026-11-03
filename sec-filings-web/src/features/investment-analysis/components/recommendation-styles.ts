import type { RecommendationAction } from '../types';

export const RECOMMENDATION_STYLES: Record<
  RecommendationAction,
  { bg: string; border: string; text: string; bar: string }
> = {
  BUY: {
    bg: 'bg-success/10',
    border: 'border-success',
    text: 'text-success',
    bar: 'bg-success',
  },
  SELL: {
    bg: 'bg-danger/10',
    border: 'border-danger',
    text: 'text-danger',
    bar: 'bg-danger',
  },
  HOLD: {
    bg: 'bg-warning/10',
    border: 'border-warning',
    text: 'text-warning',
    bar: 'bg-warning',
  },
} as const;

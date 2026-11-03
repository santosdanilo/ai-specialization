import type { RecommendationAction } from '../types';

export const RECOMMENDATION_STYLES: Record<
  RecommendationAction,
  { bg: string; border: string; text: string }
> = {
  BUY: {
    bg: 'bg-green-50',
    border: 'border-green-500',
    text: 'text-green-700',
  },
  SELL: {
    bg: 'bg-red-50',
    border: 'border-red-500',
    text: 'text-red-700',
  },
  HOLD: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-500',
    text: 'text-yellow-700',
  },
} as const;

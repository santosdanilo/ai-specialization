import React from 'react';

interface LoadingSkeletonProps {
  /** Variante do skeleton: simples para RAG, completo para Agent */
  variant?: 'simple' | 'full';
}

export function LoadingSkeleton({ variant = 'simple' }: LoadingSkeletonProps) {
  if (variant === 'simple') {
    return (
      <div className="space-y-3">
        <div className="skeleton-bar h-4 w-3/4"></div>
        <div className="skeleton-bar h-4 w-full"></div>
        <div className="skeleton-bar h-4 w-5/6"></div>
        <div className="skeleton-bar h-4 w-2/3"></div>
      </div>
    );
  }

  // Skeleton completo para o modo Agent
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex justify-between items-center border-b pb-2">
        <div className="skeleton-bar h-6 w-48"></div>
        <div className="skeleton-bar h-4 w-14"></div>
      </div>

      {/* Recommendation banner skeleton */}
      <div className="p-4 rounded-xl border border-border">
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="skeleton-bar h-6 w-32"></div>
          <div className="skeleton-bar h-4 w-28"></div>
        </div>
        <div className="skeleton-bar mb-3 h-1.5 w-full"></div>
        <div className="skeleton-bar h-4 w-full"></div>
        <div className="skeleton-bar mt-2 h-4 w-3/4"></div>
      </div>

      {/* Three cards skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-card p-4 rounded-xl border border-border">
            <div className="flex items-center gap-2 mb-3">
              <div className="skeleton-bar h-2 w-2"></div>
              <div className="skeleton-bar h-3 w-24"></div>
            </div>
            <div className="space-y-2">
              <div className="skeleton-bar h-4 w-full"></div>
              <div className="skeleton-bar h-4 w-2/3"></div>
              <div className="skeleton-bar h-4 w-3/4"></div>
            </div>
          </div>
        ))}
      </div>

      {/* Risk/Opportunity skeleton */}
      <div className="grid grid-cols-2 gap-4">
        {[1, 2].map((i) => (
          <div key={i} className="p-4 rounded-xl border border-border">
            <div className="flex items-center justify-between mb-3">
              <div className="skeleton-bar h-3 w-24"></div>
              <div className="skeleton-bar h-4 w-8"></div>
            </div>
            <div className="space-y-2">
              <div className="skeleton-bar h-3 w-full"></div>
              <div className="skeleton-bar h-3 w-5/6"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

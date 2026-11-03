import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorDisplayProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorDisplay({ message, onRetry }: ErrorDisplayProps) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-danger/30 bg-danger/5 p-4">
      <AlertCircle className="h-5 w-5 text-danger mt-0.5 shrink-0" />

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground">
          Error processing request
        </p>
        <p className="text-sm text-muted-foreground mt-1 break-words font-mono">
          {message}
        </p>

        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-3 inline-flex items-center gap-1.5 rounded-md border border-border bg-card px-2.5 py-1.5 text-xs font-medium text-foreground hover:bg-muted transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Try again
          </button>
        )}
      </div>
    </div>
  );
}

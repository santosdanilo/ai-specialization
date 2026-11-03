import React from 'react';
import { BarChart3, FileText, Newspaper, TrendingUp } from 'lucide-react';

// ===========================================
// Estado vazio do chat, por modo de análise
// ===========================================

const AGENT_CAPABILITIES = [
  {
    icon: BarChart3,
    title: 'Fundamental',
    tone: 'bg-primary/10 border-primary/20',
    iconColor: 'text-primary',
    description: 'Investment thesis, grade and recommendation extracted from SEC filings.',
  },
  {
    icon: TrendingUp,
    title: 'Momentum',
    tone: 'bg-warning/10 border-warning/20',
    iconColor: 'text-warning',
    description: 'Drivers, risks and short-term outlook based on price action.',
  },
  {
    icon: Newspaper,
    title: 'Sentiment',
    tone: 'bg-success/10 border-success/20',
    iconColor: 'text-success',
    description: 'Key news themes, catalysts and overall market outlook.',
  },
];

interface EmptyStateProps {
  isAgentMode: boolean;
}

export function EmptyState({ isAgentMode }: EmptyStateProps) {
  if (!isAgentMode) {
    // Modo RAG: respostas fundamentadas em documentos
    return (
      <div className="rounded-xl border border-primary/20 bg-primary/10 p-4">
        <div className="mb-2 flex items-center gap-2">
          <FileText className="h-4 w-4 text-primary" aria-hidden />
          <h4 className="text-xs font-semibold uppercase tracking-wide text-foreground">
            Filings-grounded answers
          </h4>
        </div>
        <p className="text-xs leading-relaxed text-muted-foreground">
          Ask anything about companies or filings — answers are retrieved from the most
          relevant SEC 10-K and 10-Q excerpts with citations.
        </p>
      </div>
    );
  }

  // Modo Agent: análise multi-stream
  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
      {AGENT_CAPABILITIES.map(({ icon: Icon, title, tone, iconColor, description }) => (
        <div
          key={title}
          className={'rounded-xl border p-4 ' + tone}
        >
          <div className="mb-2 flex items-center gap-2">
            <Icon className={'h-4 w-4 ' + iconColor} aria-hidden />
            <h4 className="text-xs font-semibold uppercase tracking-wide text-foreground">{title}</h4>
          </div>
          <p className="text-xs leading-relaxed text-muted-foreground">{description}</p>
        </div>
      ))}
    </div>
  );
}

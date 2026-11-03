import React from 'react';

// ===========================================
// Componente de Card de Análise
// ===========================================

/**
 * AnalysisCard
 *
 * Card reutilizável para exibir cada tipo de análise.
 * Demonstra o princípio DRY (Don't Repeat Yourself) -
 * um único componente serve para fundamental, momentum e sentiment.
 */

type CardTone = 'primary' | 'success' | 'warning' | 'danger';

const TONE_STYLES: Record<CardTone, { dot: string; label: string }> = {
  primary: { dot: 'bg-primary', label: 'text-muted-foreground' },
  success: { dot: 'bg-success', label: 'text-success' },
  warning: { dot: 'bg-warning', label: 'text-warning' },
  danger: { dot: 'bg-danger', label: 'text-danger' },
};

interface AnalysisCardProps {
  /** Título do card */
  title: string;
  /** Itens a serem exibidos no formato label: value */
  items: Array<{
    label: string;
    value: string | number;
    /** Exibe o valor em fonte mono (scores, percentuais) */
    mono?: boolean;
  }>;
  /** Texto adicional opcional (ex: thesis ou outlook) */
  description?: string;
  /** Cor do indicador do card */
  tone?: CardTone;
}

export function AnalysisCard({ title, items, description, tone = 'primary' }: AnalysisCardProps) {
  const styles = TONE_STYLES[tone];

  return (
    <div className="bg-card p-4 rounded-xl border border-border shadow-card">
      <div className="flex items-center gap-2 mb-3">
        <span className={'h-2 w-2 rounded-full ' + styles.dot} aria-hidden />
        <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{title}</h4>
      </div>

      <div className="text-[13px]">
        <ul className="divide-y divide-border/60">
          {items.map((item, index) => (
            <li key={index} className="flex items-baseline justify-between gap-2 py-1.5 first:pt-0 last:pb-0">
              <span className="text-muted-foreground">{item.label}</span>{' '}
              <span
                className={
                  'font-medium text-foreground tabular-nums ' + (item.mono ? 'font-mono' : '')
                }
              >
                {item.value}
              </span>
            </li>
          ))}
        </ul>

        {description && (
          <p className="text-xs text-muted-foreground mt-3 pt-3 border-t border-border leading-relaxed">
            {description}
          </p>
        )}
      </div>
    </div>
  );
}

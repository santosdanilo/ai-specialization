import React from 'react';
import { ArrowDownRight, ArrowUpRight } from 'lucide-react';
import { cn } from '@/shared/lib/utils';

// ===========================================
// Componente de Riscos e Oportunidades
// ===========================================

/**
 * RiskOpportunityPanel
 *
 * Exibe lado a lado os riscos e oportunidades identificados.
 * O uso de cores (vermelho/verde) segue convenções universais
 * de UX financeira.
 */

interface RiskOpportunityPanelProps {
  /** Lista de riscos identificados */
  risks: string[];
  /** Lista de oportunidades identificadas */
  opportunities: string[];
}

export function RiskOpportunityPanel({ risks, opportunities }: RiskOpportunityPanelProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Painel de Riscos */}
      <div className="rounded-xl border border-danger/20 bg-danger/10 p-4">
        <div className="flex items-center justify-between gap-2 mb-2">
          <h4 className={cn('flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide', 'text-danger')} aria-hidden>
            <ArrowDownRight className="h-3.5 w-3.5" />
            Key Risks
          </h4>
          <span className="rounded-full bg-background/60 px-2 py-0.5 text-[11px] font-medium text-muted-foreground tabular-nums">
            {risks.length}
          </span>
        </div>
        <ul className="space-y-2">
          {risks.map((risk, index) => (
            <li
              key={index}
              className="text-sm leading-snug text-foreground flex items-start gap-2 line-clamp-2"
            >
              <span className="text-danger mt-1.5 h-1 w-1 shrink-0 rounded-full bg-danger" aria-hidden />
              <span>{risk}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Painel de Oportunidades */}
      <div className="rounded-xl border border-success/20 bg-success/10 p-4">
        <div className="flex items-center justify-between gap-2 mb-2">
          <h4 className={cn('flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide', 'text-success')} aria-hidden>
            <ArrowUpRight className="h-3.5 w-3.5" />
            Key Opportunities
          </h4>
          <span className="rounded-full bg-background/60 px-2 py-0.5 text-[11px] font-medium text-muted-foreground tabular-nums">
            {opportunities.length}
          </span>
        </div>
        <ul className="space-y-2">
          {opportunities.map((opportunity, index) => (
            <li
              key={index}
              className="text-sm leading-snug text-foreground flex items-start gap-2 line-clamp-2"
            >
              <span className="text-success mt-1.5 h-1 w-1 shrink-0 rounded-full bg-success" aria-hidden />
              <span>{opportunity}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

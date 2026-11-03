import React from 'react';
import { FinalRecommendation } from '../types';
import { RECOMMENDATION_STYLES } from './recommendation-styles';
import { cn } from '@/shared/lib/utils';

// ===========================================
// Componente de Banner de Recomendação
// ===========================================

/**
 * RecommendationBanner
 *
 * Destaca visualmente a recomendação final (BUY/SELL/HOLD).
 * Usa as constantes de estilo para manter consistência e
 * facilitar manutenção.
 */

interface RecommendationBannerProps {
  /** Dados da recomendação final */
  recommendation: FinalRecommendation;
}

export function RecommendationBanner({ recommendation }: RecommendationBannerProps) {
  // Busca os estilos baseado na ação (BUY, SELL, HOLD)
  // Usa HOLD como fallback se a ação não for reconhecida
  const styles = RECOMMENDATION_STYLES[recommendation.action] || RECOMMENDATION_STYLES.HOLD;

  const confidencePercent = Math.round(recommendation.confidence * 100);

  return (
    <div
      className={cn(
        'p-4 md:p-5 rounded-xl border',
        styles.bg,
        styles.border
      )}
    >
      {/* Linha densa: ação + confiança + horizonte */}
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className={cn('font-mono text-lg font-bold tracking-tight tabular-nums', styles.text)}>
          {recommendation.action}
        </span>
        <span className="rounded-full bg-background/60 px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
          Final recommendation
        </span>
        <span className="ml-auto flex items-center gap-2 text-xs text-muted-foreground">
          <span className="tabular-nums font-medium text-foreground">{confidencePercent}%</span>
          <span aria-hidden>·</span>
          <span>Horizon <span className="font-mono tabular-nums text-foreground">{recommendation.time_horizon}</span></span>
        </span>
      </div>

      {/* Barra de confiança */}
      <div className="mb-3 h-1.5 w-full overflow-hidden rounded-full bg-background/60" role="presentation">
        <div
          className={cn('h-full rounded-full', styles.bar)}
          style={{ width: `${confidencePercent}%` }}
        />
      </div>

      {/* Rationale */}
      <p className="text-sm leading-relaxed text-foreground">{recommendation.rationale}</p>
    </div>
  );
}

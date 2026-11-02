export interface FundamentalAnalysis {
  overall_investment_thesis: string;
  investment_grade: InvestmentGrade;
  confidence_score: number;
  key_strengths: string[];
  key_concerns: string[];
  recommendation: FundamentalRecommendation;
}

export interface MomentumAnalysis {
  overall_momentum: MomentumDirection;
  momentum_strength: MomentumStrength;
  key_momentum_drivers: string[];
  momentum_risks: string[];
  short_term_outlook: MarketOutlook;
  momentum_score: number;
}

export interface SentimentAnalysis {
  sentiment_score: number;
  sentiment_direction: SentimentDirection;
  key_news_themes: string[];
  recent_catalysts: string[];
  market_outlook: string;
}

export interface FinalRecommendation {
  action: RecommendationAction;
  confidence: number;
  rationale: string;
  key_risks: string[];
  key_opportunities: string[];
  time_horizon: TimeHorizon;
}

export type RecommendationAction = 'BUY' | 'SELL' | 'HOLD';
export type InvestmentGrade = 'A' | 'B' | 'C' | 'D';
export type FundamentalRecommendation = 'buy' | 'hold' | 'sell' | 'avoid';
export type MomentumDirection = 'positive' | 'neutral' | 'negative';
export type MomentumStrength = 'strong' | 'moderate' | 'weak';
export type MarketOutlook = 'bullish' | 'neutral' | 'bearish';
export type SentimentDirection = 'Positive' | 'Neutral' | 'Negative';
export type TimeHorizon = 'Short-term' | 'Medium-term' | 'Long-term';

export interface AgentAnalysis {
  query: string;
  ticker: string;
  execution_time: number;
  fundamental_analysis: FundamentalAnalysis;
  momentum_analysis: MomentumAnalysis;
  sentiment_analysis: SentimentAnalysis;
  final_recommendation: FinalRecommendation;
}

export interface AnalysisState {
  response: string;
  agentResponse: AgentAnalysis | null;
  isLoading: boolean;
  error: string | null;
}
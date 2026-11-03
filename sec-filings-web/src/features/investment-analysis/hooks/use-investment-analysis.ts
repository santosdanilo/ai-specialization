import { useCallback, useState } from 'react';

import { fetchAgentAnalysis, fetchRAGAnalysis } from '../api';
import { AnalysisState } from '../types';

export function useInvestmentAnalysis() {
  const [state, setState] = useState<AnalysisState>({
    response: '',
    agentResponse: null,
    isLoading: false,
    error: null,
  });

  const resetState = useCallback(() => {
    setState({
      response: '',
      agentResponse: null,
      isLoading: false,
      error: null,
    });
  }, []);

  const analyzeWithRAG = useCallback(async (query: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null, response: '' }));

    try {
      const { answer } = await fetchRAGAnalysis(query);
      setState(prev => ({ ...prev, response: answer, isLoading: false }));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setState(prev => ({ ...prev, error: errorMessage, isLoading: false }));
      console.error('RAG Error:', err);
    }
  }, []);

  const analyzeWithAgent = useCallback(async (query: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null, agentResponse: null }));

    try {
      const agentResponse = await fetchAgentAnalysis(query);
      setState(prev => ({ ...prev, agentResponse, isLoading: false }));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setState(prev => ({ ...prev, error: errorMessage, isLoading: false }));
      console.error('Agent Analysis Error:', err);
    }
  }, []);

  const retry = useCallback((query: string, isAgentMode: boolean) => {
    if (isAgentMode) {
      analyzeWithAgent(query);
    } else {
      analyzeWithRAG(query);
    }
  }, [analyzeWithAgent, analyzeWithRAG]);

  return {
    ...state,

    analyzeWithRAG,
    analyzeWithAgent,
    resetState,
    retry,
  };
}

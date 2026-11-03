import type { AgentAnalysis } from './types';

const API_CONFIG = {
  RAG_ENDPOINT: '/api/rag',
  AGENT_ENDPOINT: '/api/agent',
  DEFAULT_LIMIT: 5,
  AGENT_LIMIT: 3,
} as const;

async function postJson<T>(endpoint: string, body: Record<string, unknown>): Promise<T> {
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchRAGAnalysis(query: string): Promise<{ answer: string }> {
  return postJson(API_CONFIG.RAG_ENDPOINT, {
    query,
    limit: API_CONFIG.DEFAULT_LIMIT,
  });
}

export async function fetchAgentAnalysis(query: string): Promise<AgentAnalysis> {
  const startTime = Date.now();
  const data = await postJson<AgentAnalysis>(API_CONFIG.AGENT_ENDPOINT, {
    query,
    limit: API_CONFIG.AGENT_LIMIT,
  });

  return {
    ...data,
    execution_time: (Date.now() - startTime) / 1000,
  };
}

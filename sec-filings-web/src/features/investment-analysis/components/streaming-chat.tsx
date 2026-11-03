'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Search, Send, TrendingUp } from 'lucide-react';

import { useInvestmentAnalysis } from '../hooks/use-investment-analysis';
import { UI_MESSAGES } from '../constants';
import { LoadingSkeleton, ErrorDisplay } from '@/shared/components/ui';
import { AgentResponse } from './agent-response';
import { EmptyState } from './empty-state';

const EXAMPLE_QUERIES = [
  'Analyze AAPL fundamentals',
  'Latest 10-K risk factors for MSFT',
  'Market sentiment for TSLA',
];

export function StreamingChat() {
  const [query, setQuery] = useState('');
  const [isAgentMode, setIsAgentMode] = useState(false);

  const {
    response,
    agentResponse,
    isLoading,
    error,
    analyzeWithRAG,
    analyzeWithAgent,
    retry,
    resetState,
  } = useInvestmentAnalysis();

  const handleModeChange = (value: boolean) => {
    setIsAgentMode(value);
    setQuery('');
    resetState();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    if (isAgentMode) {
      await analyzeWithAgent(query);
    } else {
      await analyzeWithRAG(query);
    }
  };

  const handleRetry = () => {
    retry(query, isAgentMode);
  };

  const showExamples = !query.trim() && !isLoading && !response && !agentResponse && !error;

  return (
    <div className="flex h-full w-full min-h-0 flex-col">
      <div className="flex min-h-0 w-full flex-1 flex-col rounded-xl border border-border bg-card shadow-card">
        <form onSubmit={handleSubmit} className="flex min-h-0 flex-1 flex-col space-y-4 p-4 md:p-5">

          {/* Toggle de Modo */}
          <ModeToggle
            isAgentMode={isAgentMode}
            onChange={handleModeChange}
            disabled={isLoading}
          />

          {/* Input e Botão de Submit */}
          <SearchInput
            query={query}
            onChange={setQuery}
            isLoading={isLoading}
            isAgentMode={isAgentMode}
          />

          {/* Consultas de exemplo */}
          {showExamples && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-muted-foreground">Try:</span>
              {EXAMPLE_QUERIES.map((example) => (
                <button
                  key={example}
                  type="button"
                  onClick={() => setQuery(example)}
                  className="rounded-full border border-border bg-muted/50 px-3 py-1 text-xs text-muted-foreground hover:border-primary/40 hover:text-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  {example}
                </button>
              ))}
            </div>
          )}

          {/* Área de Erro */}
          {error && (
            <ErrorDisplay message={error} onRetry={handleRetry} />
          )}

          {/* Área de Resposta */}
          <ResponseArea
            isLoading={isLoading}
            isAgentMode={isAgentMode}
            response={response}
            agentResponse={agentResponse}
          />
        </form>
      </div>
    </div>
  );
}

/**
 * ModeToggle - Alterna entre modo RAG e Agent (segmented control)
 */
interface ModeToggleProps {
  isAgentMode: boolean;
  onChange: (value: boolean) => void;
  disabled: boolean;
}

function ModeToggle({ isAgentMode, onChange, disabled }: ModeToggleProps) {
  return (
    <div className="flex items-center gap-3">
      <div
        role="group"
        aria-label="Analysis mode"
        className="inline-flex rounded-lg bg-muted p-1"
      >
        <SegmentedOption
          icon={<Search className="h-3.5 w-3.5" />}
          label="RAG"
          active={!isAgentMode}
          disabled={disabled}
          onClick={() => onChange(false)}
        />
        <SegmentedOption
          icon={<TrendingUp className="h-3.5 w-3.5" />}
          label="Agent"
          active={isAgentMode}
          disabled={disabled}
          onClick={() => onChange(true)}
        />
      </div>
      {isAgentMode && (
        <span className="text-xs text-muted-foreground">
          {UI_MESSAGES.AGENT_DESCRIPTION}
        </span>
      )}
    </div>
  );
}

interface SegmentedOptionProps {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  disabled: boolean;
  onClick: () => void;
}

function SegmentedOption({ icon, label, active, disabled, onClick }: SegmentedOptionProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-pressed={active}
      className={
        'inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed ' +
        (active
          ? 'bg-card text-foreground shadow-card'
          : 'text-muted-foreground hover:text-foreground')
      }
    >
      {icon}
      {label}
    </button>
  );
}

/**
 * SearchInput - Campo de busca com botão de submit
 */
interface SearchInputProps {
  query: string;
  onChange: (value: string) => void;
  isLoading: boolean;
  isAgentMode: boolean;
}

function SearchInput({ query, onChange, isLoading, isAgentMode }: SearchInputProps) {
  const ModeIcon = isAgentMode ? TrendingUp : Search;

  return (
    <div className="flex gap-2">
      <div className="relative flex-1">
        <ModeIcon
          className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden
        />
        <input
          type="text"
          value={query}
          onChange={(e) => onChange(e.target.value)}
          placeholder={isAgentMode ? UI_MESSAGES.PLACEHOLDER_AGENT : UI_MESSAGES.PLACEHOLDER_RAG}
          className="w-full py-2.5 pl-10 pr-3 bg-background border border-border rounded-lg text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary disabled:opacity-50"
          disabled={isLoading}
        />
      </div>
      <button
        type="submit"
        disabled={isLoading || !query.trim()}
        className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        aria-label="Send message"
      >
        {isLoading ? (
          UI_MESSAGES.LOADING
        ) : (
          <>
            <span>{isAgentMode ? 'Analyze' : 'Search'}</span>
            <Send className="h-4 w-4" />
          </>
        )}
      </button>
    </div>
  );
}

/**
 * ResponseArea - Área que exibe a resposta ou loading
 */
interface ResponseAreaProps {
  isLoading: boolean;
  isAgentMode: boolean;
  response: string;
  agentResponse: ReturnType<typeof useInvestmentAnalysis>['agentResponse'];
}

function ResponseArea({ isLoading, isAgentMode, response, agentResponse }: ResponseAreaProps) {
  const isEmpty = !isLoading && ((isAgentMode && !agentResponse) || (!isAgentMode && !response));

  return (
    <div className="relative min-h-48 flex-1 overflow-y-auto rounded-lg bg-accent p-4 scrollbar-slim">
      {/* Estado de Loading */}
      {isLoading && (
        <LoadingSkeleton variant={isAgentMode ? 'full' : 'simple'} />
      )}

      {/* Resposta do Agent */}
      {!isLoading && isAgentMode && agentResponse && (
        <div className="animate-fade-in-up">
          <AgentResponse analysis={agentResponse} />
        </div>
      )}

      {/* Resposta do RAG */}
      {!isLoading && !isAgentMode && (
        <div className="prose prose-sm max-w-none animate-fade-in-up">
          <ReactMarkdown>
            {response || ''}
          </ReactMarkdown>
        </div>
      )}

      {/* Estado vazio */}
      {isEmpty && (
        <div className="flex flex-col gap-4">
          <EmptyState isAgentMode={isAgentMode} />
          <p className="text-center text-xs text-muted-foreground">
            {UI_MESSAGES.EMPTY_RESPONSE}
          </p>
        </div>
      )}
    </div>
  );
}

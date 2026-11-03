'use client';
import { StreamingChat } from "@/features/investment-analysis";
import { ThemeToggle } from "@/shared/components/ui";
import { LineChart } from "lucide-react";

export default function Home() {

  return (
    <div className="flex h-dvh flex-col overflow-hidden">
      <header className="z-10 shrink-0 border-b border-border bg-background/80 backdrop-blur">
        <div className="container px-4 md:px-6 flex h-14 items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <LineChart className="h-4 w-4" />
            </span>
            <span className="font-semibold tracking-tight text-foreground">SEC Filings RAG</span>
            <span className="rounded-full border border-primary/30 bg-primary/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-primary">Beta</span>
          </div>
          <ThemeToggle />
        </div>
      </header>

      <main className="min-h-0 flex-1 py-6 md:py-8">
        <div className="mx-auto flex h-full max-w-4xl flex-col px-4 md:px-0">
          <div className="shrink-0">
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-primary">AI investment analyst</p>
            <h1 className="text-xl font-semibold tracking-tight text-foreground md:text-2xl">Investment intelligence at your fingertips</h1>
            <p className="text-sm text-muted-foreground mt-2 mb-6 max-w-[50.4rem]">
              Ask anything about companies, stocks, or market trends. Enable Multi-Stream Analysis for comprehensive insights powered by fundamental, momentum, and sentiment analysis.
            </p>
          </div>
          <div className="min-h-0 flex-1">
            <StreamingChat />
          </div>
        </div>
      </main>

      <footer className="shrink-0 border-t border-border py-4">
        <div className="container px-4 md:px-6">
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Dev + Eficiente (Engenharia de IA)
          </p>
        </div>
      </footer>
    </div>
  );
}

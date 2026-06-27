import {
  AlertTriangle,
  FolderOpen,
  ListChecks,
  Sparkles,
  Tag,
} from "lucide-react";

import { AnalysisCard } from "@/components/analysis/AnalysisCard";
import type { EmailAnalysisResult } from "@/lib/types/analysis";

const PRIORITY_STYLES: Record<string, string> = {
  High: "bg-red-100 text-red-800 ring-red-200",
  Medium: "bg-amber-100 text-amber-900 ring-amber-200",
  Low: "bg-slate-100 text-slate-700 ring-slate-200",
};

interface AnalysisPanelProps {
  analysis: EmailAnalysisResult | null;
  isAnalyzing: boolean;
  onAnalyze: () => void;
}

export function AnalysisPanel({ analysis, isAnalyzing, onAnalyze }: AnalysisPanelProps) {
  const priorityStyle =
    analysis?.priority && PRIORITY_STYLES[analysis.priority]
      ? PRIORITY_STYLES[analysis.priority]
      : "bg-slate-100 text-slate-700 ring-slate-200";

  return (
    <section className="flex h-full min-h-0 flex-col gap-4">
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-3">
        <div className="min-w-0">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            AI Analysis
          </h2>
          <p className="text-xs text-slate-400">Rule-based classifier</p>
        </div>
        <button
          type="button"
          onClick={onAnalyze}
          disabled={isAnalyzing}
          className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <Sparkles className="h-4 w-4" />
          {isAnalyzing ? "Analyzing…" : analysis ? "Re-analyze" : "Analyze"}
        </button>
      </div>

      {!analysis ? (
        <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50/80 p-6 text-center">
          <Sparkles className="mb-3 h-8 w-8 text-indigo-400" />
          <p className="text-sm font-medium text-slate-700">No analysis yet</p>
          <p className="mt-1 max-w-xs text-sm text-slate-500">
            Select an email and run analysis to see priority, category, and suggested actions.
          </p>
        </div>
      ) : (
        <div className="min-h-0 flex-1 overflow-y-auto">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <AnalysisCard
              title="Priority"
              icon={<AlertTriangle className="h-4 w-4" />}
              accent={analysis.priority === "High" ? "urgent" : "default"}
            >
              <span
                className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset ${priorityStyle}`}
              >
                {analysis.priority}
              </span>
            </AnalysisCard>

            <AnalysisCard title="Category" icon={<Tag className="h-4 w-4" />}>
              <p className="font-medium">{analysis.category}</p>
            </AnalysisCard>

            <AnalysisCard
              title="Summary"
              icon={<FolderOpen className="h-4 w-4" />}
              accent="default"
              className="sm:col-span-2"
            >
              <p>{analysis.summary}</p>
            </AnalysisCard>

            <AnalysisCard
              title="Action Items"
              icon={<ListChecks className="h-4 w-4" />}
              accent="action"
              className="sm:col-span-2"
            >
              <ul className="space-y-1.5">
                {analysis.action_items.map((item) => (
                  <li key={item} className="flex items-start gap-2 break-words text-sm text-indigo-900">
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-indigo-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </AnalysisCard>
          </div>
        </div>
      )}
    </section>
  );
}

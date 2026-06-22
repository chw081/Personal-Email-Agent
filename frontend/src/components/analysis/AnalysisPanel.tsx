import {
  AlertTriangle,
  FolderOpen,
  MessageSquareReply,
  Sparkles,
  Tag,
} from "lucide-react";

import { AnalysisCard } from "@/components/analysis/AnalysisCard";
import { PriorityBadge } from "@/components/analysis/PriorityBadge";
import type { EmailAnalysis } from "@/lib/types/analysis";
import { formatActionLabel, formatDomainLabel } from "@/lib/utils/format";

interface AnalysisPanelProps {
  analysis: EmailAnalysis | null;
  isAnalyzing: boolean;
  onAnalyze: () => void;
}

export function AnalysisPanel({ analysis, isAnalyzing, onAnalyze }: AnalysisPanelProps) {
  return (
    <section className="flex h-full flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            AI Analysis
          </h2>
          <p className="text-xs text-slate-400">Mock classifier · demo mode</p>
        </div>
        <button
          type="button"
          onClick={onAnalyze}
          disabled={isAnalyzing}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <Sparkles className="h-4 w-4" />
          {isAnalyzing ? "Analyzing…" : analysis ? "Re-analyze" : "Analyze"}
        </button>
      </div>

      {!analysis ? (
        <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50/80 p-8 text-center">
          <Sparkles className="mb-3 h-8 w-8 text-indigo-400" />
          <p className="text-sm font-medium text-slate-700">No analysis yet</p>
          <p className="mt-1 max-w-xs text-sm text-slate-500">
            Select an email and run analysis to see priority, category, and suggested action.
          </p>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          <AnalysisCard
            title="Priority"
            icon={<AlertTriangle className="h-4 w-4" />}
            accent={analysis.priority === "critical" ? "urgent" : "default"}
          >
            <PriorityBadge priority={analysis.priority} />
            <p className="mt-2 text-xs text-slate-500">
              Confidence: {Math.round(analysis.confidence * 100)}%
            </p>
          </AnalysisCard>

          <AnalysisCard title="Category" icon={<Tag className="h-4 w-4" />}>
            <p className="font-medium">{formatDomainLabel(analysis.domain)}</p>
            <p className="mt-1 text-xs text-slate-500">{analysis.subcategory.replace(/_/g, " ")}</p>
          </AnalysisCard>

          <AnalysisCard
            title="Summary"
            icon={<FolderOpen className="h-4 w-4" />}
            accent="default"
          >
            <p>{analysis.reason ?? "No summary available."}</p>
          </AnalysisCard>

          <AnalysisCard
            title="Suggested Action"
            icon={<MessageSquareReply className="h-4 w-4" />}
            accent="action"
          >
            <p className="text-base font-semibold text-indigo-900">
              {formatActionLabel(analysis.action)}
            </p>
            <p className="mt-1 text-xs text-indigo-700/80">{analysis.model_name}</p>
          </AnalysisCard>
        </div>
      )}
    </section>
  );
}

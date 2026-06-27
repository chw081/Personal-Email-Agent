import { AlertCircle, BarChart3, Loader2, Sparkles } from "lucide-react";

import type { InboxSummaryResponse } from "@/lib/types/analysis";
import type { InboxStats } from "@/lib/utils/inbox-stats";

interface InboxSummaryCardProps {
  stats: InboxStats;
  inboxSummary: InboxSummaryResponse | null;
  isAnalyzingInbox: boolean;
  isGeneratingSummary: boolean;
  bulkError: string | null;
  summaryError: string | null;
  onAnalyzeInbox: () => void;
  onGenerateSummary: () => void;
}

function StatItem({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-slate-50 px-3 py-2">
      <p className="text-[11px] font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-0.5 text-lg font-semibold text-slate-900">{value}</p>
    </div>
  );
}

export function InboxSummaryCard({
  stats,
  inboxSummary,
  isAnalyzingInbox,
  isGeneratingSummary,
  bulkError,
  summaryError,
  onAnalyzeInbox,
  onGenerateSummary,
}: InboxSummaryCardProps) {
  const hasEmails = stats.loaded > 0;
  const isBusy = isAnalyzingInbox || isGeneratingSummary;

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3">
        <h2 className="text-sm font-semibold text-slate-900">Inbox Overview</h2>
        <p className="text-xs text-slate-500">Global inbox stats</p>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <StatItem label="Loaded" value={stats.loaded} />
        <StatItem label="Analyzed" value={stats.analyzed} />
        <StatItem label="Urgent" value={stats.urgent} />
        <StatItem label="Needs reply" value={stats.needsReply} />
      </div>

      {inboxSummary && (
        <p className="mt-3 line-clamp-3 text-xs leading-5 text-slate-600">{inboxSummary.summary}</p>
      )}

      {(bulkError || summaryError) && (
        <div className="mt-3 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-2.5 py-2 text-xs text-red-700">
          <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <p>{bulkError ?? summaryError}</p>
        </div>
      )}

      <div className="mt-3 flex flex-col gap-2">
        <button
          type="button"
          onClick={onAnalyzeInbox}
          disabled={!hasEmails || isBusy}
          className="inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-medium text-white shadow-sm transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isAnalyzingInbox ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Sparkles className="h-3.5 w-3.5" />
          )}
          {isAnalyzingInbox ? "Analyzing…" : "Analyze Inbox"}
        </button>

        <button
          type="button"
          onClick={onGenerateSummary}
          disabled={!hasEmails || isBusy}
          className="inline-flex w-full items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isGeneratingSummary ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <BarChart3 className="h-3.5 w-3.5" />
          )}
          {isGeneratingSummary ? "Generating…" : "Generate Summary"}
        </button>
      </div>
    </section>
  );
}

import { AlertCircle, ListChecks, Sparkles, Tag } from "lucide-react";

import type { EmailAnalysisResult } from "@/lib/types/analysis";

const PRIORITY_STYLES: Record<string, string> = {
  High: "bg-red-100 text-red-800 ring-red-200",
  Medium: "bg-amber-100 text-amber-900 ring-amber-200",
  Low: "bg-slate-100 text-slate-700 ring-slate-200",
};

interface InlineEmailAnalysisProps {
  analysis: EmailAnalysisResult;
}

export function InlineEmailAnalysis({ analysis }: InlineEmailAnalysisProps) {
  const priorityStyle =
    PRIORITY_STYLES[analysis.priority] ?? "bg-slate-100 text-slate-700 ring-slate-200";

  return (
    <div className="mt-3 space-y-2.5 rounded-lg border border-indigo-100 bg-indigo-50/50 p-3">
      <div className="flex flex-wrap items-center gap-2">
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset ${priorityStyle}`}
        >
          {analysis.priority}
        </span>
        <span className="inline-flex items-center gap-1 rounded-full bg-white px-2.5 py-0.5 text-xs font-medium text-slate-700 ring-1 ring-slate-200">
          <Tag className="h-3 w-3 text-slate-400" />
          {analysis.category}
        </span>
      </div>

      <div>
        <p className="mb-1 flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-slate-500">
          <Sparkles className="h-3 w-3" />
          Summary
        </p>
        <p className="text-sm leading-5 text-slate-700">{analysis.summary}</p>
      </div>

      {analysis.action_items.length > 0 && (
        <div>
          <p className="mb-1 flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-slate-500">
            <ListChecks className="h-3 w-3" />
            Action items
          </p>
          <ul className="space-y-1">
            {analysis.action_items.map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm text-slate-700">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-indigo-400" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

interface InlineEmailAnalysisErrorProps {
  message: string;
}

export function InlineEmailAnalysisError({ message }: InlineEmailAnalysisErrorProps) {
  return (
    <div className="mt-3 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
      <p>{message}</p>
    </div>
  );
}

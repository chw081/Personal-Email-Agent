import { Paperclip } from "lucide-react";

import type { EmailAnalysisResult } from "@/lib/types/analysis";
import type { Email } from "@/lib/types/email";
import {
  formatEmailDate,
  truncateText,
  withFallback,
} from "@/lib/utils/format";

const PRIORITY_STYLES: Record<string, string> = {
  High: "bg-red-100 text-red-800",
  Medium: "bg-amber-100 text-amber-900",
  Low: "bg-slate-100 text-slate-700",
};

interface InboxItemProps {
  email: Email;
  analysisResult?: EmailAnalysisResult;
  isSelected: boolean;
  onSelect: () => void;
}

export function InboxItem({
  email,
  analysisResult,
  isSelected,
  onSelect,
}: InboxItemProps) {
  const sender = truncateText(withFallback(email.sender, "Unknown sender"), 36);
  const subject = truncateText(withFallback(email.subject, "(No subject)"), 72);
  const snippet = truncateText(withFallback(email.snippet, "No preview available."), 80);
  const dateLabel = formatEmailDate(email.received_at);
  const priorityStyle =
    analysisResult?.priority && PRIORITY_STYLES[analysisResult.priority]
      ? PRIORITY_STYLES[analysisResult.priority]
      : null;

  return (
    <button
      type="button"
      onClick={onSelect}
      aria-current={isSelected ? "true" : undefined}
      className={`w-full border-b border-slate-100 px-4 py-3.5 text-left transition ${
        isSelected
          ? "bg-indigo-50/80 ring-1 ring-inset ring-indigo-200"
          : "hover:bg-slate-50"
      }`}
    >
      <div className="space-y-1.5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 items-center gap-1.5">
            {email.is_unread && (
              <span
                className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-indigo-500"
                aria-label="Unread"
              />
            )}
            <p
              className={`truncate text-sm ${
                email.is_unread ? "font-semibold text-slate-900" : "font-medium text-slate-700"
              }`}
              title={withFallback(email.sender, "Unknown sender")}
            >
              {sender}
            </p>
            {email.has_attachment && (
              <Paperclip
                className="h-3.5 w-3.5 shrink-0 text-slate-400"
                aria-label="Has attachment"
              />
            )}
          </div>

          <div className="flex shrink-0 flex-col items-end gap-1">
            <time
              className="whitespace-nowrap text-xs text-slate-400"
              dateTime={email.received_at ?? undefined}
              title={withFallback(email.received_at, "Unknown date")}
            >
              {dateLabel}
            </time>
            {analysisResult && priorityStyle && (
              <span
                className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ${priorityStyle}`}
              >
                {analysisResult.priority}
              </span>
            )}
          </div>
        </div>

        <p
          className={`truncate text-sm ${
            email.is_unread ? "font-medium text-slate-900" : "text-slate-800"
          }`}
          title={withFallback(email.subject, "(No subject)")}
        >
          {subject}
        </p>

        <p
          className="line-clamp-1 text-xs leading-5 text-slate-500"
          title={withFallback(email.snippet, "No preview available.")}
        >
          {snippet}
        </p>
      </div>
    </button>
  );
}

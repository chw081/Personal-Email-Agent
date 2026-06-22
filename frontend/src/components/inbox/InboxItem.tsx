import { Paperclip } from "lucide-react";

import { PriorityBadge } from "@/components/analysis/PriorityBadge";
import type { EmailAnalysis } from "@/lib/types/analysis";
import type { Email } from "@/lib/types/email";
import { formatRelativeTime } from "@/lib/utils/format";

interface InboxItemProps {
  email: Email;
  analysis?: EmailAnalysis;
  isSelected: boolean;
  onSelect: () => void;
}

export function InboxItem({ email, analysis, isSelected, onSelect }: InboxItemProps) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`w-full border-b border-slate-100 px-4 py-3 text-left transition ${
        isSelected
          ? "bg-indigo-50/80 ring-1 ring-inset ring-indigo-200"
          : "hover:bg-slate-50"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p
              className={`truncate text-sm ${email.is_unread ? "font-semibold text-slate-900" : "font-medium text-slate-700"}`}
            >
              {email.sender}
            </p>
            {email.has_attachment && (
              <Paperclip className="h-3.5 w-3.5 shrink-0 text-slate-400" aria-label="Has attachment" />
            )}
          </div>
          <p className="mt-0.5 truncate text-sm text-slate-800">{email.subject}</p>
          <p className="mt-1 line-clamp-1 text-xs text-slate-500">{email.snippet}</p>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1.5">
          <span className="text-xs text-slate-400">{formatRelativeTime(email.received_at)}</span>
          {analysis && <PriorityBadge priority={analysis.priority} />}
        </div>
      </div>
    </button>
  );
}

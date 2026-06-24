import { AlertCircle, Inbox, Loader2, RefreshCw } from "lucide-react";

import { InboxItem } from "@/components/inbox/InboxItem";
import type { EmailAnalysis } from "@/lib/types/analysis";
import type { Email } from "@/lib/types/email";

interface InboxListProps {
  emails: Email[];
  analyses: Record<string, EmailAnalysis | undefined>;
  selectedEmailId: string | null;
  onSelect: (emailId: string) => void;
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  emptyMessage?: string;
}

export function InboxList({
  emails,
  analyses,
  selectedEmailId,
  onSelect,
  isLoading = false,
  error = null,
  onRetry,
  emptyMessage = "No emails in this bucket.",
}: InboxListProps) {
  if (isLoading) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 p-8 text-sm text-slate-500">
        <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
        <p>Loading Gmail inbox…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 p-8 text-center">
        <AlertCircle className="h-8 w-8 text-red-400" />
        <p className="text-sm font-medium text-slate-800">Could not load emails</p>
        <p className="max-w-sm text-sm text-slate-500">{error}</p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            <RefreshCw className="h-4 w-4" />
            Retry
          </button>
        )}
      </div>
    );
  }

  if (emails.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 p-8 text-sm text-slate-500">
        <Inbox className="h-8 w-8 text-slate-300" />
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {emails.map((email) => (
        <InboxItem
          key={email.id}
          email={email}
          analysis={analyses[email.id]}
          isSelected={email.id === selectedEmailId}
          onSelect={() => onSelect(email.id)}
        />
      ))}
    </div>
  );
}

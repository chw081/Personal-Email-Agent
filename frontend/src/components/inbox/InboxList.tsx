import { InboxItem } from "@/components/inbox/InboxItem";
import type { EmailAnalysis } from "@/lib/types/analysis";
import type { Email } from "@/lib/types/email";

interface InboxListProps {
  emails: Email[];
  analyses: Record<string, EmailAnalysis | undefined>;
  selectedEmailId: string | null;
  onSelect: (emailId: string) => void;
  emptyMessage?: string;
}

export function InboxList({
  emails,
  analyses,
  selectedEmailId,
  onSelect,
  emptyMessage = "No emails in this bucket.",
}: InboxListProps) {
  if (emails.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center p-8 text-sm text-slate-500">
        {emptyMessage}
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

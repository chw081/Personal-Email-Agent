import { Mail } from "lucide-react";

import type { Email } from "@/lib/types/email";
import { formatRelativeTime } from "@/lib/utils/format";

interface EmailDetailProps {
  email: Email | null;
}

export function EmailDetail({ email }: EmailDetailProps) {
  if (!email) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-8 text-center">
        <Mail className="mb-3 h-10 w-10 text-slate-300" />
        <p className="text-sm font-medium text-slate-600">Select an email to read</p>
        <p className="mt-1 text-sm text-slate-400">Choose a message from the inbox list.</p>
      </div>
    );
  }

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <header className="border-b border-slate-100 px-6 py-5">
        <h1 className="text-xl font-semibold leading-snug text-slate-900">{email.subject}</h1>
        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-slate-600">
          <span>
            <span className="font-medium text-slate-800">{email.sender}</span>
            {email.sender_email && (
              <span className="text-slate-400"> &lt;{email.sender_email}&gt;</span>
            )}
          </span>
          <span className="text-slate-400">{formatRelativeTime(email.received_at)}</span>
        </div>
      </header>
      <div className="flex-1 overflow-y-auto px-6 py-5">
        <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">
          {email.body_text ?? email.snippet ?? "No content available."}
        </p>
      </div>
    </article>
  );
}

import type { ReactNode } from "react";
import {
  AlertCircle,
  Clock,
  Inbox,
  MessageSquare,
} from "lucide-react";

import type { Bucket } from "@/lib/types/analysis";
import { BUCKET_DESCRIPTIONS, BUCKET_LABELS } from "@/lib/utils/buckets";

const BUCKET_ICONS: Record<Bucket, ReactNode> = {
  urgent: <AlertCircle className="h-4 w-4" />,
  needs_reply: <MessageSquare className="h-4 w-4" />,
  waiting: <Clock className="h-4 w-4" />,
  fyi: <Inbox className="h-4 w-4" />,
};

const BUCKET_COLORS: Record<Bucket, string> = {
  urgent: "text-red-600 bg-red-50 border-red-200",
  needs_reply: "text-indigo-600 bg-indigo-50 border-indigo-200",
  waiting: "text-amber-700 bg-amber-50 border-amber-200",
  fyi: "text-slate-600 bg-slate-50 border-slate-200",
};

interface BucketSidebarProps {
  activeBucket: Bucket | "all";
  counts: Record<Bucket, number>;
  totalCount: number;
  onSelect: (bucket: Bucket | "all") => void;
}

export function BucketSidebar({
  activeBucket,
  counts,
  totalCount,
  onSelect,
}: BucketSidebarProps) {
  const buckets: Array<Bucket | "all"> = ["all", "urgent", "needs_reply", "waiting", "fyi"];

  return (
    <nav className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
      <p className="mb-2 px-1 text-xs font-semibold uppercase tracking-wider text-slate-500">
        Buckets
      </p>
      <div className="space-y-1">
        {buckets.map((bucket) => {
          const isActive = activeBucket === bucket;
          const label = bucket === "all" ? "All Mail" : BUCKET_LABELS[bucket];
          const count = bucket === "all" ? totalCount : counts[bucket];
          const colorClass =
            bucket === "all" ? "text-slate-700 bg-white border-slate-200" : BUCKET_COLORS[bucket];

          return (
            <button
              key={bucket}
              type="button"
              onClick={() => onSelect(bucket)}
              title={bucket === "all" ? undefined : BUCKET_DESCRIPTIONS[bucket]}
              className={`flex w-full items-center justify-between rounded-lg border px-3 py-2 text-left text-sm transition ${
                isActive
                  ? `${colorClass} font-semibold shadow-sm ring-1 ring-indigo-200`
                  : "border-transparent text-slate-600 hover:bg-slate-50"
              }`}
            >
              <span className="flex items-center gap-2">
                {bucket === "all" ? <Inbox className="h-4 w-4" /> : BUCKET_ICONS[bucket]}
                {label}
              </span>
              <span
                className={`rounded-full px-2 py-0.5 text-xs ${
                  isActive ? "bg-white/80" : "bg-slate-100 text-slate-600"
                }`}
              >
                {count}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}

import type { Priority } from "@/lib/types/analysis";

const STYLES: Record<Priority, string> = {
  critical: "bg-red-100 text-red-800 ring-red-200",
  important: "bg-amber-100 text-amber-900 ring-amber-200",
  normal: "bg-sky-100 text-sky-900 ring-sky-200",
  low: "bg-slate-100 text-slate-700 ring-slate-200",
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset ${STYLES[priority]}`}
    >
      {priority.charAt(0).toUpperCase() + priority.slice(1)}
    </span>
  );
}

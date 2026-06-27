import type { ReactNode } from "react";

interface AnalysisCardProps {
  title: string;
  icon: ReactNode;
  children: ReactNode;
  accent?: "default" | "urgent" | "action";
  className?: string;
}

const ACCENTS = {
  default: "border-slate-200 bg-white",
  urgent: "border-red-200 bg-red-50/60",
  action: "border-indigo-200 bg-indigo-50/60",
};

export function AnalysisCard({
  title,
  icon,
  children,
  accent = "default",
  className = "",
}: AnalysisCardProps) {
  return (
    <div className={`min-w-0 rounded-xl border p-4 shadow-sm ${ACCENTS[accent]} ${className}`}>
      <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-600">
        <span className="shrink-0 text-slate-400">{icon}</span>
        {title}
      </div>
      <div className="min-w-0 text-sm leading-relaxed break-words text-slate-900">{children}</div>
    </div>
  );
}

import type { ReactNode } from "react";

interface AnalysisCardProps {
  title: string;
  icon: ReactNode;
  children: ReactNode;
  accent?: "default" | "urgent" | "action";
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
}: AnalysisCardProps) {
  return (
    <div className={`rounded-xl border p-4 shadow-sm ${ACCENTS[accent]}`}>
      <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-600">
        <span className="text-slate-400">{icon}</span>
        {title}
      </div>
      <div className="text-sm leading-relaxed text-slate-900">{children}</div>
    </div>
  );
}

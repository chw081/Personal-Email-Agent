import { Mail, Sparkles } from "lucide-react";

interface DashboardHeaderProps {
  emailCount: number;
  analyzedCount: number;
  isMockMode: boolean;
}

export function DashboardHeader({
  emailCount,
  analyzedCount,
  isMockMode,
}: DashboardHeaderProps) {
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
          <Mail className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-slate-900">Personal Email Agent</h1>
          <p className="text-sm text-slate-500">AI-powered inbox triage dashboard</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden text-right sm:block">
          <p className="text-sm font-medium text-slate-700">
            {emailCount} emails · {analyzedCount} analyzed
          </p>
          <p className="flex items-center justify-end gap-1 text-xs text-slate-400">
            <Sparkles className="h-3 w-3" />
            {isMockMode ? "Mock data mode" : "Connected to API"}
          </p>
        </div>
      </div>
    </header>
  );
}

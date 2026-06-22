"use client";

import { useCallback, useMemo, useState } from "react";

import { AnalysisPanel } from "@/components/analysis/AnalysisPanel";
import { EmailDetail } from "@/components/inbox/EmailDetail";
import { InboxList } from "@/components/inbox/InboxList";
import { BucketSidebar } from "@/components/layout/BucketSidebar";
import { DashboardHeader } from "@/components/layout/DashboardHeader";
import { analyzeEmail as analyzeEmailApi } from "@/lib/api/analysis";
import { isMockMode } from "@/lib/api/client";
import { listEmails } from "@/lib/api/emails";
import {
  MOCK_ANALYSES,
  MOCK_EMAILS,
  mockClassifyEmail,
} from "@/lib/mock/emails";
import type { Bucket, EmailAnalysis } from "@/lib/types/analysis";
import type { Email } from "@/lib/types/email";
import { countByBucket, getBucket, BUCKET_LABELS } from "@/lib/utils/buckets";

export function Dashboard() {
  const mockMode = isMockMode();

  const [emails, setEmails] = useState<Email[]>(() =>
    mockMode ? MOCK_EMAILS : [],
  );
  const [analyses, setAnalyses] = useState<Record<string, EmailAnalysis>>(() =>
    mockMode ? { ...MOCK_ANALYSES } : {},
  );
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(
    MOCK_EMAILS[0]?.id ?? null,
  );
  const [activeBucket, setActiveBucket] = useState<Bucket | "all">("all");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const selectedEmail = emails.find((email) => email.id === selectedEmailId) ?? null;
  const selectedAnalysis = selectedEmailId ? analyses[selectedEmailId] : null;

  const bucketCounts = useMemo(
    () => countByBucket(emails.map((e) => e.id), analyses),
    [emails, analyses],
  );

  const filteredEmails = useMemo(() => {
    if (activeBucket === "all") return emails;
    return emails.filter((email) => getBucket(analyses[email.id]) === activeBucket);
  }, [activeBucket, analyses, emails]);

  const loadFromApi = useCallback(async () => {
    setIsLoading(true);
    try {
      const fetched = await listEmails();
      setEmails(fetched);
      if (fetched[0]) setSelectedEmailId(fetched[0].id);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!selectedEmail) return;

    setIsAnalyzing(true);
    try {
      if (mockMode) {
        await new Promise((resolve) => setTimeout(resolve, 600));
        const result = mockClassifyEmail(selectedEmail);
        setAnalyses((prev) => ({ ...prev, [selectedEmail.id]: result }));
      } else {
        const result = await analyzeEmailApi(selectedEmail.id);
        setAnalyses((prev) => ({ ...prev, [selectedEmail.id]: result }));
      }
    } finally {
      setIsAnalyzing(false);
    }
  }, [mockMode, selectedEmail]);

  return (
    <div className="flex h-screen flex-col bg-slate-100">
      <DashboardHeader
        emailCount={emails.length}
        analyzedCount={Object.keys(analyses).length}
        isMockMode={mockMode}
      />

      <div className="flex min-h-0 flex-1">
        <BucketSidebar
          activeBucket={activeBucket}
          counts={bucketCounts}
          totalCount={emails.length}
          onSelect={setActiveBucket}
        />

        <div className="flex min-w-0 flex-1 flex-col border-r border-slate-200 bg-white">
          <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <h2 className="text-sm font-semibold text-slate-800">
              {activeBucket === "all" ? "Inbox" : BUCKET_LABELS[activeBucket]}
            </h2>
            {!mockMode && (
              <button
                type="button"
                onClick={loadFromApi}
                disabled={isLoading}
                className="text-xs font-medium text-indigo-600 hover:text-indigo-500 disabled:opacity-50"
              >
                {isLoading ? "Loading…" : "Refresh from API"}
              </button>
            )}
          </div>
          <InboxList
            emails={filteredEmails}
            analyses={analyses}
            selectedEmailId={selectedEmailId}
            onSelect={setSelectedEmailId}
          />
        </div>

        <div className="flex min-w-0 flex-[1.4] flex-col gap-4 overflow-hidden p-4">
          <div className="min-h-0 flex-[1.2]">
            <EmailDetail email={selectedEmail} />
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <AnalysisPanel
              analysis={selectedAnalysis ?? null}
              isAnalyzing={isAnalyzing}
              onAnalyze={handleAnalyze}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { AnalysisPanel } from "@/components/analysis/AnalysisPanel";
import { EmailDetail } from "@/components/inbox/EmailDetail";
import { InboxList } from "@/components/inbox/InboxList";
import { BucketSidebar } from "@/components/layout/BucketSidebar";
import { DashboardHeader } from "@/components/layout/DashboardHeader";
import { analyzeEmailContent } from "@/lib/api/analysis";
import { ApiError, isMockMode } from "@/lib/api/client";
import { fetchRecentGmailEmails } from "@/lib/api/gmail";
import {
  MOCK_ANALYSES,
  MOCK_EMAILS,
  mockAnalyzeEmailContent,
} from "@/lib/mock/emails";
import type { Bucket, EmailAnalysis, EmailAnalysisResult } from "@/lib/types/analysis";
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
  const [emailAnalysisResults, setEmailAnalysisResults] = useState<
    Record<string, EmailAnalysisResult>
  >({});
  const [analyzingEmailIds, setAnalyzingEmailIds] = useState<Record<string, boolean>>({});
  const [analysisErrors, setAnalysisErrors] = useState<Record<string, string | null>>({});
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(
    mockMode ? (MOCK_EMAILS[0]?.id ?? null) : null,
  );
  const [activeBucket, setActiveBucket] = useState<Bucket | "all">("all");
  const [isLoading, setIsLoading] = useState(!mockMode);
  const [error, setError] = useState<string | null>(null);

  const selectedEmail = emails.find((email) => email.id === selectedEmailId) ?? null;
  const selectedAnalysis = selectedEmailId ? emailAnalysisResults[selectedEmailId] ?? null : null;
  const isAnalyzingSelected = selectedEmailId ? Boolean(analyzingEmailIds[selectedEmailId]) : false;

  const bucketCounts = useMemo(
    () => countByBucket(emails.map((e) => e.id), analyses),
    [emails, analyses],
  );

  const filteredEmails = useMemo(() => {
    if (activeBucket === "all") return emails;
    return emails.filter((email) => getBucket(analyses[email.id]) === activeBucket);
  }, [activeBucket, analyses, emails]);

  const loadGmailEmails = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const fetched = await fetchRecentGmailEmails(5);
      setEmails(fetched);
      setSelectedEmailId((current) => {
        if (current && fetched.some((email) => email.id === current)) {
          return current;
        }
        return fetched[0]?.id ?? null;
      });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Failed to load Gmail emails";
      setError(message);
      setEmails([]);
      setSelectedEmailId(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!mockMode) {
      void loadGmailEmails();
    }
  }, [mockMode, loadGmailEmails]);

  const handleAnalyzeEmail = useCallback(
    async (email: Email) => {
      setAnalyzingEmailIds((prev) => ({ ...prev, [email.id]: true }));
      setAnalysisErrors((prev) => ({ ...prev, [email.id]: null }));

      try {
        let result: EmailAnalysisResult;

        if (mockMode) {
          await new Promise((resolve) => setTimeout(resolve, 500));
          result = mockAnalyzeEmailContent(email);
        } else {
          result = await analyzeEmailContent({
            subject: email.subject,
            sender: email.sender,
            snippet: email.snippet ?? "",
          });
        }

        setEmailAnalysisResults((prev) => ({ ...prev, [email.id]: result }));
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Failed to analyze email";
        setAnalysisErrors((prev) => ({ ...prev, [email.id]: message }));
      } finally {
        setAnalyzingEmailIds((prev) => ({ ...prev, [email.id]: false }));
      }
    },
    [mockMode],
  );

  const handleAnalyze = useCallback(async () => {
    if (!selectedEmail) return;
    await handleAnalyzeEmail(selectedEmail);
  }, [handleAnalyzeEmail, selectedEmail]);

  return (
    <div className="flex h-screen flex-col bg-slate-100">
      <DashboardHeader
        emailCount={emails.length}
        analyzedCount={Object.keys(emailAnalysisResults).length}
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
                onClick={loadGmailEmails}
                disabled={isLoading}
                className="text-xs font-medium text-indigo-600 hover:text-indigo-500 disabled:opacity-50"
              >
                {isLoading ? "Loading…" : "Refresh Gmail"}
              </button>
            )}
          </div>
          <InboxList
            emails={filteredEmails}
            emailAnalysisResults={emailAnalysisResults}
            analyzingEmailIds={analyzingEmailIds}
            analysisErrors={analysisErrors}
            selectedEmailId={selectedEmailId}
            onSelect={setSelectedEmailId}
            onAnalyzeEmail={handleAnalyzeEmail}
            isLoading={isLoading}
            error={error}
            onRetry={mockMode ? undefined : loadGmailEmails}
            emptyMessage={
              activeBucket === "all"
                ? "Your Gmail inbox is empty."
                : "No emails in this bucket."
            }
          />
        </div>

        <div className="flex min-w-0 flex-[1.4] flex-col gap-4 overflow-hidden p-4">
          <div className="min-h-0 flex-[1.2]">
            <EmailDetail email={selectedEmail} />
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <AnalysisPanel
              analysis={selectedAnalysis}
              isAnalyzing={isAnalyzingSelected}
              onAnalyze={handleAnalyze}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

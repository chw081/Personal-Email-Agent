"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { AnalysisPanel } from "@/components/analysis/AnalysisPanel";
import { EmailDetail } from "@/components/inbox/EmailDetail";
import { InboxList } from "@/components/inbox/InboxList";
import { InboxSummaryCard } from "@/components/inbox/InboxSummaryCard";
import { BucketSidebar } from "@/components/layout/BucketSidebar";
import { DashboardHeader } from "@/components/layout/DashboardHeader";
import {
  analyzeEmailContent,
  bulkAnalyzeEmails,
  emailsToBulkRequest,
  generateInboxSummary,
} from "@/lib/api/analysis";
import { ApiError, isMockMode } from "@/lib/api/client";
import { fetchRecentGmailEmails } from "@/lib/api/gmail";
import { MOCK_EMAILS, mockAnalyzeEmailContent } from "@/lib/mock/emails";
import type { Bucket, EmailAnalysisResult, InboxSummaryResponse } from "@/lib/types/analysis";
import type { Email } from "@/lib/types/email";
import {
  BUCKET_LABELS,
  countByBucketFromResults,
  getBucketFromResult,
} from "@/lib/utils/buckets";
import { computeInboxStats } from "@/lib/utils/inbox-stats";
import { emailToAnalysisRequest } from "@/lib/utils/gmail";

export function Dashboard() {
  const mockMode = isMockMode();

  const [emails, setEmails] = useState<Email[]>(() =>
    mockMode ? MOCK_EMAILS : [],
  );
  const [emailAnalysisResults, setEmailAnalysisResults] = useState<
    Record<string, EmailAnalysisResult>
  >(() =>
    mockMode
      ? Object.fromEntries(
          MOCK_EMAILS.map((email) => [email.id, mockAnalyzeEmailContent(email)]),
        )
      : {},
  );
  const [analyzingEmailIds, setAnalyzingEmailIds] = useState<Record<string, boolean>>({});
  const [analysisErrors, setAnalysisErrors] = useState<Record<string, string | null>>({});
  const [inboxSummary, setInboxSummary] = useState<InboxSummaryResponse | null>(null);
  const [isAnalyzingInbox, setIsAnalyzingInbox] = useState(false);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [bulkError, setBulkError] = useState<string | null>(null);
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(
    mockMode ? (MOCK_EMAILS[0]?.id ?? null) : null,
  );
  const [activeBucket, setActiveBucket] = useState<Bucket | "all">("all");
  const [isLoading, setIsLoading] = useState(!mockMode);
  const [error, setError] = useState<string | null>(null);

  const selectedEmail = emails.find((email) => email.id === selectedEmailId) ?? null;
  const selectedAnalysis = selectedEmailId ? emailAnalysisResults[selectedEmailId] ?? null : null;
  const isAnalyzingSelected = selectedEmailId ? Boolean(analyzingEmailIds[selectedEmailId]) : false;
  const selectedAnalysisError = selectedEmailId ? analysisErrors[selectedEmailId] ?? null : null;

  const emailIds = useMemo(() => emails.map((email) => email.id), [emails]);

  const inboxStats = useMemo(
    () => computeInboxStats(emailIds, emailAnalysisResults),
    [emailIds, emailAnalysisResults],
  );

  const bucketCounts = useMemo(
    () => countByBucketFromResults(emailIds, emailAnalysisResults),
    [emailIds, emailAnalysisResults],
  );

  const filteredEmails = useMemo(() => {
    if (activeBucket === "all") return emails;
    return emails.filter(
      (email) => getBucketFromResult(emailAnalysisResults[email.id]) === activeBucket,
    );
  }, [activeBucket, emailAnalysisResults, emails]);

  const loadGmailEmails = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const fetched = await fetchRecentGmailEmails(20);
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
          result = await analyzeEmailContent(emailToAnalysisRequest(email));
        }

        setEmailAnalysisResults((prev) => ({ ...prev, [email.id]: result }));
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Failed to analyze email. Please try again.";
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

  const handleAnalyzeInbox = useCallback(async () => {
    if (emails.length === 0) return;

    setIsAnalyzingInbox(true);
    setBulkError(null);

    try {
      const response = await bulkAnalyzeEmails(emailsToBulkRequest(emails));

      setEmailAnalysisResults((prev) => {
        const next = { ...prev };
        response.results.forEach((result, index) => {
          const email = emails[index];
          if (email) {
            next[email.id] = result.analysis;
          }
        });
        return next;
      });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Failed to analyze inbox";
      setBulkError(message);
    } finally {
      setIsAnalyzingInbox(false);
    }
  }, [emails]);

  const handleGenerateSummary = useCallback(async () => {
    if (emails.length === 0) return;

    setIsGeneratingSummary(true);
    setSummaryError(null);

    try {
      const summary = await generateInboxSummary(emailsToBulkRequest(emails));
      setInboxSummary(summary);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Failed to generate inbox summary";
      setSummaryError(message);
    } finally {
      setIsGeneratingSummary(false);
    }
  }, [emails]);

  return (
    <div className="flex min-h-screen flex-col bg-slate-100 lg:h-screen lg:overflow-hidden">
      <DashboardHeader
        emailCount={emails.length}
        analyzedCount={inboxStats.analyzed}
        isMockMode={mockMode}
      />

      <div className="grid flex-1 grid-cols-1 gap-4 p-4 md:grid-cols-2 md:gap-6 lg:min-h-0 lg:grid-cols-[minmax(220px,260px)_minmax(280px,1fr)_minmax(320px,1.4fr)] lg:gap-6 lg:overflow-hidden">
        {/* Left column: overview + buckets */}
        <aside className="order-1 flex flex-col gap-4 md:order-1 md:col-span-2 lg:col-span-1 lg:min-h-0 lg:overflow-y-auto">
          <InboxSummaryCard
            stats={inboxStats}
            inboxSummary={inboxSummary}
            isAnalyzingInbox={isAnalyzingInbox}
            isGeneratingSummary={isGeneratingSummary}
            bulkError={bulkError}
            summaryError={summaryError}
            onAnalyzeInbox={handleAnalyzeInbox}
            onGenerateSummary={handleGenerateSummary}
          />
          <BucketSidebar
            activeBucket={activeBucket}
            counts={bucketCounts}
            totalCount={emails.length}
            onSelect={setActiveBucket}
          />
        </aside>

        {/* Middle column: inbox list */}
        <section className="order-3 flex min-h-[320px] flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm md:order-3 md:min-h-0 lg:order-2">
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
            selectedEmailId={selectedEmailId}
            onSelect={setSelectedEmailId}
            isLoading={isLoading}
            error={error}
            onRetry={mockMode ? undefined : loadGmailEmails}
            emptyMessage={
              activeBucket === "all"
                ? "Your Gmail inbox is empty."
                : "No emails in this bucket."
            }
          />
        </section>

        {/* Right column: selected email + AI analysis */}
        <section className="order-4 flex min-h-0 min-w-0 flex-col gap-4 md:order-4 md:col-span-2 md:gap-6 lg:order-3 lg:col-span-1 lg:overflow-hidden">
          <div className="min-h-[200px] shrink-0 lg:max-h-[45%] lg:min-h-0">
            <EmailDetail email={selectedEmail} />
          </div>
          <div className="flex min-h-[240px] min-w-0 flex-1 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:p-6">
            <AnalysisPanel
              analysis={selectedAnalysis}
              isAnalyzing={isAnalyzingSelected}
              error={selectedAnalysisError}
              onAnalyze={handleAnalyze}
            />
          </div>
        </section>
      </div>
    </div>
  );
}

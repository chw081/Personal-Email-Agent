import { apiFetch } from "@/lib/api/client";
import type {
  BulkEmailAnalysisRequest,
  BulkEmailAnalysisResponse,
  EmailAnalysis,
  EmailAnalysisRequest,
  EmailAnalysisResult,
  InboxSummaryResponse,
} from "@/lib/types/analysis";
import type { Email } from "@/lib/types/email";
import { emailToAnalysisRequest } from "@/lib/utils/gmail";

export function emailsToBulkRequest(emails: Email[]): BulkEmailAnalysisRequest {
  return {
    emails: emails.map((email) => emailToAnalysisRequest(email)),
  };
}

export async function analyzeEmailContent(
  payload: EmailAnalysisRequest,
): Promise<EmailAnalysisResult> {
  return apiFetch<EmailAnalysisResult>("/email-analysis/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function bulkAnalyzeEmails(
  payload: BulkEmailAnalysisRequest,
): Promise<BulkEmailAnalysisResponse> {
  return apiFetch<BulkEmailAnalysisResponse>("/email-analysis/bulk-analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function generateInboxSummary(
  payload: BulkEmailAnalysisRequest,
): Promise<InboxSummaryResponse> {
  return apiFetch<InboxSummaryResponse>("/email-analysis/inbox-summary", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function analyzeEmail(emailId: string): Promise<EmailAnalysis> {
  return apiFetch<EmailAnalysis>(`/emails/${emailId}/analyze`, {
    method: "POST",
  });
}

export async function getEmailAnalysis(emailId: string): Promise<EmailAnalysis> {
  return apiFetch<EmailAnalysis>(`/emails/${emailId}/analysis`);
}

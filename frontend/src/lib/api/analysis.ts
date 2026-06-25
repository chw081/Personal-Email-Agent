import { apiFetch } from "@/lib/api/client";
import type { EmailAnalysis, EmailAnalysisRequest, EmailAnalysisResult } from "@/lib/types/analysis";

export async function analyzeEmailContent(
  payload: EmailAnalysisRequest,
): Promise<EmailAnalysisResult> {
  return apiFetch<EmailAnalysisResult>("/email-analysis/analyze", {
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

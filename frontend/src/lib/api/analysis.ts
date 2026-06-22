import { apiFetch } from "@/lib/api/client";
import type { EmailAnalysis } from "@/lib/types/analysis";

export async function analyzeEmail(emailId: string): Promise<EmailAnalysis> {
  return apiFetch<EmailAnalysis>(`/emails/${emailId}/analyze`, {
    method: "POST",
  });
}

export async function getEmailAnalysis(emailId: string): Promise<EmailAnalysis> {
  return apiFetch<EmailAnalysis>(`/emails/${emailId}/analysis`);
}

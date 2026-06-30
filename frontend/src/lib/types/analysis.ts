export type Priority = "critical" | "important" | "normal" | "low";
export type Action = "review" | "reply" | "archive" | "delete_candidate" | "keep";
export type Bucket = "urgent" | "needs_reply" | "waiting" | "fyi";

export interface EmailAnalysisRequest {
  subject: string;
  sender: string;
  snippet?: string;
  body?: string | null;
}

export interface EmailAnalysisResult {
  summary: string;
  priority: string;
  category: string;
  action_items: string[];
}

export interface BulkEmailAnalysisRequest {
  emails: EmailAnalysisRequest[];
}

export interface AnalyzedEmail {
  original_email: EmailAnalysisRequest;
  analysis: EmailAnalysisResult;
}

export interface BulkEmailAnalysisResponse {
  results: AnalyzedEmail[];
}

export interface InboxSummaryResponse {
  total_emails: number;
  priority_counts: Record<string, number>;
  category_counts: Record<string, number>;
  top_action_items: string[];
  summary: string;
}

export interface EmailAnalysis {
  id: string;
  email_id: string;
  domain: string;
  subcategory: string;
  priority: Priority;
  action: Action;
  confidence: number;
  reason: string | null;
  model_name: string;
  schema_version: string;
  created_at: string;
}

import type { Bucket, EmailAnalysis, EmailAnalysisResult } from "@/lib/types/analysis";

export const BUCKET_LABELS: Record<Bucket, string> = {
  urgent: "Urgent",
  needs_reply: "Needs Reply",
  waiting: "Waiting",
  fyi: "FYI",
};

export const BUCKET_DESCRIPTIONS: Record<Bucket, string> = {
  urgent: "Critical security or time-sensitive items",
  needs_reply: "Messages that expect a response",
  waiting: "Items to review or follow up on",
  fyi: "Receipts, updates, and low-priority mail",
};

export function getBucket(analysis: EmailAnalysis | null | undefined): Bucket {
  if (!analysis) return "waiting";

  if (analysis.priority === "critical") return "urgent";
  if (analysis.action === "reply") return "needs_reply";
  if (analysis.action === "review") return "waiting";
  return "fyi";
}

export function getBucketFromResult(result: EmailAnalysisResult | null | undefined): Bucket {
  if (!result) return "waiting";
  if (result.priority === "High") return "urgent";
  if (result.category === "Career") return "needs_reply";
  if (result.category === "Finance") return "waiting";
  return "fyi";
}

export function countByBucket(
  emailIds: string[],
  analyses: Record<string, EmailAnalysis | undefined>,
): Record<Bucket, number> {
  const counts: Record<Bucket, number> = {
    urgent: 0,
    needs_reply: 0,
    waiting: 0,
    fyi: 0,
  };

  for (const id of emailIds) {
    counts[getBucket(analyses[id])] += 1;
  }

  return counts;
}

export function countByBucketFromResults(
  emailIds: string[],
  results: Record<string, EmailAnalysisResult | undefined>,
): Record<Bucket, number> {
  const counts: Record<Bucket, number> = {
    urgent: 0,
    needs_reply: 0,
    waiting: 0,
    fyi: 0,
  };

  for (const id of emailIds) {
    counts[getBucketFromResult(results[id])] += 1;
  }

  return counts;
}

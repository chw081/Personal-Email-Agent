import type { EmailAnalysisResult } from "@/lib/types/analysis";

export interface InboxStats {
  loaded: number;
  analyzed: number;
  urgent: number;
  needsReply: number;
}

export function computeInboxStats(
  emailIds: string[],
  results: Record<string, EmailAnalysisResult | undefined>,
): InboxStats {
  let analyzed = 0;
  let urgent = 0;
  let needsReply = 0;

  for (const id of emailIds) {
    const result = results[id];
    if (!result) continue;

    analyzed += 1;
    if (result.priority === "High") urgent += 1;
    if (result.category === "Career") needsReply += 1;
  }

  return {
    loaded: emailIds.length,
    analyzed,
    urgent,
    needsReply,
  };
}

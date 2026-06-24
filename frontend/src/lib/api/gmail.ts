import { apiFetch } from "@/lib/api/client";
import type { GmailRecentResponse } from "@/lib/types/gmail";
import type { Email } from "@/lib/types/email";
import { mapGmailResponseToEmails } from "@/lib/utils/gmail";

export async function fetchRecentGmailEmails(limit = 5): Promise<Email[]> {
  const response = await apiFetch<GmailRecentResponse>(
    `/dev/gmail/recent?limit=${limit}`,
  );
  return mapGmailResponseToEmails(response.emails);
}

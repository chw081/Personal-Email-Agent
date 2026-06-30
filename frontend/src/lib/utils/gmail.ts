import type { GmailRecentEmail, GmailRecentEmailRaw } from "@/lib/types/gmail";
import type { Email } from "@/lib/types/email";
import { decodeHtmlEntities, withFallback } from "@/lib/utils/format";

function parseSender(from: string): { sender: string; senderEmail: string | null } {
  const angleMatch = from.match(/^(.+?)\s*<([^>]+)>$/);
  if (angleMatch) {
    return {
      sender: angleMatch[1].trim().replace(/^"|"$/g, ""),
      senderEmail: angleMatch[2].trim(),
    };
  }

  if (from.includes("@")) {
    return { sender: from.trim(), senderEmail: from.trim() };
  }

  return { sender: from.trim(), senderEmail: null };
}

/** Normalize backend payload to a consistent GmailRecentEmail shape. */
export function normalizeGmailRecentEmail(raw: GmailRecentEmailRaw): GmailRecentEmail {
  const fromValue = withFallback(raw.from ?? raw.sender, "");

  return {
    gmail_id: withFallback(raw.gmail_id, ""),
    thread_id: withFallback(raw.thread_id, ""),
    from: fromValue,
    recipients: withFallback(raw.recipients, ""),
    subject: withFallback(raw.subject, ""),
    date: withFallback(raw.date, ""),
    snippet: withFallback(raw.snippet, ""),
    body_text: withFallback(raw.body_text, ""),
    has_attachment: Boolean(raw.has_attachment),
    internal_date_ms: raw.internal_date_ms ?? 0,
  };
}

export function mapGmailToEmail(gmailEmail: GmailRecentEmail): Email {
  const normalized = normalizeGmailRecentEmail(gmailEmail);
  const fromRaw = decodeHtmlEntities(normalized.from);
  const { sender, senderEmail } = parseSender(fromRaw);
  const timestamp = new Date().toISOString();
  const snippet = decodeHtmlEntities(withFallback(normalized.snippet, "")) || null;
  const bodyText =
    decodeHtmlEntities(withFallback(normalized.body_text, "")) || snippet;

  return {
    id: normalized.gmail_id,
    gmail_message_id: normalized.gmail_id,
    thread_id: normalized.thread_id || null,
    sender: withFallback(sender, "Unknown sender"),
    sender_email: senderEmail,
    subject: decodeHtmlEntities(withFallback(normalized.subject, "(No subject)")),
    snippet,
    body_text: bodyText,
    received_at: normalized.date ? normalized.date : null,
    is_unread: true,
    has_attachment: normalized.has_attachment ?? false,
    gmail_labels: ["INBOX"],
    created_at: timestamp,
    updated_at: timestamp,
  };
}

export function mapGmailResponseToEmails(emails: GmailRecentEmailRaw[]): Email[] {
  return emails.map((email) => mapGmailToEmail(normalizeGmailRecentEmail(email)));
}

export function emailToAnalysisRequest(email: Email) {
  const body = email.body_text?.trim();
  const snippet = email.snippet?.trim() ?? "";

  return {
    subject: email.subject,
    sender: email.sender,
    snippet,
    ...(body ? { body } : {}),
  };
}

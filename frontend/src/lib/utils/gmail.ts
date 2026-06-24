import type { GmailRecentEmail } from "@/lib/types/gmail";
import type { Email } from "@/lib/types/email";

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

export function mapGmailToEmail(gmailEmail: GmailRecentEmail): Email {
  const { sender, senderEmail } = parseSender(gmailEmail.from);
  const timestamp = new Date().toISOString();

  return {
    id: gmailEmail.gmail_id,
    gmail_message_id: gmailEmail.gmail_id,
    thread_id: gmailEmail.thread_id,
    sender,
    sender_email: senderEmail,
    subject: gmailEmail.subject,
    snippet: gmailEmail.snippet,
    body_text: gmailEmail.snippet,
    received_at: gmailEmail.date,
    is_unread: true,
    has_attachment: false,
    gmail_labels: ["INBOX"],
    created_at: timestamp,
    updated_at: timestamp,
  };
}

export function mapGmailResponseToEmails(emails: GmailRecentEmail[]): Email[] {
  return emails.map(mapGmailToEmail);
}

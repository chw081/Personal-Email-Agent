export interface GmailRecentEmail {
  gmail_id: string;
  thread_id: string;
  from: string;
  recipients?: string;
  subject: string;
  date: string;
  snippet: string;
  body_text?: string;
  has_attachment?: boolean;
  internal_date_ms?: number;
}

/** Raw API payload may use alternate field names before normalization. */
export interface GmailRecentEmailRaw {
  gmail_id?: string;
  thread_id?: string;
  from?: string;
  sender?: string;
  recipients?: string;
  subject?: string;
  date?: string;
  snippet?: string;
  body_text?: string;
  has_attachment?: boolean;
  internal_date_ms?: number;
}

export interface GmailRecentResponse {
  source: string;
  count: number;
  emails: GmailRecentEmailRaw[];
}

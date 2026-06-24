export interface GmailRecentEmail {
  gmail_id: string;
  thread_id: string;
  from: string;
  subject: string;
  date: string;
  snippet: string;
}

export interface GmailRecentResponse {
  source: string;
  count: number;
  emails: GmailRecentEmail[];
}

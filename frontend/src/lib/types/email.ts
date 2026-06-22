export interface Email {
  id: string;
  gmail_message_id: string | null;
  thread_id: string | null;
  sender: string;
  sender_email: string | null;
  subject: string;
  snippet: string | null;
  body_text: string | null;
  received_at: string | null;
  is_unread: boolean;
  has_attachment: boolean;
  gmail_labels: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface EmailCreate {
  gmail_message_id?: string | null;
  thread_id?: string | null;
  sender: string;
  sender_email?: string | null;
  subject: string;
  snippet?: string | null;
  body_text?: string | null;
  received_at?: string | null;
  is_unread?: boolean;
  has_attachment?: boolean;
  gmail_labels?: string[] | null;
}

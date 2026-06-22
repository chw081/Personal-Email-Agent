import { apiFetch } from "@/lib/api/client";
import type { Email, EmailCreate } from "@/lib/types/email";

export async function listEmails(): Promise<Email[]> {
  return apiFetch<Email[]>("/emails");
}

export async function getEmail(emailId: string): Promise<Email> {
  return apiFetch<Email>(`/emails/${emailId}`);
}

export async function createEmail(payload: EmailCreate): Promise<Email> {
  return apiFetch<Email>("/emails", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function seedEmails(): Promise<Email[]> {
  return apiFetch<Email[]>("/dev/seed", { method: "POST" });
}

export async function checkHealth(): Promise<{ status: string; service: string }> {
  return apiFetch<{ status: string; service: string }>("/health");
}

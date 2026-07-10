"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, ChevronRight, Loader2, Mail, Sparkles } from "lucide-react";

import { analyzeEmailContent } from "@/lib/api/analysis";
import type { EmailAnalysisRequest, EmailAnalysisResult } from "@/lib/types/analysis";

const PRESETS: { label: string; tag: string; tagColor: string; email: EmailAnalysisRequest }[] = [
  {
    label: "Interview Invite",
    tag: "High · Career",
    tagColor: "bg-red-50 text-red-700",
    email: {
      sender: "sarah.miller@techcorp.com",
      subject: "Interview Invitation – Senior Software Engineer at TechCorp",
      snippet:
        "Hi, we'd love to schedule a technical interview for the Senior SWE role. Please share your availability for next week.",
      body: `Hi,

Thank you for applying to the Senior Software Engineer position at TechCorp. We were impressed with your background and would like to move forward with a technical interview.

Please reply with your availability for a 60-minute video interview next week (Mon–Fri, 9am–5pm PT). The interview will cover system design and coding questions.

Best,
Sarah Miller
Talent Acquisition, TechCorp`,
    },
  },
  {
    label: "Job Digest",
    tag: "Low · Career",
    tagColor: "bg-slate-100 text-slate-500",
    email: {
      sender: "noreply@ziprecruiter.com",
      subject: "10 new Software Engineer jobs matching your profile",
      snippet:
        "Based on your profile and search history, here are today's top job matches from ZipRecruiter.",
      body: `Hi there,

We found 10 new jobs matching "Software Engineer" near San Francisco, CA.

1. Software Engineer II – Acme Corp ($130k–$160k)
2. Full Stack Developer – Startup XYZ ($120k–$150k)
3. Backend Engineer – ScaleUp Inc ($140k–$170k)
... and 7 more

View all matches: ziprecruiter.com/jobs/recommended

To stop receiving these emails, unsubscribe here.

– The ZipRecruiter Team`,
    },
  },
  {
    label: "Security Alert",
    tag: "High · Other",
    tagColor: "bg-amber-50 text-amber-700",
    email: {
      sender: "no-reply@accounts.google.com",
      subject: "Security alert: New sign-in to your Google Account",
      snippet:
        "A new sign-in to your Google Account was detected from an unrecognized device in Chicago, IL.",
      body: `Hi,

Your Google Account was just signed in to from a new device.

Device: Windows PC
Location: Chicago, IL, USA
Time: Jul 9, 2026, 10:42 PM

If this was you, you don't need to do anything.

If you don't recognize this sign-in, secure your account immediately:
https://myaccount.google.com/security

You can also review all connected devices:
https://myaccount.google.com/device-activity

The Google Account Team`,
    },
  },
];

const PRIORITY_STYLES: Record<string, string> = {
  High: "bg-red-50 text-red-700 ring-red-200",
  Medium: "bg-amber-50 text-amber-800 ring-amber-200",
  Low: "bg-slate-100 text-slate-600 ring-slate-200",
};

export default function DemoPage() {
  const [form, setForm] = useState<EmailAnalysisRequest>(PRESETS[0].email);
  const [activePreset, setActivePreset] = useState(0);
  const [result, setResult] = useState<EmailAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function loadPreset(index: number) {
    setActivePreset(index);
    setForm(PRESETS[index].email);
    setResult(null);
    setError(null);
  }

  async function handleAnalyze() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await analyzeEmailContent(form);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  const fieldClass =
    "w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-800 outline-none transition focus:border-indigo-400 focus:bg-white focus:ring-2 focus:ring-indigo-100";

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
              <Mail className="h-4 w-4" />
            </div>
            <div>
              <h1 className="text-base font-semibold text-slate-900">Personal Email Agent</h1>
              <p className="text-xs text-slate-400">AI Email Analysis · Public Demo</p>
            </div>
          </div>
          <Link
            href="/"
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-600 transition hover:bg-slate-50"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Dashboard
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-10">
        {/* Intro */}
        <div className="mb-8 text-center">
          <span className="mb-3 inline-flex items-center gap-1.5 rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700">
            <Sparkles className="h-3 w-3" />
            Powered by Gemini AI
          </span>
          <h2 className="text-2xl font-bold text-slate-900">AI Email Analysis Demo</h2>
          <p className="mt-2 text-slate-500">
            Paste any email below and the AI will extract priority, category, and action items.
            No Gmail login needed.
          </p>
        </div>

        {/* Presets */}
        <div className="mb-6">
          <p className="mb-2.5 text-xs font-medium uppercase tracking-wide text-slate-400">
            Try a sample
          </p>
          <div className="flex flex-wrap gap-2">
            {PRESETS.map((preset, i) => (
              <button
                key={i}
                onClick={() => loadPreset(i)}
                className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition ${
                  activePreset === i
                    ? "border-indigo-300 bg-indigo-50 text-indigo-700"
                    : "border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50"
                }`}
              >
                {preset.label}
                <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${preset.tagColor}`}>
                  {preset.tag}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Two-column layout */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Left: Email editor */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-sm font-semibold text-slate-700">Email Input</h3>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-500">From</label>
                <input
                  type="text"
                  value={form.sender}
                  onChange={(e) => setForm({ ...form, sender: e.target.value })}
                  className={fieldClass}
                  placeholder="sender@example.com"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-500">Subject</label>
                <input
                  type="text"
                  value={form.subject}
                  onChange={(e) => setForm({ ...form, subject: e.target.value })}
                  className={fieldClass}
                  placeholder="Email subject line"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-500">Snippet</label>
                <input
                  type="text"
                  value={form.snippet ?? ""}
                  onChange={(e) => setForm({ ...form, snippet: e.target.value })}
                  className={fieldClass}
                  placeholder="Short preview text (optional)"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-500">Body</label>
                <textarea
                  rows={8}
                  value={form.body ?? ""}
                  onChange={(e) => setForm({ ...form, body: e.target.value })}
                  className={fieldClass}
                  placeholder="Full email body text (optional, improves accuracy)"
                />
              </div>
              <button
                onClick={handleAnalyze}
                disabled={loading || !form.subject.trim() || !form.sender.trim()}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Analyzing…
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Analyze Email
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right: Results */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-sm font-semibold text-slate-700">Analysis Result</h3>

            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            {!result && !error && (
              <div className="flex h-56 flex-col items-center justify-center gap-3 text-slate-300">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
                  <Sparkles className="h-6 w-6" />
                </div>
                <p className="text-sm">Click &quot;Analyze Email&quot; to see results</p>
              </div>
            )}

            {result && (
              <div className="space-y-5">
                {/* Priority + Category badges */}
                <div className="flex flex-wrap gap-2">
                  <span
                    className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset ${
                      PRIORITY_STYLES[result.priority] ?? "bg-slate-100 text-slate-700 ring-slate-200"
                    }`}
                  >
                    {result.priority} Priority
                  </span>
                  <span className="inline-flex items-center rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700 ring-1 ring-inset ring-indigo-200">
                    {result.category}
                  </span>
                </div>

                {/* Summary */}
                <div>
                  <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-slate-400">
                    Summary
                  </p>
                  <p className="text-sm leading-relaxed text-slate-700">{result.summary}</p>
                </div>

                {/* Action items */}
                {result.action_items.length > 0 && (
                  <div>
                    <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
                      Action Items
                    </p>
                    <ul className="space-y-2">
                      {result.action_items.map((item, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                          <ChevronRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-indigo-400" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer note */}
        <p className="mt-8 text-center text-xs text-slate-400">
          Calls the live API at{" "}
          <a
            href="https://personal-email-agent.onrender.com/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-400 underline-offset-2 hover:underline"
          >
            personal-email-agent.onrender.com
          </a>
          . No Gmail credentials required. Email data is not stored.
        </p>
      </main>
    </div>
  );
}

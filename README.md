# Personal Email Agent

An AI-powered email management application that helps users organize, prioritize, and understand their inbox. Built as a full-stack project with a Next.js frontend and a FastAPI backend.

> **Status:** Active development — not production-ready. Gmail integration and Gemini-powered analysis work locally as an MVP; persistence, production auth, and advanced agent workflows are planned.

---

## Overview

Managing a large inbox is time-consuming. Important messages get buried, follow-ups are missed, and low-value mail competes for attention.

**Personal Email Agent** is a full-stack application designed to reduce that friction. Today it connects to Gmail, extracts readable email body text when available, displays real messages in a dashboard, and applies Gemini-powered LLM analysis (with a rule-based fallback) to help users spot priority, category, and suggested actions. The long-term goal is to evolve this into a **personal email agent** — software that understands inbox context, surfaces what matters, drafts responses, and recommends next steps while keeping the user in control.

This repository is intentionally structured so Gmail parsing, analysis providers, and UI can improve incrementally without rewriting the whole stack.

---

## Features

- Gmail OAuth integration (read-only, local)
- Real Gmail inbox retrieval with full body text extraction
- Gemini-powered AI email analysis (priority, category, summary, action items)
- Rule-based fallback analysis when LLM is unavailable or disabled
- Extensible analysis provider architecture — swap providers via configuration
- Bulk inbox analysis and inbox summary
- Frontend dashboard with per-email AI Analysis panel

---

## Current Features

### Gmail & inbox

- **Gmail OAuth (local)** — read-only OAuth flow using a Google Cloud Desktop client
- **Real Gmail retrieval** — fetches recent inbox messages via the Gmail API (`format=full`)
- **Email body extraction** — parses MIME payloads to extract plain-text body content when available
- **HTML fallback** — converts HTML parts to readable text when no plain-text body exists
- **Snippet fallback** — uses Gmail snippets only when extracted body text is unavailable
- **Attachment detection** — flags messages with attachments (`has_attachment`); attachment contents are not parsed
- **Normalized email objects** — sender, recipients, subject, date, snippet, body text, and attachment flag exposed via stable API schemas
- **Frontend dashboard** — responsive layout with inbox list, selected email detail, inbox overview, and per-email analysis
- **Refresh inbox** — reload recent Gmail messages from the dashboard

### Analysis (MVP)

- **Single-email analysis** — `POST /email-analysis/analyze`
- **Bulk inbox analysis** — `POST /email-analysis/bulk-analyze`
- **Inbox summary** — `POST /email-analysis/inbox-summary` (priority/category counts and a short summary sentence)
- **Body-first analysis** — analysis prefers extracted body text over snippets when both are available
- **Provider-based architecture** — `ANALYSIS_PROVIDER=llm` activates Gemini; `rule_based` is the default and fallback
- **Gemini LLM analysis** — Gemini is prompted with sender, subject, snippet, and body to return structured JSON (`summary`, `priority`, `category`, `action_items`); responses are validated against `EmailAnalysisResponse` before being returned
- **Rule-based fallback** — if LLM analysis fails at runtime or `ANALYSIS_PROVIDER=rule_based`, keyword-based classification is used automatically
- **Selected email AI Analysis panel** — analyze or re-analyze the currently selected message using the configured provider

### Backend architecture

- **Layered FastAPI design** — routers, services, schemas, and models
- **Stable API contracts** — Pydantic schemas for request/response shapes
- **Gmail logic in the service layer** — OAuth, MIME parsing, and API calls isolated from HTTP handlers
- **Analysis provider pattern** — `analysis_providers/` with a shared `EmailAnalysisProvider` interface; `LLMEmailAnalysisProvider` (Gemini) and `RuleBasedEmailAnalysisProvider` both available
- **SQLAlchemy + SQLite** — database models and dev endpoints (Gmail messages are not yet synced to the database)
- **Interactive API docs** — Swagger UI at `/docs`

### Developer experience

- Mock email mode for frontend development (`NEXT_PUBLIC_USE_MOCK_DATA=true`)
- Unit and API tests for Gmail parsing, analysis providers, and endpoints
- Environment-based configuration (no hardcoded machine paths)

---

## Current Limitations

Be aware of what this project **does not** do yet — and where current behavior is still basic:

| Area | Limitation |
|------|------------|
| **Body parsing** | Implemented but basic — plain text preferred, HTML converted to text; complex layouts may not render perfectly |
| **Attachments** | Detected (`has_attachment`) but **not parsed**, downloaded, or displayed |
| **Inline images** | Not extracted or analyzed |
| **Documents** | PDFs and other attachment types are not parsed |
| **Analysis** | Prompt-based MVP — limited categories (Career, Finance, Promotion, Other); no thread or conversation awareness; no attachment understanding; output quality depends on the model |
| **Auth** | No production user authentication or multi-user support |
| **Persistence** | Gmail messages are fetched on demand; they are **not** synced to the database |
| **AI agent** | No autonomous workflows, reply drafting, follow-up tracking, or automatic email actions |
| **Deployment** | Local development only — no hosted demo or production deployment |

Richer HTML cleanup, attachment parsing, database sync, additional categories, and agent workflows are on the roadmap.

---

## Tech Stack

| Layer | Technologies |
|-------|----------------|
| **Frontend** | Next.js, React, TypeScript, Tailwind CSS |
| **Backend** | Python, FastAPI, Pydantic, SQLAlchemy, SQLite |
| **Integrations** | Google Gmail API, Google OAuth (read-only), Google Gemini API (`google-genai` SDK) |

---

## Architecture

```text
Next.js Dashboard (frontend)
        │
        │  HTTP — stable JSON API contracts
        ▼
FastAPI Routers
  ├── /dev/gmail/recent      → recent inbox messages (normalized)
  ├── /email-analysis/*      → analyze, bulk-analyze, inbox-summary
  ├── /emails                → CRUD (database-backed)
  └── /dev/seed              → mock data for development
        │
        ▼
Service Layer
  ├── gmail_service          → OAuth, Gmail API, normalized email objects
  ├── gmail_content          → MIME/HTML parsing (Gmail-specific, internal)
  ├── email_analysis_service → public analysis API (selects provider, handles fallback)
  ├── analysis_providers/    → EmailAnalysisProvider interface
  │     ├── LLMEmailAnalysisProvider     (Gemini, activated via ANALYSIS_PROVIDER=llm)
  │     └── RuleBasedEmailAnalysisProvider  (default and fallback)
  ├── inbox_summary_service  → aggregate stats from analyzed results
  └── classifier_service     → legacy DB-backed classifier (separate path)
        │
        ▼
Schemas (API contracts)  ·  Models (persistence)
```

### Design principles

- **Frontend / backend separation** — the dashboard calls backend REST endpoints; it does not talk to Gmail directly.
- **Gmail parsing stays in the Gmail layer** — MIME walking, base64 decoding, and HTML-to-text conversion live in `gmail_content` / `gmail_service`; raw Gmail payloads never reach routers or the frontend.
- **Normalized email objects** — the API exposes stable fields (`body_text`, `recipients`, `has_attachment`, etc.) that the frontend maps to its own types.
- **Analysis prefers body over snippet** — `EmailAnalysisRequest` accepts an optional `body`; providers use full extracted text when available, falling back to snippets.
- **Swappable analysis providers** — `EmailAnalysisProvider` defines a small interface; `ANALYSIS_PROVIDER=llm` activates Gemini without touching routers or the frontend. LLM failures fall back to rule-based automatically.
- **Routers stay thin** — validate input, call services, return schema-typed responses.
- **Schemas define contracts** — frontend and backend agree on shapes like `EmailAnalysisRequest`, `GmailRecentEmail`, and `InboxSummaryResponse`.
- **Models are for persistence** — SQLAlchemy models support stored emails/analyses; live Gmail fetch remains separate from DB sync today.

---

## Project Structure

```text
Personal-Email-Agent/
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/       # Dashboard, inbox, analysis UI
│   │   └── lib/              # API client, types, utilities
│   ├── .env.example          # Copy to .env.local
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── routers/          # HTTP endpoints
│   │   ├── services/
│   │   │   ├── analysis_providers/  # EmailAnalysisProvider interface, LLMEmailAnalysisProvider (Gemini), RuleBasedEmailAnalysisProvider
│   │   │   ├── gmail_service.py     # OAuth + normalized Gmail fetch
│   │   │   ├── gmail_content.py     # MIME/HTML body extraction
│   │   │   └── email_analysis_service.py
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── config.py         # Settings from environment
│   │   ├── db.py             # Database session setup
│   │   └── main.py           # FastAPI app entry point
│   ├── tests/
│   ├── .example.env          # Copy to .env
│   └── requirements.txt
│
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- A Google Cloud project with the **Gmail API** enabled
- OAuth **Desktop app** credentials (`credentials.json`)
- A [Google AI Studio](https://aistudio.google.com/) API key (for Gemini analysis)

### 1. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .example.env .env
uvicorn app.main:app --reload
```

Backend: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Gmail OAuth credentials

1. In [Google Cloud Console](https://console.cloud.google.com/), create or select a project.
2. Enable the **Gmail API**.
3. Configure the **OAuth consent screen** (External or Internal for workspace testing).
4. Create **OAuth 2.0 Client ID** → Application type: **Desktop app**.
5. Download the JSON file and save it as:

```text
backend/credentials.json
```

**Do not commit `credentials.json` or `token.json`.** Both are listed in `.gitignore`.

On first successful Gmail access, the backend runs the OAuth flow in your browser and writes a refresh token to:

```text
backend/token.json
```

### 3. Backend environment variables

Copy `.example.env` to `.env` and fill in the required values:

```env
GMAIL_CREDENTIALS_PATH=credentials.json   # Path to your OAuth client credentials (relative to backend/)
GMAIL_TOKEN_PATH=token.json               # Path where the OAuth refresh token is stored (relative to backend/)
GEMINI_API_KEY=your_gemini_api_key_here   # API key from Google AI Studio; required for LLM analysis
GEMINI_MODEL=gemini-2.5-flash             # Gemini model to use; defaults to gemini-2.5-flash
ANALYSIS_PROVIDER=llm                     # Set to "llm" for Gemini or "rule_based" for keyword fallback
```

If `GEMINI_API_KEY` is missing or `ANALYSIS_PROVIDER` is not `llm`, the backend automatically falls back to rule-based analysis.

### 4. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Frontend: [http://localhost:3000](http://localhost:3000)

Default `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_USE_MOCK_DATA=false
```

Set `NEXT_PUBLIC_USE_MOCK_DATA=true` to use local mock emails without calling Gmail.

### 5. Try the dashboard

1. Start backend and frontend.
2. Open the dashboard — recent Gmail messages load automatically (or mock data if enabled).
3. Select an email to view extracted body text in the detail panel.
4. Run **AI Analysis** on the selected message (uses body text when available; routed through the configured provider).
5. Use **Analyze Inbox** or **Generate Summary** in the inbox overview panel for bulk operations.

---

## Key API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dev/gmail/recent?limit=5` | Fetch recent Gmail messages with extracted body text |
| `POST` | `/email-analysis/analyze` | Analyze a single email (subject, sender, snippet, optional body) |
| `POST` | `/email-analysis/bulk-analyze` | Analyze up to 50 emails in one request |
| `POST` | `/email-analysis/inbox-summary` | Analyze emails and return inbox-level summary |
| `GET` | `/health` | Health check |

---

## Roadmap

### Completed

- [x] FastAPI backend with layered architecture
- [x] Next.js dashboard with inbox, detail, overview, and analysis UI
- [x] Gmail OAuth and real inbox retrieval (local)
- [x] Parse Gmail email body text (plain text + HTML fallback)
- [x] Use extracted body text for analysis when available
- [x] Attachment detection (flag only)
- [x] Analysis provider architecture with shared interface
- [x] Rule-based analysis and inbox summary endpoints
- [x] Gemini LLM email analysis via `google-genai` SDK
- [x] Structured JSON prompt with `EmailAnalysisResponse` schema validation
- [x] Graceful fallback from LLM to rule-based on failure or missing key
- [x] Provider selection via `ANALYSIS_PROVIDER` environment variable
- [x] Frontend integration with backend APIs

### In progress / next

- [ ] Improve responsive UI polish across breakpoints
- [ ] Improve HTML email cleanup and rendering quality
- [ ] Better prompt engineering (few-shot examples, category tuning)
- [ ] Expand supported categories beyond the current four
- [ ] Parse attachments and documents (PDF, etc.)
- [ ] Conversation and thread awareness
- [ ] Database persistence and Gmail message sync
- [ ] Production authentication and multi-user support

### Future

- [ ] Batch prompt optimization for bulk analysis
- [ ] Multiple LLM provider support (OpenAI, Anthropic, etc.)
- [ ] RAG over historical emails for personalized context
- [ ] Email drafting and reply suggestions (with human approval)
- [ ] Smart inbox actions and follow-up tracking
- [ ] Agent workflows (triage, follow-ups, calendar integrations)
- [ ] Production deployment and observability

---

## Testing

From `backend/` with the virtual environment active:

```bash
python -m unittest discover -s tests -v
```

---

## Future Vision

The goal is to grow Personal Email Agent from an inbox analysis tool into a **trustworthy personal email agent** that:

- Understands context across threads and senders
- Prioritizes time-sensitive and high-value mail
- Suggests actions and drafts (with human approval)
- Tracks follow-ups and reduces inbox noise

All automation is intended to assist — not replace — the user's judgment. The project does not perform automatic email actions today.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

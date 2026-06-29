# Personal Email Agent

An AI-powered email management application that helps users organize, prioritize, and understand their inbox. Built as a full-stack project with a Next.js frontend and a FastAPI backend.

> **Status:** Active development — not production-ready. Gmail integration and analysis work locally as an MVP; advanced AI, persistence, and production auth are planned.

---

## Overview

Managing a large inbox is time-consuming. Important messages get buried, follow-ups are missed, and low-value mail competes for attention.

**Personal Email Agent** is a full-stack application designed to reduce that friction. Today it connects to Gmail, displays real inbox messages in a dashboard, and applies rule-based analysis to help users spot priority, category, and suggested actions. The long-term goal is to evolve this into a **personal email agent** — software that understands inbox context, surfaces what matters, drafts responses, and recommends next steps while keeping the user in control.

This repository is intentionally structured so analysis, Gmail integration, and UI can improve incrementally without rewriting the whole stack.

---

## Current Features

### Gmail & inbox

- **Gmail OAuth (local)** — read-only OAuth flow using a Google Cloud Desktop client
- **Real Gmail retrieval** — fetches recent inbox messages via the Gmail API
- **Frontend dashboard** — responsive layout with inbox list, selected email detail, inbox overview, and per-email AI analysis
- **Refresh inbox** — reload recent Gmail messages from the dashboard

### Analysis (MVP)

- **Single-email analysis** — `POST /email-analysis/analyze`
- **Bulk inbox analysis** — `POST /email-analysis/bulk-analyze`
- **Inbox summary** — `POST /email-analysis/inbox-summary` (priority/category counts and a short summary sentence)
- **Rule-based classifier** — keyword-driven priority, category, summary, and action items (not LLM-powered yet)
- **Selected email AI Analysis panel** — analyze or re-analyze the currently selected message

### Backend architecture

- **Layered FastAPI design** — routers, services, schemas, and models
- **Stable API contracts** — Pydantic schemas for request/response shapes
- **Gmail logic in the service layer** — OAuth and API calls isolated from HTTP handlers
- **SQLAlchemy + SQLite** — database models and dev endpoints (email persistence is not yet synced with Gmail)
- **Interactive API docs** — Swagger UI at `/docs`

### Developer experience

- Mock email mode for frontend development (`NEXT_PUBLIC_USE_MOCK_DATA=true`)
- Unit and API tests for analysis and Gmail services
- Environment-based configuration (no hardcoded machine paths)

---

## Current Limitations

Be aware of what this project **does not** do yet:

| Area | Limitation |
|------|------------|
| **Analysis** | Categorization is basic and rule-based (keywords), not OpenAI-powered |
| **Email content** | UI and analysis rely mainly on **snippets**, not full MIME/body parsing |
| **Attachments** | Attachments and inline images are not parsed or displayed |
| **Auth** | No production user authentication or multi-user support |
| **Persistence** | Gmail messages are fetched on demand; they are **not** synced to the database |
| **AI agent** | No autonomous workflows, reply drafting, or follow-up tracking yet |
| **Deployment** | Local development only — no hosted demo or production deployment |

OpenAI-powered analysis, richer parsing, database sync, and agent workflows are on the roadmap.

---

## Tech Stack

| Layer | Technologies |
|-------|----------------|
| **Frontend** | Next.js, React, TypeScript, Tailwind CSS |
| **Backend** | Python, FastAPI, Pydantic, SQLAlchemy, SQLite |
| **Integrations** | Google Gmail API, Google OAuth (read-only) |
| **Planned** | OpenAI SDK (dependency present; not fully wired into analysis yet) |

---

## Architecture

```text
Next.js Dashboard (frontend)
        │
        │  HTTP — stable JSON API contracts
        ▼
FastAPI Routers
  ├── /dev/gmail/recent      → recent inbox messages
  ├── /email-analysis/*      → analyze, bulk-analyze, inbox-summary
  ├── /emails                → CRUD (database-backed)
  └── /dev/seed              → mock data for development
        │
        ▼
Service Layer
  ├── gmail_service          → OAuth, token refresh, Gmail API calls
  ├── email_analysis_service → rule-based per-email analysis
  ├── inbox_summary_service  → aggregate stats from analyzed results
  └── classifier_service     → legacy DB-backed classifier (separate path)
        │
        ▼
Schemas (API contracts)  ·  Models (persistence)
```

### Design principles

- **Frontend / backend separation** — the dashboard calls backend REST endpoints; it does not talk to Gmail directly.
- **Routers stay thin** — validate input, call services, return schema-typed responses.
- **Services own business logic** — Gmail OAuth, message fetching, and analysis rules live here.
- **Schemas define contracts** — frontend and backend agree on shapes like `EmailAnalysisRequest`, `BulkEmailAnalysisResponse`, and `InboxSummaryResponse`.
- **Models are for persistence** — SQLAlchemy models support stored emails/analyses; Gmail fetch is separate from DB sync today.
- **Gmail specifics stay internal** — the frontend consumes normalized API responses (e.g. mapped `Email` objects), not raw Gmail API payloads.

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
│   │   ├── services/         # Gmail, analysis, mock data
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

You can override paths via `.env`:

```env
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
```

### 3. Frontend setup

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

### 4. Try the dashboard

1. Start backend and frontend.
2. Open the dashboard — recent Gmail messages load automatically (or mock data if enabled).
3. Select an email to view detail and run **AI Analysis** on the selected message.
4. Use **Analyze Inbox** or **Generate Summary** in the inbox overview panel for bulk operations.

---

## Key API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dev/gmail/recent?limit=5` | Fetch recent Gmail inbox messages |
| `POST` | `/email-analysis/analyze` | Analyze a single email (subject, sender, snippet) |
| `POST` | `/email-analysis/bulk-analyze` | Analyze up to 50 emails in one request |
| `POST` | `/email-analysis/inbox-summary` | Analyze emails and return inbox-level summary |
| `GET` | `/health` | Health check |

---

## Roadmap

### Completed (foundation)

- [x] FastAPI backend with layered architecture
- [x] Next.js dashboard with inbox, detail, overview, and analysis UI
- [x] Gmail OAuth and real inbox retrieval (local)
- [x] Rule-based analysis and inbox summary endpoints
- [x] Frontend integration with backend APIs

### In progress / next

- [ ] Improve responsive UI polish across breakpoints
- [ ] Richer email parsing (full bodies, not just snippets)
- [ ] Attachment and inline image support
- [ ] Replace rule-based classifier with OpenAI-powered analysis
- [ ] Database persistence and Gmail message sync
- [ ] Production authentication and multi-user support

### Future

- [ ] Agent workflows (triage, follow-ups, draft replies)
- [ ] Calendar and task integrations
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

All automation is intended to assist — not replace — the user's judgment.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

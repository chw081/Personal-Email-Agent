# Personal Email Agent

An AI-powered email management application that helps users organize, prioritize, and understand their inbox.

## Overview

Managing thousands of emails can quickly become overwhelming. Personal Email Agent is a full-stack application designed to help users process large inboxes more efficiently through email classification, summarization, prioritization, and eventually AI-driven actions.

The long-term vision is to build an intelligent email agent that can understand inbox context, identify important messages, draft responses, and help users stay organized.

---

## Features

### Current Features

* Full-stack architecture
* FastAPI backend
* Next.js frontend
* Email data models and schemas
* Mock email dataset for development
* Email classification service
* Modular API architecture
* Database integration with SQLAlchemy
* Health check and development endpoints

### Planned Features

* Gmail OAuth integration
* Real Gmail message synchronization
* OpenAI-powered email analysis
* AI-generated summaries
* Suggested actions and reply drafts
* Inbox prioritization
* Follow-up tracking
* Agent workflows for inbox management

---

## Tech Stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* SQLite
* OpenAI SDK
* Google Gmail API

---

## Project Structure

The project follows a layered architecture that separates presentation, API handling, business logic, and data models. This design makes the system easier to maintain and allows future integrations (such as Gmail sync and OpenAI-powered analysis) without requiring major changes to the frontend.

```text
Personal-Email-Agent/
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages and routing
│   │   ├── components/   # Reusable UI components
│   │   └── lib/          # Frontend utilities and API helpers
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── models/       # Database models and persistence layer
│   │   ├── schemas/      # API request/response contracts
│   │   ├── routers/      # HTTP endpoints grouped by domain
│   │   ├── services/     # Business logic and external integrations
│   │   ├── config.py     # Application configuration
│   │   ├── db.py         # Database initialization
│   │   └── main.py       # FastAPI application entry point
│   └── requirements.txt
│
└── README.md
```

A key design goal is to keep API contracts stable while allowing internal implementations to evolve. For example, mock email data can later be replaced with Gmail synchronization, and the current classifier can be replaced with an OpenAI-powered analysis service without requiring significant frontend changes.

---

## Getting Started

### Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend

npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:3000
```

---

## Development Roadmap

### Phase 1 — Foundation

* [x] FastAPI backend
* [x] Next.js frontend
* [x] Database models
* [x] API routes
* [x] Mock email data
* [x] Email classification architecture

### Phase 2 — Product Integration

* [ ] Connect frontend to backend APIs
* [ ] Display live email analysis
* [ ] Improve dashboard experience
* [ ] Add loading and error states

### Phase 3 — Real Email Support

* [ ] Gmail OAuth
* [ ] Gmail synchronization service
* [ ] Real inbox ingestion

### Phase 4 — AI-Powered Analysis

* [ ] OpenAI email classification
* [ ] Email summarization
* [ ] Action item extraction
* [ ] Priority detection
* [ ] Suggested responses

### Phase 5 — Agent Workflows

* [ ] Inbox processing agent
* [ ] Follow-up tracking
* [ ] Reply drafting
* [ ] Calendar event suggestions
* [ ] Personalized email management

---

## Architecture

```text
Next.js Frontend
        │
        ▼
FastAPI Backend
        │
        ├── Email Router
        ├── Analysis Router
        └── Development Router
        │
        ▼
Service Layer
        │
        ├── Mock Data Service
        ├── Classifier Service
        └── Gmail Service (planned)
        │
        ▼
Database
```

The system is designed around clear separation of concerns:

* **Frontend** handles user interaction and presentation.
* **Routers** expose API endpoints and coordinate requests.
* **Services** contain business logic and external integrations.
* **Schemas** define typed API contracts between frontend and backend.
* **Models** represent how data is stored and persisted.

This layered approach improves maintainability, testability, and extensibility. New capabilities such as Gmail integration, AI-powered classification, reply generation, and agent workflows can be added primarily within the service layer while preserving existing APIs and frontend behavior.

The architecture is intentionally designed to support the evolution from a traditional web application into an AI-powered email agent. Current implementations use mock email data and a basic classification pipeline, but the same interfaces can later support real inbox synchronization, LLM-powered analysis, task extraction, and autonomous email-management workflows.

---

## Current Status

This project is currently in active development.

The backend architecture, database models, API structure, and frontend foundation have been completed. The next milestone is connecting the frontend with backend APIs and integrating real Gmail data.

---

## Future Vision

The goal is to evolve this project from an email analysis application into a true AI email agent capable of:

* Understanding inbox context
* Prioritizing important messages
* Drafting replies
* Tracking follow-ups
* Recommending actions
* Helping users manage communication more efficiently

while keeping humans in control of all final decisions.

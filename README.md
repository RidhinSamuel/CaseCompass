# Case Compass

> A judicial AI platform that turns legal documents into a searchable, user-scoped knowledge base using Retrieval-Augmented Generation (RAG) and hybrid search.

[![CI](https://github.com/RidhinSamuel/CaseCompass/actions/workflows/ci.yml/badge.svg)](https://github.com/RidhinSamuel/CaseCompass/actions)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![React](https://img.shields.io/badge/react-19-61dafb)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📖 Overview

**Case Compass** helps legal professionals, judicial officers, and law students upload case files, judgements, and legal documents, then ask natural-language questions and get accurate, cited answers grounded in *their own* documents.

Each uploaded document is chunked, embedded via open-source Hugging Face models, and stored with strict per-user metadata so that **User A can never retrieve User B's chunks** — even when semantic similarity is high. Retrieval combines vector similarity, keyword filters, and case-scoped metadata for high-quality, high-precision search.

---

## ✨ Features

- 🔐 **User-scoped RAG** — every chunk carries `user_id`, `case_id`, and `permissions` metadata
- 🔍 **Hybrid search** — vector similarity (pgvector) + full-text search + metadata filtering
- 🤖 **Open-source models** — Hugging Face embeddings and LLMs, no paid API required
- 📨 **Producer/Consumer architecture** — RabbitMQ decouples ingestion from API
- ⚡ **Multiple workers** — scale ingestion horizontally to handle high upload volume
- 🗄️ **Postgres + Redis** — relational persistence + non-relational cache/session state
- 🎨 **Modern UI** — React + Vite + TypeScript + Redux Toolkit, minimal dark/light theme
- 🐳 **Fully dockerized** — one command to run the entire stack
- ✅ **CI/CD** — GitHub Actions runs smoke, unit, and functional tests on every push

---

## 🏛️ System Design

### High-Level Architecture

```
                    ┌─────────────────┐
                    │  React + Vite   │
                    │  (Redux + TS)   │
                    └────────┬────────┘
                             │ HTTPS
                             ▼
                    ┌─────────────────┐
                    │   FastAPI API   │◄──────┐
                    │   (stateless)   │       │ Cache /
                    └────────┬────────┘       │ Sessions
                             │                │
              ┌──────────────┼──────────────┐ │
              │ publish      │ query        │ │
              ▼              │              ▼ │
      ┌──────────────┐       │        ┌─────────┐
      │   RabbitMQ   │       │        │  Redis  │
      │ (durable Q)  │       │        └─────────┘
      └──────┬───────┘       │
             │ consume       │
    ┌────────┴────────┐      │
    ▼        ▼        ▼      │
 ┌────┐  ┌────┐  ┌────┐      │
 │ W1 │  │ W2 │  │ Wn │      │
 └─┬──┘  └─┬──┘  └─┬──┘      │
   └───────┼───────┘         │
           ▼                 ▼
      ┌────────────────────────┐
      │ PostgreSQL + pgvector  │
      │ (docs, chunks, users)  │
      └────────────────────────┘
```

### Design Goals

| Goal | How It's Achieved |
|------|-------------------|
| **High Availability** | Stateless FastAPI replicas behind a load balancer; RabbitMQ durable queues; Postgres persistent volumes |
| **High Throughput** | Producer/consumer decoupling; horizontally scalable workers; Redis query caching |
| **Consistency** | Postgres ACID transactions for documents and chunks; atomic ingestion status |
| **Persistence** | Postgres for source of truth; RabbitMQ durable/persistent messages |
| **Security** | User-scoped metadata on every chunk; `.env` for secrets; never commit keys |
| **Scalability** | Add workers, add API replicas, Redis cluster, Postgres read replicas |

### Data Flow

1. **Upload** — User uploads a document → API stores raw file + metadata in Postgres → publishes ingestion event to RabbitMQ.
2. **Ingest** — Worker consumes event → chunks document → generates embeddings (HuggingFace) → writes chunks + vectors to Postgres with `user_id`/`case_id` metadata.
3. **Query** — User asks a question → API embeds query → hybrid search in Postgres (vector + BM25 + metadata filter WHERE `user_id = current_user`) → LangChain LLM synthesizes an answer with citations → Redis caches the response.

---

## 🧰 Tech Stack

### Backend
- **FastAPI** — async Python web framework
- **SQLAlchemy 2.0** — ORM
- **PostgreSQL 16 + pgvector** — relational + vector store
- **Redis 7** — cache, sessions, worker coordination
- **RabbitMQ 3** — message broker
- **LangChain** — RAG orchestration
- **Hugging Face Transformers / Sentence-Transformers** — open-source embeddings & LLMs
- **Alembic** — DB migrations
- **uv** — fast Python package & environment manager

### Frontend
- **React 19** + **Vite** (TypeScript only, no plain JS)
- **Redux Toolkit** + **RTK Query**
- **Tailwind CSS** — minimal, responsive, dark/light theme
- **Vitest** + **React Testing Library**

### DevOps
- **Docker + docker-compose**
- **GitHub Actions** — CI (lint, test, build) on every push

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- (For local dev) [`uv`](https://github.com/astral-sh/uv) and Node.js 20+

### Run everything with Docker

```bash
git clone https://github.com/RidhinSamuel/CaseCompass.git
cd CaseCompass
cp .env.example .env       # then edit .env with your HF token
docker compose up --build
```

- Frontend → http://localhost:5173
- Backend API → http://localhost:8000/docs
- RabbitMQ UI → http://localhost:15672 (guest / guest)

### Local backend dev (with uv)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

### Local frontend dev

```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing

The project follows industry-standard testing tiers:

| Tier | Purpose | Tools |
|------|---------|-------|
| **Smoke** | "Does it start?" — boot API, connect DB | pytest, TestClient |
| **Unit** | Isolated function/module tests | pytest, pytest-mock |
| **Functional / Integration** | End-to-end request → DB → response | pytest, testcontainers |
| **Frontend** | Component & Redux slice tests | Vitest, RTL |

Run all backend tests:

```bash
cd backend
uv run pytest
```

Run frontend tests:

```bash
cd frontend
npm test
```

All tests run automatically in **GitHub Actions** on every push and PR.

---

## 📁 Project Structure

```
CaseCompass/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # FastAPI endpoints
│   │   ├── core/             # config, security
│   │   ├── db/               # session, base
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # RAG, hybrid search, embeddings
│   │   ├── workers/          # ingestion workers
│   │   ├── queue/            # RabbitMQ producer/consumer
│   │   └── main.py           # FastAPI entry
│   ├── tests/{unit,functional,smoke}/
│   ├── alembic/              # DB migrations
│   ├── pyproject.toml        # uv-managed deps
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/              # Redux store
│   │   ├── features/         # feature slices
│   │   ├── pages/            # route pages
│   │   ├── components/       # shared UI
│   │   └── api/              # RTK Query
│   ├── tests/
│   ├── vite.config.ts
│   └── Dockerfile
├── documents/                # architecture & module docs (MD)
├── docker/                   # extra Dockerfiles / init scripts
├── .github/workflows/        # CI pipelines
├── docker-compose.yml
└── README.md
```

---

## 📚 Documentation

See the [`/documents`](./documents) folder for deep-dive docs on every part of the system:

- [`architecture.md`](./documents/architecture.md) — full system design
- [`backend.md`](./documents/backend.md) — API, DB, workers
- [`frontend.md`](./documents/frontend.md) — React app structure
- [`rag-pipeline.md`](./documents/rag-pipeline.md) — how RAG + hybrid search work
- [`devops.md`](./documents/devops.md) — Docker, CI, deployment
- [`testing.md`](./documents/testing.md) — testing strategy

---

## 🗺️ Roadmap

- [ ] Multi-tenant workspaces (law firms)
- [ ] PDF & DOCX ingestion (currently plain text first)
- [ ] Reranking with cross-encoder models
- [ ] Streaming LLM responses
- [ ] Kubernetes deployment charts

---

## 📄 License

MIT © Ridhin Samuel

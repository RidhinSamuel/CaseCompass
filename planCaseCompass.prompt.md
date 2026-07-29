## Plan: Case Compass RAG Judicial AI Platform

TL;DR - Build a new Case Compass repository from scratch with a React + Redux frontend, FastAPI backend, RabbitMQ producer/consumer architecture, PostgreSQL hybrid search with pgvector, Redis for non-relational state/caching, plus a separate TXT project spec for a secondary medical research project.

**Steps**
1. Create repository structure for Case Compass.
   - Root files: `README.md`, `docker-compose.yml`, `.gitignore`, `.env.example`, `requirements.txt`, `package.json`.
   - Folders: `/frontend`, `/backend`, `/documents`, `/data` or `/storage` for sample files.
2. Define backend architecture.
   - Use FastAPI with SQLAlchemy and PostgreSQL.
   - Use PostgreSQL with `pgvector` for semantic vectors plus normal SQL metadata columns for hybrid retrieval.
   - Use Redis as a non-relational support layer for session state, query caching, and worker coordination.
   - Add RabbitMQ for producer/publisher architecture: ingestion producer, ingestion workers, and retrieval task workers.
   - Implement RAG pipeline in backend with LangChain and embeddings, using open-source Hugging Face models as the default embedding and LLM source.
   - Store Hugging Face API token and other secrets in `.env` and keep `.env` out of git.
3. Create frontend architecture.
   - Use React with Vite and TypeScript.
   - Use Redux Toolkit for state management.
   - Implement responsive minimal dark/light theme.
   - Add pages: Dashboard, Document upload, Case search, Case detail, Settings/theme toggle.
4. Implement ingestion, hybrid retrieval, and RAG.
   - Add document upload endpoint and ingestion event publisher in backend.
   - Store uploaded documents and case metadata in PostgreSQL.
   - Build multiple worker services to chunk documents, embed chunks, persist vectors, and update ingestion status.
   - Store chunk metadata including `user_id`, `case_id`, `document_id`, `permissions`, `tags`, and `source` so retrieval is always scoped to the correct user or case.
   - Add query endpoint that performs hybrid search: vector similarity + keyword metadata filtering + exact text matching, then uses LangChain to synthesize answers and improve injection quality.
   - Ensure search results only return chunks owned by or permitted for the requesting user.
   - Use Redis for session-level context, vector search cache, and to avoid overloading workers during bursts.
5. Create documents and documentation artifacts.
   - Add `/documents/architecture.md`, `/documents/frontend.md`, `/documents/backend.md`, `/documents/devops.md`.
   - Add external spec file: `medical-research-idea.txt` with a separate project name, document description, and functional requirements.
6. Add Docker support.
   - Create `docker-compose.yml` with services for frontend, backend, PostgreSQL, RabbitMQ, and Redis.
   - Configure backend service to install dependencies and run uvicorn.
   - Configure frontend service to build or serve local app.
   - Configure worker services so ingestion and retrieval can scale independently.
7. Plan commit points.
   - Commit after scaffolding root structure.
   - Commit after backend API + DB schema.
   - Commit after RabbitMQ + worker pipeline.
   - Commit after hybrid retrieval + RAG integration.
   - Commit after frontend UI scaffolding.
   - Commit after docs creation and Docker compose.
   - Commit after final polish and README.

**Relevant files**
- `f:\Ridhin\CaseCompass\docker-compose.yml` — orchestrate PostgreSQL, RabbitMQ, Redis, backend, frontend.
- `f:\Ridhin\CaseCompass\backend\app\main.py` — FastAPI app entrypoint.
- `f:\Ridhin\CaseCompass\backend\app\db\session.py` — Postgres connection and pgvector integration.
- `f:\Ridhin\CaseCompass\backend\app\queue\rabbitmq.py` — RabbitMQ producer and consumer glue.
- `f:\Ridhin\CaseCompass\backend\app\services\rag.py` — LangChain retrieval generation pipeline.
- `f:\Ridhin\CaseCompass\backend\app\services\workers.py` — ingestion and retrieval workers.
- `f:\Ridhin\CaseCompass\frontend\src\App.tsx` — React entry with theme toggle and main UI.
- `f:\Ridhin\CaseCompass\documents\architecture.md` — overall architecture explanation.
- `f:\Ridhin\CaseCompass\medical-research-idea.txt` — secondary medical/research project spec for future use.

**Verification**
1. Start Docker compose and confirm services start: Postgres, RabbitMQ, Redis, backend, frontend.
2. Confirm backend health endpoint returns OK.
3. Upload a sample legal document for user A and verify ingestion status and user-scoped metadata.
4. Run a search query as user A and confirm returned chunks are limited to user A or permitted case membership.
5. Run a search query as user B and verify user A’s chunks are not returned.
6. Confirm hybrid retrieval with vector + keyword metadata returns high-quality cases and generated answers.
7. Confirm React UI loads with theme toggle and responsive layout.
8. Review markdown docs to ensure each part is explained clearly.

**Decisions**
- Use PostgreSQL for document storage, metadata, and vector search with `pgvector`.
- Use Redis as the non-relational support layer for cache, session data, and worker coordination.
- Do not include MongoDB or MySQL in this project.
- Use RabbitMQ as the message broker for producer/consumer architecture.
- Use explicit user-scoped metadata on chunks and document records to enforce per-user retrieval isolation.
- Create one main Case Compass project and one TXT spec file for the secondary medical/research project.
- Use Redux Toolkit for frontend state management.

**Further Considerations**
1. If you want, I can next generate the exact file tree and architecture document before any code is written.
2. We should decide whether the frontend uses Vite or Create React App; I recommend Vite for modern minimal apps.
3. We should decide whether ingestion should support PDF/Word files now or start with plain text uploads first.

# Graph Report - CaseCompass  (2026-10-13)

## Corpus Check
- 71 files · ~13,166 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 5, .ini 1, .mako 1)

## Summary
- 437 nodes · 768 edges · 30 communities (11 shown, 19 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- App.tsx
- documents.py
- main.py
- package.json
- auth.py
- search.py
- config.py
- ingest_worker.py
- logging.py
- Case Compass
- compilerOptions
- vite-env.d.ts
- app/__init__.py
- CLAUDE.md
- co-developer.agent.md
- planCaseCompass.prompt.md
- teacher.agent.md
- {
  useRegisterUserMutation,
  useLoginUserMutation,
  useGetMeQuery,
  useGetDocumentsQuery,
  useCreateDocumentMutation,
  useSearchCasesMutation,
}
- case-compass-backend

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 18 edges
2. `User` - 16 edges
3. `Settings` - 14 edges
4. `App()` - 13 edges
5. `answer_question()` - 11 edges
6. `Case Compass` - 11 edges
7. `Base` - 10 edges
8. `Document` - 10 edges
9. `react` - 10 edges
10. `login()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `register()` --uses--> `User`  [INFERRED]
  backend/app/api/routes/auth.py → backend/app/models/user.py
- `login()` --uses--> `User`  [INFERRED]
  backend/app/api/routes/auth.py → backend/app/models/user.py
- `me()` --uses--> `User`  [INFERRED]
  backend/app/api/routes/auth.py → backend/app/models/user.py
- `create_document()` --uses--> `DocumentCreate`  [INFERRED]
  backend/app/api/routes/documents.py → backend/app/schemas/document.py
- `search()` --uses--> `User`  [INFERRED]
  backend/app/api/routes/search.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (30 total, 19 thin omitted)

### Community 0 - "App.tsx"
Cohesion: 0.07
Nodes (49): apiSlice, baseQueryWithAuth(), CreateDocumentRequest, Document, LoginRequest, rawBaseQuery, RegisterRequest, SearchHit (+41 more)

### Community 1 - "documents.py"
Cohesion: 0.08
Nodes (39): Alembic environment — reads DB URL from Settings and uses our Base metadata., get_current_user(), Session, Shared FastAPI dependencies (auth, DB session)., Resolve the current user from a JWT bearer token., create_document(), get_document(), list_documents() (+31 more)

### Community 2 - "main.py"
Cohesion: 0.06
Nodes (36): health(), get, Health-check endpoints used by Docker, load balancers, and smoke tests., Return 200 if the process is up. Does not touch dependencies., Return 200 only if the database is reachable. Load balancers use this to stop…, ready(), create_app(), lifespan() (+28 more)

### Community 3 - "package.json"
Cohesion: 0.05
Nodes (40): dependencies, lucide-react, react, react-dom, react-redux, react-router-dom, @reduxjs/toolkit, devDependencies (+32 more)

### Community 4 - "auth.py"
Cohesion: 0.09
Nodes (36): login(), me(), get, post, Session, Authentication routes: register + login + who-am-I., Create a new user account., Exchange email/password for a JWT. (+28 more)

### Community 5 - "search.py"
Cohesion: 0.09
Nodes (34): post, Session, Search endpoint: hybrid retrieval + LLM answer, scoped to the current user., Run RAG for the current user's documents only., search(), DocumentCreate, DocumentRead, BaseModel (+26 more)

### Community 6 - "config.py"
Cohesion: 0.09
Nodes (29): aio_pika, aio_pika_abc, asyncio, get_settings(), Any, Application configuration loaded from environment variables. All secrets and…, Fail fast on insecure configuration when running in production., Return a cached Settings singleton. (+21 more)

### Community 7 - "ingest_worker.py"
Cohesion: 0.13
Nodes (21): Configure root logger. Idempotent — safe to call multiple times., setup_logging(), chunk_text(), Text chunking with sensible defaults for legal documents. Legal text is often…, Split a document into overlapping chunks suitable for embedding., embed_texts(), Embed a batch of texts. Returns a list of float vectors., _handle_message() (+13 more)

### Community 8 - "logging.py"
Cohesion: 0.11
Nodes (16): AbstractRobustConnection, Structured logging setup. We use plain stdlib logging with a compact formatter…, Hide the password in a connection URL so it is safe to log., redact_url(), Any, RabbitMQClient, Thin wrapper around aio-pika providing publish + consume helpers. A single…, Establish a robust connection with auto-reconnect. (+8 more)

### Community 9 - "Case Compass"
Cohesion: 0.09
Nodes (21): Backend, Case Compass, Data Flow, Design Goals, DevOps, 📚 Documentation, ✨ Features, Frontend (+13 more)

### Community 10 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleResolution (+11 more)

## Knowledge Gaps
- **87 isolated node(s):** `case-compass-backend`, `name`, `private`, `version`, `type` (+82 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 227 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RabbitMQClient` connect `logging.py` to `config.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `User` connect `documents.py` to `auth.py`, `search.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `User` (e.g. with `get_current_user()` and `login()`) actually correct?**
  _`User` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `Settings` (e.g. with `test_cors_origins_accepts_comma_separated()` and `test_cors_origins_accepts_json_list()`) actually correct?**
  _`Settings` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `case-compass-backend`, `name`, `private` to the rest of the system?**
  _87 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `App.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.07403846153846154 - nodes in this community are weakly interconnected._
- **Should `documents.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08127721335268505 - nodes in this community are weakly interconnected._
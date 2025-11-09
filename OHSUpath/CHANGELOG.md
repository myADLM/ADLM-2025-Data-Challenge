# Changelog

All notable changes to this project will be documented in this file.



## Ideas for new features
- Add conversation-like feature so AI can read previous conversations to better understand user's need.  
- Add a button for users to choose which model they want to use.  
- Make a progress bar on frontend UI to help users understand the current stage.  
- **Important:** Add limiter to pdf preload to avoid memory overflow.

- **Query Type Detection:** Automatically classify user queries into "keyword-oriented" vs "semantic-oriented":  
  - **Keyword-oriented** (common in lab workflows): short queries with rare tokens, units, chemical names, catalog IDs, temperatures, step numbers -> prioritize sparse keyword retriever, optionally enhanced with char n-gram to handle minor typos and underscore/hyphen differences.  
  - **Semantic-oriented**: longer natural language questions, explanations, or vague requests -> prioritize dense/vector retrieval.  
- **Hybrid Weighting:** Dynamically adjust sparse vs dense retrieval weights based on query type (e.g., 0.8 sparse / 0.2 dense for keyword queries; 0.3 sparse / 0.7 dense for semantic queries).  
- **Sparse Retriever Upgrade:** Support dual backends - `bm25s` (fast, scalable) as default, with optional `rank_bm25` (plus and other variants) for experimentation; allow backend switching via config.  
- **Character n-gram re-ranking:** Apply character n-gram scoring on sparse top-N candidates to improve recall on spelling variations, merged tokens, and special identifiers (e.g., `aa_inf3` vs `aainf3`).  


**Net related Platform:**
### Core components

- **API - FastAPI (Python)**  
  Public API for health, auth, query, streaming, files, conversations; plugs into existing RAG pipeline.

- **Gateway - Node.js (TypeScript)**  
  Single browser entry; login (JWT cookie), CORS, basic rate limiting, proxy to FastAPI, SSE pass-through, add security headers.

- **Web - Next.js (TypeScript, responsive)**  
  One codebase for **desktop / tablet / mobile**; login, chat UI (supports streaming), conversation list, source preview; optional PWA later.

- **Admin - Streamlit (local only)**  
  Internal console for dataset ingest, chunking, embedding, indexing, and basic ops; not exposed to the public internet.

- **RAG Engine (Python)**  
  Load -> split -> embed -> index -> retrieve -> answer; caches & indices live in local store.

### Security & multi-user
- Login required for query/stream/files/conversations (via **JWT cookie**).
- Gateway-to-API shared key to prevent direct bypass.
- User identity forwarded via headers; per-account history isolation.
- **Per-user rate limiting / basic quotas** at the gateway.

### Files & sources
- Serve PDFs from a whitelisted data directory only.
- Inline preview; clickable citations from the chat to open documents.

### Streaming
- Server-Sent Events for real-time tokens and finalization events.

### Deployment (web hosting)
- Target: **Linux server** (or **WSL2** during Windows development) with the same layout.
- Optional reverse proxy (Nginx/Caddy) for single domain + HTTPS. Use **SSE-friendly** settings.
- Process manager (systemd) to run web / gateway / api as services.


**Known Issues**
- need to format what is sent to LLM
- need to adjust the "think" in LLM responses
- need to adjust the user display in chat


## [Unreleased]
### Added
- Placeholder for upcoming features.

### Changed
- Placeholder for upcoming changes.

### Fixed
- Placeholder for upcoming bug fixes.

---

## [0.2.45] - 2025-11-09
### Added
- Auto-scroll to cited page: citation bubbles now include `#page=X` fragment to jump directly to the referenced page in browser PDF viewer
- Path handling for nested file directories with wildcard routing support

### Changed
- Removed embedded PDF viewer/preview functionality - simplified to browser-native inline viewing
- Updated file serving from `/files/document/*` to `/files/{file_path}/download` with path parameter support
- Citation schema streamlined to minimal fields: `doc_id`, `title`, `source_url`, `page`, `snippet`, `mime_type`, `file_size`
- File endpoint now uses `Content-Disposition: inline` by default for in-browser viewing
- Gateway compression settings updated to exclude file downloads and SSE streams
- Improved error handling in conversation and query endpoints with graceful fallbacks

### Fixed
- File path resolution for documents in subdirectories using multiple fallback strategies
- Citation sources now properly initialize as empty arrays to prevent undefined errors
- SSE client disconnect handling with proper cleanup and error recovery


## [0.2.44] - 2025-11-08
### Added
- File serving endpoint (`/files/document/{file_path:path}`) with security checks to prevent path traversal
- User attribution fields (`user_id`, `user_name`, `user_email`) in Message model for tracking authors
- Gateway file proxy route (`/api/files/document/*`) for secure file access
- Collaborator identification in chat UI with distinct styling for different users
- Source document deduplication by filename in backend query processing

### Changed
- Bootstrap script now verifies dependencies instead of reinstalling on every run, improving startup time
- Updated to Pydantic v2 compatibility using `model_dump()` instead of deprecated `dict()`
- Enhanced source document handling with comprehensive error handling and graceful fallbacks
- Message retrieval endpoint includes user info and parsed sources
- Chat UI now uses bubble-style alignment (user right, others left) with color coding

### Fixed
- Gateway file routing by adding missing files router import and mount
- File path handling with wildcard pattern for nested paths
- Source JSON serialization for persisting citations across sessions
- Source field preservation in polling and initial load logic


## [0.2.43] - 2025-11-04
### Changed
- Rebranded application to "OHSUpath Reader".
- Redesigned UI with modern gradient theme and enhanced animations.
- Improved chat interface styling and interactions.

### Fixed
- Tab state and scroll position issues in sidebar and share panel toggle behavior.


## [0.2.42] - 2025-11-01
### Added
- RAG Service Integration: Created `net/api/rag_service.py` as a singleton service wrapper for the RAG pipeline, providing document retrieval and query functionality with LLM support.
- API Startup Initialization: Added FastAPI `@app.on_event("startup")` handler in `main.py` to initialize RAG service with config at application startup.
- Source Document Streaming: Enhanced SSE streaming in `query.py` to emit source documents and metadata as separate events (sources, metadata) alongside text chunks.
- Frontend Event Processing: Added multi-event SSE handling in `Client.tsx` to process sources and metadata events separately from text data.

### Changed
- Query Endpoint: Replaced echo response with actual RAG-powered AI responses using the integrated RAG service in `routers/query.py`.
- Source Document Formatting: Enhanced source document metadata to include source file, page number, and content preview (first 200 chars) for frontend display.
- Session Management: Refactored streaming persistence to use a new database session after stream completion to prevent SQLAlchemy DetachedInstanceError.
- Error Handling: Improved error handling in chat client - replaced "info" role error messages with console.error logging for cleaner UI.
- SSE Event Structure: Updated streaming to emit three event types: data (text chunks), sources (document references), and metadata (llm_enabled flag).

### Fixed
- Streaming State Management: Fixed streaming state cleanup by properly resetting `remoteStreaming` and `prevAssistantLenRef` on close and error events.
- UI Jumps During Streaming: Prevented message replacement during active streams by adding conditional check in message update logic.
- Database Session Errors: Resolved DetachedInstanceError when persisting assistant messages after streaming by creating fresh session.


## [0.2.41] - 2025-11-01
### Changed
- Data Directory: Changed `data_dir` from `data/LabDocs` to `data` to scan entire data folder recursively, including all subdirectories.
- Configuration: Updated config.yaml, config.py, rag/pipeline.py, and bootstrap/netstack.sh to use `data/` as root directory.
- SentenceTransformer Loading: Updated model loading in `rag/embedders/st_multi_gpu.py` to explicitly specify `device="cpu"` to prevent meta-tensor issues.
- minidata Directory: Completely removed `minidata/` folder and all references from codebase; project now uses only `data/` directory.

### Fixed
- BM25 Empty Index Error: Fixed `ValueError: max() arg is an empty sequence` when initializing BM25 sparse index with no documents by adding empty corpus handling in `rag/vectorstores/bm25_store.py`.
- SentenceTransformer Meta Tensor Error: Fixed `NotImplementedError: Cannot copy out of meta tensor` by loading model with explicit device parameter.
- Empty Index Persistence: Added graceful handling for saving empty BM25 indexes with proper metadata markers.


## [0.2.40] - 2025-10-20
### Changed
- Simplified `run_app.sh` by removing redundant environment exports.
- Improved SentenceTransformer model loading to avoid meta-tensor issues and ensure proper CPU fallback.
- Cleaned up function naming inconsistencies in `app.py`.


## [0.2.39] - 2025-10-19
### Added
- Progress bar: direct percentage calculation based on file count (current/total files) for smooth left-to-right progress.
- Factory reset: simplified to delete `.rag_store/` and prompt user to restart app for clean GPU initialization.

### Changed
- Progress display: show only file counts (not chunk/doc/vector counts) for cleaner UI.
- Progress bar calculation: removed phase weights, now pure file-based progress (e.g., 5000/10000 = 50%).
- Factory reset button: renamed to "Factory Reset - Delete All Data" with clear restart instruction.
- Config reload: now clears QA and index_bootstrapped flag to ensure fresh pipeline recreation.

### Fixed
- Progress bar jumping backwards: ensured monotonic increase by using file count directly across all phases.
- Factory reset GPU issue: now properly deletes entire `.rag_store/` and instructs user to restart for clean state.
- Phase display confusion: commit_done no longer shows chunk counts, uses cached file counts instead.
- Hugging Face tokenizers warnings: added `TOKENIZERS_PARALLELISM=false` to suppress fork warnings.


## [0.2.38] - 2025-10-19
### Added
- Streamlit UI: complete redesign of sidebar control panel with organized sections (Progress, Index Management, Configuration, System Info, Danger Zone).
- Granular progress tracking: real-time counters for load/split/embed/commit phases with current/total/cached display.
- Smart index optimization: fast-path check to skip unnecessary reindexing when no files changed.
- Batched processing: configurable batch sizes for file loading, embedding, and vector commits to prevent memory overflow on large datasets.
- Streamlit config generator in `run_app.sh`: auto-create `.streamlit/config.toml` to disable file watcher.
- Lazy bootstrap: defer index loading until first query or manual refresh to speed up app startup.
- UI throttling: limit progress updates to ~5 per second to prevent render overhead.

### Changed
- Linux/WSL2: switched multiprocessing start method to `fork` (set BEFORE imports in `app.py`) for improved stability and performance.
- Index manager: added `file_batch_size`, `embed_batch_size`, `commit_batch_size` config options with batched pipeline processing.
- PDF loader and chunker: proper multiprocessing pool cleanup with try/finally blocks; fallback to single-process on errors.
- `bootstrap/linux/run_app.sh`: removed conservative parallelism limits (was 2 workers) to allow full CPU utilization; added Streamlit config setup.
- Progress reporting: emit `{phase}_progress` events during load/split/embed/commit for granular UI updates.
- Config defaults in `config.yaml`: added `manager.file_batch_size=500`, `embed_batch_size=1000`, `commit_batch_size=5000`.
- Manifest loading: lightweight SQLite query at startup to display file count without full bootstrap.
- `.gitignore`: added patterns for Streamlit config, web artifacts, database files, and env files.

### Fixed
- Eliminated Streamlit "filechanged error" by disabling file watcher via config to prevent dataclass hot-reload crashes.
- Fixed "process forked after parallelism" warnings by enforcing fork mode at top of `app.py` before any module imports.
- Memory overflow on large datasets: batched processing prevents loading entire dataset into memory at once.
- Pool cleanup: proper `close()` and `join()` on all multiprocessing pools to prevent zombie processes.
- UI freeze during indexing: throttled progress updates and deferred bootstrap improve responsiveness.
- Slow startup time: lazy index loading and fast-path checks significantly reduce initial load time when index is already up to date.


## [0.2.37] - 2025-10-06
### Added
- Sharded sparse index `BM25ShardSet` (base + delta) with MinMax score fusion.
- Background compaction daemon `start_sparse_compact_daemon(...)` (quiet-period merge, atomic switch).
- Journaling for sparse ops: `SPARSE_COMPACT_*`, `SPARSE_DELTA_ERROR`.

### Changed
- `pipeline`: switch sparse retrieval to `BM25ShardSet`; filter results to existing docstore IDs.
- `index_manager`: on commit, append sparse delta shards for added/modified chunks.
- Deprecated direct use of `index/sparse_index.pkl`.

### Fixed
- Avoid refresh/commit races via interprocess lock during compaction.


## [0.2.36] - 2025-09-30
### Added
- Hybrid retriever: FAISS dense + sparse search with `bm25s` (primary) and `rank_bm25` (fallback).
- Sparse index wrapper `BM25SparseIndex`:
  - Backend selection via `sparse.backend: bm25s | rank_bm25` (default: `bm25s`).
  - `bm25s` path uses `bm25s.tokenize(...)` and `bm25s.BM25().index(...)`.
  - Fallback to `rank_bm25.BM25Okapi` with a lightweight tokenizer when `bm25s` is not available.
  - Save/load to a directory (e.g., `<index_dir>/sparse_index.pkl/`) with:
    - `meta.json` (backend, stopwords) and `id_map.json` for both backends.
    - `bm25s`: backend files saved by `bm25s.BM25.save(dir)`.
    - `rank_bm25`: `tokenized_corpus.json` for rebuild on load.
- Query-type detector (`QueryTypeDetector`) to weight keyword-like queries toward sparse (`bm25s`/`rank_bm25`) and semantic queries toward dense (FAISS).
- Character n-gram + fuzzy reranker (`CharNGramReranker`) with config:
  - `sparse.ngram_rerank.mode: auto | on | off`
  - `sparse.ngram_rerank.{n,weight,jaccard_w,fuzz_w,gap_threshold,top1_threshold,max_rerank}`
- Pipeline wiring for retrieval modes: `dense`, `sparse` (pure `bm25s`/`rank_bm25`), and `hybrid` (auto).
- English ASCII-only pass for retrieval modules to remove Unicode in comments/strings.

### Changed
- FAISS IP metric: warn if both `embedding.normalize_embeddings` and `faiss.normalize_query_in_ip` are false.
- Hybrid path performs direct FAISS search (no LC MMR) for consistent scoring.
- Config reads hardened across dict/dataclass via `_cfg_get` and `_pair_from_cfg`.

### Fixed
- Single-query handling for `bm25s` tokenization shapes.
- `rank_bm25` ranking path works without NumPy (pure-Python fallback).
- Extra dedup by `chunk_id` to reduce repeated chunks.


## [0.2.35] - 2025-09-22
### Changed
- Update `requirements.txt` for keyword-aware hybrid retrieval.


## [0.2.34] - 2025-09-15
### Added
- Share Panel to manage access (add by email, change role, remove).
- Role badge for collaborators and viewers.
- Unread handling: shadow seen and "New" divider.
- Streaming detection and send queue.

### Changed
- Polling and backoff tuned; skip when page is hidden.
- Conversation list updates avoid flicker via signature check.

### Fixed
- Empty trailing assistant bubble after stream end.
- Sticky unread counts in shared chats.


## [0.2.33] - 2025-09-14
### Added
- Unread tracking and simple view state per user.
- Read APIs to mark messages as read.
- Streaming query API (SSE); replies are saved after the stream.
- Gateway support for streaming and read actions.
- Web chat improvements:
  - Local "shadow read" to clear unread quickly.
  - Unread divider labeled "New".
  - Polling with backoff.
  - Detect active streams and queue user input.
  - Send queue runs after streaming ends.
  - Final read ping when leaving a chat.
  - Sidebar collapse polish.
  - Role badge text: "Collaborating, shared by <name>" and "Read-only, shared by <name>".

### Changed
- Shared chats sort by most recent activity.
- Deleting a chat also removes related view state.
- Gateway rate limits and proxy behavior made safer for dev and prod.
- SSR chat page degrades gracefully on gateway errors and still redirects on 401/403.
- Send button states clarified: "Sending...", "Queued", "Wait...", "Send".

### Fixed
- Unread counts sticking in shared chats.
- Rare message loss during page refresh while sending.
- More reliable SSE piping.
- Small UI issues with scrolling and collapsed sidebar.


## [0.2.32] - 2025-09-14
### Added
- Streamlit admin console inside `app.py`:
  - Tabs: "Admin - Users", "Admin - Data", "Admin - Logins".
  - Users tab: create/update users with optional password hashing.
  - Data overview: counts and simple tables for Users/Conversations/Messages.
  - Login audit: latest 200 events with timestamp, IP, agent, and joined user email.
- Database bootstrap:
  - `ensure_db_ready()` sets SQLite pragmas and runs `SQLModel.metadata.create_all`.
  - Project root is injected into `sys.path` to stabilize imports.

### Changed
- UI: set `st.set_page_config(..., layout="wide")` for more horizontal space.
- Helpers renamed for clarity:
  - `_clear_index` -> `clear_index`
  - `_ensure_index` -> `ensure_index`
  - `_clear_project_artifacts` -> `clear_project_artifacts`

### Fixed
- Streamlit deprecation warnings:
  - Replaced `use_container_width=True` with `width='stretch'` everywhere.


## [0.2.31] - 2025-09-13
### Added
- `net/web/src/app/page.tsx` : add quick links to `/login` and `/chat`, minor styling.


## [0.2.30] - 2025-09-13
### Added
- `net/web/src/lib/api.ts` : small fetch wrapper with `NEXT_PUBLIC_API_BASE` fallback to `/api`, JSON auto-parse, and `credentials: include`.


## [0.2.29] - 2025-09-13
### Added
- `ChatClient.tsx`:
  - Role tabs: All / Owned / Collaborating / Read-only with counts.
  - Load history per conversation; list sort by `last_message_at`.
  - Create-on-first-send and auto title from first message.
  - Rename and share (editor/viewer) actions.
  - SSE streaming via `/api/query/stream/:id`, chunk merge, error handling, and refresh on close.
  - Read-only banner for viewer role.


## [0.2.28] - 2025-09-13
### Added
- Protected chat routes:
  - `(protected)/chat/page.tsx`: SSR fetch conversations from Gateway; redirect to `/login` on 401/403.
  - `(protected)/chat/[public_chat_id]/page.tsx`: SSR load list and select given conversation.
- Gateway base resolution: `GATEWAY_ORIGIN || NEXT_PUBLIC_API_BASE || http://localhost:3000`.


## [0.2.27] - 2025-09-13
### Added
- net/web/src/app/login/page.tsx: SSR fetch `/api/auth/me` (uses GATEWAY_ORIGIN or derived origin); passes `next` and `force` to client.
- net/web/src/app/login/LoginClient.tsx: simple email/password form; POST `/api/auth/login`; continue/logout+switch flow; basic error display.


## [0.2.26] - 2025-09-13
### Added
- net/web/src/app/(protected)/layout.tsx: SSR auth gate. Reads `sid` cookie, calls `/api/auth/me` (uses `GATEWAY_ORIGIN` or derived origin), and redirects to `/login?next=/chat` on 401/403.


## [0.2.25] - 2025-09-13
### Added
- net/gateway/src/routes/auth.ts: POST /auth/login (proxy to API, sign JWT cookie, 204), POST /auth/logout (clear cookie), GET /auth/me (return JWT claims).
- net/gateway/src/routes/conversations.ts: proxy list/create/get/patch/delete; share list/add/patch/delete; unified upstream headers (`x-internal-key`, `x-user-id`).
- net/gateway/src/routes/query.ts: SSE proxy for POST /query/stream and /query/stream/:id; GET compatibility; normalize payload to `{content}`; extract `public_id` from path/body/query/headers/referer; stream piping with `Readable.fromWeb`.


## [0.2.24] - 2025-09-13
### Added
- net/gateway/src/routes/health.ts: GET /api/health -> { ok: true, ts }.
- net/gateway/src/routes/files.ts: GET /api/files/:id proxy to API; forwards x-internal-key and x-user-id; streams body and preserves headers.


## [0.2.23] - 2025-09-13
### Added
- net/gateway/src/middleware/auth.ts: JWT cookie parser `parseAuth` and guard `requireAuth`; clears invalid/expired token.


## [0.2.22] - 2025-09-13
### Added
- net/gateway/src/config.ts: load env (dotenv) and expose port, cookieName, jwtSecret, apiBase, internalKey, corsOrigin, rateLimit.
- net/gateway/src/server.ts: Express app with helmet/compression/cors/json/cookies/morgan/rate-limit; mount /api routes (auth, conversations, query) and start listener.


## [0.2.21] - 2025-09-13
### Added
- net/api/main.py: FastAPI app wiring; run init_db() at startup; enable CORS; mount health/auth/conversations/query routers.


## [0.2.20] - 2025-09-13
### Added
- net/api/routers/auth.py: POST /auth/login (gateway-only via internal key), records LoginEvent.
- net/api/routers/conversations.py: conversations CRUD, fetch by public_chat_id, and share members (list/add/patch/delete) with role checks.
- net/api/routers/query.py: POST /query and POST /query/stream (SSE); store user message, stream echo reply, then persist assistant reply.


## [0.2.19] - 2025-09-13
### Added
- net/api/routers/health.py: GET /health returns {"ok": true}.
- net/api/routers/files.py: placeholder for cited file viewer tool.


## [0.2.18] - 2025-09-13
### Added
- net/api/models.py: SQLModel tables (User, Conversation with public_chat_id, Message, LoginEvent, ConversationMember); helpers now_ms() and new_public_id().
- net/api/schemas.py: Pydantic models (ConversationOut/WithMessages, MessageOut, ConversationPatch, ShareCreate/Update/Out, QueryRequest, UserBrief) and AccessRole.


## [0.2.17] - 2025-09-13
### Added
- net/api/deps.py: internal key check (403) and get_current_user via x-user-id (401/400 on errors).
- net/api/security.py: bcrypt password hash/verify helpers.


## [0.2.16] - 2025-09-13
### Added
- net/api/settings.py: pydantic-settings; reads env; APP_NAME, INTERNAL_SHARED_KEY.
- net/api/db.py: SQLite engine (DB_PATH); init_db() sets WAL/foreign_keys; get_db() session dep.


## [0.2.15] - 2025-09-13
### Added
- Gateway files: package.json, tsconfig.json, package-lock.json.
- Python __init__.py in net/api/ and net/api/routers/ (mark as packages).

### Changed
- .gitignore: small update for temp ignore files.


## [0.2.14] - 2025-09-13
### Changed
- OHSUpath/net/web/src/app/layout.tsx: keep minimal RootLayout.
- OHSUpath/net/web/src/lib/sse.ts: harden POST SSE client (no-store, strict content-type check, robust multi-line parsing) and add `startChatSSE(publicId, content, handlers, extra)` helper.
- Chat page relocated from `OHSUpath/net/web/src/app/chat/page.tsx` to the protected route structure (no functional change).


## [0.2.13] - 2025-09-13
### Changed
- `.gitignore`: refine ignores for Python/Node/Next (env files, caches, build dirs).
- `OHSUpath/requirements.txt`: refresh Python deps.
- `OHSUpath/net/web/next.config.mjs`: dev rewrites to `${GATEWAY_ORIGIN || "http://localhost:3000"}`.
- `OHSUpath/net/web/package.json`: update scripts/deps; refresh lockfile.


## [0.2.12] - 2025-09-13
### Added
- bootstrap/linux/netstack.sh: helper to bootstrap envs, rotate keys, and run the dev stack (API/Gateway/Web) with tmux or background.

### Changed
- Makefile: simple wrappers for env setup, start/stop/status/logs, key rotation, and admin console.


## [0.2.11] - 2025-09-10
### Added
- Chat page: `net/web/src/app/chat/page.tsx`(SSE -> `{NEXT_PUBLIC_API_BASE || "http://localhost:3000"}/query/stream`)
- Env example: `net/web/.env.example`(`NEXT_PUBLIC_API_BASE`)


## [0.2.10] - 2025-09-10
### Added
- SSE client helper at `net/web/src/lib/sse.ts` (`startSSE`): content-type check, multi-line `data` support, lifecycle callbacks (`onOpen/onEvent/onClose`), Abort-safe close, and a 1 MB buffer cap.


## [0.2.9] - 2025-09-10
### Added
- Root layout at `net/web/src/app/layout.tsx`.
- Home page placeholder at `net/web/src/app/page.tsx`.


## [0.2.8] - 2025-09-09
### Added
- Set up default Next.js config at `net/web/next.config.mjs`.


## [0.2.7] - 2025-09-09
### Added
- Frontend TypeScript config at `net/web/tsconfig.json`.
- Track Next.js generated typings `net/web/next-env.d.ts`.


## [0.2.6] - 2025-09-09
### Added
- `net/web/package.json`: initialize **ohsupath-web** (Next.js 14, React 18, TypeScript). Scripts: `dev` (port **4000**), `build`, `start`, `typecheck`, `lint`.
- `net/web/package-lock.json`: lock dependency versions for reproducible installs.


## [0.2.5] - 2025-09-09
### Added
- `requirements.txt`: API deps.
- `.gitignore`: ignore web build artifacts - `net/web/node_modules`, `.next`, `*.tsbuildinfo`.
- `bootstrap/linux/setup.sh`: install/check Node/npm & tmux; auto-install `net/gateway` and `net/web` deps when present.

### Changed
- `bootstrap/linux/setup.sh`: extend base packages.


## [0.2.4] - 2025-09-05
### Changed
- **Linux**: switch multiprocessing start method to **`fork`** (was `spawn`) in chunking/PDF loader paths.
- **bootstrap/linux/run_app.sh**: add a **temporary mitigation** (lower parallelism, safer I/O batching, conservative defaults) to stabilize startup and indexing. Now it runs on **WSL2** and **Linux** without memory overflows, crashes, or disconnections. (mitigation only; not a final fix)

### Fixed / Mitigated
- Reduce frequency of Streamlit **"filechanged error"** and terminal warning  **"The current process just got forked, after parallelism has already been used."**  (mitigation only; not a final fix)


## [0.2.3] - 2025-09-03
### Fixed
- Force multiprocessing start method to `spawn` at startup to prevent hangs/crashes.


## [0.2.2] - 2025-08-30
### Changed
- Solve path issues when moving Windows scripts from root to `bootstrap/windows/` by resolving paths from the repository root.


## [0.2.1] - 2025-08-30
### Added
- Linux scripts mirroring Windows behavior:
  - `bootstrap/linux/setup.sh`
  - `bootstrap/linux/run_app.sh`

### Changed
- Relocated Windows files from repository root to `bootstrap/windows/` to match Linux layout.


## [0.2.0] - 2025-08-29
### Stable version release
- **Second stable end-to-end release**, consolidating the modular RAG architecture with improved resilience and reliability.

- **Modular RAG Core:**
  - Separated components: Loader, Chunker, Embedder, VectorStore, IndexManager, and Pipeline.
  - Config-driven: all parameters (paths, split, embedding, FAISS, retriever, LLM) now come from config (`config.py`, `config.yaml`, or ENV).
  - End-to-end pipeline: bootstrap -> refresh -> embed/cache -> retrieve -> answer.

- **Resilience & Incremental Updates:**
  - **Task pre-initialization**: load/split/embed runs only once; subsequent queries reuse existing vectors without recomputation.
  - **Incremental refresh**: only new/modified/deleted files are processed on each run; unchanged files are skipped.
  - **Crash-safe recovery & resume**:
    - **Journal logging** and **SQLite WAL transactions** ensure consistency even if interrupted mid-run (e.g. power loss).
    - Safe to resume indexing without full rebuild; auto-recovers from index/meta mismatches.

- **Infrastructure & Reliability:**
  - **Atomic file writes** to prevent partial/corrupt saves.
  - **Cross-platform file locking** (POSIX `flock` / Windows `msvcrt`).
  - **SQLite manifest + embedding cache** with robust schema and safe transactions.
  - **Journal rotation** with process/thread metadata for debugging.
  - Auto-recovery on index meta mismatch; safer hashing & cache keying.

- **Retrieval & LLM:**
  - Ollama integration: configurable model, retries, timeouts, headers.
  - LLM can be enabled/disabled at runtime.

- **Frontend (Streamlit app):**
  - **Collapsible Progress card** with real-time logs.
  - **PromptSpy panel** (inspect prompts + context sent to LLM).
  - **Retrieval-only mode** toggle.
  - **Factory Reset** button to wipe indexes and caches.

- **Windows Support:**
  - One-click setup & run via `.bat` and PowerShell scripts.
  - Strict mode scripts with Ollama auto-start, connectivity checks.


## [0.1.39] - 2025-08-29
### Added
- Add `bm25s` inside the requirements for future use.


## [0.1.38] - 2025-08-28
### Changed
- Windows setup script now uses strict mode with fail-fast behavior.
- Added stricter checks for installed packages.


## [0.1.37] - 2025-08-27
### Added
- Automatic Ollama service startup and model check in `run_windows.ps1`.
- Internet connectivity pre-check in `startup_windows.ps1`.

### Changed
- Improved robustness of model creation and startup flow.
- More consistent setup logging and error messages.

### Fixed
- Fixed app launch failures when Ollama service or model was missing.
- Fixed hangs during setup in offline environments.
- Fixed typos and incorrect formatting issues.


## [0.1.36] - 2025-08-27
### Added
- `startup_windows.ps1` - Windows setup (6 steps).
- `run_windows.ps1` - non-admin runner; checks elevation/Python 3.11/Streamlit and launches `app.py`.
- `Windows_Click_Me_To_Run_The_App.bat` - double-click entry for running the app.
- `Windows_Click_Me_To_Setup_The_Computer.bat` - double-click entry for setup.

### Changed
- `.gitignore` - update ignore rules.
- `requirements.txt` - update missing requirements.


## [0.1.35] - 2025-08-16
### Added
- Factory Reset in Settings to wipe `index`, `.rag_store`, `caches` (with confirmation).
- Auto-recover index meta mismatch during bootstrap (clean + rebuild).

### Changed
- Prep progress UI state before heavy work to avoid blank widgets on errors.
- Show indexing summary earlier in Settings.
- Switch distance from `L2` to `cosine` (use`faiss_metric=ip` and `normalize_embeddings=true`) in `config` for higher precision.

### Fixed
- Bootstrap no longer crashes on `Index meta mismatch`.


## [0.1.34] - 2025-08-15
### Added
- Streamlit app: collapsible Progress card, retrieval-only toggle, PromptSpy panel.
- `IndexManager.refresh(...)` now supports a `progress` callback and emits granular events (`*_start`, `*_done`, `refresh_start/done`, `commit_start/done`, `refresh_error`).
- Embedder: `allow_cpu_fallback` option and unified "safe load" policy; expose `device` property.
- Pipeline: forward `progress` kw to manager; `build_qa()` uses local import to avoid import-time side effects.
- Loader: single-process fast path; automatic worker spawn only when needed.
- Windows: guardrails for parallelism (chunker/loader fall back to 1 process on `os.name == "nt"`).
- New file: `requirements.txt`.

### Changed
- App defaults: `USE_YAML_CONFIG_DEFAULT` set to `False` (use env + defaults unless YAML is explicitly enabled).
- Multi-GPU batching: padding path clarified; minor internal cleanups.

### Fixed
- Safer device selection and fallback when CUDA is unavailable or init fails.
- More robust progress logging and journaling alignment.
- Minor logging/format issues, and edge cases in multi-GPU collection.


## [0.1.33] - 2025-08-14
### Added
- Pipeline & retriever now auto-load config (YAML/env) when `cfg=None`.
- `RagPipeline.reload_config()`; `IndexManager.reload_config()` already supported.
- `serve()` reads retriever/FAISS knobs (`use_mmr`, `lambda_mult`, `score_threshold`, `search_kwargs`, `normalize_query_in_ip`).
- `build_qa()` reads LLM extras: `enabled`, `chain_type_kwargs`, `request_timeout_s`, `max_retries`, `headers`.

### Changed
- `embedding.normalize_embeddings` and legacy `embedding.normalize` both supported.
- Warn if `faiss_metric="ip"` with no embedding or query normalization.

### Fixed
- Only pass `chain_type_kwargs` when it hase been set already.
- `_build_ollama_llm` correctly uses `llm.model` / `llm.base_url` and forwards timeout/retries/headers.


## [0.1.32] - 2025-08-14
### Added
- Added `rag/pipeline.py`: assembles loader/chunker/embedder/FAISS/manager; exposes `bootstrap/refresh/serve/build_qa`.
- Added `rag/retriever.py`: Ollama-backed `build_qa` with community fallback.

### Changed
- ST embedder: `embed()` now accepts `str | List[str] | []` and routes to single/multi-GPU consistently.

### Fixed
- Avoid `np.stack([])` on empty batches.
- Prevent 1D encode outputs from triggering dim-mismatch on single-query.


## [0.1.31] - 2025-08-14
### Added
- IndexManager: support automatic config loading from `config.yaml` when `cfg=None` (calls `load_config`), plus new `from_config()` factory method.
- Added `_cfg_get()` helper to support both attribute-style and dictionary-style config access.
- Added `reload_config()` method to allow hot-reloading configuration at runtime.

### Changed
- All config lookups in `refresh()` now use `_cfg_get()` for improved robustness and compatibility.

### Fixed
- Fixed failure to read config values in `refresh()` when `load_config()` returns a dictionary.
- Prevented potential `AttributeError` when optional config sections are missing.


## [0.1.30] - 2025-08-14
### Added
- IndexManager: end-to-end pipeline (scan -> diff -> load -> split -> embed(+cache) -> delete/upsert -> persist -> manifest).
- Embed cache integration with collision-safe keys (text hash + model sig + normalize + dim).
- Journal events: BEGIN_REFRESH / END_REFRESH (with ok flag, counts, elapsed ms).

### Changed
- Lock scope minimized: heavy I/O/compute out of lock; only mutations (delete/upsert/persist/manifest) are locked.
- Lazy hashing: file sha256 only for added/size-or-mtime-changed files.

### Fixed
- Safer cache keying prevents stale hits when model, normalization, or embedding dim changes.
- Robust deletion even when loader uses `file_path` instead of `source`.


## [0.1.29] - 2025-08-13
### Fixed
- Chunk.file_path changed to Optional[str]; relax VectorIndex.as_retriever Protocol
- st_multi_gpu: drop redundant load_config check; detect missing outputs in multi route


## [0.1.28] - 2025-08-13
### Added
- ST embedder now auto-loads settings from config file.
- New embedding config knobs: multi_gpu, dtype, pad_to_batch, in_queue_maxsize.
### Changed
- Respect runtime.device ("cpu") to force CPU and disable multi-GPU.


## [0.1.27] - 2025-08-13
### Added
- Robust Sentence-Transformers embedder with persistent multi-GPU workers (spawn).
- Optional padding of tail batch; configurable per-GPU queue depth.
### Fixed
- Avoid reloading model each call; strict dim checks; deadlock-safe collection; neatly shutdown.


## [0.1.26] - 2025-08-13
### Added
- `RctsChunkerParallel` now auto-loads settings from `config.yaml` when `cfg` is omitted.
- New config keys: `split.num_proc`, `split.source_keys`, `split.page_keys`.
- `chunk_id` length is now driven by `hashing.chunk_id_hash_len`.

### Changed
- `SplitCfg` now has defaults for `source_keys`, `page_keys`, `chunk_id_hash_len` (backward compatible).
- All tunables can be changed in config; no code edits required.

### Fixed
- Tests constructing `SplitCfg(...)` directly no longer fail due to missing fields.


## [0.1.25] - 2025-08-13
### Added
- `RctsChunkerParallel` now supports optional multiprocessing for faster chunking.
- Stable `chunk_id` generation based on source, page, chunk params, and content hash.
- Metadata is sanitized to avoid multiprocessing pickling errors.

### Changed
- `num_proc="max"` is capped by document count.
- Improved extraction of `source` and `page` from metadata with fallback keys.
- `chunk_id` is now stored in metadata.

### Fixed
- Handles missing `source` or `page` without errors.
- Avoids crash when `os.cpu_count()` returns `None`.


## [0.1.24] - 2025-08-13
### Changed
- `PdfLoaderOptimized` now loads settings directly from `config.py` / `config.yaml`.
- No need to pass `LoaderCfg` manually for common parameters.


## [0.1.23] - 2025-08-13
### Added
- Optimized PDF loader with parallel processing support.
- Configurable options for file discovery, prefetch budget, batch size, and text extraction mode.
- Error handling returns structured placeholder documents for unreadable files.

### Changed
- Improved ordering and consistency between single and parallel load modes.
- Safer defaults for process count and file batching.

### Fixed
- Handling of large files exceeding prefetch limits.
- Improved robustness for corrupted or partially unreadable PDFs.


## [0.1.22] - 2025-08-13
### Added
- FAISS options: meta check toggle, delete behavior toggle, file encoding.
- Retriever extras: `normalize_query_in_ip`, `search_kwargs`.
- Backward-compatible load for old `id_map` formats.

### Changed
- IP mode now stores unit-norm vectors (cosine-style).
- JSON read/write uses the chosen encoding.
- Meta mismatch can raise or soft-reset (based on config).

### Fixed
- More robust vector shape/dtype handling.
- Fewer issues across FAISS/LangChain versions.


## [0.1.21] - 2025-08-12
### Added
- New `FaissIndex` in `rag/vectorstores/faiss_store.py`.
- Supports `l2` and `ip` metrics.
- In-memory index with retriever support.
- Atomic save/load (writes temp files, then replace).
- Index meta check on load (`embedding_dim`, `metric`, `model_sig`).
- Adapter `_CallableToEmbeddingsAdapter` to wrap callables as `Embeddings`.
  - Optional normalization in `ip` mode (for cosine-like search).
- Compatible `Document` import (`langchain_core` / `langchain.schema`).

### Changed
- `index_to_docstore_id` unified to `Dict[int, str]` (row -> chunk_id).
- `as_retriever(...)` now requires an `embedding` (Embeddings or callable).
- In `ip` mode:
  - Store vectors are normalized on `upsert`.
  - Query vectors are normalized when using the callable adapter.

### Fixed
- Errors when a callable embedding returned wrong shapes (now coerced to 2D float32).
- Type error when `FAISS` expected an `Embeddings` object (adapter now subclasses `Embeddings`).
- `id_map` JSON keys restored to `int` on load; also supports old list-of-pairs format.


## [0.1.20] - 2025-08-12
### Added
- Added `embed_cache` config section with options for table name, batch limits, and JSON formatting.

### Changed
- Updated `rag/cache/embed_cache.py` to use settings from `embed_cache` config.
- Improved batch handling with placeholder caching and optional chunk size limit.

### Fixed
- Deduplicated keys in `get_many` before querying to avoid redundant lookups.


## [0.1.19] - 2025-08-12
### Added
- Added `rag/cache/embed_cache.py` for SQLite-based embedding cache with configurable PRAGMA settings.


## [0.1.18] - 2025-08-12
### Added
- Added `sqlite` config section (`journal_mode`, `busy_timeout_ms`, `synchronous`, `connect_timeout_s`) to tune SQLite behavior via YAML/env.

### Changed
- `rag/manifest_sqlite.py`: schema/PRAGMA now config-driven; explicit transactions with `BEGIN IMMEDIATE`; supports `str` and `PathLike` paths.

### Fixed
- Robust path handling for bare filenames; create parent dirs when needed.


## [0.1.17] - 2025-08-12
### Added
- **manifest_sqlite** (`rag/manifest_sqlite.py`):
  - Implemented `_conn()` context manager to initialize SQLite manifest database with schema creation and WAL mode.
  - Added `load_all()` to retrieve all file metadata as `dict[str, FileMeta]`.
  - Added `save_bulk()` to overwrite manifest contents in bulk with transaction safety.

### Changed
- **manifest_sqlite**:
  - `_conn()`:
    - Now supports `str` and `os.PathLike` paths (e.g., `Path`, `FsLayout.manifest_db`).
    - Automatically creates parent directory if it does not exist; handles bare filenames without error.
    - Executes `PRAGMA journal_mode=WAL;` for concurrent read/write performance.
    - Executes `PRAGMA busy_timeout=30000;` (30 seconds) to wait for locks before failing.
    - Executes `PRAGMA synchronous=NORMAL;` to improve write performance while keeping durability trade-off acceptable.
  - `save_bulk()`:
    - Starts with `BEGIN IMMEDIATE` to acquire a write lock early and fail fast if unavailable.
    - Wraps operations in an explicit transaction with rollback on error.


## [0.1.16] - 2025-08-12
### Changed
- **types**:
  - `Chunk.meta` type updated from generic `Dict` to `Dict[str, Any]` for more precise typing.
  - `Document` import now prefers `langchain_core.documents` with fallback to `langchain.schema` for compatibility with newer LangChain versions.
- **fs_paths**:
  - `interprocess_lock()` POSIX branch now uses non-blocking flock with retry/backoff and timeout, matching Windows locking behavior and preventing indefinite blocking.
- **journal**:
  - `journal_append()`:
    - `tid` is now a numeric thread identifier; `tid_native` retains native thread ID; `tid_name` stores the thread name.
    - Added `default=str` to JSON serialization to handle non-serializable objects gracefully.
    - Ensures the `journal_log` parent directory exists even if located outside `layout.base`.
  - `rotate_journal()`:
    - Added lower-bound safeguard for `keep` (minimum 1).
    - Added directory `fsync` after rotation to persist rename/unlink operations and reduce data loss risk in power failure scenarios.


## [0.1.15] - 2025-08-11
### Added
- **Journal module** in `rag/storage/journal.py`:
  - `journal_append()` writes JSONL with fields: `ts`, `event`, `data`, `host`, `pid`, `tid` (name), `tid_native` (numeric), `tid_name` (alias of name).
  - `iter_journal()` simple JSONL reader.
  - `rotate_journal()` size-based rotation (`journal.log` -> `.1..N`).
  - Atomic appends via `O_APPEND`; optional `fsync`.
  - Optional compact JSON; optional per-record size guard.
- **Config sections**:
  - `journal`: `enable_lock`, `fsync_default`, `compact_json`, `max_record_bytes`, `rotate_max_bytes`, `rotate_keep`, `default_tail_n`.
  - `lock`: `timeout_s`, `backoff_initial_s`, `backoff_max_s`.

### Changed
- `journal_append()` now reads defaults from config.
- Records now include process/thread context (`pid`, `tid_native`, `tid_name`) for easier debugging.
- `interprocess_lock()` signature now accepts `timeout_s`, `backoff_initial_s`, `backoff_max_s`.
- **Windows locking** now uses non-blocking `msvcrt.locking` + retry/backoff to avoid deadlocks; still raises on timeout.
- `ensure_dirs(layout)` is used before writing to guarantee directory presence.

### Fixed
- Fixed intermittent `OSError: [Errno 36] Resource deadlock avoided` on Windows during concurrent writes.
- Env override handling in `load_config()` is more robust (case-insensitive path to nested dataclass fields; supports float), fixing cases where `CONFIG__paths__journal_filename` did not apply in some shells.


## [0.1.14] - 2025-08-11
### Added
- Added persistent layout fields under `paths` (`store_dir`, `index_dirname`, `manifest_filename`, `embed_cache_filename`, `journal_filename`, `lock_filename`, `tmp_dirname`).
- Added `hashing` section (`normalize`, `encoding`, `chunk_id_hash_len`) to centrally control chunk ID and cache key generation.

### Changed
- `FsLayout.from_base(...)` now accepts the above naming parameters (defaults preserved; backward compatible).
- `sha256_str()` now has an `encoding` parameter; docs clarify using `normalize=None` skips normalization for better performance.

### Fixed
- Fixed typos in comments and inline docs.


## [0.1.13] - 2025-08-11
### Added
- **Atomic file write helper** `atomic_write_text` in `rag/storage/fs_paths.py`  
  - Writes to a temporary file and atomically replaces the target.  
  - Supports `preserve_mode=True` to keep original file permissions, including Windows read-only attributes.  
  - Cleans up temporary files on any error.  
  - Handles cross-device writes by falling back to the target directory when necessary.  
  - Ensures durability by syncing both file and containing directory.
- **Cross-platform interprocess locking** via `interprocess_lock` in `rag/storage/fs_paths.py`  
  - Uses `fcntl.flock` on POSIX and `msvcrt.locking` on Windows.  
  - Raises `RuntimeError` on lock acquisition failure.  
  - Guarantees exclusive file locking between processes.

### Changed
- `FsLayout.from_base` now expands `~` to the user home directory and accepts `os.PathLike` objects in addition to strings.
- **Locking behavior is now stricter:** on both POSIX and Windows, failure to acquire a lock will raise a `RuntimeError` immediately rather than silently continuing without locking.



## [0.1.12] - 2025-08-11
### Added
- Filesystem layout helpers `FsLayout` and `ensure_dirs` in `rag/storage/fs_paths.py`.


## [0.1.11] - 2025-08-11
### Added
- SHA-256 helpers `sha256_bytes` and `sha256_str` in `rag/hashing.py`.


## [0.1.10] - 2025-08-11
### Added
- Core dataclasses and Protocol interfaces in `rag/types.py` for RAG components.


## [0.1.9] - 2025-08-10
### Added
- Offline-first support: embedding model is now loaded from a **local folder path** (default configuration updated accordingly).
- Directory placeholders: added `.gitkeep` files in `models/`, `data/`, and `minidata/` to preserve directory structure without committing large files.

### Changed
- Default embedding model reverted from **`InstructorXL`** back to **`all-MiniLM-L6-v2`** after performance testing showed `InstructorXL` was significantly slower in local runs. `InstructorXL` remains available but is now commented out in the config for optional use.
- Default `embedding.model_name` updated from HF model ID (`sentence-transformers/all-MiniLM-L6-v2`) to a **local path** (`./models/all-MiniLM-L6-v2`) to avoid network calls.

### Fixed
- Fixed YAML config typo: moved `embedding` section to top level to ensure proper offline loading.
- Prevented unintended Hugging Face Hub calls in offline mode by using local paths instead of model IDs.
- Ensured required empty directories are tracked via `.gitkeep` files, avoiding missing folders in fresh clones.


## [0.1.8] - 2025-08-10
### Added
- Add file placeholders for modular rag


## [0.1.7] - 2025-08-10
### Stable version release
- First stable end-to-end release: the full load -> split -> embed -> index -> retrieve -> answer pipeline now runs reliably with stage-wise progress. This milestone consolidates the 0.1.4-0.1.6 improvements (PyMuPDF parsing, FAISS indexing, centralized config, and page-level progress) into a one-click, predictable startup.


## [0.1.6] - 2025-08-10
### Added
- **PDF page-level progress bar** in Terminal: pre-count total pages across all PDFs and update as each page is loaded.  
- Pre-count total pages for more accurate load time estimation.  

### Changed
- Migrated Ollama integration from `langchain_community.llms.Ollama` to `langchain-ollama`'s `OllamaLLM`.  
- Migrated embeddings import from `langchain_community.embeddings` to `langchain-huggingface`'s `HuggingFaceEmbeddings`.  
- Improved Terminal logging format for document loading, splitting, and embedding steps.  
- Reduced verbose per-page printouts in favor of cleaner progress display.  

### Fixed
- Corrected some typos in docstrings and log messages.  
- Removed some unused imports and variables from `app.py` and `rag_engine.py`.  


## [0.1.5] - 2025-08-08
### Added
- **Centralized configuration management** via `config.py` (default developer values) and `config.yaml` (user-editable values).  
- Added support for **environment variable overrides** with `CONFIG__section__field=value` format, enabling easy deployment in VM/Docker.  
- Added `USE_YAML_CONFIG` toggle in `app.py` to switch between YAML+env or env-only configuration modes.  
- New YAML fields for:  
  - PDF ingestion (`paths.allowed_extensions`, `paths.pdf_text_mode`)  
  - Runtime tuning (`min_threads`, `reserve_threads`, `max_workers`, `device`)  
  - Chunk splitting parameters (`chunk_size`, `chunk_overlap`, `min_chars_per_page`)  
  - Embedding and FAISS settings (`model_name`, `embedding_dim`, `batch_size`, `faiss_metric`)  
  - LLM configuration (`provider`, `model`, `chain_type`, `base_url`, `params`)  
  - UI customization (`title`, `page_title`, `input_label`, `spinner_text`)  

### Changed
- Refactored `app.py` and `rag_engine.py` to **read all settings from `Config` object**, eliminating hardcoded values.  
- PDF loading now uses `cfg.paths.pdf_text_mode` and skips pages below `cfg.split.min_chars_per_page`.  
- File scanning now filters by `cfg.paths.allowed_extensions` instead of fixed `.pdf`.  
- Thread pool sizing now respects `cfg.runtime.max_workers` and `cfg.runtime.reserve_threads`.  
- LLM initialization now reads provider/model/params dynamically from config instead of fixed Ollama model.  
- Streamlit UI elements (page title, input prompt, spinner text) now come from config.  

### Fixed
- Updated `InMemoryDocstore` import to `langchain_community.docstore.in_memory` for compatibility with newer LangChain versions.  
- Prevented CUDA errors by falling back to CPU automatically when `cfg.runtime.device` requests GPU but it's unavailable.  
- Avoided loading empty pages by stripping text and checking minimum length before adding to `Document` list.  


## [0.1.4] - 2025-08-08
### Added
- Added support for `.invoke()` method in `RetrievalQA`, replacing deprecated `__call__`.
- Integrated `fitz` (PyMuPDF) for more reliable PDF parsing, replacing `PyPDFLoader`.
- Added progress bars (`tqdm`) for visual feedback during document splitting and embedding.
- Implemented explicit FAISS indexing logic in `embed_documents()` using `faiss.IndexFlatL2`.
- Stored vector index and document mappings in `InMemoryDocstore`.
- Verified embedding dimensions to ensure consistency (expects shape `(1, 384)`).
- Added timing logs and GPU availability checks for improved diagnostics.
- **Added in-memory PDF caching:** all PDF files are now loaded into memory in bulk before text extraction, eliminating disk IO bottlenecks.

### Changed
- Refactored chunk embedding to use manual FAISS construction instead of the built-in `from_documents`.
- Improved error handling and logging in `load_documents_from_folder()` and embedding logic.
- Changed retriever `search_type` to `"similarity"` with `k=4` top results.
- **Significantly improved initialization performance:** loading and parsing large PDF datasets (previously ~1 hour or more to fully load the given data) now completes in ~3 minutes before splitting.

### Fixed
- Fixed missing `source_documents` error caused by deprecated API usage.
- Improved stability in multi-threaded PDF loading with better exception handling.


## [0.1.3] - 2025-08-07
### Added
- Basic multithreaded document loading using `ThreadPoolExecutor`
- Logging for document loading progress and chunking samples
- CUDA availability check during embedding model loading
- Sample outputs for loaded documents and chunks to assist debugging

### Changed
- `load_documents_from_folder` now supports recursive folder search
- Switched to threaded loading of PDFs for improved performance
- Refactored code structure in `rag_engine.py` for clarity and maintainability

### Fixed
- Error handling added to PDF loading to prevent app crash on malformed files
- Improved chunking logic to avoid silent failures on empty input


## [0.1.2] - 2025-08-07
### Added
- Create app.py and rag_engine.py.

### Changed
- Update CHANGELOG and README.

## [0.1.1] - 2025-08-06
### Added
- Create Readme and Changelog.
- Add issue and branch 1-use-GCR-pipeline
- Give collaborators permission to create issue, branch.

## [0.1.0] - 2025-08-06
### Added
- Initial commit.
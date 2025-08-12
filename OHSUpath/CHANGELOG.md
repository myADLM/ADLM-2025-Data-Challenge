# Changelog

All notable changes to this project will be documented in this file.



## Ideas for new features
- Currently can not fully work offline, make the whole pipeline fully offline.  
- Add conversation-like feature so AI can read previous conversations to better understand user's need.  
- Add a button for users to choose which model they want to use.  
- Make a progress bar on frontend UI to help users understand the current stage.  
- When adding or deleting PDFs from the database, avoid reinitializing the entire model if possible.  
- After finishing initialization (load, split, embed, etc.), save the result locally so that it can be reused next time without reprocessing.  
- **Important:** Add limiter to pdf preload to avoid memory overflow.


## [Unreleased]
### Added
- Placeholder for upcoming features.

### Changed
- Placeholder for upcoming changes.

### Fixed
- Placeholder for upcoming bug fixes.

---

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
- First stable end-to-end release: the full load → split → embed → index → retrieve → answer pipeline now runs reliably with stage-wise progress. This milestone consolidates the 0.1.4–0.1.6 improvements (PyMuPDF parsing, FAISS indexing, centralized config, and page-level progress) into a one-click, predictable startup.


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
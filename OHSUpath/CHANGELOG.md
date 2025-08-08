# Changelog

All notable changes to this project will be documented in this file.



## Ideas for new features
- Currently can not fully work offline, make the whole pipeline fully offline.  
- Add conversation-like feature so AI can read previous conversations to better understand user's need.  
- Put all the configurations in one file so it's easier to manage and adjust, such as AI model address, database address, etc.  
- Have both `config.py` and `config.yaml`: `config.py` for local test and debug, `config.yaml` for deployment in VM, Docker, etc.  
- Add a button for users to choose which model they want to use.  
- Adjust the log in terminal to be more friendly for debugging, and make a progress bar on frontend UI to help users understand the current stage.  
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
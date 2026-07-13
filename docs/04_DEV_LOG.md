# DocAgent Development Log

**Version:** v1.0

---

## Task 1 - Initialize Backend

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Initialized FastAPI backend.
- Configured `uv` and `pyproject.toml`.
- Configured CORS middleware.
- Added `GET /health` endpoint.
- Verified backend startup successfully.

### Notes

- Project environment is ready.
- Backend development can continue with Task 2.

---

## Task 2 - Initialize Frontend

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Scaffolded Vue 3 + Vite project.
- Installed dependencies including `vue-router@4`.
- Configured Vite API proxy (`/api` → `http://localhost:8000`).
- Created router with Home (`/`) and Chat (`/chat`) routes.
- Built minimal layout: App.vue header + nav + `<router-view>`.
- Created placeholder pages: HomePage.vue, ChatPage.vue.
- Replaced Vite boilerplate styles with Linear-inspired minimal CSS.
- Verified frontend builds and dev server starts.

### Notes

- Two-page structure is wired and ready for Phase 2 (Knowledge Base) and Phase 4 (Frontend).
- API proxy avoids CORS issues during development.

---

## Task 3 - Configure AI Environment

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Installed `sentence-transformers` and `python-dotenv` as backend dependencies.
- Created `backend/core/config.py` — centralized configuration loading from `.env`.
- Verified all config defaults match `.env.example`.
- Ollama installed and `qwen2.5:3b` pulled successfully.
- OLLAMA_MODELS configured to `D:\mysofterware\Ollama\models`.

### Notes

- Embedding model (`BAAI/bge-small-zh-v1.5`) will be auto-downloaded by `sentence-transformers` on first use.
- Backend is ready for Phase 2 (Knowledge Base) implementation.

---

## Task 4 - PDF Upload

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Created `POST /api/upload` endpoint in `backend/api/upload.py`.
- Implemented three-layer PDF validation:
  1. MIME type check (`application/pdf`).
  2. File size limit (50 MB).
  3. Magic bytes check (`%PDF` header).
- Saved uploaded files to `backend/data/uploads/` with unique names (`{uuid}_{original_stem}.pdf`).
- Created `backend/utils/response.py` — unified `success_response` / `error_response` helpers.
- Added `DATA_DIR` to `backend/core/config.py` for centralized path management.
- Registered upload router in `backend/main.py`.

### Verified

- Valid PDF with correct MIME → accepted and saved.
- Non-PDF file → rejected (MIME type).
- Non-PDF content with PDF MIME → rejected (magic bytes).
- Uploaded file content matches original.

### Notes

- PyMuPDF will be added in Task 5 for actual PDF text extraction.
- File size limit is 50 MB (adjustable in the code).

---

## Task 5 - PDF Parsing

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Installed `pymupdf` (fitz) as a backend dependency.
- Created `backend/models/document.py` — Pydantic models:
  - `DocumentPage`: page number, text content, character count.
  - `ParsedDocument`: filename, total non-empty pages, list of pages, total character count.
- Created `backend/services/parser.py` — `PDFParser` class:
  - `parse(file_path: Path) -> ParsedDocument`
  - Extracts text page by page via PyMuPDF.
  - Skips empty/stripped pages automatically.
  - Preserves original 1-based page numbers for citation support.
  - Raises `FileNotFoundError` for missing files; PyMuPDF raises `FileDataError` for non-PDF files.

### Verified

- 4-page PDF with 2 empty pages → correctly reports 2 non-empty pages.
- Page numbers preserved (1 and 3, not re-indexed).
- Per-page and total character counts accurate.
- Missing files and non-PDF files raise appropriate errors.

### Notes

- Parser is fully independent of chunking (Task 6) and embedding (Task 7).
- Page numbers stored for future citation support (Task 12).
- Structured output is ready for the next task.

---

## Task 6 - Text Chunking

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Installed `langchain` and `langchain-text-splitters` as backend dependencies.
- Created `backend/models/chunk.py` — `TextChunk` model:
  - `chunk_index`: sequential index across the entire document.
  - `page_number`: source page for citation support.
  - `text`: chunk content.
  - `char_count`: character count.
- Created `backend/services/chunker.py` — `DocumentChunker` class:
  - Uses LangChain's `RecursiveCharacterTextSplitter` with separators tuned for Chinese text (`\n\n`, `\n`, `。`, `. `, ` `).
  - Chunks each page independently — no cross-page chunks.
  - Reads `CHUNK_SIZE` (500) and `CHUNK_OVERLAP` (100) from config.
  - Returns a flat `list[TextChunk]` with sequential indices.

### Verified

- 2-page Chinese PDF → 4 chunks, all correctly attributed to their source page.
- No chunks exceed the configured size limit.
- `chunk_index` is sequential (0, 1, 2, 3).
- Single-page short text → 1 chunk with correct metadata.
- Default config values (500/100) used automatically via `core.config`.

### Notes

- Chunker is independent of parsing (Task 5) and embedding (Task 7).
- Chinese-aware separators ensure clean breaks at sentence/paragraph boundaries.
- Flat chunk list with page numbers is ready for embedding generation.
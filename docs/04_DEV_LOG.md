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

---

## Task 7 - Embedding Generation

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Created `backend/models/embedding.py` — `ChunkEmbedding` model:
  - Carries forward `chunk_index`, `page_number`, `text` from the chunk.
  - Stores the embedding vector as `list[float]` for JSON serialisability.
- Created `backend/services/embedder.py` — `EmbeddingService` class:
  - Loads `BAAI/bge-small-zh-v1.5` via `sentence-transformers` once at instantiation.
  - `embed_chunks(chunks) → list[ChunkEmbedding]` — batch-encodes all texts.
  - Normalises embeddings (L2 norm ≈ 1.0) for cosine-similarity search in FAISS.
  - Exposes `dim` property (512) for downstream dimension checks.

### Verified

- Full pipeline: parse → chunk → embed produces 1:1 chunk-to-embedding mapping.
- All embeddings have dimension 512.
- All embeddings are L2-normalised (norm ≈ 1.0000).
- Metadata (`chunk_index`, `page_number`) preserved through the pipeline.

### Notes

- The model is downloaded from HuggingFace on first use and cached locally.
- Embeddings are normalised so FAISS `IndexFlatIP` (inner product) can be used for cosine similarity.
- Ready for FAISS indexing (Task 8).

---

## Task 8 - Build FAISS Index

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Installed `faiss-cpu` as a backend dependency.
- Created `backend/models/search.py` — `SearchResult` model:
  - `chunk_index`, `page_number`, `text`, `score` (cosine similarity via inner product).
- Created `backend/services/vector_store.py` — `VectorStore` class:
  - `build(embeddings)` — creates `IndexFlatIP`, adds normalised vectors.
  - `search(query_embedding, top_k)` — returns top-K `SearchResult` objects sorted by score.
  - `save(directory)` — persists `index.faiss` + `metadata.json` to disk.
  - `load(directory)` — restores index and metadata from disk.
  - `__len__` — returns vector count.
  - Raises `RuntimeError` if searched before `build()`.

### Verified

- Three semantically distinct pages (deep learning, Python, databases).
- Three queries each hit the correct page at rank 1.
- Persist → reload produces identical search results.
- Empty store raises `RuntimeError` on search.
- Missing files raise `FileNotFoundError` on load.

### Notes

- Uses `IndexFlatIP` (exact search, no approximation) — ideal for MVP with small document collections.
- Vector store directory (`backend/data/vector_store/`) is gitignored (runtime data).
- Ready for retrieval pipeline (Task 9).

---

## Task 9 - Retrieval Pipeline

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Created `backend/services/retriever.py` — `RetrievalService` class:
  - Wires `EmbeddingService` + `VectorStore` into a single `retrieve(question, top_k)` call.
  - Returns `list[SearchResult]` ranked by cosine similarity.
  - Returns `[]` for empty/blank questions.
  - Reads `TOP_K` default from config.

### Verified

- Three semantically distinct topics (CNN, Python decorators, pH/chemistry).
- Three natural-language queries each hit the correct page at rank 1 with clear score margins.
- Empty string → `[]`.
- Blank string → `[]`.
- `top_k=2` returns exactly 2 results.

### Notes

- Retrieval is the bridge between the knowledge base (Phase 2) and answer generation (Phase 3).
- The service is stateless — it depends on an already-built `VectorStore`.
- Ready for prompt generation (Task 10).

---

## Task 10 - Prompt Generation

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Created `backend/prompts/qa_template.txt` — Chinese prompt template for Qwen2.5:
  - System role: "你是一个专业的文档助手"
  - `{context}` placeholder for retrieved chunks.
  - `{question}` placeholder for user input.
  - Instructions: answer from context only, acknowledge gaps, cite page numbers.
- Created `backend/services/prompt_builder.py` — `PromptBuilder` class:
  - Loads template from disk on init (not hardcoded).
  - `build(context_chunks, question) → str` — formats chunks with `[页码 N]` labels and fills the template.
  - `_format_context()` renders each chunk as a labelled block.

### Verified

- Full chain: retrieve → build prompt produces well-formed output.
- Context chunks formatted with `[页码 N]` markers.
- All template sections present (参考文档内容, 用户问题, 回答要求).
- Prompt contains the correct question and relevant context.

### Notes

- Template is stored as a file, not hardcoded — easy to iterate on prompt engineering.
- Ready for Chat API (Task 11).

---

## Task 11 - Chat API

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Created `backend/services/llm.py` — `LLMService` class:
  - Calls Ollama `/api/generate` via HTTP (`requests`).
  - Configurable `base_url` and `model` (defaults from config).
  - Returns raw generated text.
- Created `backend/services/pipeline.py` — `ProcessingPipeline` class:
  - Orchestrates the full parse → chunk → embed → index → save flow.
  - `process(file_path) → int` returns chunk count.
  - Reused by the upload endpoint.
- Created `backend/api/chat.py` — `POST /api/chat` endpoint:
  - Request: `{"question": "..."}`.
  - Response: `{"answer": "...", "sources": [{"page": 1, "content": "..."}]}`.
  - Loads vector store from disk; returns 503 if no knowledge base exists.
  - Returns 400 for empty questions.
  - Returns 502 if LLM generation fails.
- Updated `backend/api/upload.py` — runs `ProcessingPipeline` after saving the PDF.
- Updated `backend/main.py` — registered chat router.
- Added `VECTOR_STORE_DIR` to `backend/core/config.py`.

### Verified (end-to-end)

- Upload PDF → index built automatically (1 chunk).
- Question "什么是Spring IoC？" → LLM answers correctly with "根据文档第一页" citation.
- Upload new PDF → index rebuilt, old content replaced.
- Question about new content "什么是反向传播？" → LLM answers about backpropagation citing page 1.
- Empty question → 400 with unified error.
- No knowledge base → 503 with clear message.

### Notes

- The complete RAG pipeline is now wired as a single API flow.
- Phase 3 (RAG) is complete. Ready for citation display (Task 12).

---

## Task 12 - Citation Support

**Status:** ✅ Completed

**Date:** 2026-07-13

### Completed

- Added `filename` field to `SearchResult` model — carries the original PDF name
  through the search pipeline.
- Updated `VectorStore`:
  - `build()` now accepts a `filename` argument stored alongside chunk metadata.
  - `save()` persists filename in `metadata.json` as a structured dict
    (`{"filename": "...", "chunks": [...]}`).
  - `load()` supports both the new format and legacy flat-list format
    (backward compatible).
  - `search()` populates `filename` in every `SearchResult`.
- Updated `ProcessingPipeline.process()` to pass the PDF filename to
  `VectorStore.build()`.
- Updated `Source` model in `chat.py` to include `filename` alongside `page`
  and `content`.
- Created `POST /api/reset` endpoint in `backend/api/reset.py`:
  - Deletes the vector store directory (index + metadata).
  - Clears uploaded PDFs.
  - Returns 200 with success message; idempotent ("Nothing to reset" if
    already empty).
- Registered reset router in `backend/main.py`.
- Improved prompt template — LLM now cites `【第N页】` inline in answers for
  structured, verifiable citations.

### Verified

- Chat API `sources[]` now includes `filename`, `page`, and `content` for
  every retrieved chunk.
- LLM answer text includes `【第N页】` citation markers.
- Reset clears the knowledge base; subsequent chat returns 503.
- Double reset is idempotent.
- Re-upload after reset works correctly (full pipeline executes).

### Notes

- The `filename` stored is the unique server-side name (e.g.
  `{uuid8}_{stem}.pdf`), not the user's original filename. This is
  intentional — the original name is already returned by the upload endpoint.
- Metadata format change (list → dict) is backward compatible with pre-Task
  12 indexes.
- Phase 4 (Frontend) is next: Task 13 (Upload Page) and Task 14 (Chat Page).
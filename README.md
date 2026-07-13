# DocAgent

A local AI document assistant powered by RAG (Retrieval-Augmented Generation).

Upload PDF documents, build a searchable knowledge base, and ask questions — answers are generated from your documents with page-level citations.

## Tech Stack

| Module     | Technology              |
|------------|-------------------------|
| Frontend   | Vue 3 + Vite            |
| Backend    | FastAPI (Python)        |
| LLM        | Ollama + Qwen2.5-3B     |
| Embedding  | BAAI/bge-small-zh-v1.5  |
| Vector DB  | FAISS                   |
| PDF Parser | PyMuPDF                 |

## Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com/) with `qwen2.5:3b` pulled

## Quick Start

### 1. Clone and configure

```bash
git clone <repo-url> && cd DocAgent
cp .env.example .env          # edit if needed
```

### 2. Backend

```bash
cd backend
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Use

1. Open `http://localhost:5173` in your browser.
2. Upload a PDF on the **Home** page.
3. Ask questions on the **Chat** page.

## API Endpoints

| Method | Path          | Description                        |
|--------|---------------|------------------------------------|
| GET    | `/health`     | Health check                       |
| POST   | `/api/upload` | Upload a PDF and build the index   |
| POST   | `/api/chat`   | Ask a question (RAG)               |
| POST   | `/api/reset`  | Delete the current knowledge base  |

## Project Structure

```text
DocAgent/
├── backend/
│   ├── api/          # REST endpoints
│   ├── core/         # Configuration
│   ├── models/       # Pydantic models
│   ├── prompts/      # LLM prompt templates
│   ├── services/     # Business logic (parser, chunker, embedder, etc.)
│   └── utils/        # Helpers
├── frontend/
│   └── src/
│       ├── pages/    # HomePage, ChatPage
│       └── router/   # Vue Router config
├── docs/             # PRD, spec, task list, dev log
├── .env.example
└── README.md
```

## Documentation

- [PRD](docs/01_PRD.md)
- [AI Coding Spec](docs/02_AI_CODING_SPEC.md)
- [Task List](docs/03_TASK.md)
- [Development Log](docs/04_DEV_LOG.md)

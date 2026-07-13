# DocAgent AI Coding Specification

**Version:** v1.0

---

# 1. Tech Stack

| Module          | Technology                   |
| --------------- | ---------------------------- |
| Frontend        | Vue 3 + Vite                 |
| Backend         | FastAPI                      |
| LLM             | Ollama + Qwen2.5-3B-Instruct |
| Embedding       | BAAI/bge-small-zh-v1.5       |
| Vector Store    | FAISS                        |
| PDF Parser      | PyMuPDF                      |
| RAG Framework   | LangChain                    |
| Package Manager | uv                           |

---

# 2. Project Structure

```text
DocAgent/
├── backend/
│   ├── api/
│   ├── core/
│   ├── services/
│   ├── models/
│   ├── prompts/
│   ├── utils/
│   ├── data/
│   ├── vector_store/
│   └── main.py
│
├── frontend/
│   ├── src/
│   └── public/
│
├── docs/
│
├── tests/
│
├── requirements.txt
├── .env
└── README.md
```

---

# 3. System Architecture

```text
PDF
 ↓
Document Loader
 ↓
Text Splitter
 ↓
Embedding
 ↓
FAISS

Question
 ↓
Embedding
 ↓
Similarity Search
 ↓
Top-K Chunks
 ↓
Prompt
 ↓
Qwen
 ↓
Answer + Citation
```

---

# 4. Data Flow

## Upload Flow

Upload PDF

↓

Parse PDF

↓

Split Text

↓

Generate Embeddings

↓

Build FAISS Index

↓

Ready

---

## Chat Flow

Question

↓

Embedding

↓

FAISS Search

↓

Top-K Chunks

↓

Prompt Template

↓

Qwen

↓

Answer + Citation

---

# 5. API Design

## POST /api/upload

Upload PDF and build vector index.

Response

```json
{
  "success": true,
  "message": "Upload successful"
}
```

---

## POST /api/chat

Request

```json
{
  "question": "什么是 Spring IoC？"
}
```

Response

```json
{
  "answer": "...",
  "sources": [
    {
      "page": 12,
      "content": "..."
    }
  ]
}
```

---

## POST /api/reset

Delete current knowledge base.

---

# 6. Development Rules

* Follow RESTful API design.
* Keep frontend and backend separated.
* One module, one responsibility.
* Use type hints for all Python functions.
* Store configuration in `.env`.
* Do not hardcode prompts in business logic.
* Return unified JSON responses.
* Handle exceptions centrally.
* Keep functions small and readable.

---

# 7. Coding Standards

* Use snake_case for Python.
* Use camelCase for JavaScript.
* Add docstrings to public functions.
* Keep each file focused on one feature.
* Avoid duplicate code.
* Prioritize readability over clever implementations.

---

# 8. MVP Scope

Included:

* PDF upload
* PDF parsing
* Text chunking
* Embedding
* FAISS indexing
* RAG retrieval
* AI question answering
* Citation display

Not Included:

* Login
* OCR
* Word documents
* Chat history
* Multi-user support
* Cloud deployment
* Multi-knowledge-base management

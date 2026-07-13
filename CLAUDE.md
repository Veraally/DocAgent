# CLAUDE.md

# DocAgent

This file defines the long-term development rules for Claude Code.

Before starting any development task, always read:

* `docs/01_PRD.md`
* `docs/02_AI_CODING_SPEC.md`
* `docs/03_TASK.md`
* `docs/04_DEV_LOG.md` (if it exists)

These documents are the source of truth for this project.

---

# Development Workflow

* Complete only one task at a time.
* Do not implement future tasks unless explicitly requested.
* Keep the project runnable after every completed task.
* Explain the files you created or modified.
* If requirements are unclear, ask before implementing.
* Do not refactor unrelated code unless explicitly requested.
* If a requested change conflicts with the project documentation, stop and ask for clarification before making changes.
* Use `uv` with `pyproject.toml` for Python dependency management.

---

# Coding Principles

* Keep the implementation simple (KISS).
* Avoid duplicate code (DRY).
* One module, one responsibility.
* Prefer readability over clever implementations.
* Follow the existing project architecture.
* Do not introduce unnecessary dependencies.

---

# Backend

* Use FastAPI.
* Follow RESTful API design.
* Use Python type hints.
* Handle exceptions centrally.
* Return a consistent JSON response format.
* Store configuration in `.env`.

---

# Frontend

* Use Vue 3.
* Use Vue Router for page navigation.
* Keep components small and reusable.
* Use asynchronous API requests.
* Keep the UI clean and responsive.

---

# RAG

* Parse PDF using PyMuPDF.
* Split documents into chunks before embedding.
* Use HuggingFace `sentence-transformers` for embedding generation.
* Generate embeddings before indexing.
* Use FAISS as the vector store.
* Persist the FAISS index to disk and reload it on startup.
* Use the model configured in `.env`.
* Every answer should include document citations whenever available.

---

# UI Style

Use a modern interface inspired by Linear.

Design principles:

* Minimal
* Clean layout
* Plenty of whitespace
* Rounded corners
* Soft shadows
* Responsive design

---

# Documentation

* Treat `docs/01_PRD.md`, `docs/02_AI_CODING_SPEC.md`, and `docs/03_TASK.md` as the source of truth.
* Do not modify these documents unless explicitly requested.
* The only exception is `docs/04_DEV_LOG.md`, which should be updated after each completed task.

---

# Security

* Never hardcode secrets.
* Never commit API keys, passwords, or tokens.
* Never commit the `.env` file.
* Follow the `.gitignore` configuration.
* Do not expose local file paths or sensitive system information in API responses.

---

# Git

* One task, one commit.
* Keep commit messages clear and concise.
* Do not modify unrelated files.
* Make the smallest possible change to accomplish the current task.

---

# After Completing Each Task

1. Update `docs/04_DEV_LOG.md`.
2. Explain the implementation and the purpose of each created or modified file.
3. Wait for review before continuing.
4. Do not continue to the next task until approval.
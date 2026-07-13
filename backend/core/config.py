"""Application configuration loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env")


# --- Ollama (LLM) ---
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5:3b")

# --- Embedding ---
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")

# --- RAG ---
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
TOP_K: int = int(os.getenv("TOP_K", "5"))

# --- Paths ---
DATA_DIR: Path = _project_root / "backend" / "data"
VECTOR_STORE_DIR: Path = DATA_DIR / "vector_store"

"""FAISS vector store service.

Builds a searchable index from :class:`~models.embedding.ChunkEmbedding`
objects, persists it to disk, and provides similarity search for RAG
retrieval.
"""

import json
from pathlib import Path

import faiss
import numpy as np

from models.embedding import ChunkEmbedding
from models.search import SearchResult


class VectorStore:
    """A FAISS-backed vector index with associated chunk metadata."""

    def __init__(self, dim: int = 512) -> None:
        """Create an empty vector store.

        Call :meth:`build` to populate the index before searching.
        """
        self.dim = dim
        self.index: faiss.Index | None = None
        self._metadata: list[dict] = []
        self._filename: str = ""

    @property
    def filename(self) -> str:
        """The original PDF filename this index was built from."""
        return self._filename

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self, embeddings: list[ChunkEmbedding], filename: str = "") -> None:
        """Build a FAISS index from *embeddings*.

        Uses ``IndexFlatIP`` (inner product) because embeddings are
        L2-normalised, making inner product equivalent to cosine similarity.

        Args:
            embeddings: Chunks with their embedding vectors.
            filename: The original PDF filename (stored for citations).
        """
        vectors = np.array(
            [e.embedding for e in embeddings], dtype=np.float32
        )
        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(vectors)
        self._filename = filename

        self._metadata = [
            {
                "chunk_index": e.chunk_index,
                "page_number": e.page_number,
                "text": e.text,
            }
            for e in embeddings
        ]

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self, query_embedding: list[float], top_k: int = 5
    ) -> list[SearchResult]:
        """Return the *top_k* chunks most similar to *query_embedding*.

        Args:
            query_embedding: A single embedding vector (same dimension as
                the index).
            top_k: Number of results to return.

        Returns:
            Results sorted by descending similarity score.

        Raises:
            RuntimeError: If :meth:`build` has not been called yet.
        """
        if self.index is None:
            raise RuntimeError("VectorStore has no index. Call build() first.")

        query = np.array([query_embedding], dtype=np.float32)
        scores, indices = self.index.search(query, top_k)

        results: list[SearchResult] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self._metadata):
                continue
            meta = self._metadata[idx]
            results.append(
                SearchResult(
                    chunk_index=meta["chunk_index"],
                    page_number=meta["page_number"],
                    text=meta["text"],
                    score=float(score),
                    filename=self._filename,
                )
            )
        return results

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, directory: Path) -> None:
        """Persist the index and metadata to *directory*.

        Creates ``index.faiss`` and ``metadata.json`` inside *directory*.
        The directory is created if it does not exist.
        """
        if self.index is None:
            raise RuntimeError("Nothing to save — no index has been built.")

        directory.mkdir(parents=True, exist_ok=True)

        index_path = directory / "index.faiss"
        meta_path = directory / "metadata.json"

        faiss.write_index(self.index, str(index_path))

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(
                {"filename": self._filename, "chunks": self._metadata},
                f,
                ensure_ascii=False,
                indent=2,
            )

    @classmethod
    def load(cls, directory: Path, dim: int = 512) -> "VectorStore":
        """Load a previously saved index and metadata from *directory*.

        Args:
            directory: Path containing ``index.faiss`` and ``metadata.json``.
            dim: Embedding dimension (must match the saved index).

        Returns:
            A :class:`VectorStore` ready for :meth:`search`.

        Raises:
            FileNotFoundError: If *directory* or its files are missing.
        """
        index_path = directory / "index.faiss"
        meta_path = directory / "metadata.json"

        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found: {index_path}")
        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata not found: {meta_path}")

        store = cls(dim=dim)
        store.index = faiss.read_index(str(index_path))

        with open(meta_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, list):
            # Legacy format (pre-Task 12): flat list of chunk dicts
            store._metadata = raw
            store._filename = ""
        else:
            store._metadata = raw.get("chunks", [])
            store._filename = raw.get("filename", "")

        return store

    def __len__(self) -> int:
        """Return the number of vectors in the index."""
        if self.index is None:
            return 0
        return self.index.ntotal

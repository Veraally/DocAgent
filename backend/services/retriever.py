"""RAG retrieval pipeline.

Orchestrates the embedding and vector-search steps to turn a raw user
question into a set of relevant document chunks.
"""

from core.config import TOP_K
from models.search import SearchResult
from services.embedder import EmbeddingService
from services.vector_store import VectorStore


class RetrievalService:
    """Retrieve relevant document chunks for a user question.

    Wires together :class:`EmbeddingService` and :class:`VectorStore` so
    callers only need to pass a question string.
    """

    def __init__(
        self,
        embedder: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        self._embedder = embedder
        self._store = vector_store

    def retrieve(
        self, question: str, top_k: int = TOP_K
    ) -> list[SearchResult]:
        """Return the *top_k* most relevant chunks for *question*.

        Args:
            question: The raw user question.
            top_k: Number of chunks to retrieve (default from config).

        Returns:
            Ranked list of :class:`SearchResult` objects (highest score
            first).  Returns an empty list if *question* is blank.

        Raises:
            RuntimeError: If the vector store has not been built yet.
        """
        if not question or not question.strip():
            return []

        query_vec = self._embedder.model.encode(
            [question],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0].tolist()

        return self._store.search(query_vec, top_k)

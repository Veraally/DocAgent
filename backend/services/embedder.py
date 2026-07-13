"""Embedding generation service.

Converts :class:`~models.chunk.TextChunk` objects into
:class:`~models.embedding.ChunkEmbedding` objects by running each chunk's
text through a HuggingFace sentence-transformer model.

The model is loaded once at instantiation and reused for all subsequent
calls, keeping generation fast and memory-efficient.
"""

from sentence_transformers import SentenceTransformer

from core.config import EMBEDDING_MODEL
from models.chunk import TextChunk
from models.embedding import ChunkEmbedding


class EmbeddingService:
    """Generate embeddings for text chunks using a local transformer model."""

    def __init__(self, model_name: str = EMBEDDING_MODEL) -> None:
        """Load the sentence-transformer model.

        The model is downloaded from HuggingFace on first use and cached
        locally for subsequent runs.
        """
        self.model = SentenceTransformer(model_name)

    @property
    def dim(self) -> int:
        """Return the embedding vector dimension."""
        return self.model.get_embedding_dimension()

    def embed_chunks(self, chunks: list[TextChunk]) -> list[ChunkEmbedding]:
        """Generate embeddings for every chunk in *chunks*.

        Args:
            chunks: The text chunks to embed.

        Returns:
            A list of :class:`ChunkEmbedding` objects, one per input chunk,
            preserving order and carrying all metadata forward.
        """
        if not chunks:
            return []

        texts = [chunk.text for chunk in chunks]
        vectors = self.model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True,
        )

        return [
            ChunkEmbedding(
                chunk_index=chunk.chunk_index,
                page_number=chunk.page_number,
                text=chunk.text,
                embedding=vector.tolist(),
            )
            for chunk, vector in zip(chunks, vectors)
        ]

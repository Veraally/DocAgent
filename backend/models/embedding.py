"""Data model for a text chunk paired with its embedding vector."""

from pydantic import BaseModel


class ChunkEmbedding(BaseModel):
    """A :class:`~models.chunk.TextChunk` combined with its embedding vector.

    ``embedding`` is stored as a list of floats for JSON serialisability.
    Downstream consumers (e.g. FAISS) can convert it to a numpy array via
    ``numpy.array(embedding, dtype=numpy.float32)``.
    """

    chunk_index: int
    page_number: int
    text: str
    embedding: list[float]

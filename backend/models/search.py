"""Data model for a single FAISS search result."""

from pydantic import BaseModel


class SearchResult(BaseModel):
    """One hit from a vector similarity search.

    ``score`` is the raw FAISS distance/similarity.  With L2-normalised
    embeddings and ``IndexFlatIP`` this is cosine similarity (higher is
    better, range ``[-1, 1]``).
    """

    chunk_index: int
    page_number: int
    text: str
    score: float
    filename: str = ""

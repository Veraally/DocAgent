"""Data model for a single text chunk produced during document splitting."""

from pydantic import BaseModel


class TextChunk(BaseModel):
    """A contiguous piece of text from a single page of a PDF.

    ``page_number`` points to the original page so citations can reference
    the exact source location.
    """

    chunk_index: int
    page_number: int
    text: str
    char_count: int

"""Document data models for PDF parsing results.

These models carry page-level text extracted from a PDF, preserving page
numbers so that downstream tasks (chunking, citation) can reference the
original document location.
"""

from pydantic import BaseModel


class DocumentPage(BaseModel):
    """A single page extracted from a PDF."""

    page_number: int
    text: str
    char_count: int


class ParsedDocument(BaseModel):
    """The result of parsing a single PDF file.

    ``total_pages`` reflects the actual page count of the original PDF
    (including empty pages), while ``pages`` contains only the non-empty
    pages.  This keeps metadata accurate for citation purposes.
    """

    filename: str
    total_pages: int
    pages: list[DocumentPage]
    total_chars: int

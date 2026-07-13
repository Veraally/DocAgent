"""Text chunking service.

Splits the text of each :class:`~models.document.DocumentPage` into smaller,
overlapping chunks using LangChain's ``RecursiveCharacterTextSplitter``.
Chunks never cross page boundaries so every chunk maps to a single source
page for accurate citations.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import CHUNK_OVERLAP, CHUNK_SIZE
from models.chunk import TextChunk
from models.document import ParsedDocument


class DocumentChunker:
    """Split a parsed document into overlapping text chunks."""

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", ". ", " ", ""],
            length_function=len,
        )

    def chunk(self, document: ParsedDocument) -> list[TextChunk]:
        """Split *document* into chunks, preserving page numbers.

        Each page is chunked independently so no chunk spans across pages.
        A sequential ``chunk_index`` is assigned across the whole document.

        Args:
            document: The parsed PDF to split.

        Returns:
            A flat list of :class:`TextChunk` objects ready for embedding.
        """
        chunks: list[TextChunk] = []
        chunk_index = 0

        for page in document.pages:
            page_chunks = self._splitter.split_text(page.text)
            for text in page_chunks:
                chunks.append(
                    TextChunk(
                        chunk_index=chunk_index,
                        page_number=page.page_number,
                        text=text,
                        char_count=len(text),
                    )
                )
                chunk_index += 1

        return chunks

"""Document processing pipeline.

Orchestrates the full parse → chunk → embed → index → save flow for a
single uploaded PDF.
"""

from pathlib import Path

from core.config import VECTOR_STORE_DIR
from services.chunker import DocumentChunker
from services.embedder import EmbeddingService
from services.parser import PDFParser
from services.vector_store import VectorStore


class ProcessingPipeline:
    """Run the complete knowledge-base build for one PDF file."""

    def __init__(self) -> None:
        self._parser = PDFParser()
        self._chunker = DocumentChunker()
        self._embedder = EmbeddingService()
        self._store = VectorStore(dim=self._embedder.dim)

    def process(self, file_path: Path) -> int:
        """Parse, chunk, embed, index, and persist *file_path*.

        Args:
            file_path: Path to an uploaded PDF file.

        Returns:
            The number of chunks that were indexed.
        """
        parsed = self._parser.parse(file_path)
        chunks = self._chunker.chunk(parsed)
        embeddings = self._embedder.embed_chunks(chunks)

        self._store.build(embeddings, filename=file_path.name)
        self._store.save(VECTOR_STORE_DIR)

        return len(chunks)

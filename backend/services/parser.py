"""PDF parsing service.

Extracts text from PDF files using PyMuPDF, preserving page numbers and
returning structured :class:`ParsedDocument` objects.  This module has no
knowledge of chunking or embedding — it only produces clean, per-page text.
"""

from pathlib import Path

import fitz  # PyMuPDF

from models.document import DocumentPage, ParsedDocument


class PDFParser:
    """Read a PDF file and extract its text page by page."""

    @staticmethod
    def parse(file_path: Path) -> ParsedDocument:
        """Extract text from *file_path* and return a structured document.

        Pages that contain no text after stripping whitespace are
        automatically skipped so downstream tasks (chunking, embedding)
        never receive empty content.

        Args:
            file_path: Absolute or relative path to a PDF file.

        Returns:
            A :class:`ParsedDocument` with metadata and a list of
            :class:`DocumentPage` objects, one per non-empty page.

        Raises:
            FileNotFoundError: If *file_path* does not exist.
            ValueError: If the file cannot be opened as a PDF.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        doc: fitz.Document = fitz.open(str(file_path))
        pages: list[DocumentPage] = []
        total_chars = 0

        try:
            total_pages = len(doc)

            for page_index in range(total_pages):
                page: fitz.Page = doc[page_index]
                text: str = page.get_text().strip()

                # Skip pages with no readable text
                if not text:
                    continue

                page_number = page_index + 1  # 1-based for humans
                char_count = len(text)
                total_chars += char_count

                pages.append(
                    DocumentPage(
                        page_number=page_number,
                        text=text,
                        char_count=char_count,
                    )
                )
        finally:
            doc.close()

        return ParsedDocument(
            filename=file_path.name,
            total_pages=total_pages,
            pages=pages,
            total_chars=total_chars,
        )

"""Prompt builder service.

Assembles the final LLM prompt by injecting retrieved document context and
the user's question into a template stored under ``backend/prompts/``.
"""

from pathlib import Path

from models.search import SearchResult

_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "prompts" / "qa_template.txt"


class PromptBuilder:
    """Build a prompt string for the RAG-based Q&A LLM call."""

    def __init__(self, template_path: Path | None = None) -> None:
        """Load the prompt template from disk.

        Args:
            template_path: Path to a custom template file.  Defaults to
                ``backend/prompts/qa_template.txt``.
        """
        path = template_path or _TEMPLATE_PATH
        self._template = path.read_text(encoding="utf-8")

    def build(
        self, context_chunks: list[SearchResult], question: str
    ) -> str:
        """Format the prompt with retrieved context and the user question.

        Args:
            context_chunks: Ranked search results from the retriever.
            question: The raw user question.

        Returns:
            A complete prompt string ready to send to the LLM.
        """
        context = self._format_context(context_chunks)
        return self._template.format(context=context, question=question)

    @staticmethod
    def _format_context(chunks: list[SearchResult]) -> str:
        """Render each chunk as a labelled block with its page number."""
        blocks: list[str] = []
        for chunk in chunks:
            blocks.append(f"[页码 {chunk.page_number}]\n{chunk.text}")
        return "\n\n".join(blocks)

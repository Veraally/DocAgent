"""Chat API endpoint — RAG-based question answering."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import VECTOR_STORE_DIR
from services.embedder import EmbeddingService
from services.llm import LLMService
from services.prompt_builder import PromptBuilder
from services.retriever import RetrievalService
from services.vector_store import VectorStore
from utils.response import error_response

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    filename: str
    page: int
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


def _build_rag_chain() -> tuple[RetrievalService, PromptBuilder]:
    """Load the vector store and wire up retrieval + prompt services."""
    store = VectorStore.load(VECTOR_STORE_DIR)
    embedder = EmbeddingService()
    retriever = RetrievalService(embedder, store)
    prompt_builder = PromptBuilder()
    return retriever, prompt_builder


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Answer a question using the RAG pipeline.

    Loads the FAISS index from disk, retrieves relevant chunks, builds a
    prompt, and calls the local LLM to generate an answer with citations.
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail=error_response("Question cannot be empty."),
        )

    # Load index (fail early if no knowledge base exists)
    try:
        retriever, prompt_builder = _build_rag_chain()
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=error_response(
                "No knowledge base found. Please upload a PDF first."
            ),
        )

    # RAG pipeline
    results = retriever.retrieve(request.question)
    if not results:
        return ChatResponse(
            answer="未找到相关文档内容，请尝试其他问题或上传相关PDF。",
            sources=[],
        )

    prompt = prompt_builder.build(results, request.question)

    llm = LLMService()
    try:
        answer = llm.generate(prompt)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=error_response(f"LLM generation failed: {str(e)}"),
        )

    sources = [
        Source(filename=r.filename, page=r.page_number, content=r.text)
        for r in results
    ]

    return ChatResponse(answer=answer, sources=sources)

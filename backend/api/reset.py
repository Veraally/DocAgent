"""Knowledge-base reset API endpoint.

Deletes the current FAISS index and document metadata so the user can
upload a new document to replace the existing knowledge base.
"""

import shutil

from fastapi import APIRouter

from core.config import DATA_DIR, VECTOR_STORE_DIR
from utils.response import success_response

router = APIRouter()


@router.post("/api/reset")
def reset_knowledge_base() -> dict:
    """Delete the current knowledge base (vector store and uploads).

    After this call the server returns to a clean state with no indexed
    documents.  The client should upload a new PDF before sending questions.
    """
    removed = False

    # Remove the vector store directory
    if VECTOR_STORE_DIR.exists():
        shutil.rmtree(VECTOR_STORE_DIR)
        removed = True

    # Remove uploaded PDFs (but keep the directory with .gitkeep)
    upload_dir = DATA_DIR / "uploads"
    if upload_dir.exists():
        for item in upload_dir.iterdir():
            if item.name != ".gitkeep":
                if item.is_file():
                    item.unlink()
                else:
                    shutil.rmtree(item)

    return success_response(
        message="Knowledge base reset" if removed else "Nothing to reset",
    )

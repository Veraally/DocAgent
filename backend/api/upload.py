"""PDF upload API endpoint."""

import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from core.config import DATA_DIR
from utils.response import error_response, success_response

router = APIRouter()

PDF_MIME_TYPE = "application/pdf"
PDF_MAGIC_BYTES = b"%PDF"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _validate_pdf(file: UploadFile) -> None:
    """Validate that the uploaded file is a genuine PDF.

    Checks both the content-type header and the file's magic bytes.
    Raises ``HTTPException`` with a unified error response on failure.
    """
    # 1. Check MIME type
    if file.content_type != PDF_MIME_TYPE:
        raise HTTPException(
            status_code=400,
            detail=error_response(
                "Only PDF files are allowed.",
                data={"content_type": file.content_type},
            ),
        )

    # 2. Check file size (read once, keep in memory for validation)
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        file.file.seek(0)
        raise HTTPException(
            status_code=400,
            detail=error_response(
                f"File size exceeds {MAX_FILE_SIZE // (1024 * 1024)} MB limit.",
            ),
        )

    # 3. Check PDF magic bytes
    if not content.startswith(PDF_MAGIC_BYTES):
        file.file.seek(0)
        raise HTTPException(
            status_code=400,
            detail=error_response("Invalid PDF file."),
        )

    # Rewind so the endpoint can re-read the file
    file.file.seek(0)


def _sanitize_filename(filename: str) -> str:
    """Return a safe stem from the original filename."""
    return Path(filename).stem


@router.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    """Upload a PDF file, validate it, and save it to the data directory.

    Returns a unified JSON response with the saved filename on success.
    """
    _validate_pdf(file)

    safe_stem = _sanitize_filename(file.filename or "document")
    unique_name = f"{uuid.uuid4().hex[:8]}_{safe_stem}.pdf"

    upload_dir = DATA_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / unique_name
    content = await file.read()
    file_path.write_bytes(content)

    return success_response(
        message="Upload successful",
        data={
            "filename": unique_name,
            "original_name": file.filename,
        },
    )

"""DocAgent Backend - FastAPI Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from api.upload import router as upload_router

app = FastAPI(
    title="DocAgent",
    description="AI Document Assistant - RAG-based PDF Q&A system",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(chat_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint to verify the server is running."""
    return {"status": "ok"}

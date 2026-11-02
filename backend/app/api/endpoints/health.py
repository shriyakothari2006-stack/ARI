
"""Health and diagnostic endpoints for ARI and Gemini."""

from datetime import datetime, timezone
from fastapi import APIRouter

from app.core.config import settings
from app.models.schemas import (
    HealthStatus,
    GeminiHealthResponse,
    EmbeddingsHealthResponse,
    VectorDBHealthResponse,
)
from app.services.grok_service import gemini_service
from app.rag.embeddings import embedding_service
from app.rag.vector_store import vector_store

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])


@router.get("", response_model=HealthStatus)
def get_system_health():
    """Returns overall system health."""

    is_configured = settings.is_gemini_configured
    chroma_health = vector_store.check_health()
    embeddings_health = embedding_service.check_health()

    overall = (
        "healthy"
        if is_configured and chroma_health["status"] == "ready"
        else "degraded"
    )

    return HealthStatus(
        status=overall,
        version="1.0.0",
        timestamp=datetime.now(timezone.utc),
        services={
            "backend": "operational",
            "database": "sqlite_ready",
            "gemini_configured": is_configured,
            "gemini_model": settings.GEMINI_MODEL,
            "embeddings": embeddings_health["status"],
            "vector_store": chroma_health["status"],
        },
    )


@router.get("/gemini", response_model=GeminiHealthResponse)
def get_gemini_health(test_live: bool = False):
    """Checks Gemini configuration and optionally tests a live connection."""

    if not settings.is_gemini_configured:
        return GeminiHealthResponse(
            configured=False,
            status="not_configured",
            model=settings.GEMINI_MODEL,
            message="Gemini API key is missing. Add GEMINI_API_KEY to backend/.env.",
            latency_ms=None,
            endpoint_tested="Gemini generate_content",
        )

    if not test_live:
        return GeminiHealthResponse(
            configured=True,
            status="configured (untested)",
            model=settings.GEMINI_MODEL,
            message="Gemini API key is configured. Pass ?test_live=true to test the connection.",
            latency_ms=None,
            endpoint_tested="Gemini generate_content",
        )

    test_result = gemini_service.test_connection()

    return GeminiHealthResponse(
        configured=True,
        status=test_result["status"],
        model=settings.GEMINI_MODEL,
        message=test_result["message"],
        latency_ms=test_result.get("latency_ms"),
        endpoint_tested="Gemini generate_content",
    )


@router.get("/embeddings", response_model=EmbeddingsHealthResponse)
def get_embeddings_health():
    """Checks the embedding model."""

    result = embedding_service.check_health()

    return EmbeddingsHealthResponse(
        model_name=result.get("model_name", settings.EMBEDDING_MODEL),
        status=result["status"],
        embedding_dimension=result.get("embedding_dimension"),
        message=result.get("message", "Embedding service status retrieved."),
    )


@router.get("/vector-db", response_model=VectorDBHealthResponse)
def get_vector_db_health():
    """Checks the vector database."""

    result = vector_store.check_health()

    return VectorDBHealthResponse(
        status=result["status"],
        storage_path=str(settings.absolute_chroma_path),
        total_collections=result.get("total_collections", 0),
        total_vectors=result.get("total_vectors", 0),
        message=result.get("message", "Vector database status retrieved."),
    )

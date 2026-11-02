"""Settings and configuration inspection endpoints."""

from fastapi import APIRouter

from app.core.config import settings
from app.models.schemas import SystemSettingsResponse
from app.services.language_service import language_service
from app.rag.embeddings import embedding_service
from app.rag.vector_store import vector_store

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=SystemSettingsResponse)
def get_system_settings():
    """Returns application settings without exposing secret keys."""

    return SystemSettingsResponse(
        gemini_configured=settings.is_gemini_configured,
        gemini_model=settings.GEMINI_MODEL,
        embedding_model=settings.EMBEDDING_MODEL,
        similarity_threshold=settings.SIMILARITY_THRESHOLD,
        top_k_results=settings.TOP_K_RESULTS,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        max_upload_size_mb=settings.MAX_UPLOAD_SIZE_MB,
        allowed_extensions=settings.ALLOWED_EXTENSIONS,
        supported_languages=language_service.get_supported_languages(),
    )


@router.get("/status")
def get_detailed_status():
    """Returns operational status across all subsystems."""

    embeddings_status = embedding_service.check_health()
    vector_status = vector_store.check_health()

    return {
        "gemini": {
            "configured": settings.is_gemini_configured,
            "model": settings.GEMINI_MODEL,
            "endpoint": "Gemini generate_content",
        },
        "embeddings": embeddings_status,
        "vector_database": vector_status,
        "storage": {
            "database_path": str(settings.absolute_db_path),
            "chroma_path": str(settings.absolute_chroma_path),
            "upload_dir": str(settings.absolute_upload_dir),
        },
        "limits": {
            "max_upload_mb": settings.MAX_UPLOAD_SIZE_MB,
            "similarity_threshold": settings.SIMILARITY_THRESHOLD,
            "top_k": settings.TOP_K_RESULTS,
        },
    }

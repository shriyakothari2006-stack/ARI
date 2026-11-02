
"""FastAPI application entrypoint for ARI — Multilingual RAG Knowledge Assistant."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.database.session import init_db
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""

    logger.info("Initializing ARI Backend and SQLite database...")

    init_db()

    logger.info(
        "ARI Backend initialized successfully. Ready for requests on port %d.",
        settings.PORT,
    )

    yield

    logger.info("Shutting down ARI Backend...")


app = FastAPI(
    title="ARI — Multilingual RAG Knowledge Assistant",
    description=(
        "Multilingual Retrieval-Augmented Generation (RAG) platform "
        "powered by Google Gemini, persistent ChromaDB, and "
        "SentenceTransformers."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": (
                "An internal server error occurred. "
                "Please verify backend logs."
            )
        },
    )


# Register API Routes
app.include_router(api_router)


@app.get("/")
def root():

    return {
        "name": "ARI — Multilingual RAG Knowledge Assistant",
        "tagline": "Knowledge, in every language.",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "gemini_model": settings.GEMINI_MODEL,
        "gemini_configured": settings.is_gemini_configured,
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )

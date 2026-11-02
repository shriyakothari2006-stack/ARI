
"""Application configuration using Pydantic Settings."""

from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    FRONTEND_ORIGIN: str = "http://localhost:5173"

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    # Google Gemini API Configuration
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API Key",
    )

    GEMINI_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Default Gemini generation model",
    )

    # Hosted Gemini Embedding Configuration
    EMBEDDING_MODEL: str = Field(
        default="gemini-embedding-001",
        description="Google Gemini multilingual embedding model",
    )

    EMBEDDING_DIMENSION: int = Field(
        default=768,
        description="Embedding vector dimensions",
    )

    EMBEDDING_BATCH_SIZE: int = Field(
        default=8,
        description="Number of document chunks per embedding request",
    )

    # Multilingual RAG Configuration
    SIMILARITY_THRESHOLD: float = Field(
        default=0.35,
        description="Minimum cosine similarity / relevance threshold",
    )

    TOP_K_RESULTS: int = Field(
        default=4,
        description="Number of top retrieved chunks",
    )

    CHUNK_SIZE: int = Field(
        default=800,
        description="Document chunk size",
    )

    CHUNK_OVERLAP: int = Field(
        default=120,
        description="Document chunk overlap",
    )

    # File and Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    CHROMA_PATH: str = "../storage/chroma"

    DATABASE_PATH: str = "../storage/database/ari.db"

    UPLOAD_DIR: str = "../storage/documents"

    # Upload Limits
    MAX_UPLOAD_SIZE_MB: int = 25

    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf",
        ".docx",
        ".txt",
        ".md",
    ]

    # Environment Configuration
    model_config = SettingsConfigDict(
        env_file=str(
            Path(__file__).resolve().parent.parent.parent / ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Absolute Storage Paths
    @property
    def absolute_chroma_path(self) -> Path:
        path = Path(self.CHROMA_PATH)

        if not path.is_absolute():
            path = (self.BASE_DIR / path).resolve()

        path.mkdir(parents=True, exist_ok=True)

        return path

    @property
    def absolute_db_path(self) -> Path:
        path = Path(self.DATABASE_PATH)

        if not path.is_absolute():
            path = (self.BASE_DIR / path).resolve()

        path.parent.mkdir(parents=True, exist_ok=True)

        return path

    @property
    def absolute_upload_dir(self) -> Path:
        path = Path(self.UPLOAD_DIR)

        if not path.is_absolute():
            path = (self.BASE_DIR / path).resolve()

        path.mkdir(parents=True, exist_ok=True)

        return path

    # Gemini Configuration Validation
    @property
    def is_gemini_configured(self) -> bool:
        """Check whether a valid-looking Gemini API key is configured."""

        if not self.GEMINI_API_KEY:
            return False

        clean = self.GEMINI_API_KEY.strip()

        if not clean or clean.lower() in [
            "your_gemini_api_key_here",
            "none",
            "null",
            "replace_me",
        ]:
            return False

        return len(clean) > 8


settings = Settings()

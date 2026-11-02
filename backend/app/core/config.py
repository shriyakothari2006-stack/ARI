
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
        default=None, description="Google Gemini API Key"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Default Gemini model"
    )

    # Multilingual RAG Configuration
    EMBEDDING_MODEL: str = Field(
        default="intfloat/multilingual-e5-base",
        description="Sentence Transformer model for multilingual embeddings"
    )
    SIMILARITY_THRESHOLD: float = Field(
        default=0.35,
        description="Minimum cosine similarity / relevance threshold"
    )
    TOP_K_RESULTS: int = Field(default=4, description="Number of top chunks")
    CHUNK_SIZE: int = Field(default=800, description="Chunk size")
    CHUNK_OVERLAP: int = Field(default=120, description="Chunk overlap")

    # File and Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    CHROMA_PATH: str = "../storage/chroma"
    DATABASE_PATH: str = "../storage/database/ari.db"
    UPLOAD_DIR: str = "../storage/documents"

    # Upload Limits
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".md"]

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def absolute_chroma_path(self) -> Path:
        p = Path(self.CHROMA_PATH)
        if not p.is_absolute():
            p = (self.BASE_DIR / p).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def absolute_db_path(self) -> Path:
        p = Path(self.DATABASE_PATH)
        if not p.is_absolute():
            p = (self.BASE_DIR / p).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def absolute_upload_dir(self) -> Path:
        p = Path(self.UPLOAD_DIR)
        if not p.is_absolute():
            p = (self.BASE_DIR / p).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def is_gemini_configured(self) -> bool:
        """Check whether a Gemini API key is configured."""
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

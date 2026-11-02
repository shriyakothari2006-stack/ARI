"""Multilingual embedding service using SentenceTransformers (intfloat/multilingual-e5-base)."""
import time
from typing import List, Optional
from app.core.config import settings
from app.core.logging import logger

_model_instance = None
_model_loading = False


class MultilingualEmbeddings:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self.model_name = model_name
        self._dimension: Optional[int] = None

    def _get_model(self):
        global _model_instance, _model_loading
        if _model_instance is None:
            _model_loading = True
            logger.info("Loading multilingual embedding model: %s...", self.model_name)
            from sentence_transformers import SentenceTransformer
            _model_instance = SentenceTransformer(self.model_name)
            _model_loading = False
            logger.info("Multilingual embedding model loaded successfully.")
        return _model_instance

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            model = self._get_model()
            self._dimension = model.get_sentence_embedding_dimension()
        return self._dimension

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds document texts prefixed with 'passage: ' and L2-normalized."""
        model = self._get_model()
        prefixed = [f"passage: {t.strip()}" for t in texts]
        embeddings = model.encode(prefixed, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Embeds a single query string prefixed with 'query: ' and L2-normalized."""
        model = self._get_model()
        prefixed = f"query: {query.strip()}"
        embedding = model.encode(prefixed, normalize_embeddings=True, show_progress_bar=False)
        return embedding.tolist()

    def check_health(self) -> dict:
        global _model_instance, _model_loading
        if _model_loading:
            return {
                "status": "loading",
                "model_name": self.model_name,
                "dimension": None,
                "message": "Model is currently being downloaded/loaded.",
            }
        try:
            # Check if model can be initialized or is already loaded
            if _model_instance is None:
                return {
                    "status": "ready (lazy-loaded)",
                    "model_name": self.model_name,
                    "dimension": 768,  # Standard multilingual-e5-base dimension
                    "message": "Model will be initialized on first document ingestion or retrieval.",
                }
            return {
                "status": "ready",
                "model_name": self.model_name,
                "dimension": self.dimension,
                "message": "Model is loaded and ready for multilingual semantic vector calculations.",
            }
        except Exception as e:
            return {
                "status": "error",
                "model_name": self.model_name,
                "dimension": None,
                "message": f"Failed to initialize embedding model: {str(e)}",
            }


embedding_service = MultilingualEmbeddings()

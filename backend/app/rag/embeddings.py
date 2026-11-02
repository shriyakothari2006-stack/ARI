
"""Google Gemini hosted multilingual embedding service for ARI."""

import threading
from typing import List

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logging import logger


_client = None
_client_lock = threading.Lock()


def get_client():
    """Create one shared Gemini API client."""
    global _client

    if _client is None:
        with _client_lock:
            if _client is None:
                if not settings.is_gemini_configured:
                    raise RuntimeError("GEMINI_API_KEY is not configured.")

                _client = genai.Client(api_key=settings.GEMINI_API_KEY)

    return _client


class MultilingualEmbeddings:
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        self.batch_size = settings.EMBEDDING_BATCH_SIZE

    def _embed_batch(self, texts: List[str], task_type: str):
        client = get_client()

        response = client.models.embed_content(
            model=self.model_name,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=self.dimension,
            ),
        )

        if not response.embeddings:
            raise RuntimeError("Gemini returned no embeddings.")

        vectors = []

        for item in response.embeddings:
            if not item.values:
                raise RuntimeError("Gemini returned an empty embedding.")

            vector = [float(value) for value in item.values]

            if len(vector) != self.dimension:
                raise RuntimeError(
                    f"Expected {self.dimension} dimensions, "
                    f"received {len(vector)}."
                )

            # Normalize vectors for cosine similarity.
            norm = sum(value * value for value in vector) ** 0.5

            if norm == 0:
                raise RuntimeError("Gemini returned a zero-length vector.")

            vectors.append([value / norm for value in vector])

        return vectors

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed document chunks for retrieval."""

        if not texts:
            return []

        all_vectors = []

        for start in range(0, len(texts), self.batch_size):
            batch = texts[start:start + self.batch_size]

            vectors = self._embed_batch(
                batch,
                task_type="RETRIEVAL_DOCUMENT",
            )

            all_vectors.extend(vectors)

        logger.info("Generated %d document embeddings.", len(all_vectors))
        return all_vectors

    def embed_query(self, query: str) -> List[float]:
        """Embed a user search query."""

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        vectors = self._embed_batch(
            [query.strip()],
            task_type="RETRIEVAL_QUERY",
        )

        return vectors[0]

    def check_health(self) -> dict:
        """Check configuration without making an API request."""

        configured = settings.is_gemini_configured

        return {
            "status": "ready" if configured else "error",
            "model_name": self.model_name,
            "dimension": self.dimension,
            "message": (
                "Gemini hosted embeddings are configured."
                if configured
                else "GEMINI_API_KEY is missing or invalid."
            ),
        }


embedding_service = MultilingualEmbeddings()

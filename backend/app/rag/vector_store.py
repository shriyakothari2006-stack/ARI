
"""Persistent ChromaDB Vector Store using Gemini embeddings."""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings
from app.core.logging import logger
from app.rag.embeddings import embedding_service


class VectorStore:

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or settings.absolute_chroma_path
        self._client: Optional[chromadb.PersistentClient] = None

    def _get_client(self) -> chromadb.PersistentClient:
        if self._client is None:
            self.storage_path.mkdir(parents=True, exist_ok=True)

            self._client = chromadb.PersistentClient(
                path=str(self.storage_path),
                settings=ChromaSettings(
                    anonymized_telemetry=False
                ),
            )

            logger.info(
                "ChromaDB initialized at: %s",
                self.storage_path,
            )

        return self._client

    def _get_collection_name(self, kb_id: str) -> str:
        """Use a separate collection namespace for Gemini embeddings."""

        clean_id = re.sub(
            r"[^a-zA-Z0-9_-]",
            "_",
            str(kb_id),
        ).lower().strip("_-")

        if not clean_id:
            clean_id = "default"

        # Separate from all previous E5 collections.
        name = f"kb_{clean_id}_gemini001"

        # ChromaDB collection names must not exceed 63 characters.
        return name[:63]

    def get_or_create_collection(self, kb_id: str = "default"):
        client = self._get_client()
        name = self._get_collection_name(kb_id)

        return client.get_or_create_collection(
            name=name,
            metadata={
                "hnsw:space": "cosine",
                "embedding_model": settings.EMBEDDING_MODEL,
                "embedding_dimension": settings.EMBEDDING_DIMENSION,
            },
        )

    def index_chunks(
        self,
        kb_id: str,
        chunks: List[Dict[str, Any]],
    ) -> int:
        """Generate Gemini embeddings and index document chunks."""

        if not chunks:
            return 0

        collection = self.get_or_create_collection(kb_id)

        chunk_ids = [str(c["chunk_id"]) for c in chunks]
        texts = [str(c["text"]) for c in chunks]

        metadatas = [
            {
                "document_id": str(c["document_id"]),
                "document_name": str(c["document_name"]),
                "page_number": (
                    int(c["page_number"])
                    if c.get("page_number") is not None
                    else -1
                ),
                "section": str(c.get("section") or "General"),
                "chunk_index": int(c["chunk_index"]),
            }
            for c in chunks
        ]

        logger.info(
            "Generating Gemini embeddings for %d chunks in KB '%s'...",
            len(chunks),
            kb_id,
        )

        embeddings = embedding_service.embed_documents(texts)

        if len(embeddings) != len(texts):
            raise RuntimeError(
                "Embedding count does not match document chunk count."
            )

        collection.upsert(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        logger.info(
            "Successfully indexed %d chunks using Gemini in KB '%s'.",
            len(chunks),
            kb_id,
        )

        return len(chunks)

    def search(
        self,
        kb_id: str,
        query: str,
        top_k: int = settings.TOP_K_RESULTS,
        threshold: float = settings.SIMILARITY_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """Search the Gemini embedding collection."""

        collection = self.get_or_create_collection(kb_id)

        count = collection.count()

        if count == 0:
            logger.info(
                "Gemini collection for KB '%s' is empty.",
                kb_id,
            )
            return []

        query_embedding = embedding_service.embed_query(query)

        actual_k = min(top_k, count)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        if not results or not results.get("ids") or not results["ids"][0]:
            return []

        matched_chunks = []

        ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        for chunk_id, text, meta, distance in zip(
            ids,
            docs,
            metas,
            distances,
        ):
            similarity = round(1.0 - float(distance), 4)

            if similarity < threshold:
                continue

            raw_page = meta.get("page_number", -1)

            matched_chunks.append({
                "chunk_id": chunk_id,
                "document_id": meta.get("document_id"),
                "document_name": meta.get("document_name"),
                "page_number": (
                    raw_page if raw_page != -1 else None
                ),
                "section": meta.get("section"),
                "text": text,
                "similarity_score": similarity,
            })

        matched_chunks.sort(
            key=lambda item: item["similarity_score"],
            reverse=True,
        )

        return matched_chunks

    def delete_document_chunks(
        self,
        kb_id: str,
        document_id: str,
    ) -> int:
        """Delete all Gemini vectors belonging to one document."""

        collection = self.get_or_create_collection(kb_id)

        result = collection.get(
            where={
                "document_id": str(document_id)
            }
        )

        ids_to_delete = result.get("ids", [])

        if ids_to_delete:
            collection.delete(ids=ids_to_delete)

            logger.info(
                "Deleted %d Gemini chunks for document '%s'.",
                len(ids_to_delete),
                document_id,
            )

        return len(ids_to_delete)

    def delete_collection(self, kb_id: str):
        """Delete only the Gemini collection, never the old E5 collection."""

        client = self._get_client()
        name = self._get_collection_name(kb_id)

        try:
            client.delete_collection(name=name)

            logger.info(
                "Deleted Gemini collection '%s'.",
                name,
            )

        except Exception as exc:
            logger.warning(
                "Could not delete collection '%s': %s",
                name,
                str(exc),
            )

    def count_vectors(self, kb_id: str) -> int:
        try:
            collection = self.get_or_create_collection(kb_id)
            return collection.count()

        except Exception:
            logger.exception(
                "Could not count Gemini vectors for KB '%s'.",
                kb_id,
            )
            return 0

    def check_health(self) -> dict:
        try:
            client = self._get_client()
            collections = client.list_collections()

            total_vectors = sum(
                collection.count()
                for collection in collections
                if collection.name.endswith("_gemini001")
            )

            gemini_collections = [
                collection
                for collection in collections
                if collection.name.endswith("_gemini001")
            ]

            return {
                "status": "ready",
                "storage_path": str(self.storage_path),
                "total_collections": len(gemini_collections),
                "total_vectors": total_vectors,
                "embedding_model": settings.EMBEDDING_MODEL,
                "embedding_dimension": settings.EMBEDDING_DIMENSION,
                "message": (
                    f"Gemini ChromaDB is operational with "
                    f"{len(gemini_collections)} collections and "
                    f"{total_vectors} vectors."
                ),
            }

        except Exception as exc:
            logger.exception("ChromaDB health check failed.")

            return {
                "status": "error",
                "storage_path": str(self.storage_path),
                "total_collections": 0,
                "total_vectors": 0,
                "message": str(exc),
            }


vector_store = VectorStore()

"""Persistent ChromaDB Vector Store for multilingual document chunks."""
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
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            logger.info("ChromaDB PersistentClient initialized at: %s", self.storage_path)
        return self._client

    def _get_collection_name(self, kb_id: str) -> str:
        # Chroma collection names must be 3-63 chars, alphanumeric with dashes/underscores
        clean_id = kb_id.replace("-", "_").lower()
        return f"kb_{clean_id}"

    def get_or_create_collection(self, kb_id: str = "default"):
        client = self._get_client()
        name = self._get_collection_name(kb_id)
        # Use cosine similarity space for normalized e5 embeddings
        return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})

    def index_chunks(self, kb_id: str, chunks: List[Dict[str, Any]]) -> int:
        """Indexes document chunks with embeddings into persistent ChromaDB."""
        if not chunks:
            return 0

        collection = self.get_or_create_collection(kb_id)

        chunk_ids = [c["chunk_id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [
            {
                "document_id": str(c["document_id"]),
                "document_name": str(c["document_name"]),
                "page_number": int(c["page_number"]) if c.get("page_number") is not None else -1,
                "section": str(c.get("section") or "General"),
                "chunk_index": int(c["chunk_index"]),
            }
            for c in chunks
        ]

        logger.info("Generating multilingual embeddings for %d chunks in KB '%s'...", len(chunks), kb_id)
        embeddings = embedding_service.embed_documents(texts)

        # Upsert into ChromaDB to prevent duplicate indexing
        collection.upsert(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        logger.info("Successfully indexed %d chunks in ChromaDB for KB '%s'.", len(chunks), kb_id)
        return len(chunks)

    def search(
        self,
        kb_id: str,
        query: str,
        top_k: int = settings.TOP_K_RESULTS,
        threshold: float = settings.SIMILARITY_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """Semantic search against persistent ChromaDB with multilingual query embedding and similarity scoring."""
        collection = self.get_or_create_collection(kb_id)
        count = collection.count()
        if count == 0:
            logger.info("Collection for KB '%s' is empty.", kb_id)
            return []

        query_embedding = embedding_service.embed_query(query)
        actual_k = min(top_k, count)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_k,
            include=["documents", "metadatas", "distances"],
        )

        matched_chunks = []
        if not results or not results.get("ids") or not results["ids"][0]:
            return []

        ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        for chunk_id, text, meta, dist in zip(ids, docs, metas, distances):
            # ChromaDB cosine distance: distance = 1 - cosine_similarity
            # Therefore similarity = 1 - distance
            similarity = round(1.0 - float(dist), 4)

            # Check similarity against configurable threshold
            if similarity >= threshold:
                raw_page = meta.get("page_number", -1)
                page = raw_page if raw_page != -1 else None

                matched_chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": meta.get("document_id"),
                    "document_name": meta.get("document_name"),
                    "page_number": page,
                    "section": meta.get("section"),
                    "text": text,
                    "similarity_score": similarity,
                })

        # Sort by similarity descending
        matched_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matched_chunks

    def delete_document_chunks(self, kb_id: str, document_id: str) -> int:
        """Deletes all chunks associated with a specific document from ChromaDB."""
        collection = self.get_or_create_collection(kb_id)
        # Query matching IDs first
        result = collection.get(where={"document_id": document_id})
        ids_to_delete = result.get("ids", [])
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            logger.info("Deleted %d chunks for document '%s' from ChromaDB.", len(ids_to_delete), document_id)
        return len(ids_to_delete)

    def delete_collection(self, kb_id: str):
        client = self._get_client()
        name = self._get_collection_name(kb_id)
        try:
            client.delete_collection(name=name)
            logger.info("Deleted ChromaDB collection '%s'.", name)
        except Exception as e:
            logger.warning("Could not delete collection '%s': %s", name, str(e))

    def count_vectors(self, kb_id: str) -> int:
        try:
            collection = self.get_or_create_collection(kb_id)
            return collection.count()
        except Exception:
            return 0

    def check_health(self) -> dict:
        try:
            client = self._get_client()
            collections = client.list_collections()
            total_vecs = sum(c.count() for c in collections)
            return {
                "status": "ready",
                "storage_path": str(self.storage_path),
                "total_collections": len(collections),
                "total_vectors": total_vecs,
                "message": f"ChromaDB is operational with {len(collections)} collections and {total_vecs} vectors.",
            }
        except Exception as e:
            return {
                "status": "error",
                "storage_path": str(self.storage_path),
                "total_collections": 0,
                "total_vectors": 0,
                "message": f"ChromaDB health check failed: {str(e)}",
            }


vector_store = VectorStore()

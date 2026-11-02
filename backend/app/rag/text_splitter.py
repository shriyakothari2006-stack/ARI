"""Recursive text splitter for document chunking with metadata and unique ID preservation."""
import re
import uuid
from typing import List, Dict, Any
from app.core.config import settings


class RecursiveTextSplitter:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
        separators: List[str] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "।", "۔", ". ", "? ", "! ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        """Splits a single string into chunks recursively using separator hierarchy."""
        return self._split(text, self.separators)

    def _split(self, text: str, separators: List[str]) -> List[str]:
        final_chunks = []
        separator = separators[-1]
        new_separators = []

        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break

        splits = text.split(separator) if separator else list(text)

        good_splits = []
        for s in splits:
            if not s:
                continue
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if new_separators:
                    sub_splits = self._split(s, new_separators)
                    good_splits.extend(sub_splits)
                else:
                    # Hard cut if no more separators exist
                    for start in range(0, len(s), self.chunk_size - self.chunk_overlap):
                        good_splits.append(s[start: start + self.chunk_size])

        # Merge splits up to chunk_size with chunk_overlap
        current_chunk = []
        current_len = 0

        for piece in good_splits:
            piece_len = len(piece) + (len(separator) if current_chunk else 0)
            if current_len + piece_len <= self.chunk_size:
                current_chunk.append(piece)
                current_len += piece_len
            else:
                if current_chunk:
                    merged = separator.join(current_chunk).strip()
                    if merged:
                        final_chunks.append(merged)
                    # Keep overlap pieces
                    overlap_chunk = []
                    overlap_len = 0
                    for prev_piece in reversed(current_chunk):
                        if overlap_len + len(prev_piece) <= self.chunk_overlap:
                            overlap_chunk.insert(0, prev_piece)
                            overlap_len += len(prev_piece)
                        else:
                            break
                    current_chunk = overlap_chunk + [piece]
                    current_len = sum(len(p) for p in current_chunk) + len(separator) * max(0, len(current_chunk) - 1)
                else:
                    final_chunks.append(piece)

        if current_chunk:
            merged = separator.join(current_chunk).strip()
            if merged:
                final_chunks.append(merged)

        return final_chunks

    def split_documents(self, documents: List[Dict[str, Any]], document_id: str) -> List[Dict[str, Any]]:
        """Takes loaded document pages/sections and generates chunk dictionaries with rich metadata."""
        chunks = []
        chunk_index = 0

        for doc in documents:
            text = doc.get("text", "")
            if not text.strip():
                continue

            page_number = doc.get("page_number")
            section = doc.get("section")
            doc_name = doc.get("document_name", "Unknown document")

            text_chunks = self.split_text(text)
            for chunk_text in text_chunks:
                clean_chunk = chunk_text.strip()
                if not clean_chunk:
                    continue

                chunk_id = f"{document_id}_chunk_{chunk_index}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "document_name": doc_name,
                    "page_number": page_number,
                    "section": section,
                    "chunk_index": chunk_index,
                    "text": clean_chunk,
                })
                chunk_index += 1

        return chunks

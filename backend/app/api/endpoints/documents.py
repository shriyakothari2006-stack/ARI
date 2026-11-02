"""Document management endpoints: upload, listing, details, deletion, and re-indexing."""
import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.core.security import sanitize_filename, validate_file_upload
from app.database.session import get_db
from app.database.repository import DocumentRepository
from app.models.schemas import DocumentResponse
from app.rag.document_loader import DocumentLoader, DocumentLoadError
from app.rag.text_splitter import RecursiveTextSplitter
from app.rag.vector_store import vector_store

router = APIRouter(prefix="/documents", tags=["Documents"])
splitter = RecursiveTextSplitter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    knowledge_base_id: str = Form("default"),
    db: Session = Depends(get_db),
):
    """Uploads a document (PDF, DOCX, TXT, MD), parses text, chunks, embeds into ChromaDB, and records in SQLite."""
    original_filename = file.filename or "uploaded_document"
    clean_filename = sanitize_filename(original_filename)

    # Read file content into memory to check size
    file_bytes = await file.read()
    validate_file_upload(clean_filename, len(file_bytes))

    # Save to disk
    upload_dir = settings.absolute_upload_dir
    save_path = upload_dir / f"{knowledge_base_id}_{clean_filename}"

    # Handle duplicates by appending counter if needed
    counter = 1
    stem = Path(clean_filename).stem
    suffix = Path(clean_filename).suffix
    while save_path.exists():
        clean_filename = f"{stem}_{counter}{suffix}"
        save_path = upload_dir / f"{knowledge_base_id}_{clean_filename}"
        counter += 1

    with open(save_path, "wb") as f:
        f.write(file_bytes)

    logger.info("Saved file to disk: %s (%d bytes)", save_path, len(file_bytes))

    # Parse and extract text
    try:
        pages = DocumentLoader.load_file(save_path)
    except DocumentLoadError as dle:
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(dle))
    except Exception as e:
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while parsing the document: {str(e)}",
        )

    # Determine total pages/sections
    total_pages = max(1, len(pages))
    file_ext = Path(clean_filename).suffix.lower().lstrip(".")

    # Create document record in database
    doc_record = DocumentRepository.create(
        db=db,
        filename=clean_filename,
        file_type=file_ext,
        file_size=len(file_bytes),
        file_path=str(save_path),
        total_pages=total_pages,
        total_chunks=0,
        kb_id=knowledge_base_id,
    )

    # Split into chunks and index into ChromaDB
    try:
        chunks = splitter.split_documents(pages, document_id=doc_record.id)
        if not chunks:
            raise DocumentLoadError("Could not generate valid chunks from document text.")

        indexed_count = vector_store.index_chunks(knowledge_base_id, chunks)
        DocumentRepository.update_status(db, doc_record.id, status="indexed", total_chunks=indexed_count)
        doc_record.total_chunks = indexed_count
    except Exception as e:
        logger.error("Failed to index document chunks: %s", str(e))
        DocumentRepository.update_status(db, doc_record.id, status="failed", total_chunks=0, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embeddings and index chunks: {str(e)}",
        )

    return doc_record


@router.get("", response_model=List[DocumentResponse])
def list_documents(knowledge_base_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Lists all uploaded documents, optionally filtered by knowledge base."""
    docs = DocumentRepository.get_all(db, kb_id=knowledge_base_id)
    return docs


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """Retrieves metadata for a specific document."""
    doc = DocumentRepository.get_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return doc


@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Deletes a document from SQLite, removes vectors from ChromaDB, and deletes the local file."""
    doc = DocumentRepository.get_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    kb_id = doc.knowledge_base_id

    # 1. Remove vectors from ChromaDB
    deleted_chunks = vector_store.delete_document_chunks(kb_id=kb_id, document_id=document_id)

    # 2. Delete local file
    try:
        local_path = Path(doc.file_path)
        if local_path.exists():
            local_path.unlink()
    except Exception as e:
        logger.warning("Could not delete local file %s: %s", doc.file_path, str(e))

    # 3. Remove SQLite record
    DocumentRepository.delete(db, document_id)

    return {
        "success": True,
        "message": f"Document '{doc.filename}' and {deleted_chunks} associated chunks deleted successfully.",
    }


@router.post("/{document_id}/reindex", response_model=DocumentResponse)
def reindex_document(document_id: str, db: Session = Depends(get_db)):
    """Re-reads the local file, re-chunks, and re-embeds into ChromaDB."""
    doc = DocumentRepository.get_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    local_path = Path(doc.file_path)
    if not local_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Underlying document file not found on server disk.",
        )

    # Clear existing chunks from vector store
    vector_store.delete_document_chunks(kb_id=doc.knowledge_base_id, document_id=doc.id)

    # Parse and chunk again
    pages = DocumentLoader.load_file(local_path)
    chunks = splitter.split_documents(pages, document_id=doc.id)
    indexed_count = vector_store.index_chunks(doc.knowledge_base_id, chunks)

    updated_doc = DocumentRepository.update_status(
        db, doc.id, status="indexed", total_chunks=indexed_count, error=None
    )
    return updated_doc

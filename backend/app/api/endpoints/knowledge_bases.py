"""Knowledge base management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.repository import KnowledgeBaseRepository
from app.models.schemas import KnowledgeBaseCreate, KnowledgeBaseResponse
from app.rag.vector_store import vector_store

router = APIRouter(prefix="/knowledge-bases", tags=["Knowledge Bases"])


@router.post("", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_base(data: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    """Creates a new isolated Knowledge Base."""
    kb = KnowledgeBaseRepository.create(db, data)
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        created_at=kb.created_at,
        document_count=0,
        total_chunks=0,
    )


@router.get("", response_model=List[KnowledgeBaseResponse])
def list_knowledge_bases(db: Session = Depends(get_db)):
    """Lists all knowledge bases with document and vector chunk counts."""
    kbs = KnowledgeBaseRepository.get_all(db)
    result = []
    for kb in kbs:
        doc_count = len(kb.documents) if kb.documents else 0
        total_chunks = sum(d.total_chunks for d in kb.documents) if kb.documents else 0
        result.append(
            KnowledgeBaseResponse(
                id=kb.id,
                name=kb.name,
                description=kb.description,
                created_at=kb.created_at,
                document_count=doc_count,
                total_chunks=total_chunks,
            )
        )
    return result


@router.delete("/{kb_id}")
def delete_knowledge_base(kb_id: str, db: Session = Depends(get_db)):
    """Deletes a knowledge base and its vector collection."""
    if kb_id == "default":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The default knowledge base cannot be deleted.",
        )

    # Clean up ChromaDB collection
    vector_store.delete_collection(kb_id)

    deleted = KnowledgeBaseRepository.delete(db, kb_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found.")

    return {"success": True, "message": f"Knowledge base '{kb_id}' deleted."}

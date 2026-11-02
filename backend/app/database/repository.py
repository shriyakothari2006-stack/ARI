"""Database repository layer for managing Knowledge Bases, Documents, Conversations, and Messages."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.db_models import KnowledgeBaseModel, DocumentModel, ConversationModel, MessageModel
from app.models.schemas import KnowledgeBaseCreate, DocumentCitation


class KnowledgeBaseRepository:
    @staticmethod
    def get_all(db: Session) -> List[KnowledgeBaseModel]:
        return db.query(KnowledgeBaseModel).order_by(KnowledgeBaseModel.created_at).all()

    @staticmethod
    def get_by_id(db: Session, kb_id: str) -> Optional[KnowledgeBaseModel]:
        return db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first()

    @staticmethod
    def create(db: Session, data: KnowledgeBaseCreate) -> KnowledgeBaseModel:
        kb = KnowledgeBaseModel(name=data.name, description=data.description)
        db.add(kb)
        db.commit()
        db.refresh(kb)
        return kb

    @staticmethod
    def delete(db: Session, kb_id: str) -> bool:
        kb = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first()
        if not kb:
            return False
        db.delete(kb)
        db.commit()
        return True


class DocumentRepository:
    @staticmethod
    def get_all(db: Session, kb_id: Optional[str] = None) -> List[DocumentModel]:
        query = db.query(DocumentModel)
        if kb_id:
            query = query.filter(DocumentModel.knowledge_base_id == kb_id)
        return query.order_by(desc(DocumentModel.created_at)).all()

    @staticmethod
    def get_by_id(db: Session, doc_id: str) -> Optional[DocumentModel]:
        return db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()

    @staticmethod
    def create(
        db: Session,
        filename: str,
        file_type: str,
        file_size: int,
        file_path: str,
        total_pages: int = 1,
        total_chunks: int = 0,
        kb_id: str = "default",
    ) -> DocumentModel:
        doc = DocumentModel(
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path,
            total_pages=total_pages,
            total_chunks=total_chunks,
            knowledge_base_id=kb_id,
            status="indexed",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def update_status(db: Session, doc_id: str, status: str, total_chunks: int = 0, error: Optional[str] = None):
        doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        if doc:
            doc.status = status
            doc.total_chunks = total_chunks
            doc.error_message = error
            db.commit()
            db.refresh(doc)
        return doc

    @staticmethod
    def delete(db: Session, doc_id: str) -> Optional[DocumentModel]:
        doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        if not doc:
            return None
        db.delete(doc)
        db.commit()
        return doc


class ConversationRepository:
    @staticmethod
    def get_all(db: Session) -> List[ConversationModel]:
        return db.query(ConversationModel).order_by(desc(ConversationModel.updated_at)).all()

    @staticmethod
    def get_by_id(db: Session, conv_id: str) -> Optional[ConversationModel]:
        return db.query(ConversationModel).filter(ConversationModel.id == conv_id).first()

    @staticmethod
    def create(db: Session, title: str = "New Chat", kb_id: str = "default") -> ConversationModel:
        conv = ConversationModel(title=title, knowledge_base_id=kb_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv

    @staticmethod
    def update_title(db: Session, conv_id: str, new_title: str) -> Optional[ConversationModel]:
        conv = db.query(ConversationModel).filter(ConversationModel.id == conv_id).first()
        if conv:
            conv.title = new_title
            db.commit()
            db.refresh(conv)
        return conv

    @staticmethod
    def delete(db: Session, conv_id: str) -> bool:
        conv = db.query(ConversationModel).filter(ConversationModel.id == conv_id).first()
        if not conv:
            return False
        db.delete(conv)
        db.commit()
        return True


class MessageRepository:
    @staticmethod
    def get_by_conversation(db: Session, conv_id: str) -> List[MessageModel]:
        return db.query(MessageModel).filter(MessageModel.conversation_id == conv_id).order_by(MessageModel.created_at).all()

    @staticmethod
    def add_message(
        db: Session,
        conv_id: str,
        role: str,
        content: str,
        language: str = "en",
        citations: Optional[List[dict]] = None,
        model: Optional[str] = None,
    ) -> MessageModel:
        msg = MessageModel(
            conversation_id=conv_id,
            role=role,
            content=content,
            language=language,
            model=model,
        )
        msg.citations = citations or []
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

"""SQLAlchemy database models for conversations, messages, documents, and knowledge bases."""
from datetime import datetime, timezone
import json
import uuid
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class KnowledgeBaseModel(Base):
    __tablename__ = "knowledge_bases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

    documents: Mapped[List["DocumentModel"]] = relationship(
        "DocumentModel", back_populates="knowledge_base", cascade="all, delete-orphan"
    )
    conversations: Mapped[List["ConversationModel"]] = relationship(
        "ConversationModel", back_populates="knowledge_base"
    )


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    knowledge_base_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, default="default"
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    total_pages: Mapped[int] = mapped_column(Integer, default=1)
    total_chunks: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="indexed")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    knowledge_base: Mapped["KnowledgeBaseModel"] = relationship("KnowledgeBaseModel", back_populates="documents")


class ConversationModel(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(200), default="New Chat")
    knowledge_base_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("knowledge_bases.id", ondelete="SET NULL"), nullable=True, default="default"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    knowledge_base: Mapped[Optional["KnowledgeBaseModel"]] = relationship(
        "KnowledgeBaseModel", back_populates="conversations"
    )
    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel", back_populates="conversation", cascade="all, delete-orphan", order_by="MessageModel.created_at"
    )


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default="en")
    citations_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="[]")
    model: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

    conversation: Mapped["ConversationModel"] = relationship("ConversationModel", back_populates="messages")

    @property
    def citations(self) -> list:
        if not self.citations_json:
            return []
        try:
            return json.loads(self.citations_json)
        except Exception:
            return []

    @citations.setter
    def citations(self, value: list):
        self.citations_json = json.dumps(value or [])

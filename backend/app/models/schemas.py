
"""Pydantic schemas for API requests, responses, citations, and system status."""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


# ==========================================
# Health and Diagnostics Schemas
# ==========================================

class HealthStatus(BaseModel):
    status: str = Field(description="'healthy' or 'degraded'")
    version: str = "1.0.0"
    timestamp: datetime
    services: dict[str, Any]


class GeminiHealthResponse(BaseModel):
    configured: bool
    status: str
    model: str
    message: str
    latency_ms: Optional[float] = None
    endpoint_tested: str = "Gemini generate_content"


class EmbeddingsHealthResponse(BaseModel):
    model_name: str
    status: str
    embedding_dimension: Optional[int] = None
    message: str


class VectorDBHealthResponse(BaseModel):
    status: str
    storage_path: str
    total_collections: int
    total_vectors: int
    message: str


# ==========================================
# Document & Knowledge Base Schemas
# ==========================================

class DocumentCitation(BaseModel):
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    chunk_id: str
    snippet: str
    similarity_score: float


class DocumentResponse(BaseModel):
    id: str
    knowledge_base_id: str
    filename: str
    file_type: str
    file_size: int
    total_pages: int
    total_chunks: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    document_count: int = 0
    total_chunks: int = 0


# ==========================================
# Chat & Conversation Schemas
# ==========================================

class ChatMessageCreate(BaseModel):
    conversation_id: Optional[str] = None
    knowledge_base_id: Optional[str] = "default"
    message: str = Field(min_length=1, description="User question or message")
    stream: bool = False
    use_general_knowledge: bool = False


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    language: Optional[str] = "en"
    citations: List[DocumentCitation] = []
    model: Optional[str] = None
    created_at: datetime


class ConversationResponse(BaseModel):
    id: str
    title: str
    knowledge_base_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    messages: Optional[List[MessageResponse]] = None


class ConversationUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class ChatResponse(BaseModel):
    conversation_id: str
    message: MessageResponse
    detected_language: str
    retrieval_used: bool
    context_chunks_retrieved: int


# ==========================================
# Settings Schemas
# ==========================================

class SystemSettingsResponse(BaseModel):
    gemini_configured: bool
    gemini_model: str
    embedding_model: str
    similarity_threshold: float
    top_k_results: int
    chunk_size: int
    chunk_overlap: int
    max_upload_size_mb: int
    allowed_extensions: List[str]
    supported_languages: List[dict]

"""Chat endpoints: conversational turns, multi-turn context, conversation history, and citations."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.database.session import get_db
from app.database.repository import ConversationRepository, MessageRepository
from app.models.schemas import (
    ChatMessageCreate,
    ChatResponse,
    MessageResponse,
    ConversationResponse,
    ConversationUpdate,
    DocumentCitation,
)
from app.rag.pipeline import rag_pipeline

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def send_chat_message(data: ChatMessageCreate, db: Session = Depends(get_db)):
    """Receives a user question, processes it through the Multilingual RAG pipeline with Grok,

    persists conversation turns, and returns the grounded answer with citations.
    """
    user_text = data.message.strip()
    if not user_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty.")

    kb_id = data.knowledge_base_id or "default"

    # 1. Resolve or create conversation
    conv_id = data.conversation_id
    if not conv_id:
        # Generate initial title from first 6 words of message
        words = user_text.split()
        initial_title = " ".join(words[:6]) + ("..." if len(words) > 6 else "")
        conv = ConversationRepository.create(db, title=initial_title, kb_id=kb_id)
        conv_id = conv.id
    else:
        conv = ConversationRepository.get_by_id(db, conv_id)
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    # 2. Fetch existing conversation context (last turns)
    existing_messages = MessageRepository.get_by_conversation(db, conv_id)
    history_context = [
        {"role": m.role, "content": m.content}
        for m in existing_messages[-6:]
    ]

    # 3. Save User Message to Database
    user_msg_record = MessageRepository.add_message(
        db=db,
        conv_id=conv_id,
        role="user",
        content=user_text,
    )

    # 4. Execute Multilingual RAG Pipeline
    try:
        rag_result = rag_pipeline.execute_rag(
            query=user_text,
            kb_id=kb_id,
            conversation_history=history_context,
            use_general_knowledge=data.use_general_knowledge,
        )
    except Exception as e:
        logger.error("RAG Pipeline execution failed: %s", str(e))
        error_msg = str(e)
        # Still record the error message or return user-friendly explanation
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg,
        )

    answer_text = rag_result["answer"]
    detected_lang = rag_result["detected_language"]
    citations = rag_result["citations"]

    # 5. Save Assistant Message to Database
    citations_data = [c.model_dump() for c in citations]
    asst_msg_record = MessageRepository.add_message(
        db=db,
        conv_id=conv_id,
        role="assistant",
        content=answer_text,
        language=detected_lang,
        citations=citations_data,
        model=rag_result["model"],
    )

    return ChatResponse(
        conversation_id=conv_id,
        message=MessageResponse(
            id=asst_msg_record.id,
            conversation_id=conv_id,
            role="assistant",
            content=answer_text,
            language=detected_lang,
            citations=citations,
            model=rag_result["model"],
            created_at=asst_msg_record.created_at,
        ),
        detected_language=detected_lang,
        retrieval_used=rag_result["retrieval_used"],
        context_chunks_retrieved=rag_result["context_chunks_retrieved"],
    )


@router.get("/history", response_model=List[ConversationResponse])
def get_conversations_history(db: Session = Depends(get_db)):
    """Retrieves all conversation sessions with metadata."""
    convs = ConversationRepository.get_all(db)
    result = []
    for c in convs:
        result.append(
            ConversationResponse(
                id=c.id,
                title=c.title,
                knowledge_base_id=c.knowledge_base_id,
                created_at=c.created_at,
                updated_at=c.updated_at,
                message_count=len(c.messages) if c.messages else 0,
            )
        )
    return result


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation_details(conversation_id: str, db: Session = Depends(get_db)):
    """Retrieves a single conversation including all message history and citations."""
    conv = ConversationRepository.get_by_id(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    formatted_messages = []
    for m in conv.messages:
        citations_list = [DocumentCitation(**c) for c in m.citations] if m.citations else []
        formatted_messages.append(
            MessageResponse(
                id=m.id,
                conversation_id=m.conversation_id,
                role=m.role,
                content=m.content,
                language=m.language,
                citations=citations_list,
                model=m.model,
                created_at=m.created_at,
            )
        )

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        knowledge_base_id=conv.knowledge_base_id,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=len(formatted_messages),
        messages=formatted_messages,
    )


@router.patch("/{conversation_id}", response_model=ConversationResponse)
def rename_conversation(conversation_id: str, data: ConversationUpdate, db: Session = Depends(get_db)):
    """Renames an existing conversation."""
    conv = ConversationRepository.update_title(db, conversation_id, data.title.strip())
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        knowledge_base_id=conv.knowledge_base_id,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=len(conv.messages) if conv.messages else 0,
    )


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Deletes a conversation and all its messages."""
    deleted = ConversationRepository.delete(db, conversation_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return {"success": True, "message": "Conversation deleted."}

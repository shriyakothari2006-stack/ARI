"""Central API Router registering all resource endpoints under /api."""
from fastapi import APIRouter
from app.api.endpoints import health, documents, knowledge_bases, chat, settings

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(documents.router)
api_router.include_router(knowledge_bases.router)
api_router.include_router(chat.router)
api_router.include_router(settings.router)

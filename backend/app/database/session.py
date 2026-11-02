"""Database session management and initial schema migration."""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger
from app.models.db_models import Base, KnowledgeBaseModel

# Create SQLite database engine
db_path = settings.absolute_db_path
engine = create_engine(
    f"sqlite:///{db_path}",
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes database tables and creates default knowledge base if not exists."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        # Check if default knowledge base exists
        default_kb = session.query(KnowledgeBaseModel).filter_by(id="default").first()
        if not default_kb:
            default_kb = KnowledgeBaseModel(
                id="default",
                name="Default Knowledge Base",
                description="Primary multilingual knowledge base for ARI.",
            )
            session.add(default_kb)
            session.commit()
            logger.info("Initialized default knowledge base in SQLite.")


def get_db() -> Generator[Session, None, None]:
    """Dependency for providing a transactional SQLite database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

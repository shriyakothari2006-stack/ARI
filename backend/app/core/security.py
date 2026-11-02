"""Security utilities for input sanitization, file path validation, and prompt boundaries."""
import os
import re
from pathlib import Path
from fastapi import HTTPException, status
from app.core.config import settings

# Safe filename regex: alphanumeric, dash, underscore, dot
SAFE_FILENAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-. ]+$")


def sanitize_filename(filename: str) -> str:
    """Sanitizes an uploaded filename to prevent directory traversal or malformed paths."""
    # Strip any directory path components
    basename = os.path.basename(filename).strip()
    # Replace spaces with underscores
    clean = re.sub(r"[^\w\-. ]", "_", basename)
    if not clean or clean.startswith("."):
        clean = f"document_{clean.lstrip('.')}"
    return clean


def validate_file_upload(filename: str, file_size: int):
    """Validates an uploaded file for extension and size limits."""
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum permitted limit of {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )


def build_safe_rag_prompt(user_query: str, context_chunks: list[dict]) -> str:
    """Wraps retrieved chunks as untrusted data within strict delimiter tags to prevent prompt injection."""
    context_blocks = []
    for idx, chunk in enumerate(context_chunks, 1):
        doc_name = chunk.get("document_name", "Unknown document")
        page = chunk.get("page_number")
        page_str = f"Page {page}" if page else "Section reference"
        text = chunk.get("text", "").strip()

        # Sanitize internal delimiter tags
        safe_text = text.replace("<document>", "&lt;document&gt;").replace("</document>", "&lt;/document&gt;")
        context_blocks.append(
            f'<document index="{idx}" source="{doc_name}" location="{page_str}">\n{safe_text}\n</document>'
        )

    joined_context = "\n\n".join(context_blocks)
    return f"""<retrieved_context>
{joined_context}
</retrieved_context>

<user_question>
{user_query}
</user_question>"""

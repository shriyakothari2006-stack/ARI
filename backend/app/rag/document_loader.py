"""Document loaders for PDF, DOCX, TXT, and Markdown files with metadata extraction."""
from pathlib import Path
from typing import List, Dict, Any
import pymupdf as fitz  # PyMuPDF
import docx  # python-docx


class DocumentLoadError(Exception):
    """Custom exception raised when document extraction fails."""
    pass


class DocumentLoader:
    @staticmethod
    def load_file(file_path: Path) -> List[Dict[str, Any]]:
        """Loads a document and returns a list of page/section dicts.

        Each dict format:
        {
            "text": str,
            "page_number": int | None,
            "section": str | None,
            "document_name": str,
        }
        """
        if not file_path.exists():
            raise DocumentLoadError(f"File not found: {file_path}")

        file_size = file_path.stat().st_size
        if file_size == 0:
            raise DocumentLoadError("Uploaded file is empty (0 bytes).")

        ext = file_path.suffix.lower()
        doc_name = file_path.name

        if ext == ".pdf":
            return DocumentLoader._load_pdf(file_path, doc_name)
        elif ext == ".docx":
            return DocumentLoader._load_docx(file_path, doc_name)
        elif ext in [".txt", ".md"]:
            return DocumentLoader._load_text(file_path, doc_name)
        else:
            raise DocumentLoadError(f"Unsupported document format: {ext}")

    @staticmethod
    def _load_pdf(file_path: Path, doc_name: str) -> List[Dict[str, Any]]:
        pages = []
        try:
            doc = fitz.open(str(file_path))
            if doc.page_count == 0:
                raise DocumentLoadError("PDF contains 0 pages.")

            total_extracted_text = 0
            for page_idx in range(doc.page_count):
                page = doc.load_page(page_idx)
                text = page.get_text("text").strip()
                if text:
                    total_extracted_text += len(text)
                    pages.append({
                        "text": text,
                        "page_number": page_idx + 1,
                        "section": f"Page {page_idx + 1}",
                        "document_name": doc_name,
                    })
            doc.close()

            if total_extracted_text == 0:
                raise DocumentLoadError(
                    "The PDF contains no extractable text. It may consist purely of scanned images without OCR."
                )
            return pages
        except Exception as e:
            if isinstance(e, DocumentLoadError):
                raise e
            raise DocumentLoadError(f"Failed to parse PDF: {str(e)}") from e

    @staticmethod
    def _load_docx(file_path: Path, doc_name: str) -> List[Dict[str, Any]]:
        try:
            doc = docx.Document(str(file_path))
            sections = []
            current_section_title = "Introduction / Header"
            current_text_buffer = []

            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if not text:
                    continue

                # Check if paragraph is a heading
                if paragraph.style and paragraph.style.name.startswith("Heading"):
                    if current_text_buffer:
                        sections.append({
                            "text": "\n".join(current_text_buffer),
                            "page_number": None,
                            "section": current_section_title,
                            "document_name": doc_name,
                        })
                        current_text_buffer = []
                    current_section_title = text
                else:
                    current_text_buffer.append(text)

            # Flush remaining text
            if current_text_buffer:
                sections.append({
                    "text": "\n".join(current_text_buffer),
                    "page_number": None,
                    "section": current_section_title,
                    "document_name": doc_name,
                })

            # Also inspect tables in DOCX
            for t_idx, table in enumerate(doc.tables, 1):
                table_rows = []
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_data:
                        table_rows.append(" | ".join(row_data))
                if table_rows:
                    sections.append({
                        "text": "\n".join(table_rows),
                        "page_number": None,
                        "section": f"Table {t_idx}",
                        "document_name": doc_name,
                    })

            if not sections:
                raise DocumentLoadError("The DOCX document contains no extractable text.")
            return sections
        except Exception as e:
            if isinstance(e, DocumentLoadError):
                raise e
            raise DocumentLoadError(f"Failed to parse DOCX: {str(e)}") from e

    @staticmethod
    def _load_text(file_path: Path, doc_name: str) -> List[Dict[str, Any]]:
        try:
            # Handle UTF-8 with fallback to Latin-1
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = file_path.read_text(encoding="latin-1")

            clean = content.strip()
            if not clean:
                raise DocumentLoadError("Text file is empty.")

            return [{
                "text": clean,
                "page_number": 1,
                "section": "Main Document",
                "document_name": doc_name,
            }]
        except Exception as e:
            if isinstance(e, DocumentLoadError):
                raise e
            raise DocumentLoadError(f"Failed to read text file: {str(e)}") from e

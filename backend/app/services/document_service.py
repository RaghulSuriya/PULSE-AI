import os
import logging
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.source import DocumentItem
from app.services.ai_engine.extractor import action_extractor
from app.models.task import TaskItem

logger = logging.getLogger("pulse.document")

class DocumentService:
    """
    Document Understanding & Text Extraction.
    Supports PDF, DOCX, and Text file text parsing into structured tasks and deadlines.
    """

    async def parse_and_process_document(
        self,
        db: AsyncSession,
        user_id: str,
        filename: str,
        file_bytes: bytes,
        file_type: str
    ) -> Tuple[DocumentItem, int]:
        raw_text = ""
        
        if file_type == "pdf":
            try:
                import io
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(file_bytes))
                pages_text = [page.extract_text() for page in reader.pages if page.extract_text()]
                raw_text = "\n".join(pages_text)
            except Exception as e:
                logger.error(f"Error parsing PDF: {e}")
                raw_text = f"Document content for {filename}"
        elif file_type == "docx":
            try:
                import io
                import docx
                doc = docx.Document(io.BytesIO(file_bytes))
                raw_text = "\n".join([p.text for p in doc.paragraphs if p.text])
            except Exception as e:
                logger.error(f"Error parsing DOCX: {e}")
                raw_text = f"Document content for {filename}"
        else:
            raw_text = file_bytes.decode("utf-8", errors="ignore")

        # Run AI extraction
        extraction = await action_extractor.extract_action_plan(filename, raw_text)

        doc_item = DocumentItem(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            raw_text=raw_text[:2000], # Store preview snippet
            extracted_summary=f"Goal: {extraction.goal}. Requirements: {len(extraction.required_documents)}. Consequences: {extraction.consequences}",
            processed=True
        )
        db.add(doc_item)
        await db.flush()

        # Create tasks
        created_count = 0
        for subtask in extraction.tasks:
            task = TaskItem(
                user_id=user_id,
                source="DOCUMENT",
                source_reference=doc_item.id,
                title=subtask.title,
                description=subtask.description or f"Requirement from document: {filename}",
                category="COLLEGE" if "college" in raw_text.lower() or "internship" in raw_text.lower() else "GENERAL",
                priority=subtask.priority,
                status="PENDING",
                estimated_duration=subtask.estimated_minutes,
                confidence=extraction.confidence,
                consequence=extraction.consequences,
                explanation=f"Extracted from document '{filename}' with confidence {int(extraction.confidence * 100)}%"
            )
            db.add(task)
            created_count += 1

        await db.commit()
        await db.refresh(doc_item)
        return doc_item, created_count

document_service = DocumentService()

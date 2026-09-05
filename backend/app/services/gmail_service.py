import logging
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import OAuthAccount
from app.models.source import EmailMessage
from app.services.ai_engine.relevance import relevance_classifier
from app.services.ai_engine.extractor import action_extractor
from app.models.task import TaskItem
from app.utils import ensure_utc, now_utc, parse_iso_utc

logger = logging.getLogger("pulse.gmail")

class GmailService:
    """
    Real Gmail API integration & Ingestion Pipeline.
    Gmail -> Normalization -> Relevance Classifier -> Actionability Classifier -> Task Generation.
    Avoids duplicate processing by tracking message IDs.
    """

    async def fetch_and_ingest_live_messages(self, db: AsyncSession, user_id: str) -> List[EmailMessage]:
        """
        Queries live Gmail API for recent messages using authenticated user's OAuth access token.
        """
        from app.api.v1.auth import get_valid_google_token
        access_token = await get_valid_google_token(db, user_id)

        if not access_token:
            logger.info(f"No valid Google OAuth token for user {user_id}. Skipping live Gmail fetch.")
            return []

        headers = {"Authorization": f"Bearer {access_token}"}
        list_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=10"

        processed_emails = []
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(list_url, headers=headers)
                if res.status_code != 200:
                    logger.warning(f"Gmail API list messages failed: {res.status_code} {res.text}")
                    return []

                msg_list = res.json().get("messages", [])
                for msg_meta in msg_list:
                    msg_id = msg_meta["id"]
                    # Fetch message detail
                    detail_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=full"
                    detail_res = await client.get(detail_url, headers=headers)
                    if detail_res.status_code == 200:
                        msg_data = detail_res.json()
                        snippet = msg_data.get("snippet", "")
                        headers_list = msg_data.get("payload", {}).get("headers", [])
                        
                        subject = next((h["value"] for h in headers_list if h["name"].lower() == "subject"), "No Subject")
                        sender = next((h["value"] for h in headers_list if h["name"].lower() == "from"), "Unknown Sender")

                        email_item = await self.process_raw_email(
                            db, user_id, msg_id, sender, subject, snippet, snippet
                        )
                        processed_emails.append(email_item)

        except Exception as e:
            logger.error(f"Error fetching live Gmail messages: {e}")

        return processed_emails

    async def process_raw_email(
        self,
        db: AsyncSession,
        user_id: str,
        message_id: str,
        sender: str,
        subject: str,
        snippet: str,
        body_text: str,
        received_at: Optional[datetime] = None
    ) -> EmailMessage:
        # Check if already processed
        stmt = select(EmailMessage).where(EmailMessage.user_id == user_id, EmailMessage.message_id == message_id)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            return existing

        # Run AI relevance classification
        classification = await relevance_classifier.classify_communication(sender, subject, body_text or snippet)

        email_msg = EmailMessage(
            user_id=user_id,
            message_id=message_id,
            sender=sender,
            subject=subject,
            snippet=snippet,
            body_text=body_text,
            received_at=ensure_utc(received_at) or now_utc(),
            classification=classification.classification,
            confidence=classification.confidence,
            reasoning=classification.reasoning,
            processed=True
        )
        db.add(email_msg)
        await db.flush()

        # If ACTION_REQUIRED, generate task(s)
        if classification.classification == "ACTION_REQUIRED":
            extraction = await action_extractor.extract_action_plan(subject, body_text or snippet)
            
            for subtask in extraction.tasks:
                dl = parse_iso_utc(classification.detected_deadline) if classification.detected_deadline else None
                task = TaskItem(
                    user_id=user_id,
                    source="EMAIL",
                    source_reference=email_msg.id,
                    title=subtask.title,
                    description=subtask.description or f"Extracted from email: {subject}",
                    category="COLLEGE" if "college" in (subject + body_text).lower() or "placement" in (subject + body_text).lower() else "GENERAL",
                    priority=subtask.priority,
                    status="PENDING",
                    deadline=dl,
                    estimated_duration=subtask.estimated_minutes,
                    confidence=classification.confidence,
                    consequence=classification.consequence_summary,
                    explanation=f"Generated from email '{subject}' because: " + "; ".join(classification.reasoning)
                )
                db.add(task)

        await db.commit()
        await db.refresh(email_msg)
        return email_msg

gmail_service = GmailService()

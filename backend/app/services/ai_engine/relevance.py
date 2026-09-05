import re
from datetime import datetime, timedelta
from app.schemas.ai_extraction import EmailClassificationResult
from app.services.ai_engine.base import llm_provider

class RelevanceClassifier:
    """
    AI Relevance & Actionability Classifier.
    Evaluates raw emails and notifications into strict categories with evidence reasoning.
    """
    SYSTEM_PROMPT = (
        "You are PULSE AI's Relevance & Actionability Classifier.\n"
        "Analyze digital communications (emails, SMS, app alerts) and classify into exact categories:\n"
        "- ACTION_REQUIRED: Needs user action, contains deadlines, bills, exam timetables, job opportunities.\n"
        "- INFORMATION_ONLY: Official announcements or status updates with no required user task.\n"
        "- PROMOTIONAL: Sales, marketing, discounts, newsletters, general solicitations.\n"
        "- IRRELEVANT: Spam, automated system logs, noise.\n"
        "- UNCERTAIN: Ambiguous content requiring human review.\n\n"
        "Never convert newsletters or sales pitches into actionable tasks."
    )

    async def classify_communication(self, sender: str, title_or_subject: str, body_text: str) -> EmailClassificationResult:
        full_text = f"Sender: {sender}\nSubject: {title_or_subject}\nBody: {body_text}"

        def heuristic_fallback() -> EmailClassificationResult:
            text = (title_or_subject + " " + body_text + " " + sender).lower()
            reasons = []
            
            # Action required keywords
            action_keywords = [
                "deadline", "due date", "bill", "invoice", "payment", "recharge", "exam", 
                "internship", "placement", "assignment", "submit", "application", "urgent", 
                "action required", "renew", "electricity", "delivery tomorrow", "scheduled"
            ]
            
            promo_keywords = [
                "unsubscribe", "discount", "% off", "sale", "limited time offer", "buy now", 
                "newsletter", "promotional", "special deal", "cashback", "coupon"
            ]

            if any(k in text for k in promo_keywords) and not any(k in text for k in ["bill", "due"]):
                return EmailClassificationResult(
                    classification="PROMOTIONAL",
                    confidence=0.92,
                    reasoning=["Matched promotional offer signatures", "Contains marketing/discount terminology"],
                    is_actionable=False,
                    urgency="NONE"
                )

            matched_actions = [k for k in action_keywords if k in text]
            if matched_actions:
                # Detect approximate deadline
                detected_dl = None
                if "due" in text or "deadline" in text or "before" in text:
                    tomorrow = datetime.utcnow() + timedelta(days=2)
                    detected_dl = tomorrow.strftime("%Y-%m-%d 23:59:00")

                return EmailClassificationResult(
                    classification="ACTION_REQUIRED",
                    confidence=0.95,
                    reasoning=[
                        f"Contains actionable key indicators: {', '.join(matched_actions[:3])}",
                        "Requires explicit user completion or submission",
                        "Contains impending deadline or requirement"
                    ],
                    is_actionable=True,
                    urgency="HIGH" if any(k in text for k in ["urgent", "today", "tomorrow", "due"]) else "MEDIUM",
                    detected_deadline=detected_dl,
                    consequence_summary="Potential missed opportunity, late penalty, or incomplete duty if ignored.",
                    estimated_duration_minutes=30
                )

            if any(k in text for k in ["announcement", "fyi", "circular", "update", "meeting summary"]):
                return EmailClassificationResult(
                    classification="INFORMATION_ONLY",
                    confidence=0.88,
                    reasoning=["Informational update with no mandatory response required"],
                    is_actionable=False,
                    urgency="LOW"
                )

            return EmailClassificationResult(
                classification="IRRELEVANT",
                confidence=0.85,
                reasoning=["Routine communication without actionable task signals"],
                is_actionable=False,
                urgency="NONE"
            )

        return await llm_provider.generate_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=full_text,
            response_schema=EmailClassificationResult,
            fallback_factory=heuristic_fallback
        )

relevance_classifier = RelevanceClassifier()

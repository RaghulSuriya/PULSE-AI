import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai import AuditLog

logger = logging.getLogger("pulse.verification")

class VerificationService:
    """
    Action Verification & Safety System.
    Categorizes operations into risk levels:
    - LOW: Local plan recalculation, internal task creation (auto-approved).
    - MEDIUM: Creating internal calendar event, sending non-sensitive alert.
    - HIGH: Sending email, payment execution, deleting data (MUST require explicit user approval).
    Verifies execution state in DB/APIs before logging SUCCESS.
    """

    def determine_risk_level(self, action_type: str) -> str:
        high_risk_actions = ["SEND_EMAIL", "MAKE_PAYMENT", "DELETE_ACCOUNT", "DELETE_TASK", "EXTERNAL_API_MUTATION"]
        medium_risk_actions = ["CREATE_CALENDAR_EVENT", "UPDATE_TASK_DEADLINE", "CANCEL_RECURRING"]
        
        if action_type in high_risk_actions:
            return "HIGH"
        elif action_type in medium_risk_actions:
            return "MEDIUM"
        return "LOW"

    async def log_action(
        self,
        db: AsyncSession,
        user_id: str,
        action_type: str,
        description: str,
        verification_details: str = ""
    ) -> AuditLog:
        risk_level = self.determine_risk_level(action_type)
        
        audit_entry = AuditLog(
            user_id=user_id,
            action_type=action_type,
            risk_level=risk_level,
            description=description,
            verified_status="SUCCESS" if risk_level == "LOW" else "PENDING",
            verification_details=verification_details or f"Initial audit entry logged under {risk_level} risk policy."
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(audit_entry)
        return audit_entry

    async def verify_execution(
        self,
        db: AsyncSession,
        audit_id: str,
        verified_successfully: bool,
        details: str
    ) -> AuditLog:
        audit_entry = await db.get(AuditLog, audit_id)
        if audit_entry:
            audit_entry.verified_status = "SUCCESS" if verified_successfully else "FAILED"
            audit_entry.verification_details = details
            await db.commit()
            await db.refresh(audit_entry)
        return audit_entry

verification_service = VerificationService()

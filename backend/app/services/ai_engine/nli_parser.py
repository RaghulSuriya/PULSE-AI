import re
from datetime import timedelta
from app.schemas.ai_extraction import NaturalLanguageInputParsed
from app.services.ai_engine.base import llm_provider
from app.utils import now_utc

class NLIParser:
    """
    Natural Language Input Parser.
    Converts conversational commands into structured intents (CREATE_TASK, ADD_CALENDAR_EVENT, REPLAN_DAY).
    """
    SYSTEM_PROMPT = (
        "You are PULSE AI's Natural Language Input Parser.\n"
        "Parse free-form user statements into structured intents:\n"
        "- CREATE_TASK: Flexible todo request (e.g. 'Study AWS tomorrow for 2 hours')\n"
        "- ADD_CALENDAR_EVENT: Fixed commitment with specific start/end times (e.g. 'Meeting tomorrow 2 to 3 PM')\n"
        "- REPLAN_DAY: User reported delay or unable to complete task (e.g. 'I couldn't finish my assignment today')\n"
        "- MARK_COMPLETED: User completed a task manually."
    )

    async def parse_input(self, text: str) -> NaturalLanguageInputParsed:
        def heuristic_fallback() -> NaturalLanguageInputParsed:
            lower = text.lower()
            tomorrow = (now_utc() + timedelta(days=1)).strftime("%Y-%m-%d")

            # Check for unable to complete / replan triggers
            if any(k in lower for k in ["couldn't finish", "can't finish", "missed", "delay", "replan", "postpone", "running late"]):
                return NaturalLanguageInputParsed(
                    intent="REPLAN_DAY",
                    replan_reason=text,
                    confidence=0.95
                )

            # Check for fixed calendar meetings
            if "meeting" in lower or "appointment" in lower or re.search(r'\b(at|\d+ to \d+|\d+pm|\d+am)\b', lower):
                return NaturalLanguageInputParsed(
                    intent="ADD_CALENDAR_EVENT",
                    title=text,
                    duration_minutes=60,
                    target_date=tomorrow,
                    target_time="14:00",
                    is_fixed_commitment=True,
                    confidence=0.90
                )

            # Parse duration from prompt if present (e.g. "for 2 hours" -> 120 mins)
            duration = 45
            match = re.search(r'(\d+)\s*(hour|hr|h|minute|min|m)', lower)
            if match:
                val, unit = int(match.group(1)), match.group(2)
                duration = val * 60 if unit.startswith(('h', 'hour')) else val

            return NaturalLanguageInputParsed(
                intent="CREATE_TASK",
                title=text,
                duration_minutes=duration,
                priority="SHOULD_DO",
                target_date=tomorrow if "tomorrow" in lower else None,
                confidence=0.92
            )

        return await llm_provider.generate_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=text,
            response_schema=NaturalLanguageInputParsed,
            fallback_factory=heuristic_fallback
        )

nli_parser = NLIParser()

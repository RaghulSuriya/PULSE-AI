from datetime import datetime, timezone
from typing import Optional

MAX_UTC_DATETIME = datetime.max.replace(tzinfo=timezone.utc)

def now_utc() -> datetime:
    """Returns the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)

def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Ensures a datetime is timezone-aware and normalized to UTC.
    - If dt is None, returns None.
    - If dt is offset-naive (e.g. from legacy SQLite records or strptime without tz),
      assigns UTC timezone (dt.replace(tzinfo=timezone.utc)).
    - If dt is offset-aware, converts to UTC (dt.astimezone(timezone.utc)).
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def parse_iso_utc(date_str: str) -> Optional[datetime]:
    """Parses an ISO date/datetime string into a timezone-aware UTC datetime."""
    if not date_str or not date_str.strip():
        return None
    try:
        s = date_str.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        parsed = datetime.fromisoformat(s)
        return ensure_utc(parsed)
    except Exception:
        return None

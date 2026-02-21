from datetime import datetime, date
from fastapi import HTTPException, status

_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y")

def parse_date(date_str: str | None) -> date | None:
    """Parse a date string supporting YYYY-MM-DD, DD/MM/YYYY, DD/MM/YY."""
    if not date_str:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid date format: '{date_str}'. Use YYYY-MM-DD or DD/MM/YYYY.",
    )

def to_datetime(d: date | datetime | None) -> datetime | None:
    """Coerce a date to datetime (midnight UTC); pass-through for datetime."""
    if d is None:
        return None
    if isinstance(d, datetime):
        return d
    return datetime.combine(d, datetime.min.time())
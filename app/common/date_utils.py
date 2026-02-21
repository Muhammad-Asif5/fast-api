from datetime import datetime, date
from fastapi import HTTPException, status


def parse_date(date_str: str) -> date:
    """Parse string to date. Supports YYYY-MM-DD, DD/MM/YYYY, DD/MM/YY"""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid date format: {date_str}. Use YYYY-MM-DD or DD/MM/YYYY"
    )

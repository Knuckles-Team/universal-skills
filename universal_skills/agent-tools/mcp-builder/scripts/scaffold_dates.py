"""Resolve scaffold generation dates without inventing delivery evidence."""

import os
from datetime import UTC, date, datetime


def generation_date(value: str | None = None) -> date:
    """Prefer an explicit ISO date, then SOURCE_DATE_EPOCH, then today's UTC date."""
    if value is not None:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError("generation date must use YYYY-MM-DD")
        return parsed
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch is not None:
        if not epoch.isdecimal():
            raise ValueError("SOURCE_DATE_EPOCH must be a non-negative integer")
        try:
            return datetime.fromtimestamp(int(epoch), UTC).date()
        except (OverflowError, OSError, ValueError) as exc:
            raise ValueError(
                "SOURCE_DATE_EPOCH is outside the supported date range"
            ) from exc
    return datetime.now(UTC).date()

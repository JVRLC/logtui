from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """Normalized representation shared by every input and parser."""

    id: int | None = None
    timestamp: datetime | None = None
    level: str | None = None
    service: str | None = None
    message: str
    source: str
    fields: dict[str, Any] = Field(default_factory=dict)
    raw: str | None = None

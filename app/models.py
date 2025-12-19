from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    """Модель книги (DTO для передачи между слоями)."""

    id: Optional[int]
    title: str
    author: str
    path: str
    size_bytes: int
    format: str
    added_at: datetime
    note: str

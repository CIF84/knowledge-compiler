"""Conservative, deterministic plain-text normalization."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

from .models import SourceDocument


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("source text must be a string")
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def normalize_document(text: str, *, metadata: Mapping[str, Any] | None = None) -> SourceDocument:
    normalized = normalize_text(text)
    if not normalized:
        raise ValueError("source text is empty after normalization")
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return SourceDocument(id=f"text-{digest}", text=normalized, metadata=metadata or {})

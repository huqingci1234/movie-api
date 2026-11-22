"""Normalize resolution labels for metadata returned by authorized providers."""
from __future__ import annotations

import re
from typing import Any

_PATTERNS = (
    ("4K", re.compile(r"2160\s*p?|3840\s*[x×]\s*2160|\b4k\b|uhd", re.I)),
    ("1080P", re.compile(r"1080\s*p?", re.I)),
    ("720P", re.compile(r"720\s*p?", re.I)),
    ("SD", re.compile(r"480\s*p?|360\s*p?|\bsd\b", re.I)),
)
_ORDER = {"4K": 0, "1080P": 1, "720P": 2, "SD": 3, "未知": 4}


def detect_quality(item: dict[str, Any]) -> str:
    """Infer a display label from provider metadata; this does not verify actual pixels."""
    fields = ("resolution", "quality", "definition", "vod_remarks", "remark", "vod_name", "name")
    text = " ".join(str(item.get(field, "")) for field in fields)
    for label, pattern in _PATTERNS:
        if pattern.search(text):
            return label
    return "未知"


def sort_by_quality(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a new list with 4K-first ordering while preserving original item objects."""
    return sorted(items, key=lambda item: _ORDER[detect_quality(item)])

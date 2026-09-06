"""Privacy-aware JSON normalization for persistent audit arguments."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit, urlunsplit

REDACTED = "[REDACTED]"
_SENSITIVE_KEY_PATTERN = re.compile(
    r"(?:api[_-]?key|authorization|cookie|password|secret|token)",
    re.IGNORECASE,
)


def redact_value(value: Any, *, key: str | None = None) -> Any:
    """Return a JSON-safe value with credential-like fields redacted."""
    if key is not None and _SENSITIVE_KEY_PATTERN.search(key):
        return REDACTED
    if isinstance(value, Mapping):
        return {
            str(item_key): redact_value(item_value, key=str(item_key))
            for item_key, item_value in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [redact_value(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, str):
        return _sanitize_url(value)
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    if hasattr(value, "model_dump"):
        return redact_value(value.model_dump(mode="json", exclude_none=True))
    return repr(value)


def _sanitize_url(value: str) -> str:
    """Remove URL credentials, query parameters, and fragments."""
    try:
        parts = urlsplit(value)
        hostname = parts.hostname
        port = parts.port
    except ValueError:
        return value
    if parts.scheme not in {"http", "https"} or not hostname:
        return value
    host = hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    netloc = f"{host}:{port}" if port is not None else host
    return urlunsplit((parts.scheme, netloc, parts.path, "", ""))

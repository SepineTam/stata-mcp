"""Generate audit run IDs with directly recoverable UTC timestamps."""

from __future__ import annotations

import hashlib
import re
import time
from datetime import datetime, timezone
from uuid import uuid4

RUN_ID_PATTERN = re.compile(
    r"^(?P<timestamp>\d{8}T\d{12}Z)_(?P<digest>[0-9a-f]{16})$"
)


def generate_run_id(
    tool: str,
    source_reference: str,
    timestamp_ns: int | None = None,
) -> tuple[str, datetime, int]:
    """Return a unique run ID, its readable time, and source nanoseconds."""
    effective_timestamp_ns = time.time_ns() if timestamp_ns is None else timestamp_ns
    started_at = datetime.fromtimestamp(
        effective_timestamp_ns / 1_000_000_000,
        tz=timezone.utc,
    )
    readable_timestamp = started_at.strftime("%Y%m%dT%H%M%S%fZ")
    digest_input = (
        f"{effective_timestamp_ns}\0{tool}\0{source_reference}\0{uuid4().hex}".encode(
            "utf-8"
        )
    )
    digest = hashlib.sha256(digest_input).hexdigest()[:16]
    return (
        f"{readable_timestamp}_{digest}",
        started_at,
        effective_timestamp_ns,
    )


def parse_run_id_timestamp(run_id: str) -> datetime:
    """Recover the UTC invocation timestamp encoded in a run ID."""
    match = RUN_ID_PATTERN.fullmatch(run_id)
    if match is None:
        raise ValueError(f"Invalid audit run ID: {run_id}")
    parsed = datetime.strptime(
        match.group("timestamp"),
        "%Y%m%dT%H%M%S%fZ",
    )
    return parsed.replace(tzinfo=timezone.utc)

"""Data models shared by audit middleware and tool-specific artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AuditRun:
    """One auditable tool invocation."""

    run_id: str
    tool: str
    source_reference: str
    interface: str
    started_at: str
    started_at_ns: int


@dataclass
class AuditExecutionContext:
    """Mutable artifacts associated with one run across execution layers."""

    run: AuditRun
    store: Any
    artifacts: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DofileSnapshot:
    """An exact do-file snapshot linked to one run."""

    path: Path
    sha256: str
    size_bytes: int
    reused: bool

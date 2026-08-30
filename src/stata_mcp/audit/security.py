"""Cross-ledger security decisions linked to the active tool run."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

from .context import current_audit_context
from .redaction import redact_value

SecurityDecision = Literal["blocked", "warning"]


def record_security_event(
    *,
    decision: SecurityDecision,
    stage: str,
    risk_type: str,
    source_path: str | Path | None = None,
    source_sha256: str | None = None,
    findings: Sequence[Mapping[str, Any]] | None = None,
    executed: bool,
) -> str | None:
    """Write a security decision and link it to the current tool run."""
    context = current_audit_context()
    if context is None:
        return None

    sequence = len(context.security_event_ids) + 1
    security_event_id = f"sec_{context.run.run_id}_{sequence:02d}"
    safe_findings = [_safe_finding(item) for item in findings or ()]
    event: dict[str, Any] = {
        "schema_version": 1,
        "security_event_id": security_event_id,
        "run_id": context.run.run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
        "tool": context.run.tool,
        "decision": decision,
        "stage": stage,
        "risk_type": risk_type,
        "executed": executed,
        "findings": safe_findings,
    }
    if source_path is not None:
        event["source_path"] = redact_value(str(source_path))
    if source_sha256 is not None:
        event["source_sha256"] = source_sha256

    context.store.append_security_event(event)
    context.security_event_ids.append(security_event_id)
    if decision == "blocked":
        context.terminal_event = "blocked"
    return security_event_id


def _safe_finding(finding: Mapping[str, Any]) -> dict[str, Any]:
    """Retain identifiers and locations, never dangerous source content."""
    allowed_keys = ("line", "type", "rule_id")
    return {
        key: redact_value(finding[key])
        for key in allowed_keys
        if key in finding and finding[key] is not None
    }

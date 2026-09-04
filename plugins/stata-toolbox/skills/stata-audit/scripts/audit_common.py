"""Shared readers and correlation helpers for Stata-MCP audit evidence."""

from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SUPPORTED_SCHEMA_VERSION = 1
TERMINAL_EVENTS = {"completed", "failed", "timeout", "blocked", "interrupted"}


@dataclass(frozen=True)
class LoadedRecord:
    """One JSONL record with immutable source provenance."""

    file_path: Path
    relative_file: str
    line_number: int
    payload: dict[str, Any]

    def derived(self) -> dict[str, Any]:
        """Return a JSON-safe record including its source location."""
        return {
            "file": self.relative_file,
            "line": self.line_number,
            "record": self.payload,
        }


@dataclass(frozen=True)
class AuditIssue:
    """One limitation or integrity problem found while reading evidence."""

    severity: str
    code: str
    message: str
    file: str | None = None
    line: int | None = None
    run_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return the issue in a stable JSON representation."""
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "run_id": self.run_id,
        }


@dataclass
class AuditBundle:
    """All audit, snapshot, and optional debug records for one artifact root."""

    root: Path
    records: list[LoadedRecord]
    issues: list[AuditIssue]

    @property
    def tool_records(self) -> list[LoadedRecord]:
        """Return durable lifecycle records, excluding the security ledger."""
        return [
            record
            for record in self.records
            if record.relative_file.startswith("audit/")
            and record.relative_file != "audit/security.jsonl"
            and record.payload.get("event") in {"started", *TERMINAL_EVENTS}
        ]

    @property
    def security_records(self) -> list[LoadedRecord]:
        """Return records from the central security ledger."""
        return [
            record
            for record in self.records
            if record.relative_file == "audit/security.jsonl"
        ]

    @property
    def snapshot_records(self) -> list[LoadedRecord]:
        """Return snapshot metadata records."""
        return [
            record
            for record in self.records
            if record.relative_file == "snapshot/metadata.jsonl"
        ]

    @property
    def debug_records(self) -> list[LoadedRecord]:
        """Return rotating checkpoint and trace records."""
        return [
            record
            for record in self.records
            if record.relative_file.startswith("debug/")
        ]


def parse_timestamp(value: Any) -> datetime | None:
    """Parse an ISO 8601 audit timestamp and normalize it to UTC."""
    if not isinstance(value, str) or not value:
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def timestamp_sort_key(record: LoadedRecord) -> tuple[datetime, str, int]:
    """Sort records by UTC time while keeping deterministic provenance order."""
    timestamp = parse_timestamp(
        record.payload.get("timestamp") or record.payload.get("created_at")
    )
    return (
        timestamp or datetime.min.replace(tzinfo=UTC),
        record.relative_file,
        record.line_number,
    )


def load_audit_bundle(
    artifact_root: Path,
    *,
    include_debug: bool = True,
) -> AuditBundle:
    """Read audit evidence without modifying any source file."""
    root = artifact_root.expanduser().resolve()
    records: list[LoadedRecord] = []
    issues: list[AuditIssue] = []
    if not root.exists():
        issues.append(
            AuditIssue(
                "error",
                "artifact_root_missing",
                f"Artifact root does not exist: {root}",
            )
        )
        return AuditBundle(root=root, records=records, issues=issues)

    candidate_files = list((root / "audit").glob("*.jsonl"))
    snapshot_metadata = root / "snapshot" / "metadata.jsonl"
    if snapshot_metadata.is_file():
        candidate_files.append(snapshot_metadata)
    if include_debug:
        candidate_files.extend((root / "debug").glob("*.jsonl*"))

    safe_files: set[Path] = set()
    for candidate in candidate_files:
        if not candidate.is_file():
            continue
        resolved_candidate = candidate.resolve()
        try:
            resolved_candidate.relative_to(root)
        except ValueError:
            issues.append(
                AuditIssue(
                    "error",
                    "evidence_path_outside_root",
                    f"Evidence path resolves outside the artifact root: {candidate}",
                )
            )
            continue
        safe_files.add(resolved_candidate)
    unique_files = sorted(safe_files)
    if not any(path.parent.name == "audit" for path in unique_files):
        issues.append(
            AuditIssue(
                "error",
                "audit_ledgers_missing",
                f"No audit JSONL ledgers found under {root / 'audit'}",
            )
        )

    for file_path in unique_files:
        relative_file = file_path.relative_to(root).as_posix()
        try:
            stream = file_path.open("r", encoding="utf-8")
        except OSError as error:
            issues.append(
                AuditIssue(
                    "error",
                    "file_unreadable",
                    str(error),
                    file=relative_file,
                )
            )
            continue
        with stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as error:
                    issues.append(
                        AuditIssue(
                            "error",
                            "malformed_json",
                            error.msg,
                            file=relative_file,
                            line=line_number,
                        )
                    )
                    continue
                if not isinstance(payload, dict):
                    issues.append(
                        AuditIssue(
                            "error",
                            "record_not_object",
                            "A JSONL line must contain one JSON object.",
                            file=relative_file,
                            line=line_number,
                        )
                    )
                    continue
                schema_version = payload.get("schema_version")
                if schema_version != SUPPORTED_SCHEMA_VERSION:
                    issues.append(
                        AuditIssue(
                            "error",
                            "unsupported_schema",
                            f"Unsupported schema_version: {schema_version!r}",
                            file=relative_file,
                            line=line_number,
                            run_id=_text(payload.get("run_id")),
                        )
                    )
                records.append(
                    LoadedRecord(
                        file_path=file_path,
                        relative_file=relative_file,
                        line_number=line_number,
                        payload=payload,
                    )
                )

    records.sort(key=timestamp_sort_key)
    return AuditBundle(root=root, records=records, issues=issues)


def build_run_views(bundle: AuditBundle) -> tuple[list[dict[str, Any]], list[AuditIssue]]:
    """Pair lifecycle records and return one neutral view per run."""
    by_run: dict[str, list[LoadedRecord]] = defaultdict(list)
    issues: list[AuditIssue] = []
    for record in bundle.tool_records:
        run_id = _text(record.payload.get("run_id"))
        if not run_id:
            issues.append(
                AuditIssue(
                    "error",
                    "run_id_missing",
                    "Tool lifecycle record has no run_id.",
                    file=record.relative_file,
                    line=record.line_number,
                )
            )
            continue
        by_run[run_id].append(record)

    runs: list[dict[str, Any]] = []
    for run_id, records in by_run.items():
        records.sort(key=timestamp_sort_key)
        started = [record for record in records if record.payload.get("event") == "started"]
        terminal = [
            record
            for record in records
            if record.payload.get("event") in TERMINAL_EVENTS
        ]
        if len(started) != 1:
            issues.append(
                AuditIssue(
                    "error",
                    "started_event_count",
                    f"Run has {len(started)} started events; expected exactly one.",
                    run_id=run_id,
                )
            )
        if len(terminal) == 0:
            issues.append(
                AuditIssue(
                    "warning",
                    "terminal_event_missing",
                    "Run has no terminal event and requires investigation.",
                    run_id=run_id,
                )
            )
        elif len(terminal) > 1:
            issues.append(
                AuditIssue(
                    "error",
                    "terminal_event_count",
                    f"Run has {len(terminal)} terminal events; expected at most one.",
                    run_id=run_id,
                )
            )

        start_record = started[0] if started else records[0]
        terminal_record = terminal[-1] if terminal else None
        start_time = parse_timestamp(start_record.payload.get("timestamp"))
        end_time = (
            parse_timestamp(terminal_record.payload.get("timestamp"))
            if terminal_record
            else start_time
        )
        duration_ms = _number(
            terminal_record.payload.get("duration_ms") if terminal_record else None
        )
        if duration_ms is None and start_time is not None and end_time is not None:
            duration_ms = max(0.0, (end_time - start_time).total_seconds() * 1000)

        tool = _text(start_record.payload.get("tool")) or Path(
            start_record.relative_file
        ).stem
        runs.append(
            {
                "run_id": run_id,
                "tool": tool,
                "status": (
                    _text(terminal_record.payload.get("event"))
                    if terminal_record
                    else "incomplete"
                ),
                "started_at": start_time.isoformat() if start_time else None,
                "ended_at": end_time.isoformat() if end_time else None,
                "duration_ms": duration_ms,
                "executed": (
                    terminal_record.payload.get("executed")
                    if terminal_record
                    else None
                ),
                "source_reference": start_record.payload.get("source_reference"),
                "input": start_record.payload.get("input"),
                "client": start_record.payload.get("client"),
                "protocol_version": start_record.payload.get("protocol_version"),
                "request_id": start_record.payload.get("request_id"),
                "security_event_ids": (
                    terminal_record.payload.get("security_event_ids", [])
                    if terminal_record
                    else []
                ),
                "artifacts": (
                    terminal_record.payload.get("artifacts", {})
                    if terminal_record
                    else {}
                ),
                "error": (
                    terminal_record.payload.get("error")
                    if terminal_record
                    else None
                ),
                "provenance": [record.derived() for record in records],
            }
        )

    runs.sort(key=lambda run: (run.get("started_at") or "", run["run_id"]))
    return runs, issues


def summarize_runs(runs: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Compute factual usage metrics without assigning a subjective score."""
    run_list = list(runs)
    status_counts = Counter(str(run.get("status")) for run in run_list)
    tool_counts = Counter(str(run.get("tool")) for run in run_list)
    durations = [
        float(run["duration_ms"])
        for run in run_list
        if isinstance(run.get("duration_ms"), (int, float))
    ]
    timestamps = [
        timestamp
        for run in run_list
        for timestamp in (
            parse_timestamp(run.get("started_at")),
            parse_timestamp(run.get("ended_at")),
        )
        if timestamp is not None
    ]
    active_days = {
        timestamp.date().isoformat()
        for run in run_list
        if (timestamp := parse_timestamp(run.get("started_at"))) is not None
    }
    return {
        "total_runs": len(run_list),
        "status_counts": dict(sorted(status_counts.items())),
        "tool_counts": dict(sorted(tool_counts.items())),
        "active_days": len(active_days),
        "observed_start": min(timestamps).isoformat() if timestamps else None,
        "observed_end": max(timestamps).isoformat() if timestamps else None,
        "duration_ms": {
            "median": round(statistics.median(durations), 3) if durations else None,
            "maximum": round(max(durations), 3) if durations else None,
        },
    }


def mask_path(value: Any, project_root: Path) -> Any:
    """Keep useful relative paths while hiding unrelated absolute directories."""
    if not isinstance(value, str) or not value:
        return value
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        return value
    try:
        relative = candidate.resolve().relative_to(project_root.resolve())
    except (OSError, ValueError):
        return f"<external>/{candidate.name}"
    return f"<project>/{relative.as_posix()}"


def safe_json_for_html(value: Any) -> str:
    """Serialize inline JSON without allowing data to close a script element."""
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return (
        encoded.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def sha256_file(path: Path) -> str:
    """Hash one file without loading it entirely into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_snapshot_object(root: Path, snapshot: dict[str, Any]) -> Path | None:
    """Resolve a snapshot path, including relocated content-addressed bundles."""
    recorded = snapshot.get("snapshot_path")
    if isinstance(recorded, str) and recorded:
        recorded_path = Path(recorded).expanduser()
        if recorded_path.is_file():
            return recorded_path
    digest = snapshot.get("sha256")
    if isinstance(digest, str) and digest:
        fallback = root / "snapshot" / "objects" / f"{digest}.do"
        if fallback.is_file():
            return fallback
    return None


def write_json(value: Any) -> None:
    """Print UTF-8 JSON for humans and downstream tools."""
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None

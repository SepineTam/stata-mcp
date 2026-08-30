"""Append-only audit storage and immutable do-file snapshots."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping

from .models import AuditRun, DofileSnapshot
from .redaction import redact_value
from .run_id import generate_run_id

AuditTerminalEvent = Literal[
    "completed",
    "failed",
    "timeout",
    "blocked",
    "interrupted",
]

SCHEMA_VERSION = 1
_APPEND_LOCK = threading.Lock()
_SNAPSHOT_LOCK = threading.Lock()
_TOOL_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


class AuditStore:
    """Persist per-tool JSONL events and exact source snapshots."""

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.audit_path = self.base_path / "audit"
        self.snapshot_path = self.base_path / "snapshot"
        self.snapshot_objects_path = self.snapshot_path / "objects"

    def start_run(
        self,
        tool: str,
        source_reference: str,
        input_payload: Mapping[str, Any],
        interface: str = "runtime",
        client: Mapping[str, Any] | None = None,
        protocol_version: str | None = None,
        request_id: str | None = None,
        timestamp_ns: int | None = None,
    ) -> AuditRun:
        """Create a run and append its initial event before execution."""
        self._validate_tool_name(tool)
        normalized_source = str(source_reference)
        run_id, started_at, started_at_ns = generate_run_id(
            tool,
            normalized_source,
            timestamp_ns=timestamp_ns,
        )
        run = AuditRun(
            run_id=run_id,
            tool=tool,
            source_reference=normalized_source,
            interface=interface,
            started_at=started_at.isoformat(timespec="microseconds"),
            started_at_ns=started_at_ns,
        )
        event: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run.run_id,
            "event": "started",
            "tool": tool,
            "timestamp": run.started_at,
            "interface": interface,
            "source_reference": redact_value(normalized_source),
            "input": redact_value(dict(input_payload)),
        }
        if client is not None:
            event["client"] = redact_value(dict(client))
        if protocol_version is not None:
            event["protocol_version"] = protocol_version
        if request_id is not None:
            event["request_id"] = request_id
        self._append_tool_event(tool, event)
        return run

    def finish_run(
        self,
        run: AuditRun,
        event: AuditTerminalEvent,
        *,
        artifacts: Mapping[str, Any] | None = None,
        output: Mapping[str, Any] | None = None,
        error: Mapping[str, Any] | None = None,
        timestamp_ns: int | None = None,
    ) -> None:
        """Append the terminal event without modifying prior records."""
        if event not in {
            "completed",
            "failed",
            "timeout",
            "blocked",
            "interrupted",
        }:
            raise ValueError(f"Unsupported terminal audit event: {event}")
        finished_at_ns = time.time_ns() if timestamp_ns is None else timestamp_ns
        finished_at = datetime.fromtimestamp(
            finished_at_ns / 1_000_000_000,
            tz=timezone.utc,
        )
        event_payload: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run.run_id,
            "event": event,
            "tool": run.tool,
            "timestamp": finished_at.isoformat(timespec="microseconds"),
            "duration_ms": max(
                0,
                round((finished_at_ns - run.started_at_ns) / 1_000_000, 3),
            ),
        }
        if artifacts:
            event_payload["artifacts"] = redact_value(dict(artifacts))
        if output:
            event_payload["output"] = redact_value(dict(output))
        if error:
            event_payload["error"] = redact_value(dict(error))
        self._append_tool_event(run.tool, event_payload)

    def snapshot_dofile(self, run: AuditRun, dofile_path: Path) -> DofileSnapshot:
        """Store exact do-file bytes and append one metadata record."""
        resolved_path = Path(dofile_path).resolve()
        source_bytes = resolved_path.read_bytes()
        full_hash = hashlib.sha256(source_bytes).hexdigest()

        self._ensure_directories()
        target_path, reused = self._write_or_reuse_snapshot(
            self.snapshot_objects_path / f"{full_hash}.do",
            source_bytes,
            full_hash,
        )
        snapshot = DofileSnapshot(
            path=target_path,
            sha256=full_hash,
            size_bytes=len(source_bytes),
            reused=reused,
        )
        self._append_jsonl(
            self.snapshot_path / "metadata.jsonl",
            {
                "schema_version": SCHEMA_VERSION,
                "run_id": run.run_id,
                "tool": run.tool,
                "created_at": run.started_at,
                "original_path": resolved_path.as_posix(),
                "original_name": resolved_path.name,
                "snapshot_path": target_path.resolve().as_posix(),
                "sha256": full_hash,
                "sha256_prefix": full_hash[:8],
                "size_bytes": len(source_bytes),
                "reused": reused,
            },
        )
        return snapshot

    def _append_tool_event(self, tool: str, payload: Mapping[str, Any]) -> None:
        self._ensure_directories()
        self._append_jsonl(self.audit_path / f"{tool}.jsonl", payload)

    def _ensure_directories(self) -> None:
        self.base_path.mkdir(parents=True, exist_ok=True)
        gitignore = self.base_path / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n", encoding="utf-8")
        self.audit_path.mkdir(exist_ok=True)
        self.snapshot_path.mkdir(exist_ok=True)
        self.snapshot_objects_path.mkdir(exist_ok=True)

    @staticmethod
    def _append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
        encoded_line = (
            json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
        with _APPEND_LOCK:
            file_descriptor = os.open(
                path,
                os.O_APPEND | os.O_CREAT | os.O_WRONLY,
                0o600,
            )
            try:
                written_bytes = os.write(file_descriptor, encoded_line)
                if written_bytes != len(encoded_line):
                    raise OSError(
                        f"Incomplete audit write to {path}: "
                        f"{written_bytes}/{len(encoded_line)} bytes"
                    )
                os.fsync(file_descriptor)
            finally:
                os.close(file_descriptor)

    def _write_or_reuse_snapshot(
        self,
        target_path: Path,
        source_bytes: bytes,
        full_hash: str,
    ) -> tuple[Path, bool]:
        with _SNAPSHOT_LOCK:
            if target_path.exists():
                existing_hash = hashlib.sha256(target_path.read_bytes()).hexdigest()
                if existing_hash == full_hash:
                    return target_path, True
                raise RuntimeError(
                    f"Snapshot object hash mismatch for {target_path}"
                )

            temporary_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    dir=self.snapshot_path,
                    prefix=".snapshot-",
                    suffix=".tmp",
                    delete=False,
                ) as temporary_file:
                    temporary_path = Path(temporary_file.name)
                    temporary_file.write(source_bytes)
                    temporary_file.flush()
                    os.fsync(temporary_file.fileno())
                os.replace(temporary_path, target_path)
            finally:
                if temporary_path is not None:
                    temporary_path.unlink(missing_ok=True)
        return target_path, False

    @staticmethod
    def _validate_tool_name(tool: str) -> None:
        if _TOOL_NAME_PATTERN.fullmatch(tool) is None:
            raise ValueError(f"Invalid audit tool name: {tool}")

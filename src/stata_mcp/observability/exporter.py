"""Local privacy-safe OpenTelemetry span export."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Sequence

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from .checkpoints import CheckpointWriter


class LocalJsonlSpanExporter(SpanExporter):
    """Export completed spans to a rotating local JSONL file."""

    def __init__(
        self,
        artifact_root: str | Path,
        *,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 3,
    ) -> None:
        self.writer = CheckpointWriter(
            artifact_root,
            filename="traces.jsonl",
            max_bytes=max_bytes,
            backup_count=backup_count,
        )

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Write completed spans without propagating storage failures."""
        succeeded = True
        for span in spans:
            succeeded = self.writer.append(_serialize_span(span)) and succeeded
        return SpanExportResult.SUCCESS if succeeded else SpanExportResult.FAILURE

    def shutdown(self) -> None:
        """Release exporter resources."""

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        """Report success because every span is written synchronously."""
        return True


def _serialize_span(span: ReadableSpan) -> dict[str, Any]:
    context = span.context
    parent_span_id = None
    if span.parent is not None and span.parent.is_valid:
        parent_span_id = f"{span.parent.span_id:016x}"

    start_time = span.start_time or 0
    end_time = span.end_time or start_time
    payload: dict[str, Any] = {
        "schema_version": 1,
        "name": span.name,
        "process_id": os.getpid(),
        "trace_id": f"{context.trace_id:032x}",
        "span_id": f"{context.span_id:016x}",
        "parent_span_id": parent_span_id,
        "kind": span.kind.name,
        "status": span.status.status_code.name,
        "start_time_unix_nano": start_time,
        "end_time_unix_nano": end_time,
        "duration_ms": round((end_time - start_time) / 1_000_000, 3),
        "attributes": dict(span.attributes or {}),
    }
    return payload

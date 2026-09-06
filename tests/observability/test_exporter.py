"""Tests for the local OpenTelemetry span exporter."""

from __future__ import annotations

import json
import os
from pathlib import Path

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult

from stata_mcp.observability.exporter import LocalJsonlSpanExporter


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_local_span_exporter_writes_trace_ids_and_redacts_credentials(
    tmp_path: Path,
) -> None:
    exporter = LocalJsonlSpanExporter(tmp_path)
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span(
        "get_data_info.dataframe_read",
        attributes={
            "statamcp.run_id": "run-1",
            "statamcp.api_key": "secret-value",
            "statamcp.suffix": "dta",
        },
    ):
        pass

    events = _read_jsonl(tmp_path / "debug" / "traces.jsonl")
    assert len(events) == 1
    assert events[0]["name"] == "get_data_info.dataframe_read"
    assert len(events[0]["trace_id"]) == 32
    assert len(events[0]["span_id"]) == 16
    assert events[0]["process_id"] == os.getpid()
    assert events[0]["attributes"]["statamcp.run_id"] == "run-1"
    assert events[0]["attributes"]["statamcp.api_key"] == "[REDACTED]"
    assert events[0]["attributes"]["statamcp.suffix"] == "dta"
    assert events[0]["duration_ms"] >= 0


def test_local_span_exporter_reports_failure_without_raising(tmp_path: Path) -> None:
    exporter = LocalJsonlSpanExporter(tmp_path)
    provider = TracerProvider()
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span("safe") as span:
        pass

    exporter.writer.append = lambda payload: False

    assert exporter.export((span,)) == SpanExportResult.FAILURE

"""Reusable diagnostic steps backed by checkpoints and OpenTelemetry spans."""

from __future__ import annotations

import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..audit.context import current_audit_context
from ..audit.redaction import redact_value
from .checkpoints import current_checkpoint_writer

_tracer = trace.get_tracer("stata_mcp.observability")


@contextmanager
def debug_step(
    step: str,
    *,
    tool: str | None = None,
    request_id: str | None = None,
    attributes: Mapping[str, Any] | None = None,
) -> Iterator[None]:
    """Record one non-blocking execution step without changing its behavior."""
    started_ns = time.perf_counter_ns()
    safe_attributes = redact_value(dict(attributes or {}))
    audit_context = current_audit_context()
    run_id = audit_context.run.run_id if audit_context is not None else None

    span_attributes = _span_attributes(tool, request_id, run_id, safe_attributes)
    with _tracer.start_as_current_span(
        step,
        attributes=span_attributes,
        record_exception=False,
        set_status_on_exception=False,
    ) as span:
        common = _common_payload(
            step=step,
            tool=tool,
            request_id=request_id,
            run_id=run_id,
            attributes=safe_attributes,
            span=span,
        )
        _emit({**common, "event": "started"})
        try:
            yield
        except BaseException as error:
            span.set_attribute("error.type", type(error).__qualname__)
            span.set_status(Status(StatusCode.ERROR))
            _emit(
                {
                    **common,
                    "event": "failed",
                    "duration_ms": _elapsed_ms(started_ns),
                    "error_type": type(error).__qualname__,
                }
            )
            raise
        else:
            _emit(
                {
                    **common,
                    "event": "completed",
                    "duration_ms": _elapsed_ms(started_ns),
                }
            )


def _common_payload(
    *,
    step: str,
    tool: str | None,
    request_id: str | None,
    run_id: str | None,
    attributes: Any,
    span: trace.Span,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": step,
    }
    if tool is not None:
        payload["tool"] = tool
    if request_id is not None:
        payload["request_id"] = request_id
    if run_id is not None:
        payload["run_id"] = run_id
    if attributes:
        payload["attributes"] = attributes

    span_context = span.get_span_context()
    if span_context.is_valid:
        payload["trace_id"] = f"{span_context.trace_id:032x}"
        payload["span_id"] = f"{span_context.span_id:016x}"
    return payload


def _span_attributes(
    tool: str | None,
    request_id: str | None,
    run_id: str | None,
    attributes: Any,
) -> dict[str, str | bool | int | float]:
    result: dict[str, str | bool | int | float] = {}
    if tool is not None:
        result["statamcp.tool.name"] = tool
    if request_id is not None:
        result["statamcp.request.id"] = request_id
    if run_id is not None:
        result["statamcp.run_id"] = run_id
    if isinstance(attributes, Mapping):
        for key, value in attributes.items():
            if isinstance(value, str | bool | int | float):
                result[f"statamcp.{key}"] = value
    return result


def _emit(payload: Mapping[str, Any]) -> None:
    writer = current_checkpoint_writer()
    if writer is None:
        return
    try:
        writer.append(payload)
    except Exception:
        return


def _elapsed_ms(started_ns: int) -> float:
    return round((time.perf_counter_ns() - started_ns) / 1_000_000, 3)

"""Tests for MCP tools/call audit middleware."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import anyio
import pytest
from opentelemetry.sdk.trace import TracerProvider

from stata_mcp.audit import (
    AuditExecutionContext,
    AuditMiddleware,
    AuditStore,
    bind_audit_context,
    current_audit_context,
)


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _context(
    *,
    method: str = "tools/call",
    tool: str = "help",
    arguments: dict | None = None,
    protocol_version: str = "2026-07-28",
    client_name: str = "codex",
):
    client_info = SimpleNamespace(
        model_dump=lambda **kwargs: {"name": client_name, "version": "1.2.3"}
    )
    client_params = SimpleNamespace(client_info=client_info)
    session = SimpleNamespace(client_params=client_params)
    return SimpleNamespace(
        method=method,
        params={"name": tool, "arguments": arguments or {}},
        request_id="request-1",
        protocol_version=protocol_version,
        session=session,
    )


def test_middleware_records_completed_tool_call_and_exposes_run_context(
    tmp_path: Path,
) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    middleware = AuditMiddleware(store)
    observed_run_id = None

    async def call_next(ctx):
        nonlocal observed_run_id
        observed = current_audit_context()
        assert observed is not None
        observed_run_id = observed.run.run_id
        observed.artifacts["result_sha256"] = "abc"
        return {"ok": True}

    async def run_case():
        return await middleware(
            _context(arguments={"cmd": "regress"}),
            call_next,
        )

    result = anyio.run(run_case)

    assert result == {"ok": True}
    events = _read_jsonl(tmp_path / ".statamcp" / "audit" / "help.jsonl")
    assert [event["event"] for event in events] == ["started", "completed"]
    assert {event["run_id"] for event in events} == {observed_run_id}
    assert events[0]["client"]["name"] == "codex"
    assert events[1]["artifacts"] == {"result_sha256": "abc"}
    assert current_audit_context() is None


def test_middleware_records_failure_and_reraises(tmp_path: Path) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    middleware = AuditMiddleware(store)

    async def call_next(ctx):
        raise RuntimeError("tool failed")

    async def run_case():
        return await middleware(_context(tool="stata_do"), call_next)

    with pytest.raises(RuntimeError, match="tool failed"):
        anyio.run(run_case)

    events = _read_jsonl(tmp_path / ".statamcp" / "audit" / "stata_do.jsonl")
    assert [event["event"] for event in events] == ["started", "failed"]
    assert events[1]["error"]["type"] == "RuntimeError"
    assert current_audit_context() is None


def test_middleware_ignores_non_tool_messages(tmp_path: Path) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    middleware = AuditMiddleware(store)

    async def call_next(ctx):
        return {"tools": []}

    async def run_case():
        return await middleware(_context(method="tools/list"), call_next)

    result = anyio.run(run_case)

    assert result == {"tools": []}
    assert not (tmp_path / ".statamcp").exists()


def test_middleware_marks_error_results_as_failed(tmp_path: Path) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    middleware = AuditMiddleware(store)

    async def call_next(ctx):
        return SimpleNamespace(is_error=True)

    async def run_case():
        return await middleware(_context(tool="get_data_info"), call_next)

    anyio.run(run_case)

    events = _read_jsonl(
        tmp_path / ".statamcp" / "audit" / "get_data_info.jsonl"
    )
    assert [event["event"] for event in events] == ["started", "failed"]
    assert events[1]["output"] == {"is_error": True}


def test_middleware_isolates_concurrent_run_contexts(tmp_path: Path) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    middleware = AuditMiddleware(store)
    observed_run_ids: list[str] = []

    async def call_one(command: str) -> None:
        async def call_next(ctx):
            observed = current_audit_context()
            assert observed is not None
            observed_run_ids.append(observed.run.run_id)
            await anyio.sleep(0)
            assert current_audit_context() is observed
            return {"ok": True}

        await middleware(_context(arguments={"cmd": command}), call_next)

    async def run_case() -> None:
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(call_one, "regress")
            task_group.start_soon(call_one, "summarize")

    anyio.run(run_case)

    assert len(set(observed_run_ids)) == 2
    assert current_audit_context() is None


def test_audit_context_propagates_to_sync_tool_worker(tmp_path: Path) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    run = store.start_run("stata_do", "/project/test.do", {})
    execution_context = AuditExecutionContext(run=run, store=store)

    async def run_case():
        with bind_audit_context(execution_context):
            return await anyio.to_thread.run_sync(current_audit_context)

    observed = anyio.run(run_case)

    assert observed is execution_context
    assert current_audit_context() is None


def test_middleware_adds_run_id_to_current_otel_span(tmp_path: Path) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    middleware = AuditMiddleware(store)
    provider = TracerProvider()
    tracer = provider.get_tracer("test")

    async def call_next(ctx):
        return {"isError": False}

    async def run_case():
        with tracer.start_as_current_span("tools/call get_data_info") as span:
            await middleware(_context(tool="get_data_info"), call_next)
            return span

    span = anyio.run(run_case)
    events = _read_jsonl(
        tmp_path / ".statamcp" / "audit" / "get_data_info.jsonl"
    )

    assert span.attributes["statamcp.run_id"] == events[0]["run_id"]


def test_middleware_starts_and_cancels_watchdog_for_target_tools(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    state = {"started": 0, "cancelled": 0, "tool": None, "run_id": None}

    class FakeWatchdog:
        def __init__(self, *, tool, run_id, delays=(30.0, 120.0)):
            state["tool"] = tool
            state["run_id"] = run_id

        def start(self):
            state["started"] += 1

        def cancel(self):
            state["cancelled"] += 1

    monkeypatch.setattr(
        "stata_mcp.audit.middleware.SlowCallWatchdog",
        FakeWatchdog,
    )
    middleware = AuditMiddleware(AuditStore(tmp_path / ".statamcp"))

    async def call_next(ctx):
        return {"isError": False}

    anyio.run(middleware, _context(tool="get_data_info"), call_next)

    assert state["started"] == 1
    assert state["cancelled"] == 1
    assert state["tool"] == "get_data_info"
    assert state["run_id"]

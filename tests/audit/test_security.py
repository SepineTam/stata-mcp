"""Tests for cross-ledger security audit linkage."""

from __future__ import annotations

import json
from pathlib import Path

import anyio

from stata_mcp.audit import (
    AuditExecutionContext,
    AuditMiddleware,
    AuditStore,
    bind_audit_context,
    record_security_event,
)


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_security_event_links_to_tool_run_without_command_content(tmp_path: Path) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    run = store.start_run("stata_do", "/project/bad.do", {})
    context = AuditExecutionContext(run=run, store=store)

    with bind_audit_context(context):
        security_event_id = record_security_event(
            decision="blocked",
            stage="guard",
            risk_type="shell_command",
            source_path="/project/bad.do",
            source_sha256="abc123",
            findings=[{"line": 3, "type": "shell", "content": "shell rm -rf x"}],
            executed=False,
        )

    assert security_event_id is not None
    assert context.terminal_event == "blocked"
    assert context.security_event_ids == [security_event_id]
    event = _read_jsonl(tmp_path / ".statamcp" / "audit" / "security.jsonl")[0]
    assert event["security_event_id"] == security_event_id
    assert event["run_id"] == run.run_id
    assert event["decision"] == "blocked"
    assert event["executed"] is False
    assert event["findings"] == [{"line": 3, "type": "shell"}]
    assert "shell rm -rf x" not in json.dumps(event)


def test_middleware_terminal_event_references_security_event(tmp_path: Path) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    middleware = AuditMiddleware(store)
    fake_context = type(
        "FakeContext",
        (),
        {
            "method": "tools/call",
            "params": {
                "name": "stata_do",
                "arguments": {"dofile_path": "/project/bad.do"},
            },
            "request_id": "request-1",
            "protocol_version": "2026-07-28",
            "session": type("Session", (), {"client_params": None})(),
        },
    )()

    async def call_next(context):
        record_security_event(
            decision="blocked",
            stage="guard",
            risk_type="dangerous_command",
            source_path="/project/bad.do",
            findings=[{"line": 1, "type": "shell"}],
            executed=False,
        )
        return {"action": "Security check, dofile not executed"}

    async def run_case():
        return await middleware(fake_context, call_next)

    result = anyio.run(run_case)

    assert result["action"] == "Security check, dofile not executed"
    tool_events = _read_jsonl(
        tmp_path / ".statamcp" / "audit" / "stata_do.jsonl"
    )
    security_event = _read_jsonl(
        tmp_path / ".statamcp" / "audit" / "security.jsonl"
    )[0]
    assert [event["event"] for event in tool_events] == ["started", "blocked"]
    assert tool_events[1]["executed"] is False
    assert tool_events[1]["security_event_ids"] == [
        security_event["security_event_id"]
    ]
    assert tool_events[1]["run_id"] == security_event["run_id"]

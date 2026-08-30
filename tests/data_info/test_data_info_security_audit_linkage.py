"""Tests for get_data_info cross-ledger security linkage."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import anyio

from stata_mcp.api.get_data_info import get_data_info
from stata_mcp.audit import AuditMiddleware, AuditStore


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_blocked_local_data_path_links_tool_and_security_ledgers(
    tmp_path: Path,
) -> None:
    working_dir = tmp_path / "work"
    outside_dir = tmp_path / "outside"
    working_dir.mkdir()
    outside_dir.mkdir()
    data_path = outside_dir / "private.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "\n".join(
            [
                "[PROJECT]",
                f'WORKING_DIR = "{working_dir.as_posix()}"',
                "",
                "[SECURITY]",
                "strict_data_info_local_boundary = true",
            ]
        ),
        encoding="utf-8",
    )
    store = AuditStore(working_dir / ".statamcp")
    middleware = AuditMiddleware(store)
    request_context = SimpleNamespace(
        method="tools/call",
        params={
            "name": "get_data_info",
            "arguments": {"data_path": data_path.as_posix()},
        },
        request_id="request-1",
        protocol_version="2026-07-28",
        session=SimpleNamespace(client_params=None),
    )

    async def call_next(context):
        return get_data_info(
            data_path=data_path.as_posix(),
            config_file=config_path,
            tool_context="mcp",
        )

    async def run_case():
        return await middleware(request_context, call_next)

    result = anyio.run(run_case)

    assert result == "Access denied: data file must be within the working directory."
    tool_events = _read_jsonl(
        working_dir / ".statamcp" / "audit" / "get_data_info.jsonl"
    )
    security_event = _read_jsonl(
        working_dir / ".statamcp" / "audit" / "security.jsonl"
    )[0]
    assert [event["event"] for event in tool_events] == ["started", "blocked"]
    assert tool_events[1]["executed"] is False
    assert tool_events[1]["security_event_ids"] == [
        security_event["security_event_id"]
    ]
    assert security_event["tool"] == "get_data_info"
    assert security_event["stage"] == "data_path_guard"
    assert security_event["risk_type"] == "local_path_outside_boundary"


def test_blocked_data_url_is_sanitized_in_security_ledger(tmp_path: Path) -> None:
    working_dir = tmp_path / "work"
    working_dir.mkdir()
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "\n".join(
            [
                "[PROJECT]",
                f'WORKING_DIR = "{working_dir.as_posix()}"',
                "",
                "[BETA]",
                "enable_data_info_url_guard = true",
                'data_info_allowed_url_domains = ["example.com"]',
            ]
        ),
        encoding="utf-8",
    )
    source = "https://evil.com/private.csv?token=secret#fragment"
    store = AuditStore(working_dir / ".statamcp")
    middleware = AuditMiddleware(store)
    request_context = SimpleNamespace(
        method="tools/call",
        params={"name": "get_data_info", "arguments": {"data_path": source}},
        request_id="request-2",
        protocol_version="2026-07-28",
        session=SimpleNamespace(client_params=None),
    )

    async def call_next(context):
        return get_data_info(
            data_path=source,
            config_file=config_path,
            tool_context="mcp",
        )

    async def run_case():
        return await middleware(request_context, call_next)

    anyio.run(run_case)

    security_path = working_dir / ".statamcp" / "audit" / "security.jsonl"
    security_text = security_path.read_text(encoding="utf-8")
    security_event = json.loads(security_text.splitlines()[0])
    assert security_event["risk_type"] == "url_domain_not_allowed"
    assert security_event["source_path"] == "https://evil.com/private.csv"
    assert "token=secret" not in security_text
    assert "fragment" not in security_text

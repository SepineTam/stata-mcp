"""Tests for append-only audit storage and run identifiers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from stata_mcp.audit import AuditStore, parse_run_id_timestamp


FIXED_TIMESTAMP_NS = 1_788_012_625_123_456_789


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_run_id_contains_recoverable_time_and_remains_unique(tmp_path: Path) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    kwargs = {
        "tool": "stata_do",
        "source_reference": "/project/analysis.do",
        "input_payload": {"dofile_path": "/project/analysis.do"},
        "timestamp_ns": FIXED_TIMESTAMP_NS,
    }

    first_run = store.start_run(**kwargs)
    second_run = store.start_run(**kwargs)
    expected = datetime.fromtimestamp(
        FIXED_TIMESTAMP_NS / 1_000_000_000,
        tz=timezone.utc,
    )

    assert first_run.run_id != second_run.run_id
    assert parse_run_id_timestamp(first_run.run_id) == expected
    assert first_run.run_id.startswith(expected.strftime("%Y%m%dT%H%M%S%fZ_"))


def test_store_writes_client_aware_lifecycle_and_redacts_secrets(tmp_path: Path) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    run = store.start_run(
        tool="get_data_info",
        source_reference="/project/private.dta",
        input_payload={
            "data_path": "/project/private.dta",
            "api_key": "secret-value",
            "nested": {"password": "hidden", "head": 5},
        },
        interface="mcp",
        client={"name": "codex", "version": "1.0"},
        protocol_version="2026-07-28",
        request_id="request-7",
        timestamp_ns=FIXED_TIMESTAMP_NS,
    )
    store.finish_run(
        run,
        event="completed",
        artifacts={"result_sha256": "abc"},
        timestamp_ns=FIXED_TIMESTAMP_NS + 1_000_000,
    )

    events = _read_jsonl(
        tmp_path / ".statamcp" / "audit" / "get_data_info.jsonl"
    )

    assert [event["event"] for event in events] == ["started", "completed"]
    assert events[0]["client"] == {"name": "codex", "version": "1.0"}
    assert events[0]["protocol_version"] == "2026-07-28"
    assert events[0]["request_id"] == "request-7"
    assert events[0]["input"]["api_key"] == "[REDACTED]"
    assert events[0]["input"]["nested"] == {
        "password": "[REDACTED]",
        "head": 5,
    }
    assert events[1]["duration_ms"] == 1.0


def test_store_removes_url_credentials_query_and_fragment(tmp_path: Path) -> None:
    store = AuditStore(tmp_path / ".statamcp")
    source = "https://user:pass@example.com/data.dta?token=secret#section"

    store.start_run(
        tool="get_data_info",
        source_reference=source,
        input_payload={"data_path": source},
    )

    event = _read_jsonl(
        tmp_path / ".statamcp" / "audit" / "get_data_info.jsonl"
    )[0]
    assert event["source_reference"] == "https://example.com/data.dta"
    assert event["input"]["data_path"] == "https://example.com/data.dta"


def test_snapshot_filename_is_full_sha256_and_reused_across_runs(tmp_path: Path) -> None:
    dofile = tmp_path / "分析 file.do"
    source_bytes = b"display 1\n"
    dofile.write_bytes(source_bytes)
    expected_hash = hashlib.sha256(source_bytes).hexdigest()
    store = AuditStore(tmp_path / ".statamcp")
    first_run = store.start_run("stata_do", dofile.as_posix(), {})
    second_run = store.start_run("stata_do", dofile.as_posix(), {})

    first = store.snapshot_dofile(first_run, dofile)
    second = store.snapshot_dofile(second_run, dofile)

    assert first.path == second.path
    assert first.path == (
        tmp_path / ".statamcp" / "snapshot" / "objects" / f"{expected_hash}.do"
    )
    assert first.reused is False
    assert second.reused is True
    metadata = _read_jsonl(
        tmp_path / ".statamcp" / "snapshot" / "metadata.jsonl"
    )
    assert [item["original_name"] for item in metadata] == [
        "分析 file.do",
        "分析 file.do",
    ]
    assert [item["reused"] for item in metadata] == [False, True]

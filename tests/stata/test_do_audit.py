"""Tests for audited do-file execution and snapshot correlation."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from stata_mcp.audit import AuditExecutionContext, AuditStore, bind_audit_context
from stata_mcp.stata.stata_do.async_do import AsyncStataDo
from stata_mcp.stata.stata_do.do import StataDo


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _dofile(tmp_path: Path) -> Path:
    dofile = tmp_path / "analysis file.do"
    dofile.write_text("display 1\n", encoding="utf-8")
    return dofile


def test_stata_do_reuses_middleware_run_and_executes_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    base_path = tmp_path / ".statamcp"
    log_path = base_path / "stata-mcp-log"
    log_path.mkdir(parents=True)
    store = AuditStore(base_path)
    run = store.start_run(
        "stata_do",
        (tmp_path / "analysis file.do").as_posix(),
        {"dofile_path": (tmp_path / "analysis file.do").as_posix()},
        interface="mcp",
    )
    execution_context = AuditExecutionContext(run=run, store=store)
    executor = StataDo(
        "stata",
        log_path,
        is_unix=True,
        cwd=tmp_path,
        audit_store=store,
    )
    fake_execute = Mock(return_value={"text": log_path / "run.log"})
    monkeypatch.setattr(executor, "_execute_unix_like", fake_execute)

    with bind_audit_context(execution_context):
        result = executor.execute_dofile(_dofile(tmp_path), enable_smcl=False)

    executed_path = fake_execute.call_args.args[0]
    assert executed_path.parent == base_path / "snapshot"
    assert executed_path.read_text(encoding="utf-8") == "display 1\n"
    assert result == {"text": log_path / "run.log"}
    metadata = _read_jsonl(base_path / "snapshot" / "metadata.jsonl")
    assert metadata[0]["run_id"] == run.run_id
    assert metadata[0]["original_path"].endswith("analysis file.do")
    assert len(metadata[0]["sha256"]) == 64
    assert execution_context.artifacts["snapshot_path"] == executed_path.as_posix()


def test_direct_stata_do_creates_standalone_lifecycle(tmp_path: Path) -> None:
    base_path = tmp_path / ".statamcp"
    log_path = base_path / "stata-mcp-log"
    log_path.mkdir(parents=True)
    store = AuditStore(base_path)
    executor = StataDo(
        "stata",
        log_path,
        is_unix=True,
        cwd=tmp_path,
        audit_store=store,
    )
    executor._execute_unix_like = Mock(return_value={"text": log_path / "run.log"})

    executor.execute_dofile(_dofile(tmp_path), enable_smcl=False)

    events = _read_jsonl(base_path / "audit" / "stata_do.jsonl")
    assert [event["event"] for event in events] == ["started", "completed"]
    assert events[1]["artifacts"]["snapshot_path"].endswith("analysis_file.do")


def test_async_stata_do_reuses_middleware_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    base_path = tmp_path / ".statamcp"
    log_path = base_path / "stata-mcp-log"
    log_path.mkdir(parents=True)
    store = AuditStore(base_path)
    dofile = _dofile(tmp_path)
    run = store.start_run(
        "stata_do",
        dofile.as_posix(),
        {"dofile_path": dofile.as_posix()},
        interface="mcp",
    )
    execution_context = AuditExecutionContext(run=run, store=store)
    executor = AsyncStataDo(
        "stata",
        log_path,
        is_unix=True,
        cwd=tmp_path,
        audit_store=store,
    )
    fake_execute = AsyncMock(return_value={"text": log_path / "run.log"})
    monkeypatch.setattr(executor, "_execute_unix_like_async", fake_execute)

    async def run_case():
        with bind_audit_context(execution_context):
            return await executor.execute_dofile_async(dofile, enable_smcl=False)

    result = asyncio.run(run_case())

    executed_path = fake_execute.await_args.args[0]
    assert executed_path.parent == base_path / "snapshot"
    assert result == {"text": log_path / "run.log"}
    metadata = _read_jsonl(base_path / "snapshot" / "metadata.jsonl")
    assert metadata[0]["run_id"] == run.run_id

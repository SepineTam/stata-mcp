"""Tests for Stata do-file diagnostic checkpoints."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from stata_mcp.audit import AuditStore
from stata_mcp.observability import CheckpointWriter, configure_checkpoint_writer
from stata_mcp.stata.stata_do.async_do import AsyncStataDo
from stata_mcp.stata.stata_do.do import StataDo


def _read_events(artifact_root: Path) -> list[dict]:
    checkpoint_path = artifact_root / "debug" / "checkpoints.jsonl"
    return [
        json.loads(line)
        for line in checkpoint_path.read_text(encoding="utf-8").splitlines()
    ]


def _assert_completed_steps(events: list[dict], expected_steps: set[str]) -> None:
    for step in expected_steps:
        step_events = [event for event in events if event["step"] == step]
        assert [event["event"] for event in step_events] == [
            "started",
            "completed",
        ]


@pytest.fixture(autouse=True)
def reset_checkpoint_writer():
    configure_checkpoint_writer(None)
    yield
    configure_checkpoint_writer(None)


def test_sync_stata_do_records_validation_snapshot_execution_and_finalize(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    artifact_root = tmp_path / ".statamcp"
    log_dir = artifact_root / "stata-mcp-log"
    log_dir.mkdir(parents=True)
    dofile = tmp_path / "analysis.do"
    dofile.write_text("display 1\n", encoding="utf-8")
    executor = StataDo(
        stata_cli="stata",
        log_file_path=log_dir,
        is_unix=True,
        cwd=tmp_path,
        audit_store=AuditStore(artifact_root),
    )
    configure_checkpoint_writer(CheckpointWriter(artifact_root))

    def fake_execute(*args, **kwargs):
        return {"text": log_dir / "analysis.log"}

    monkeypatch.setattr(executor, "_execute_unix_like", fake_execute)

    result = executor.execute_dofile(dofile, log_file_name="analysis")

    assert result == {"text": log_dir / "analysis.log"}
    events = _read_events(artifact_root)
    _assert_completed_steps(
        events,
        {
            "stata_do.input_validation",
            "stata_do.snapshot",
            "stata_do.process_execution",
            "stata_do.audit_finalize",
        },
    )
    correlated = [
        event
        for event in events
        if event["step"] in {"stata_do.snapshot", "stata_do.process_execution"}
    ]
    assert all(event.get("run_id") for event in correlated)
    assert len({event["run_id"] for event in correlated}) == 1


def test_async_stata_do_records_snapshot_execution_and_finalize(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    artifact_root = tmp_path / ".statamcp"
    log_dir = artifact_root / "stata-mcp-log"
    log_dir.mkdir(parents=True)
    dofile = tmp_path / "analysis.do"
    dofile.write_text("display 1\n", encoding="utf-8")
    executor = AsyncStataDo(
        stata_cli="stata",
        log_file_path=log_dir,
        is_unix=True,
        cwd=tmp_path,
        audit_store=AuditStore(artifact_root),
    )
    configure_checkpoint_writer(CheckpointWriter(artifact_root))

    async def fake_execute(*args, **kwargs):
        return {"text": log_dir / "analysis.log"}

    monkeypatch.setattr(executor, "_execute_unix_like_async", fake_execute)

    result = asyncio.run(
        executor.execute_dofile_async(dofile, log_file_name="analysis")
    )

    assert result == {"text": log_dir / "analysis.log"}
    events = _read_events(artifact_root)
    _assert_completed_steps(
        events,
        {
            "stata_do.input_validation",
            "stata_do.snapshot",
            "stata_do.process_execution",
            "stata_do.audit_finalize",
        },
    )

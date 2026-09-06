"""Tests for non-blocking diagnostic steps."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stata_mcp.observability.checkpoints import (
    CheckpointWriter,
    configure_checkpoint_writer,
)
from stata_mcp.observability.steps import debug_step


def _events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


@pytest.fixture(autouse=True)
def reset_checkpoint_writer():
    configure_checkpoint_writer(None)
    yield
    configure_checkpoint_writer(None)


def test_debug_step_records_started_and_completed(tmp_path: Path) -> None:
    configure_checkpoint_writer(CheckpointWriter(tmp_path))

    with debug_step(
        "get_data_info.serialization",
        tool="get_data_info",
        request_id="request-1",
        attributes={"suffix": "dta"},
    ):
        pass

    events = _events(tmp_path / "debug" / "checkpoints.jsonl")
    assert [event["event"] for event in events] == ["started", "completed"]
    assert {event["step"] for event in events} == {"get_data_info.serialization"}
    assert {event["tool"] for event in events} == {"get_data_info"}
    assert {event["request_id"] for event in events} == {"request-1"}
    assert events[1]["duration_ms"] >= 0
    assert events[0]["attributes"] == {"suffix": "dta"}


def test_debug_step_records_error_type_and_reraises(tmp_path: Path) -> None:
    configure_checkpoint_writer(CheckpointWriter(tmp_path))

    with pytest.raises(ValueError, match="private detail"):
        with debug_step("stata_do.execution", tool="stata_do"):
            raise ValueError("private detail")

    events = _events(tmp_path / "debug" / "checkpoints.jsonl")
    assert [event["event"] for event in events] == ["started", "failed"]
    assert events[1]["error_type"] == "ValueError"
    assert "private detail" not in json.dumps(events[1])


def test_debug_step_does_not_change_result_when_writer_fails(
    monkeypatch,
) -> None:
    class FailingWriter:
        def append(self, payload):
            raise RuntimeError("diagnostics failed")

    configure_checkpoint_writer(FailingWriter())

    with debug_step("get_data_info.summary", tool="get_data_info"):
        result = 42

    assert result == 42

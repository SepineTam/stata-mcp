"""Tests for privacy-safe slow-call snapshots."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stata_mcp.observability.checkpoints import (
    CheckpointWriter,
    configure_checkpoint_writer,
)
from stata_mcp.observability.watchdog import SlowCallWatchdog


@pytest.fixture(autouse=True)
def reset_checkpoint_writer():
    configure_checkpoint_writer(None)
    yield
    configure_checkpoint_writer(None)


def test_slow_call_watchdog_writes_sanitized_thread_locations(
    tmp_path: Path,
) -> None:
    configure_checkpoint_writer(CheckpointWriter(tmp_path))
    watchdog = SlowCallWatchdog(
        tool="get_data_info",
        run_id="run-1",
        trace_id="a" * 32,
        span_id="b" * 16,
        process_id=4321,
        delays=(),
    )

    watchdog._write_snapshot(30.0)

    checkpoint_text = (tmp_path / "debug" / "checkpoints.jsonl").read_text(
        encoding="utf-8"
    )
    event = json.loads(checkpoint_text)
    assert event["event"] == "slow"
    assert event["step"] == "get_data_info.watchdog"
    assert event["tool"] == "get_data_info"
    assert event["run_id"] == "run-1"
    assert event["trace_id"] == "a" * 32
    assert event["span_id"] == "b" * 16
    assert event["process_id"] == 4321
    assert event["delay_seconds"] == 30.0
    assert event["threads"]
    assert "/Users/" not in checkpoint_text
    assert "test_watchdog.py" in checkpoint_text


def test_cancelled_watchdog_does_not_write_snapshot(tmp_path: Path) -> None:
    configure_checkpoint_writer(CheckpointWriter(tmp_path))
    watchdog = SlowCallWatchdog(
        tool="stata_do",
        run_id="run-2",
        delays=(),
    )

    watchdog.cancel()
    watchdog._write_snapshot(30.0)

    assert not (tmp_path / "debug" / "checkpoints.jsonl").exists()


def test_watchdog_without_recording_span_keeps_run_and_process_fallback(
    tmp_path: Path,
) -> None:
    configure_checkpoint_writer(CheckpointWriter(tmp_path))
    watchdog = SlowCallWatchdog(
        tool="stata_do",
        run_id="run-fallback",
        process_id=9876,
        delays=(),
    )

    watchdog._write_snapshot(30.0)

    event = json.loads(
        (tmp_path / "debug" / "checkpoints.jsonl").read_text(encoding="utf-8")
    )
    assert event["run_id"] == "run-fallback"
    assert event["process_id"] == 9876
    assert "trace_id" not in event
    assert "span_id" not in event

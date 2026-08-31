"""Tests for the local diagnostic checkpoint writer."""

from __future__ import annotations

import json
from pathlib import Path

from stata_mcp.observability.checkpoints import CheckpointWriter


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_checkpoint_writer_appends_jsonl_and_redacts_credentials(
    tmp_path: Path,
) -> None:
    writer = CheckpointWriter(tmp_path, max_bytes=1024, backup_count=2)

    assert writer.append(
        {
            "event": "started",
            "step": "dataframe_read",
            "attributes": {"api_key": "secret-value", "suffix": "dta"},
        }
    )

    records = _read_jsonl(tmp_path / "debug" / "checkpoints.jsonl")
    assert records == [
        {
            "attributes": {"api_key": "[REDACTED]", "suffix": "dta"},
            "event": "started",
            "step": "dataframe_read",
        }
    ]


def test_checkpoint_writer_rotates_before_exceeding_limit(tmp_path: Path) -> None:
    writer = CheckpointWriter(tmp_path, max_bytes=100, backup_count=2)

    assert writer.append({"event": "started", "step": "x" * 70})
    assert writer.append({"event": "completed", "step": "y" * 70})

    active_path = tmp_path / "debug" / "checkpoints.jsonl"
    backup_path = tmp_path / "debug" / "checkpoints.jsonl.1"
    assert active_path.exists()
    assert backup_path.exists()
    assert _read_jsonl(active_path)[0]["event"] == "completed"
    assert _read_jsonl(backup_path)[0]["event"] == "started"


def test_checkpoint_writer_fails_open_when_directory_is_unwritable(
    tmp_path: Path,
    monkeypatch,
) -> None:
    writer = CheckpointWriter(tmp_path)

    def fail_open(*args, **kwargs):
        raise OSError("disk unavailable")

    monkeypatch.setattr(Path, "open", fail_open)

    assert writer.append({"event": "started", "step": "safe"}) is False

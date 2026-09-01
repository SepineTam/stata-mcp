"""Tests for privacy-safe get_data_info diagnostic logging."""

from __future__ import annotations

import importlib
import json
import logging
import re
from pathlib import Path

from stata_mcp.api import get_data_info
from stata_mcp.observability import CheckpointWriter, configure_checkpoint_writer


def _write_config(tmp_path: Path, working_dir: Path, *, is_cache: bool = False) -> Path:
    """Write an isolated data-info configuration for a test."""
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "\n".join(
            [
                "[PROJECT]",
                f'WORKING_DIR = "{working_dir.as_posix()}"',
                "",
                "[data_info]",
                f"is_cache = {str(is_cache).lower()}",
            ]
        ),
        encoding="utf-8",
    )
    return config_path


def _diagnostic_messages(caplog) -> list[str]:
    """Return only get_data_info diagnostic events."""
    return [message for message in caplog.messages if message.startswith("event=get_data_info")]


def test_get_data_info_logs_correlated_pipeline_without_sensitive_content(
    caplog,
    tmp_path: Path,
) -> None:
    """Lifecycle logs should expose stages without paths, variable names, or values."""
    working_dir = tmp_path / "private-workspace"
    working_dir.mkdir()
    data_path = working_dir / "confidential-survey.csv"
    sensitive_value = "participant-secret-9842"
    data_path.write_text(
        f"private_income,private_group\n1,{sensitive_value}\n2,control\n",
        encoding="utf-8",
    )
    config_path = _write_config(tmp_path, working_dir)

    with caplog.at_level(logging.DEBUG):
        result = get_data_info(data_path.as_posix(), config_file=config_path)

    messages = _diagnostic_messages(caplog)
    joined_messages = "\n".join(messages)
    request_ids = {
        match.group(1)
        for message in messages
        if (match := re.search(r"request_id=([a-f0-9]{12})", message))
    }

    assert result
    assert len(request_ids) == 1
    assert "event=get_data_info.request.started" in joined_messages
    assert "event=get_data_info.path.validated" in joined_messages
    assert "event=get_data_info.dataframe_read.started" in joined_messages
    dataframe_messages = [
        message for message in messages if "dataframe_read" in message
    ]
    assert any("occurrence=1" in message for message in dataframe_messages)
    assert not any("occurrence=2" in message for message in dataframe_messages)
    assert "event=get_data_info.serialization.completed" in joined_messages
    assert "event=get_data_info.request.completed" in joined_messages
    assert "result_utf8_bytes=" in joined_messages
    assert data_path.as_posix() not in joined_messages
    assert data_path.name not in joined_messages
    assert "private_income" not in joined_messages
    assert sensitive_value not in joined_messages


def test_get_data_info_redacts_exception_message_from_traceback_log(
    caplog,
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Diagnostic tracebacks should retain frames while redacting path-bearing messages."""
    working_dir = tmp_path / "private-workspace"
    working_dir.mkdir()
    data_path = working_dir / "confidential-survey.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    config_path = _write_config(tmp_path, working_dir)
    get_data_info_module = importlib.import_module("stata_mcp.api.get_data_info")

    class _FailingDataInfo:
        def __init__(self, data_path, *args, **kwargs) -> None:
            self.data_path = data_path

        @property
        def info(self):
            raise RuntimeError(f"failed to process {self.data_path}")

    monkeypatch.setattr(
        get_data_info_module,
        "get_data_handler",
        lambda extension: _FailingDataInfo,
    )

    with caplog.at_level(logging.DEBUG):
        result = get_data_info(data_path.as_posix(), config_file=config_path)

    joined_messages = "\n".join(_diagnostic_messages(caplog))

    assert result.startswith("Failed to generate data summary for")
    assert "event=get_data_info.request.failed" in joined_messages
    assert "event=get_data_info.request.stack" in joined_messages
    assert "message redacted" not in joined_messages
    assert data_path.as_posix() not in joined_messages
    assert data_path.name not in joined_messages


def test_get_data_info_logs_cold_cache_and_cache_hit_read_counts(
    caplog,
    tmp_path: Path,
) -> None:
    """Cache diagnostics should expose the read that still occurs after a cache hit."""
    working_dir = tmp_path / "workspace"
    working_dir.mkdir()
    data_path = working_dir / "sample.csv"
    data_path.write_text("x,y\n1,2\n3,4\n", encoding="utf-8")
    config_path = _write_config(tmp_path, working_dir, is_cache=True)

    with caplog.at_level(logging.DEBUG):
        get_data_info(data_path.as_posix(), config_file=config_path)

    cold_messages = "\n".join(_diagnostic_messages(caplog))
    cold_dataframe_messages = [
        message
        for message in _diagnostic_messages(caplog)
        if "dataframe_read" in message
    ]
    assert 'outcome="miss_not_found"' in cold_messages
    assert "event=get_data_info.cache_write.completed" in cold_messages
    assert any("occurrence=1" in message for message in cold_dataframe_messages)
    assert not any(
        "occurrence=2" in message for message in cold_dataframe_messages
    )

    caplog.clear()
    with caplog.at_level(logging.DEBUG):
        get_data_info(data_path.as_posix(), config_file=config_path)

    hit_messages = "\n".join(_diagnostic_messages(caplog))
    assert 'outcome="hit"' in hit_messages
    assert "dataframe_reads=1" in hit_messages
    assert not any(
        "dataframe_read" in message and "occurrence=2" in message
        for message in _diagnostic_messages(caplog)
    )


def test_get_data_info_records_debug_steps_without_sensitive_content(
    tmp_path: Path,
) -> None:
    working_dir = tmp_path / "private-workspace"
    working_dir.mkdir()
    data_path = working_dir / "confidential-survey.csv"
    data_path.write_text(
        "private_income,private_group\n1,treatment\n2,control\n",
        encoding="utf-8",
    )
    config_path = _write_config(tmp_path, working_dir)
    writer = CheckpointWriter(tmp_path / ".statamcp")
    configure_checkpoint_writer(writer)

    try:
        result = get_data_info(data_path.as_posix(), config_file=config_path)
    finally:
        configure_checkpoint_writer(None)

    assert result
    checkpoint_path = (
        tmp_path / ".statamcp" / "debug" / "checkpoints.jsonl"
    )
    checkpoint_text = checkpoint_path.read_text(encoding="utf-8")
    events = [json.loads(line) for line in checkpoint_text.splitlines()]
    step_events = {
        step: [event["event"] for event in events if event["step"] == step]
        for step in {
            "get_data_info.runtime",
            "get_data_info.path_validation",
            "get_data_info.handler_initialization",
            "get_data_info.info_pipeline",
            "get_data_info.dataframe_read",
            "get_data_info.summary",
            "get_data_info.serialization",
        }
    }

    assert all(values for values in step_events.values())
    assert all(
        values == ["started", "completed"] * (len(values) // 2)
        for values in step_events.values()
    )
    assert data_path.as_posix() not in checkpoint_text
    assert data_path.name not in checkpoint_text
    assert "private_income" not in checkpoint_text
    assert "treatment" not in checkpoint_text

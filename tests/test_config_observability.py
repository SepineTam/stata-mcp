"""Configuration tests for default local debug tracing."""

from __future__ import annotations

from pathlib import Path

from stata_mcp.config import Config


def test_local_debug_tracing_defaults_to_enabled(tmp_path: Path) -> None:
    config = Config(config_file=tmp_path / "missing.toml")

    assert config.DEBUG_TRACING_ON is True
    assert config.DEBUG_TRACING_MAX_BYTES == 10 * 1024 * 1024
    assert config.DEBUG_TRACING_BACKUP_COUNT == 3


def test_local_debug_tracing_reads_explicit_configuration(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
[DEBUG.tracing]
ENABLED = false
MAX_BYTES = 2048
BACKUP_COUNT = 1
""".strip(),
        encoding="utf-8",
    )

    config = Config(config_file=config_path)

    assert config.DEBUG_TRACING_ON is False
    assert config.DEBUG_TRACING_MAX_BYTES == 2048
    assert config.DEBUG_TRACING_BACKUP_COUNT == 1

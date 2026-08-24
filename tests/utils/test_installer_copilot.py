"""Tests for GitHub Copilot CLI installer support."""

from __future__ import annotations

import json
from unittest.mock import Mock

import pytest

from stata_mcp.utils.installer import Installer


@pytest.fixture
def installer():
    return Installer(is_env=False)


def test_copilot_routes_to_copilot_installer(installer, monkeypatch):
    install = Mock()
    monkeypatch.setattr(installer, "install_to_copilot", install)

    installer.install("copilot")

    install.assert_called_once_with()


def test_copilot_cli_success_skips_config_file(installer, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    install_from_cli = Mock(return_value=True)
    monkeypatch.setattr(installer, "install_from_cli", install_from_cli)

    installer.install_to_copilot()

    install_from_cli.assert_called_once_with(
        cli_bin="copilot",
        command=[
            "mcp",
            "add",
            "stata-mcp",
            "--env",
            f"STATA_CLI={installer.STATA_CLI}",
            "--",
            "uvx",
            "stata-mcp",
        ],
    )
    assert not (tmp_path / ".copilot" / "mcp-config.json").exists()


def test_missing_copilot_cli_writes_official_config(
    installer, monkeypatch, tmp_path
):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    monkeypatch.setattr(installer, "install_from_cli", lambda **_kwargs: False)

    installer.install_to_copilot()

    config_path = tmp_path / ".copilot" / "mcp-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config == {
        "mcpServers": {
            "stata-mcp": {
                "type": "local",
                "command": "uvx",
                "args": ["stata-mcp"],
                "env": {},
                "tools": ["*"],
            }
        }
    }


def test_fallback_preserves_existing_servers(installer, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    monkeypatch.setattr(installer, "install_from_cli", lambda **_kwargs: False)
    config_path = tmp_path / ".copilot" / "mcp-config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        '{"mcpServers":{"other":{"type":"local","command":"other"}}}\n',
        encoding="utf-8",
    )

    installer.install_to_copilot()

    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config["mcpServers"]["other"]["command"] == "other"
    assert config["mcpServers"]["stata-mcp"]["type"] == "local"
    backups = list(config_path.parent.glob("mcp-config.backup-*.json"))
    assert len(backups) == 1

"""Tests for WorkBuddy installer support."""

from __future__ import annotations

import json
from unittest.mock import Mock

import pytest

from stata_mcp.utils.installer import Installer


@pytest.fixture
def installer():
    return Installer(is_env=False)


@pytest.mark.parametrize("client", ["workbuddy", "wb"])
def test_client_aliases_route_to_same_installer(installer, monkeypatch, client):
    install = Mock()
    monkeypatch.setattr(installer, "install_to_workbuddy", install)

    installer.install(client)

    install.assert_called_once_with()


def test_installs_to_workbuddy_config(installer, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", tmp_path.as_posix())

    installer.install_to_workbuddy()

    config_path = tmp_path / ".workbuddy" / "mcp.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config == {
        "mcpServers": {
            "stata-mcp": {
                "command": "uvx",
                "args": ["stata-mcp"],
                "env": {},
            }
        }
    }


def test_existing_servers_are_preserved_and_backed_up(
    installer, monkeypatch, tmp_path
):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    config_path = tmp_path / ".workbuddy" / "mcp.json"
    config_path.parent.mkdir(parents=True)
    original = '{"mcpServers":{"other":{"command":"other-mcp"}}}\n'
    config_path.write_text(original, encoding="utf-8")

    installer.install_to_workbuddy()

    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config["mcpServers"]["other"] == {"command": "other-mcp"}
    assert config["mcpServers"]["stata-mcp"]["command"] == "uvx"
    backups = list(config_path.parent.glob("mcp.backup-*.json"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == original


def test_existing_stata_mcp_is_not_duplicated(
    installer, monkeypatch, tmp_path
):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    config_path = tmp_path / ".workbuddy" / "mcp.json"
    config_path.parent.mkdir(parents=True)
    original = '{"mcpServers":{"stata-mcp":{"command":"uvx"}}}\n'
    config_path.write_text(original, encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        installer.install_to_workbuddy()

    assert exc_info.value.code == 0
    assert config_path.read_text(encoding="utf-8") == original

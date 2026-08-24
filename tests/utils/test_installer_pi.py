"""Tests for layered Pi installer support."""

from __future__ import annotations

import json
import subprocess
from unittest.mock import Mock

import pytest

import stata_mcp.utils.installer.installer as installer_module
from stata_mcp.utils.installer import Installer, Verifier, VerifyOutcome


@pytest.fixture
def installer():
    return Installer(is_env=False)


def test_pi_routes_to_pi_installer(installer, monkeypatch):
    install = Mock()
    monkeypatch.setattr(installer, "install_to_pi", install)

    installer.install("pi")

    install.assert_called_once_with()


def test_install_all_excludes_pi(installer, monkeypatch):
    regular_install = Mock()
    pi_install = Mock()
    mapping = {"regular": regular_install, "pi": pi_install}
    monkeypatch.setattr(
        Installer,
        "client_function_mapping",
        property(lambda _self: mapping),
    )

    installer.install_all()

    regular_install.assert_called_once_with()
    pi_install.assert_not_called()


def test_pi_present_installs_adapter_and_writes_config(
    installer, monkeypatch, tmp_path, capsys
):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    monkeypatch.setattr(installer, "is_pi_available", lambda: True)
    install_adapter = Mock(return_value=True)
    monkeypatch.setattr(installer, "install_pi_adapter", install_adapter)

    installer.install_to_pi()

    install_adapter.assert_called_once_with()
    config_path = tmp_path / ".pi" / "agent" / "mcp.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config["mcpServers"]["stata-mcp"]["command"] == "uvx"
    output = capsys.readouterr().out
    assert "Pi MCP adapter and Stata-MCP configuration are ready" in output


def test_pi_missing_prepares_config_without_installing_adapter(
    installer, monkeypatch, tmp_path, capsys
):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    monkeypatch.setattr(installer, "is_pi_available", lambda: False)
    install_adapter = Mock()
    monkeypatch.setattr(installer, "install_pi_adapter", install_adapter)

    installer.install_to_pi()

    install_adapter.assert_not_called()
    config_path = tmp_path / ".pi" / "agent" / "mcp.json"
    assert config_path.exists()
    output = capsys.readouterr().out
    assert "Pi is not installed" in output
    assert "not active yet" in output
    assert "pi install npm:pi-mcp-adapter" in output


def test_adapter_failure_still_prepares_config(
    installer, monkeypatch, tmp_path, capsys
):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    monkeypatch.setattr(installer, "is_pi_available", lambda: True)
    monkeypatch.setattr(installer, "install_pi_adapter", lambda: False)

    installer.install_to_pi()

    config_path = tmp_path / ".pi" / "agent" / "mcp.json"
    assert config_path.exists()
    output = capsys.readouterr().out
    assert "could not be installed" in output
    assert "pi install npm:pi-mcp-adapter" in output


def test_existing_pi_config_does_not_exit_or_duplicate(
    installer, monkeypatch, tmp_path
):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    monkeypatch.setattr(installer, "is_pi_available", lambda: False)
    config_path = tmp_path / ".pi" / "agent" / "mcp.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        '{"mcpServers":{"stata-mcp":{"command":"uvx"}}}\n',
        encoding="utf-8",
    )

    installer.install_to_pi()

    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert list(config["mcpServers"]) == ["stata-mcp"]


def test_install_pi_adapter_runs_pi_package_command(installer, monkeypatch):
    monkeypatch.setattr(installer_module.shutil, "which", lambda _name: "/bin/pi")
    run = Mock(
        return_value=subprocess.CompletedProcess(
            ["/bin/pi", "install", "npm:pi-mcp-adapter"], 0, "installed\n", ""
        )
    )
    monkeypatch.setattr(installer_module.subprocess, "run", run)

    assert installer.install_pi_adapter() is True

    run.assert_called_once_with(
        ["/bin/pi", "install", "npm:pi-mcp-adapter"],
        check=True,
        capture_output=True,
        text=True,
    )


def test_install_pi_adapter_accepts_already_installed(installer, monkeypatch):
    monkeypatch.setattr(installer_module.shutil, "which", lambda _name: "/bin/pi")
    error = subprocess.CalledProcessError(
        1,
        ["/bin/pi", "install", "npm:pi-mcp-adapter"],
        stderr="Package is already installed",
    )
    monkeypatch.setattr(
        installer_module.subprocess,
        "run",
        Mock(side_effect=error),
    )

    assert installer.install_pi_adapter() is True


def test_pi_adapter_detection_uses_pi_list(installer, monkeypatch):
    monkeypatch.setattr(installer_module.shutil, "which", lambda _name: "/bin/pi")
    monkeypatch.setattr(
        installer_module.subprocess,
        "run",
        Mock(
            return_value=subprocess.CompletedProcess(
                ["/bin/pi", "list"], 0, "npm:pi-mcp-adapter\n", ""
            )
        ),
    )

    assert installer.is_pi_adapter_installed() is True


def _write_pi_config(tmp_path):
    config_path = tmp_path / ".pi" / "agent" / "mcp.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        '{"mcpServers":{"stata-mcp":{"command":"uvx"}}}',
        encoding="utf-8",
    )
    return config_path


def test_verify_pi_is_verified_when_runtime_is_ready(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    _write_pi_config(tmp_path)
    monkeypatch.setattr(Installer, "is_pi_available", staticmethod(lambda: True))
    monkeypatch.setattr(Installer, "is_pi_adapter_installed", lambda _self: True)

    result = Verifier(sys_os="darwin").verify_client("pi")

    assert result.outcome == VerifyOutcome.VERIFIED
    assert result.location == "pi"


def test_verify_pi_warns_when_pi_is_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    _write_pi_config(tmp_path)
    monkeypatch.setattr(Installer, "is_pi_available", staticmethod(lambda: False))

    result = Verifier(sys_os="darwin").verify_client("pi")

    assert result.outcome == VerifyOutcome.WARNING
    assert result.reason is not None
    assert "Pi is not installed" in result.reason


def test_verify_pi_warns_when_adapter_is_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    _write_pi_config(tmp_path)
    monkeypatch.setattr(Installer, "is_pi_available", staticmethod(lambda: True))
    monkeypatch.setattr(Installer, "is_pi_adapter_installed", lambda _self: False)

    result = Verifier(sys_os="darwin").verify_client("pi")

    assert result.outcome == VerifyOutcome.WARNING
    assert result.reason is not None
    assert "pi-mcp-adapter is not installed" in result.reason

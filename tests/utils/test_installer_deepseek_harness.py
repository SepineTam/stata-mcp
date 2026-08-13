"""Tests for DeepSeek Harness installer support."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from stata_mcp.utils.installer import Installer


@pytest.fixture
def installer():
    return Installer(is_env=False)


@pytest.mark.parametrize("client", ["dsh", "deepseek-harness"])
def test_client_aliases_route_to_same_installer(installer, monkeypatch, client):
    install = Mock()
    monkeypatch.setattr(installer, "install_to_deepseek_harness", install)

    installer.install(client)

    install.assert_called_once_with()


def test_installs_to_dsh_home_web_profile(installer, monkeypatch, tmp_path):
    dsh_home = tmp_path / "custom-dsh-home"
    monkeypatch.setenv("DSH_HOME", str(dsh_home))

    installer.install_to_deepseek_harness()

    config_path = dsh_home / "profiles" / "web" / "cordis.patch.yml"
    content = config_path.read_text(encoding="utf-8")
    assert "# File:" not in content
    assert "Your patch layer for this dsh profile" not in content
    assert "    - id: stata-mcp" in content
    assert "      name: '@deepseek-ai/dsh-mcp-client'" in content
    assert "        serverName: stata-mcp" in content
    assert "        transport: stdio" in content
    assert "        command: uvx" in content
    assert "        args: ['stata-mcp', 'server']" in content
    assert "Tools appear as mcp__stata-mcp__*." in content
    assert "mcp__stata__*" not in content
    assert "cwd:" not in content
    assert "        toolCallTimeoutMs: 1200000" in content
    assert "          maxAttempts: 5" in content


def test_existing_patch_is_preserved_and_backed_up(installer, tmp_path):
    config_path = tmp_path / "cordis.patch.yml"
    original = "- insert:\n    - id: another-plugin\n      config: {}\n"
    config_path.write_text(original, encoding="utf-8")

    installer.install_to_deepseek_harness_config(config_path)

    content = config_path.read_text(encoding="utf-8")
    backups = list(tmp_path.glob("cordis.patch.backup-*.yml"))
    assert content.startswith(original.rstrip("\n"))
    assert content.count("    - id: stata-mcp") == 1
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == original


@pytest.mark.parametrize("entry_id", ["stata-mcp", "'stata-mcp'", '"stata-mcp"'])
def test_existing_canonical_entry_is_not_duplicated(installer, tmp_path, entry_id):
    config_path = tmp_path / "cordis.patch.yml"
    original = f"- insert:\n    - id: {entry_id}\n      config: {{}}\n"
    config_path.write_text(original, encoding="utf-8")

    installer.install_to_deepseek_harness_config(config_path)

    assert config_path.read_text(encoding="utf-8") == original
    assert not list(tmp_path.glob("cordis.patch.backup-*.yml"))


@pytest.mark.parametrize("entry_id", ["mcp-for-stata", "mcp-stata", "another-plugin"])
def test_noncanonical_id_does_not_block_install(installer, tmp_path, entry_id):
    config_path = tmp_path / "cordis.patch.yml"
    original = (
        f"- insert:\n    - id: {entry_id}\n      config:\n"
        "        serverName: stata-mcp\n"
    )
    config_path.write_text(original, encoding="utf-8")

    installer.install_to_deepseek_harness_config(config_path)

    content = config_path.read_text(encoding="utf-8")
    assert content.startswith(original.rstrip("\n"))
    assert content.count("    - id: stata-mcp") == 1
    assert len(list(tmp_path.glob("cordis.patch.backup-*.yml"))) == 1


def test_top_level_mapping_is_rejected_without_changes(installer, tmp_path, capsys):
    config_path = tmp_path / "cordis.patch.yml"
    original = "plugins:\n  - id: another-plugin\n"
    config_path.write_text(original, encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        installer.install_to_deepseek_harness_config(config_path)

    assert exc_info.value.code == 1
    assert config_path.read_text(encoding="utf-8") == original
    assert not list(tmp_path.glob("cordis.patch.backup-*.yml"))
    assert "must contain a top-level YAML list" in capsys.readouterr().out


def test_comments_and_yaml_document_marker_allow_install(installer, tmp_path):
    config_path = tmp_path / "cordis.patch.yml"
    original = "# Existing DSH patch\n---\n- insert:\n    - id: another-plugin\n"
    config_path.write_text(original, encoding="utf-8")

    installer.install_to_deepseek_harness_config(config_path)

    content = config_path.read_text(encoding="utf-8")
    assert content.startswith(original.rstrip("\n"))
    assert content.count("- insert:") == 2

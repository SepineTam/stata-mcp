"""Installation discovery contracts for macOS, Windows, and unsupported systems."""

from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from stata_mcp.cli import _cli
from stata_mcp.core.types import OSNotSupported, StataMCPError
from stata_mcp.utils import discovery


@pytest.fixture(autouse=True)
def isolated_inventory(monkeypatch):
    monkeypatch.setenv("PATH", "")
    monkeypatch.delenv("STATA_CLI", raising=False)
    monkeypatch.delenv("stata_cli", raising=False)
    monkeypatch.setattr(discovery, "_windows_roots", lambda: [])
    monkeypatch.setitem(
        sys.modules, "app_scanner", SimpleNamespace(get_installed_apps=lambda: [])
    )
    monkeypatch.setitem(
        sys.modules, "winapps", SimpleNamespace(list_installed=lambda: [])
    )


def make_executable(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    path.chmod(0o755)
    return path


def make_app(path, executable="stata-mp"):
    make_executable(path / "Contents" / "MacOS" / executable)
    return path


def set_platform(monkeypatch, system):
    monkeypatch.setattr(discovery.platform, "system", lambda: system)


def set_mac_apps(monkeypatch, paths):
    monkeypatch.setattr(
        sys.modules["app_scanner"],
        "get_installed_apps",
        lambda: [{"name": "StataMP", "path": str(path)} for path in paths],
    )


def test_macos_keeps_same_name_installations_and_deduplicates(monkeypatch, tmp_path):
    set_platform(monkeypatch, "Darwin")
    classic = make_app(tmp_path / "Stata" / "StataMP.app")
    current = make_app(tmp_path / "StataNow" / "StataMP.app", "StataMP")
    set_mac_apps(monkeypatch, [current, classic, classic])
    monkeypatch.setenv("STATA_CLI", str(current / "Contents" / "MacOS" / "StataMP"))

    assert discovery.discover_stata() == sorted([str(classic), str(current)])


def test_macos_filters_unrelated_missing_and_empty_bundles(monkeypatch, tmp_path):
    set_platform(monkeypatch, "Darwin")
    unrelated = make_app(tmp_path / "Other.app")
    empty = tmp_path / "StataSE.app"
    empty.mkdir()
    set_mac_apps(monkeypatch, [unrelated, empty, tmp_path / "StataMP.app"])

    assert discovery.discover_stata() == []


def test_macos_path_symlink_returns_bundle(monkeypatch, tmp_path):
    set_platform(monkeypatch, "Darwin")
    app = make_app(tmp_path / "Custom" / "StataBE.app", "stata-be")
    directory = tmp_path / "bin"
    directory.mkdir()
    try:
        (directory / "stata-be").symlink_to(app / "Contents" / "MacOS" / "stata-be")
    except OSError:
        pytest.skip("Creating symlinks is not permitted on this host")
    monkeypatch.setenv("PATH", str(directory))

    assert discovery.discover_stata() == [str(app)]


@pytest.mark.skipif(
    sys.platform == "win32", reason="Windows does not implement Unix executable bits"
)
def test_macos_ignores_nonexecutable_binary(monkeypatch, tmp_path):
    set_platform(monkeypatch, "Darwin")
    app = make_app(tmp_path / "StataMP.app")
    (app / "Contents" / "MacOS" / "stata-mp").chmod(0o644)
    set_mac_apps(monkeypatch, [app])

    assert discovery.discover_stata() == []


def test_windows_uses_inventory_and_excludes_utilities(monkeypatch, tmp_path):
    set_platform(monkeypatch, "Windows")
    location = tmp_path / "Custom Stata 19"
    mp = make_executable(location / "StataMP-64.exe")
    se = make_executable(location / "StataSE.exe")
    make_executable(location / "uninstall.exe")
    make_executable(location / "StataUpdate.exe")
    other = make_executable(tmp_path / "Other" / "StataMP.exe")
    monkeypatch.setattr(
        sys.modules["winapps"],
        "list_installed",
        lambda: [
            SimpleNamespace(name="Stata/MP 19", install_location=location),
            SimpleNamespace(name="Stata 18", install_location=None),
            SimpleNamespace(name="Other", install_location=other.parent),
        ],
    )

    assert discovery.discover_stata() == sorted([str(mp), str(se)])


def test_windows_missing_registry_location_uses_standard_directory(
    monkeypatch, tmp_path
):
    set_platform(monkeypatch, "Windows")
    binary = make_executable(tmp_path / "Stata18" / "StataMP-64.exe")
    monkeypatch.setattr(discovery, "_windows_roots", lambda: [tmp_path, tmp_path])
    monkeypatch.setenv("STATA_CLI", str(binary))
    monkeypatch.setenv("PATH", str(binary.parent))

    assert discovery.discover_stata() == [str(binary)]


def test_windows_environment_command_is_resolved_using_path(monkeypatch, tmp_path):
    set_platform(monkeypatch, "Windows")
    binary = make_executable(tmp_path / "StataMP-64.exe")
    monkeypatch.setenv("STATA_CLI", binary.name)
    monkeypatch.setenv("PATH", str(tmp_path))

    assert discovery.discover_stata() == [str(binary)]


@pytest.mark.parametrize("system", ["Linux", "FreeBSD", "Unknown"])
def test_unsupported_os_raises_before_reading_inventory(monkeypatch, system):
    set_platform(monkeypatch, system)
    monkeypatch.setattr(
        discovery,
        "_application_candidates",
        lambda system: pytest.fail("Inventory was read"),
    )

    with pytest.raises(OSNotSupported, match="^OS not supported$") as caught:
        discovery.discover_stata()
    assert isinstance(caught.value, StataMCPError)


def test_cli_prints_only_paths(monkeypatch, capsys, tmp_path):
    set_platform(monkeypatch, "Darwin")
    app = make_app(tmp_path / "StataMP.app")
    set_mac_apps(monkeypatch, [app])
    monkeypatch.setattr(sys, "argv", ["stata-mcp", "discover"])
    monkeypatch.setattr(
        _cli, "handle_server", lambda args: pytest.fail("Server was started")
    )

    with pytest.raises(SystemExit) as caught:
        _cli.main()
    assert caught.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == f"{app}\n"
    assert captured.err == ""


def test_cli_unsupported_os_is_one_error_line(monkeypatch, capsys):
    set_platform(monkeypatch, "Linux")
    monkeypatch.setattr(sys, "argv", ["stata-mcp", "discover"])

    with pytest.raises(SystemExit) as caught:
        _cli.main()
    assert caught.value.code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "OS not supported\n"


def test_cli_no_installations_is_empty_success(monkeypatch, capsys):
    set_platform(monkeypatch, "Darwin")
    monkeypatch.setattr(sys, "argv", ["stata-mcp", "discover"])

    with pytest.raises(SystemExit) as caught:
        _cli.main()
    assert caught.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""

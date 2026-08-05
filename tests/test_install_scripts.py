from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POWERSHELL_SCRIPTS = (
    PROJECT_ROOT / "scripts" / "install.ps1",
    PROJECT_ROOT / "scripts" / "install.bat",
)
SHELL_SCRIPTS = (
    PROJECT_ROOT / "scripts" / "install.sh",
    PROJECT_ROOT / "scripts" / "install.command",
)
POWERSHELL_MARKER = "# --- PowerShell script starts below this line ---\n"


def read_powershell_payload(script_path: Path) -> str:
    script_content = script_path.read_text(encoding="utf-8")
    if script_path.suffix == ".bat":
        return script_content.split(POWERSHELL_MARKER, maxsplit=1)[1]
    return script_content


@pytest.mark.parametrize("script_path", POWERSHELL_SCRIPTS)
def test_windows_uv_installer_isolated_from_current_shell(script_path: Path) -> None:
    script_content = read_powershell_payload(script_path)

    assert "function Invoke-UvInstaller" in script_content
    assert "Get-Process -Id $PID" in script_content
    assert "-ExecutionPolicy Bypass" in script_content
    assert "return ($LASTEXITCODE -eq 0)" in script_content
    assert "exit 1" not in script_content


@pytest.mark.parametrize("script_path", POWERSHELL_SCRIPTS)
def test_windows_installer_recovers_uv_from_standard_locations(
    script_path: Path,
) -> None:
    script_content = read_powershell_payload(script_path)

    assert "function Add-UvToPath" in script_content
    assert '".local\\bin\\uv.exe"' in script_content
    assert '".cargo\\bin\\uv.exe"' in script_content
    assert "Test-Path -LiteralPath $uvCandidate -PathType Leaf" in script_content


def test_windows_installers_keep_their_powershell_payloads_in_sync() -> None:
    powershell_content = POWERSHELL_SCRIPTS[0].read_text(encoding="utf-8")
    batch_payload = read_powershell_payload(POWERSHELL_SCRIPTS[1])

    assert batch_payload.replace(".bat", ".ps1") == powershell_content


@pytest.mark.parametrize("script_path", SHELL_SCRIPTS)
def test_shell_installer_handles_piped_execution_safely(script_path: Path) -> None:
    script_content = script_path.read_text(encoding="utf-8")

    assert "set -eo pipefail" in script_content
    assert "open_terminal_input" in script_content
    assert "exec 3< /dev/tty" in script_content
    assert "<&3" in script_content
    assert "uv_available" in script_content
    assert '"$HOME/.local/bin/uv"' in script_content
    assert '"$HOME/.cargo/bin/uv"' in script_content


def test_shell_installers_keep_their_implementation_in_sync() -> None:
    shell_lines = SHELL_SCRIPTS[0].read_text(encoding="utf-8").splitlines()
    command_lines = SHELL_SCRIPTS[1].read_text(encoding="utf-8").splitlines()

    assert shell_lines[10:] == command_lines[10:]

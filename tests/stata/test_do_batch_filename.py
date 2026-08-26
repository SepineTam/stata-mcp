"""Tests that the Windows launcher batch filename is never derived from user input.

The batch path is passed to a shell on Windows, so the do-file name (whose
stem may legally contain characters that cmd.exe treats as syntax) must never
be interpolated into the batch filename. Regression guard for the fix that
replaced ``{dofile_path.stem}`` with a random uuid-based name in both
``_execute_windows`` and ``_execute_windows_with_monitors``.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from stata_mcp.stata.stata_do.do import StataDo

BATCH_NAME_PATTERN = re.compile(r"^stata_batch__[0-9a-f]{32}\.do$")
METACHARACTERS = "&^%!"


class TestGenerateBatchFileName:
    def test_matches_safe_pattern(self):
        name = StataDo._generate_batch_file_name()

        assert BATCH_NAME_PATTERN.fullmatch(name)

    def test_unique_across_calls(self):
        names = {StataDo._generate_batch_file_name() for _ in range(64)}

        assert len(names) == 64

    def test_contains_no_shell_metacharacters(self):
        for _ in range(16):
            name = StataDo._generate_batch_file_name()

            assert not any(char in name for char in METACHARACTERS)


class _FakeCompletedProcess:
    returncode = 0
    stdout = ""
    stderr = ""


class _FakePopen:
    returncode = 0

    def poll(self):
        return 0

    def communicate(self, timeout=None):
        return ("", "")

    def terminate(self):
        pass

    def wait(self, timeout=None):
        return 0

    def kill(self):
        pass


@pytest.fixture
def malicious_dofile(tmp_path: Path) -> Path:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    dofile = work_dir / "x&calc.exe&.do"
    dofile.write_text("display 123\n")
    return dofile


@pytest.fixture
def executor(tmp_path: Path) -> StataDo:
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return StataDo(
        stata_cli=r"C:\Program Files\Stata18\StataMP-64.exe",
        log_file_path=log_dir,
        is_unix=False,
        cwd=tmp_path,
    )


class TestExecuteWindowsUsesSafeBatchName:
    def test_run_command_line_has_no_metacharacters(
        self, monkeypatch, executor, malicious_dofile, tmp_path
    ):
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = list(cmd)
            return _FakeCompletedProcess()

        monkeypatch.setattr(
            "stata_mcp.stata.stata_do.do.subprocess.run", fake_run
        )

        executor.execute_dofile(malicious_dofile)

        cmd = captured["cmd"]
        assert BATCH_NAME_PATTERN.fullmatch(Path(cmd[3]).name)
        assert not any(char in " ".join(cmd) for char in "&^%!")
        assert "calc.exe" not in " ".join(cmd)


class TestExecuteWindowsWithMonitorsUsesSafeBatchName:
    def test_popen_command_line_has_no_metacharacters(
        self, monkeypatch, executor, malicious_dofile
    ):
        captured = {}

        def fake_popen(cmd, **kwargs):
            captured["cmd"] = list(cmd)
            return _FakePopen()

        monkeypatch.setattr(
            "stata_mcp.stata.stata_do.do.subprocess.Popen", fake_popen
        )
        executor.monitors = [SimpleNamespace(start=lambda proc: None,
                                             stop=lambda: None)]
        executor.IS_MONITOR = True

        executor.execute_dofile(malicious_dofile)

        cmd = captured["cmd"]
        assert BATCH_NAME_PATTERN.fullmatch(Path(cmd[3]).name)
        assert not any(char in " ".join(cmd) for char in "&^%!")
        assert "calc.exe" not in " ".join(cmd)

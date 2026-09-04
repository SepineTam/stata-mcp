from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_ROOT = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "stata-toolbox"
    / "skills"
    / "stata-audit"
)
SCRIPTS = SKILL_ROOT / "scripts"


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )


@pytest.fixture
def audit_root(tmp_path: Path) -> Path:
    root = tmp_path / ".statamcp"
    data_run = "20260830T080000000000Z_1111111111111111"
    stata_run = "20260830T080500000000Z_2222222222222222"
    blocked_run = "20260830T081000000000Z_3333333333333333"
    security_id = f"sec_{blocked_run}_01"

    write_jsonl(
        root / "audit" / "get_data_info.jsonl",
        [
            {
                "schema_version": 1,
                "run_id": data_run,
                "event": "started",
                "tool": "get_data_info",
                "timestamp": "2026-08-30T08:00:00+00:00",
                "interface": "mcp",
                "source_reference": str(tmp_path / "data.dta"),
                "input": {"data_path": str(tmp_path / "data.dta")},
                "client": {"name": "test-client", "version": "1"},
            },
            {
                "schema_version": 1,
                "run_id": data_run,
                "event": "completed",
                "tool": "get_data_info",
                "timestamp": "2026-08-30T08:00:01+00:00",
                "duration_ms": 1000.0,
                "executed": True,
            },
        ],
    )
    write_jsonl(
        root / "audit" / "stata_do.jsonl",
        [
            {
                "schema_version": 1,
                "run_id": stata_run,
                "event": "started",
                "tool": "stata_do",
                "timestamp": "2026-08-30T08:05:00+00:00",
                "interface": "mcp",
                "source_reference": str(tmp_path / "analysis.do"),
                "input": {"dofile_path": str(tmp_path / "analysis.do")},
            },
            {
                "schema_version": 1,
                "run_id": stata_run,
                "event": "completed",
                "tool": "stata_do",
                "timestamp": "2026-08-30T08:05:02+00:00",
                "duration_ms": 2000.0,
                "executed": True,
            },
        ],
    )
    write_jsonl(
        root / "audit" / "read_log.jsonl",
        [
            {
                "schema_version": 1,
                "run_id": blocked_run,
                "event": "started",
                "tool": "read_log",
                "timestamp": "2026-08-30T08:10:00+00:00",
                "interface": "mcp",
                "source_reference": "/outside/result.log",
                "input": {"file_path": "/outside/result.log"},
            },
            {
                "schema_version": 1,
                "run_id": blocked_run,
                "event": "blocked",
                "tool": "read_log",
                "timestamp": "2026-08-30T08:10:00.050000+00:00",
                "duration_ms": 50.0,
                "executed": False,
                "security_event_ids": [security_id],
            },
        ],
    )
    write_jsonl(
        root / "audit" / "security.jsonl",
        [
            {
                "schema_version": 1,
                "security_event_id": security_id,
                "run_id": blocked_run,
                "timestamp": "2026-08-30T08:10:00.040000+00:00",
                "tool": "read_log",
                "decision": "blocked",
                "stage": "path_validation",
                "risk_type": "outside_allowed_directories",
                "executed": False,
                "findings": [{"rule_id": "path.boundary"}],
                "source_path": "/outside/result.log",
            }
        ],
    )

    source_bytes = b"sysuse auto, clear\nsummarize price\n"
    digest = hashlib.sha256(source_bytes).hexdigest()
    object_path = root / "snapshot" / "objects" / f"{digest}.do"
    object_path.parent.mkdir(parents=True, exist_ok=True)
    object_path.write_bytes(source_bytes)
    write_jsonl(
        root / "snapshot" / "metadata.jsonl",
        [
            {
                "schema_version": 1,
                "run_id": stata_run,
                "tool": "stata_do",
                "created_at": "2026-08-30T08:05:00+00:00",
                "original_path": str(tmp_path / "analysis.do"),
                "original_name": "analysis.do",
                "snapshot_path": str(object_path),
                "sha256": digest,
                "sha256_prefix": digest[:8],
                "size_bytes": len(source_bytes),
                "reused": False,
            }
        ],
    )
    write_jsonl(
        root / "debug" / "traces.jsonl",
        [
            {
                "schema_version": 1,
                "trace_id": "a" * 32,
                "span_id": "b" * 16,
                "name": "tools/call read_log",
                "start_time_unix_nano": 1788077400000000000,
                "end_time_unix_nano": 1788077400050000000,
                "attributes": {"statamcp.run_id": blocked_run},
            }
        ],
    )
    return root


def run_script(script_name: str, *arguments: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script_name), *arguments],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def test_validation_passes_for_linked_evidence(audit_root: Path, tmp_path: Path) -> None:
    result = run_script("validate_audit.py", str(audit_root), "--json", cwd=tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is True
    assert payload["checked"]["runs"] == 3
    assert payload["checked"]["security_events"] == 1
    assert payload["checked"]["snapshot_records"] == 1


def test_security_report_distinguishes_prevented_calls(
    audit_root: Path, tmp_path: Path
) -> None:
    result = run_script("security_audit.py", str(audit_root), "--json", cwd=tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary"]["prevented"] == 1
    assert payload["summary"]["unlinked"] == 0
    assert payload["events"][0]["source_path"] == "<external>/result.log"


def test_analysis_and_run_inspection(audit_root: Path, tmp_path: Path) -> None:
    analysis = run_script("analyze_audit.py", str(audit_root), "--json", cwd=tmp_path)
    assert analysis.returncode == 0, analysis.stdout + analysis.stderr
    assert json.loads(analysis.stdout)["summary"]["total_runs"] == 3

    run_id = "20260830T081000000000Z_3333333333333333"
    inspection = run_script(
        "inspect_audit.py",
        str(audit_root),
        "--run-id",
        run_id,
        "--json",
        cwd=tmp_path,
    )
    assert inspection.returncode == 0, inspection.stdout + inspection.stderr
    matches = json.loads(inspection.stdout)["matches"]
    assert {match["file"] for match in matches} == {
        "audit/read_log.jsonl",
        "audit/security.jsonl",
        "debug/traces.jsonl",
    }


def test_html_report_uses_relative_template_and_requested_name(
    audit_root: Path, tmp_path: Path
) -> None:
    output_path = tmp_path / "20260830-1610-stata_do.html"
    result = run_script(
        "render_audit_html.py",
        str(audit_root),
        "--tool",
        "stata_do",
        "--output",
        str(output_path),
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"REPORT_PATH={output_path}" in result.stdout
    rendered = output_path.read_text(encoding="utf-8")
    assert "Time position" in rendered
    assert "Times New Roman" in rendered
    assert "20260830T080500000000Z_2222222222222222" in rendered
    assert "20260830T080000000000Z_1111111111111111" not in rendered
    assert "__AUDIT_DATA__" not in rendered
    assert str(tmp_path) not in rendered


def test_validation_detects_snapshot_tampering(audit_root: Path, tmp_path: Path) -> None:
    snapshot_object = next((audit_root / "snapshot" / "objects").glob("*.do"))
    snapshot_object.write_bytes(b"tampered")

    result = run_script("validate_audit.py", str(audit_root), "--json", cwd=tmp_path)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["valid"] is False
    assert any(
        issue["code"] == "snapshot_hash_mismatch" for issue in payload["issues"]
    )


def test_renderer_rejects_path_like_tool_name(
    audit_root: Path, tmp_path: Path
) -> None:
    result = run_script(
        "render_audit_html.py",
        str(audit_root),
        "--tool",
        "../../outside",
        cwd=tmp_path,
    )

    assert result.returncode == 2
    assert "tool must be 'all'" in result.stderr
    assert not (tmp_path / "outside.html").exists()


def test_html_renderer_escapes_embedded_script_text(
    audit_root: Path, tmp_path: Path
) -> None:
    ledger = audit_root / "audit" / "get_data_info.jsonl"
    records = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
    records[0]["source_reference"] = "</script><script>window.injected=true</script>"
    write_jsonl(ledger, records)
    output_path = tmp_path / "safe.html"

    result = run_script(
        "render_audit_html.py",
        str(audit_root),
        "--output",
        str(output_path),
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    rendered = output_path.read_text(encoding="utf-8")
    assert "</script><script>window.injected" not in rendered
    assert "\\u003c/script\\u003e" in rendered
    assert "Content-Security-Policy" in rendered


def test_validation_rejects_mismatched_security_tool(
    audit_root: Path, tmp_path: Path
) -> None:
    security_ledger = audit_root / "audit" / "security.jsonl"
    records = [
        json.loads(line)
        for line in security_ledger.read_text(encoding="utf-8").splitlines()
    ]
    records[0]["tool"] = "stata_do"
    write_jsonl(security_ledger, records)

    result = run_script("validate_audit.py", str(audit_root), "--json", cwd=tmp_path)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert any(
        issue["code"] == "security_tool_mismatch" for issue in payload["issues"]
    )


def test_validation_fails_when_audit_ledgers_are_missing(tmp_path: Path) -> None:
    empty_root = tmp_path / ".statamcp"
    empty_root.mkdir()

    result = run_script("validate_audit.py", str(empty_root), "--json", cwd=tmp_path)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["valid"] is False
    assert any(
        issue["code"] == "audit_ledgers_missing" for issue in payload["issues"]
    )

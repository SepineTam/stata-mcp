"""Subprocess acceptance for default local observability setup."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_configure_local_observability_links_checkpoints_and_spans(
    tmp_path: Path,
) -> None:
    script = "\n".join(
        [
            "from stata_mcp.observability import configure_local_observability, debug_step",
            f"configure_local_observability({str(tmp_path)!r})",
            "with debug_step('get_data_info.serialization', tool='get_data_info', run_id='run-1'):",
            "    pass",
        ]
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    checkpoints = [
        json.loads(line)
        for line in (tmp_path / "debug" / "checkpoints.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    traces = [
        json.loads(line)
        for line in (tmp_path / "debug" / "traces.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]

    assert [event["event"] for event in checkpoints] == [
        "started",
        "completed",
    ]
    assert len({event["trace_id"] for event in checkpoints}) == 1
    assert traces[0]["trace_id"] == checkpoints[0]["trace_id"]
    assert traces[0]["attributes"]["statamcp.run_id"] == "run-1"

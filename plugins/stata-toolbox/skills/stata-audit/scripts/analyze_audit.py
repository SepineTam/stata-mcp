#!/usr/bin/env python3
"""Produce a neutral usage analysis from Stata-MCP audit evidence."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from audit_common import build_run_views, load_audit_bundle, summarize_runs, write_json


def build_findings(
    summary: dict[str, Any],
    *,
    snapshot_count: int,
    snapshot_reuse_count: int,
    security_count: int,
    incomplete_count: int,
) -> list[str]:
    """Translate measurements into bounded, factual observations."""
    findings = [
        (
            f"Observed {summary['total_runs']} tool runs across "
            f"{summary['active_days']} active day(s)."
        )
    ]
    if summary["tool_counts"]:
        leading_tool, leading_count = max(
            summary["tool_counts"].items(), key=lambda item: item[1]
        )
        findings.append(
            f"Most frequently used tool: {leading_tool} ({leading_count} runs)."
        )
    findings.append(
        f"Security ledger contains {security_count} decision(s); "
        "review each linked blocked run before treating it as an execution failure."
    )
    findings.append(
        f"Snapshot metadata contains {snapshot_count} record(s), including "
        f"{snapshot_reuse_count} content reuse record(s)."
    )
    if incomplete_count:
        findings.append(
            f"{incomplete_count} run(s) lack a terminal event and require investigation."
        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifact_root",
        nargs="?",
        type=Path,
        default=Path.cwd() / ".statamcp",
        help="Artifact root (default: ./.statamcp)",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    bundle = load_audit_bundle(args.artifact_root, include_debug=False)
    runs, run_issues = build_run_views(bundle)
    summary = summarize_runs(runs)
    client_counts = Counter(
        str(run["client"].get("name"))
        for run in runs
        if isinstance(run.get("client"), dict) and run["client"].get("name")
    )
    interface_counts = Counter(
        str(provenance["record"].get("interface"))
        for run in runs
        for provenance in run.get("provenance", [])
        if provenance["record"].get("event") == "started"
        and provenance["record"].get("interface")
    )
    snapshot_count = len(bundle.snapshot_records)
    snapshot_reuse_count = sum(
        record.payload.get("reused") is True for record in bundle.snapshot_records
    )
    incomplete_count = summary["status_counts"].get("incomplete", 0)
    findings = build_findings(
        summary,
        snapshot_count=snapshot_count,
        snapshot_reuse_count=snapshot_reuse_count,
        security_count=len(bundle.security_records),
        incomplete_count=incomplete_count,
    )
    result = {
        "artifact_root": bundle.root.as_posix(),
        "summary": {
            **summary,
            "clients": dict(sorted(client_counts.items())),
            "interfaces": dict(sorted(interface_counts.items())),
            "security_events": len(bundle.security_records),
            "snapshot_records": snapshot_count,
            "snapshot_reuse_records": snapshot_reuse_count,
        },
        "findings": findings,
        "limitations": [
            "Client names are self-reported and are not verified identities.",
            "Audit timing shows recorded tool calls, not unrecorded human or agent work.",
            "A missing terminal event is an investigation lead, not proof of execution.",
            *[
                issue.message
                for issue in [*bundle.issues, *run_issues]
            ],
        ],
    }

    if args.json:
        write_json(result)
    else:
        print(f"Audit analysis: {bundle.root}")
        print(f"Observed period: {summary['observed_start']} — {summary['observed_end']}")
        print(f"Tool runs: {summary['total_runs']}")
        print(f"By tool: {summary['tool_counts']}")
        print(f"By status: {summary['status_counts']}")
        for finding in findings:
            print(f"- {finding}")
        print("Limitations:")
        for limitation in result["limitations"]:
            print(f"- {limitation}")
    return (
        1
        if any(
            issue.severity == "error" for issue in [*bundle.issues, *run_issues]
        )
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())

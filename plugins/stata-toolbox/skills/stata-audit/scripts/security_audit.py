#!/usr/bin/env python3
"""Summarize security decisions and confirm their tool-run linkage."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from audit_common import build_run_views, load_audit_bundle, mask_path, write_json


def security_outcome(payload: dict[str, Any]) -> str:
    """Classify whether a finding was prevented or allowed with warning."""
    decision = payload.get("decision")
    executed = payload.get("executed")
    if decision == "blocked" and executed is False:
        return "prevented"
    if decision == "warning" and executed is True:
        return "executed_with_warning"
    return "inconsistent"


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
    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Show recorded absolute source paths",
    )
    args = parser.parse_args()

    bundle = load_audit_bundle(args.artifact_root, include_debug=False)
    runs, run_issues = build_run_views(bundle)
    runs_by_id = {run["run_id"]: run for run in runs}
    events: list[dict[str, Any]] = []
    for record in bundle.security_records:
        payload = record.payload
        run_id = payload.get("run_id")
        security_event_id = payload.get("security_event_id")
        source_path = payload.get("source_path")
        if not args.show_paths:
            source_path = mask_path(source_path, Path.cwd())
        findings = payload.get("findings")
        rule_ids = []
        if isinstance(findings, list):
            rule_ids = [
                finding.get("rule_id")
                for finding in findings
                if isinstance(finding, dict) and finding.get("rule_id")
            ]
        parent_run = runs_by_id.get(str(run_id), {})
        parent_security_ids = parent_run.get("security_event_ids", [])
        link_valid = bool(
            security_event_id
            and security_event_id in parent_security_ids
            and parent_run.get("tool") == payload.get("tool")
        )
        events.append(
            {
                "timestamp": payload.get("timestamp"),
                "security_event_id": security_event_id,
                "run_id": run_id,
                "tool": payload.get("tool"),
                "decision": payload.get("decision"),
                "executed": payload.get("executed"),
                "outcome": security_outcome(payload),
                "stage": payload.get("stage"),
                "risk_type": payload.get("risk_type"),
                "rule_ids": rule_ids,
                "source_path": source_path,
                "linked_from_terminal": link_valid,
                "parent_run_status": (
                    parent_run.get("status")
                    if run_id is not None
                    else None
                ),
                "provenance": {
                    "file": record.relative_file,
                    "line": record.line_number,
                },
            }
        )

    outcome_counts = Counter(event["outcome"] for event in events)
    risk_counts = Counter(str(event["risk_type"]) for event in events)
    result = {
        "artifact_root": bundle.root.as_posix(),
        "summary": {
            "security_events": len(events),
            "prevented": outcome_counts.get("prevented", 0),
            "executed_with_warning": outcome_counts.get("executed_with_warning", 0),
            "inconsistent": outcome_counts.get("inconsistent", 0),
            "unlinked": sum(not event["linked_from_terminal"] for event in events),
            "risk_types": dict(sorted(risk_counts.items())),
        },
        "events": events,
        "reader_issues": [
            issue.as_dict() for issue in [*bundle.issues, *run_issues]
        ],
    }

    if args.json:
        write_json(result)
    else:
        summary = result["summary"]
        print(f"Security audit: {bundle.root}")
        print(
            f"{summary['security_events']} decisions; "
            f"{summary['prevented']} prevented; "
            f"{summary['executed_with_warning']} executed with warning; "
            f"{summary['unlinked']} unlinked"
        )
        for event in events:
            rules = ", ".join(event["rule_ids"]) or "no rule_id"
            print(
                f"{event['timestamp']}  {event['outcome']}  {event['tool']}  "
                f"{event['risk_type']}  {rules}  {event['security_event_id']}"
            )

    has_integrity_problem = bool(
        outcome_counts.get("inconsistent", 0)
        or any(not event["linked_from_terminal"] for event in events)
        or any(issue.severity == "error" for issue in [*bundle.issues, *run_issues])
    )
    return 1 if has_integrity_problem else 0


if __name__ == "__main__":
    raise SystemExit(main())

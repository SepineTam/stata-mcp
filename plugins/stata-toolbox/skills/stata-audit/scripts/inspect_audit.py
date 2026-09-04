#!/usr/bin/env python3
"""Inspect recent audit records or reconstruct one run across ledgers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_common import (
    load_audit_bundle,
    parse_timestamp,
    timestamp_sort_key,
    write_json,
)


def record_run_id(payload: dict[str, Any]) -> str | None:
    """Find a run ID in durable or OpenTelemetry-style records."""
    run_id = payload.get("run_id")
    if isinstance(run_id, str):
        return run_id
    attributes = payload.get("attributes")
    if isinstance(attributes, dict):
        traced_run_id = attributes.get("statamcp.run_id")
        if isinstance(traced_run_id, str):
            return traced_run_id
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifact_root",
        nargs="?",
        type=Path,
        default=Path.cwd() / ".statamcp",
        help="Artifact root (default: ./.statamcp)",
    )
    parser.add_argument("--run-id", help="Reconstruct one exact run across files")
    parser.add_argument("--tool", help="Limit recent records to one tool ledger")
    parser.add_argument("--limit", type=int, default=20, help="Recent record limit")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    bundle = load_audit_bundle(args.artifact_root, include_debug=True)
    selected = bundle.records
    if args.run_id:
        selected = [
            record
            for record in selected
            if record_run_id(record.payload) == args.run_id
        ]
    elif args.tool:
        selected = [
            record
            for record in selected
            if record.payload.get("tool") == args.tool
            or record.relative_file == f"audit/{args.tool}.jsonl"
        ]
    selected = sorted(selected, key=timestamp_sort_key)
    if not args.run_id:
        selected = selected[-max(0, args.limit) :]

    result = {
        "artifact_root": bundle.root.as_posix(),
        "query": {
            "run_id": args.run_id,
            "tool": args.tool,
            "limit": args.limit,
        },
        "matches": [record.derived() for record in selected],
        "reader_issues": [issue.as_dict() for issue in bundle.issues],
    }
    if args.json:
        write_json(result)
    else:
        print(f"Audit evidence: {bundle.root}")
        print(f"Matches: {len(selected)}")
        for record in selected:
            timestamp = (
                record.payload.get("timestamp")
                or record.payload.get("created_at")
                or "unknown-time"
            )
            parsed = parse_timestamp(timestamp)
            display_time = parsed.isoformat() if parsed else str(timestamp)
            event = (
                record.payload.get("event")
                or record.payload.get("decision")
                or record.payload.get("name")
                or "record"
            )
            tool = record.payload.get("tool") or "-"
            print(
                f"{display_time}  {tool}  {event}  "
                f"{record.relative_file}:{record.line_number}"
            )
            print(json.dumps(record.payload, ensure_ascii=False, indent=2))
        for issue in bundle.issues:
            print(f"[{issue.severity.upper()}] {issue.code}: {issue.message}")

    if args.run_id and not selected:
        return 1
    return 1 if any(issue.severity == "error" for issue in bundle.issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())

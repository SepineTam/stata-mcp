#!/usr/bin/env python3
"""Validate lifecycle, security linkage, and snapshot integrity."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from audit_common import (
    AuditIssue,
    build_run_views,
    find_snapshot_object,
    load_audit_bundle,
    parse_timestamp,
    sha256_file,
    write_json,
)


def validate_security_links(bundle: Any, runs: list[dict[str, Any]]) -> list[AuditIssue]:
    """Check every terminal security ID against the central ledger."""
    issues: list[AuditIssue] = []
    security_by_id: dict[str, Any] = {}
    for record in bundle.security_records:
        security_id = record.payload.get("security_event_id")
        decision = record.payload.get("decision")
        executed = record.payload.get("executed")
        if decision not in {"blocked", "warning"}:
            issues.append(
                AuditIssue(
                    "error",
                    "security_decision_invalid",
                    f"Unsupported security decision: {decision!r}",
                    file=record.relative_file,
                    line=record.line_number,
                )
            )
        elif (decision == "blocked" and executed is not False) or (
            decision == "warning" and executed is not True
        ):
            issues.append(
                AuditIssue(
                    "error",
                    "security_execution_inconsistent",
                    f"Security decision {decision!r} conflicts with executed={executed!r}.",
                    file=record.relative_file,
                    line=record.line_number,
                )
            )
        if not isinstance(security_id, str) or not security_id:
            issues.append(
                AuditIssue(
                    "error",
                    "security_event_id_missing",
                    "Security record has no security_event_id.",
                    file=record.relative_file,
                    line=record.line_number,
                )
            )
            continue
        if security_id in security_by_id:
            issues.append(
                AuditIssue(
                    "error",
                    "security_event_id_duplicate",
                    f"Duplicate security_event_id: {security_id}",
                    file=record.relative_file,
                    line=record.line_number,
                )
            )
        security_by_id[security_id] = record

    referenced_ids: set[str] = set()
    for run in runs:
        if run["status"] == "blocked" and not run.get("security_event_ids"):
            issues.append(
                AuditIssue(
                    "error",
                    "blocked_security_link_missing",
                    "Blocked run does not link to a security event.",
                    run_id=run["run_id"],
                )
            )
        if run["status"] == "blocked" and run.get("executed") is not False:
            issues.append(
                AuditIssue(
                    "error",
                    "blocked_execution_inconsistent",
                    "Blocked run must record executed as false.",
                    run_id=run["run_id"],
                )
            )
        for security_id in run.get("security_event_ids", []):
            if not isinstance(security_id, str):
                continue
            referenced_ids.add(security_id)
            security_record = security_by_id.get(security_id)
            if security_record is None:
                issues.append(
                    AuditIssue(
                        "error",
                        "security_link_missing",
                        f"Linked security event does not exist: {security_id}",
                        run_id=run["run_id"],
                    )
                )
                continue
            if security_record.payload.get("run_id") != run["run_id"]:
                issues.append(
                    AuditIssue(
                        "error",
                        "security_run_mismatch",
                        f"Security event {security_id} points to another run.",
                        run_id=run["run_id"],
                    )
                )
            if security_record.payload.get("tool") != run["tool"]:
                issues.append(
                    AuditIssue(
                        "error",
                        "security_tool_mismatch",
                        f"Security event {security_id} points to another tool.",
                        run_id=run["run_id"],
                    )
                )
            if (
                run["status"] == "blocked"
                and security_record.payload.get("decision") != "blocked"
            ):
                issues.append(
                    AuditIssue(
                        "error",
                        "blocked_decision_mismatch",
                        f"Blocked run links to a non-blocked decision: {security_id}",
                        run_id=run["run_id"],
                    )
                )

    for security_id, record in security_by_id.items():
        if security_id not in referenced_ids:
            issues.append(
                AuditIssue(
                    "warning",
                    "security_event_unlinked",
                    f"Security event is not linked from a terminal event: {security_id}",
                    file=record.relative_file,
                    line=record.line_number,
                    run_id=str(record.payload.get("run_id") or "") or None,
                )
            )
    return issues


def validate_snapshots(bundle: Any, runs: list[dict[str, Any]]) -> list[AuditIssue]:
    """Hash snapshot objects and check expected run coverage."""
    issues: list[AuditIssue] = []
    snapshots_by_run: dict[str, list[Any]] = {}
    for record in bundle.snapshot_records:
        run_id = record.payload.get("run_id")
        if isinstance(run_id, str):
            snapshots_by_run.setdefault(run_id, []).append(record)
        expected_hash = record.payload.get("sha256")
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            issues.append(
                AuditIssue(
                    "error",
                    "snapshot_hash_invalid",
                    "Snapshot metadata has no valid full SHA-256 digest.",
                    file=record.relative_file,
                    line=record.line_number,
                    run_id=run_id if isinstance(run_id, str) else None,
                )
            )
            continue
        object_path = find_snapshot_object(bundle.root, record.payload)
        if object_path is None:
            issues.append(
                AuditIssue(
                    "error",
                    "snapshot_object_missing",
                    f"Snapshot object not found for SHA-256 {expected_hash}.",
                    file=record.relative_file,
                    line=record.line_number,
                    run_id=run_id if isinstance(run_id, str) else None,
                )
            )
            continue
        actual_hash = sha256_file(object_path)
        if actual_hash != expected_hash:
            issues.append(
                AuditIssue(
                    "error",
                    "snapshot_hash_mismatch",
                    f"Snapshot bytes do not match recorded SHA-256: {object_path}",
                    file=record.relative_file,
                    line=record.line_number,
                    run_id=run_id if isinstance(run_id, str) else None,
                )
            )

    for run in runs:
        snapshot_count = len(snapshots_by_run.get(run["run_id"], []))
        if snapshot_count > 1:
            issues.append(
                AuditIssue(
                    "error",
                    "snapshot_metadata_duplicate",
                    f"Run has {snapshot_count} snapshot metadata records; expected one.",
                    run_id=run["run_id"],
                )
            )
        if (
            run["tool"] == "stata_do"
            and run["status"] == "completed"
            and run.get("executed") is not False
            and snapshot_count == 0
        ):
            issues.append(
                AuditIssue(
                    "error",
                    "executed_snapshot_missing",
                    "Completed stata_do run has no snapshot metadata.",
                    run_id=run["run_id"],
                )
            )
    return issues


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

    bundle = load_audit_bundle(args.artifact_root, include_debug=True)
    runs, run_issues = build_run_views(bundle)
    timestamp_issues: list[AuditIssue] = []
    for record in bundle.records:
        timestamp_value = record.payload.get("timestamp") or record.payload.get(
            "created_at"
        )
        if timestamp_value is not None and parse_timestamp(timestamp_value) is None:
            timestamp_issues.append(
                AuditIssue(
                    "error",
                    "timestamp_invalid",
                    f"Invalid ISO 8601 timestamp: {timestamp_value!r}",
                    file=record.relative_file,
                    line=record.line_number,
                    run_id=(
                        record.payload.get("run_id")
                        if isinstance(record.payload.get("run_id"), str)
                        else None
                    ),
                )
            )

    issues = [
        *bundle.issues,
        *run_issues,
        *timestamp_issues,
        *validate_security_links(bundle, runs),
        *validate_snapshots(bundle, runs),
    ]
    severity_counts = Counter(issue.severity for issue in issues)
    result = {
        "artifact_root": bundle.root.as_posix(),
        "valid": severity_counts.get("error", 0) == 0,
        "checked": {
            "records": len(bundle.records),
            "runs": len(runs),
            "security_events": len(bundle.security_records),
            "snapshot_records": len(bundle.snapshot_records),
            "debug_records": len(bundle.debug_records),
        },
        "issue_counts": dict(sorted(severity_counts.items())),
        "issues": [issue.as_dict() for issue in issues],
    }

    if args.json:
        write_json(result)
    else:
        status = "PASS" if result["valid"] else "FAIL"
        print(f"Audit validation: {status}")
        print(f"Evidence root: {bundle.root}")
        print(f"Checked: {result['checked']}")
        for issue in issues:
            location = issue.file or issue.run_id or "audit"
            if issue.line is not None:
                location = f"{location}:{issue.line}"
            print(
                f"[{issue.severity.upper()}] {issue.code} at {location}: "
                f"{issue.message}"
            )
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

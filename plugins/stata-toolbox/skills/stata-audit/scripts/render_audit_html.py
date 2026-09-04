#!/usr/bin/env python3
"""Render linked Stata-MCP JSONL evidence as a standalone HTML dashboard."""

from __future__ import annotations

import argparse
import html
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from audit_common import (
    build_run_views,
    load_audit_bundle,
    mask_path,
    safe_json_for_html,
    summarize_runs,
)
from validate_audit import validate_security_links, validate_snapshots

TOOL_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


def tool_name(value: str) -> str:
    """Accept the all-tools selector or one safe audit ledger stem."""
    if value == "all" or TOOL_NAME_PATTERN.fullmatch(value):
        return value
    raise argparse.ArgumentTypeError(
        "tool must be 'all' or start with a letter and contain only "
        "letters, digits, underscores, and hyphens"
    )


def masked_run(run: dict[str, Any], project_root: Path, show_paths: bool) -> dict[str, Any]:
    """Return only report fields, masking absolute paths by default."""
    copied = {
        key: run.get(key)
        for key in (
            "run_id",
            "tool",
            "status",
            "started_at",
            "ended_at",
            "duration_ms",
            "executed",
            "client",
            "protocol_version",
            "request_id",
            "security_event_ids",
            "error",
        )
    }
    copied["source_reference"] = (
        run.get("source_reference")
        if show_paths
        else mask_path(run.get("source_reference"), project_root)
    )
    artifacts = run.get("artifacts")
    copied["artifacts"] = _mask_mapping(artifacts, project_root, show_paths)
    return copied


def _mask_mapping(value: Any, project_root: Path, show_paths: bool) -> Any:
    if show_paths:
        return value
    if isinstance(value, dict):
        return {
            key: (
                mask_path(item, project_root)
                if "path" in str(key).lower()
                else _mask_mapping(item, project_root, show_paths)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_mask_mapping(item, project_root, show_paths) for item in value]
    return value


def atomic_write(path: Path, content: str) -> None:
    """Write a derived report atomically without touching source evidence."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifact_root",
        nargs="?",
        type=Path,
        default=Path.cwd() / ".statamcp",
        help="Artifact root (default: ./.statamcp)",
    )
    parser.add_argument(
        "--tool",
        default="all",
        type=tool_name,
        help="Render all tools or one exact tool name (default: all)",
    )
    parser.add_argument("--output", type=Path, help="Explicit HTML output path")
    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Show recorded absolute paths instead of masking them",
    )
    args = parser.parse_args()

    bundle = load_audit_bundle(args.artifact_root, include_debug=True)
    all_runs, run_issues = build_run_views(bundle)
    validation_issues = [
        *bundle.issues,
        *run_issues,
        *validate_security_links(bundle, all_runs),
        *validate_snapshots(bundle, all_runs),
    ]
    runs = all_runs
    if args.tool != "all":
        runs = [run for run in runs if run["tool"] == args.tool]
    selected_run_ids = {run["run_id"] for run in runs}
    security = [
        record.payload
        for record in bundle.security_records
        if record.payload.get("run_id") in selected_run_ids
    ]
    snapshots = [
        record.payload
        for record in bundle.snapshot_records
        if record.payload.get("run_id") in selected_run_ids
    ]
    debug = [
        _debug_summary(record.payload)
        for record in bundle.debug_records
        if _debug_run_id(record.payload) in selected_run_ids
    ]
    project_root = Path.cwd().resolve()
    report_data = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "artifact_root": (
            bundle.root.as_posix()
            if args.show_paths
            else mask_path(bundle.root.as_posix(), project_root)
        ),
        "tool_filter": args.tool,
        "paths_masked": not args.show_paths,
        "summary": summarize_runs(runs),
        "runs": [masked_run(run, project_root, args.show_paths) for run in runs],
        "security": [
            _mask_mapping(record, project_root, args.show_paths)
            for record in security
        ],
        "snapshots": [
            _mask_mapping(record, project_root, args.show_paths)
            for record in snapshots
        ],
        "debug": debug,
        "issues": [
            issue.as_dict() for issue in validation_issues
        ],
    }

    template_path = (
        Path(__file__).resolve().parent.parent / "assets" / "audit_dashboard.html"
    )
    template = template_path.read_text(encoding="utf-8")
    rendered = template.replace("__AUDIT_DATA__", safe_json_for_html(report_data))
    report_title = (
        "Stata-MCP Audit Dashboard"
        if args.tool == "all"
        else f"Stata-MCP Audit · {args.tool}"
    )
    rendered = rendered.replace(
        "__REPORT_TITLE__",
        html.escape(report_title, quote=True),
    )

    output_path = args.output
    if output_path is None:
        suffix = "audit" if args.tool == "all" else args.tool
        filename = f"{datetime.now().astimezone():%Y%m%d-%H%M}-{suffix}.html"
        output_path = bundle.root / "reports" / "html" / filename
    output_path = output_path.expanduser().resolve()
    atomic_write(output_path, rendered)
    print(f"REPORT_PATH={output_path}")
    print(f"RUNS={len(runs)} SECURITY_EVENTS={len(security)} SNAPSHOTS={len(snapshots)}")
    return 1 if any(issue["severity"] == "error" for issue in report_data["issues"]) else 0


def _debug_run_id(payload: dict[str, Any]) -> str | None:
    run_id = payload.get("run_id")
    if isinstance(run_id, str):
        return run_id
    attributes = payload.get("attributes")
    if isinstance(attributes, dict):
        value = attributes.get("statamcp.run_id")
        return value if isinstance(value, str) else None
    return None


def _debug_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Keep correlation fields without embedding arbitrary trace attributes."""
    return {
        "run_id": _debug_run_id(payload),
        "trace_id": payload.get("trace_id"),
        "span_id": payload.get("span_id"),
        "name": payload.get("name") or payload.get("step"),
        "duration_ms": payload.get("duration_ms"),
        "timestamp": payload.get("timestamp"),
        "start_time_unix_nano": payload.get("start_time_unix_nano"),
        "end_time_unix_nano": payload.get("end_time_unix_nano"),
    }


if __name__ == "__main__":
    raise SystemExit(main())

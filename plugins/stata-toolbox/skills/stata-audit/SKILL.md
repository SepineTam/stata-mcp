---
name: stata-audit
description: Inspect, validate, summarize, and render local Stata-MCP audit evidence under .statamcp. Use when a user asks what tools ran, whether a security guard blocked anything, how one run links across JSONL files, whether snapshots are intact, or wants an interactive audit dashboard.
metadata:
  version: "0.1.0"
---

# Stata-MCP Audit

Read Stata-MCP evidence without changing the source JSONL ledgers or snapshot
objects. Resolve every script and template relative to this skill directory,
while resolving the default evidence root from the user's current working
directory as `<cwd>/.statamcp`.

## Choose the Narrowest Script

| User need | Script | Result |
| --- | --- | --- |
| Check security blocks or warnings | `scripts/security_audit.py` | Security decisions, whether execution was prevented, risk types, and linkage state |
| Summarize project usage | `scripts/analyze_audit.py` | Neutral counts, observed period, tool mix, outcomes, snapshots, and limitations |
| Inspect recent records or one run | `scripts/inspect_audit.py` | Source-preserving records joined by exact `run_id` |
| Check evidence integrity | `scripts/validate_audit.py` | Lifecycle, timestamp, security-link, and full SHA-256 snapshot checks |
| Open an interactive view | `scripts/render_audit_html.py` | Standalone English HTML dashboard with linked ledgers and a movable time window |

Use the user's project directory as the command working directory. Example:

```bash
python /absolute/path/to/stata-audit/scripts/validate_audit.py .statamcp
```

All scripts accept an optional artifact-root argument and default to
`./.statamcp`. The text output is suitable for a quick review; add `--json`
when structured downstream analysis is useful.

## Review Rules

- Join lifecycle records with exact `run_id`, not filename or time proximity.
- Treat `event == "blocked"` with `executed == false` as a prevented call. A
  normal blocked call is security evidence, not a script failure.
- Follow `security_event_ids` to `audit/security.jsonl` and report missing or
  inconsistent links.
- Verify snapshot bytes against the complete recorded SHA-256. The first eight
  characters are display-only.
- Treat missing terminal events as investigation leads, not proof that a tool
  executed or failed.
- Treat client name and version as self-reported metadata, not verified user or
  agent identity.
- Keep full paths masked unless the user explicitly needs them. The reporting
  scripts support `--show-paths` for that case.
- Never edit, sort, truncate, rotate, replay, or repair evidence in place.

## Script Usage

Security review:

```bash
python scripts/security_audit.py .statamcp
python scripts/security_audit.py .statamcp --json
```

Project usage analysis:

```bash
python scripts/analyze_audit.py .statamcp
```

Inspect the latest records or reconstruct one exact run:

```bash
python scripts/inspect_audit.py .statamcp --limit 20
python scripts/inspect_audit.py .statamcp --run-id <exact-run-id> --json
```

Validate evidence:

```bash
python scripts/validate_audit.py .statamcp
```

Exit code `0` means no integrity error was found. Exit code `1` means the
evidence is missing, malformed, inconsistent, or failed a snapshot hash check.
Warnings remain visible but do not alone fail validation.

Render the combined dashboard or one tool view:

```bash
python scripts/render_audit_html.py .statamcp
python scripts/render_audit_html.py .statamcp --tool stata_do
```

The default output directory is:

```text
<cwd>/.statamcp/reports/html/
```

Combined reports use `YYYYMMDD-HHMM-audit.html`. A filtered report uses the
tool name, for example `YYYYMMDD-HHMM-stata_do.html`. The renderer locates
`assets/audit_dashboard.html` from its own Python-file location, so it works
regardless of the user's current directory.

The dashboard derives its global start and end from the minimum and maximum
timestamps in the selected evidence. Its two `Time position` handles start at
those exact boundaries and control the visible chart start and end. Ordinary
text uses Times New Roman; tool names, run IDs, ledgers, hashes, and paths use a
monospace code font. Times are displayed as `YYYY-MM-DD HH-MM` with the viewer's
local time-zone name and UTC offset.

After rendering, report the exact generated path and ask whether the user wants
to open it. Open it only after the user agrees. Use the platform's normal local
file opener (`open` on macOS, `xdg-open` on Linux, or `start` on Windows).

## Reporting Boundaries

State conclusions as measurements from recorded tool calls. Do not claim that
the audit captures unrecorded thinking, manual Stata actions, authorship, or a
continuous agent session. If evidence has parse errors, unsupported schema
versions, unmatched lifecycle events, missing security links, or failed hashes,
surface those limitations before summarizing behavior.

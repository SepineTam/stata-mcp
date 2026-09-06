# Reading Audit Files

This guide answers common audit questions using read-only commands. Replace
`.statamcp` when `PROJECT.FOLDER_TAG` points to another artifact directory.

!!! warning "Keep the source evidence unchanged"

    Do not edit, truncate, rotate, sort in place, or replay files under
    `.statamcp/`. Run queries against the originals and write any derived report
    to a different directory. Audit files can contain sensitive local paths and
    research metadata even after credential redaction.

## 1. Locate the Evidence

From the project working directory:

=== "macOS / Linux"

    ```bash
    find .statamcp/audit -maxdepth 1 -type f -name '*.jsonl' -print
    find .statamcp/snapshot -maxdepth 2 -type f -print
    ```

=== "Windows PowerShell"

    ```powershell
    Get-ChildItem .statamcp\audit\*.jsonl
    Get-ChildItem .statamcp\snapshot -Recurse -File
    ```

If the directory does not exist, confirm the MCP server's `WORKING_DIR` and
`FOLDER_TAG`, then make one tool call. The artifact root is created lazily when
evidence is first persisted.

## 2. Inspect Recent Records

Every non-empty line is one complete JSON object.

=== "macOS / Linux"

    ```bash
    tail -n 5 .statamcp/audit/stata_do.jsonl
    tail -n 1 .statamcp/audit/stata_do.jsonl | jq .
    ```

=== "Windows PowerShell"

    ```powershell
    Get-Content .statamcp\audit\stata_do.jsonl -Tail 5
    Get-Content .statamcp\audit\stata_do.jsonl -Tail 1 |
      ConvertFrom-Json | ConvertTo-Json -Depth 10
    ```

Do not assume that the last line in one file is the newest event across the
whole system. Cross-file investigations should join on `run_id` and compare the
UTC `timestamp` fields.

## 3. Reconstruct One Run

Copy the exact `run_id` from a tool event:

```text
20260830T083015123456Z_2ce5d65f457ce14a
```

=== "macOS / Linux with jq"

    ```bash
    RUN_ID='20260830T083015123456Z_2ce5d65f457ce14a'

    find .statamcp/audit .statamcp/snapshot .statamcp/debug \
      -type f \( -name '*.jsonl' -o -name '*.jsonl.[0-9]*' \) \
      -print 2>/dev/null |
      while IFS= read -r audit_file; do
        jq -c --arg run_id "$RUN_ID" \
          'select(.run_id == $run_id)' "$audit_file"
      done
    ```

=== "Windows PowerShell"

    ```powershell
    $RunId = '20260830T083015123456Z_2ce5d65f457ce14a'
    $Files = @(
      Get-ChildItem .statamcp\audit\*.jsonl
      Get-Item .statamcp\snapshot\metadata.jsonl -ErrorAction SilentlyContinue
      Get-ChildItem .statamcp\debug\*.jsonl* -ErrorAction SilentlyContinue
    )

    $Files | Get-Content | ForEach-Object { $_ | ConvertFrom-Json } |
      Where-Object { $_.run_id -eq $RunId } |
      Sort-Object timestamp |
      ConvertTo-Json -Depth 10
    ```

Interpret the result in this order:

1. Pair the tool `started` event with its terminal event.
2. Read terminal `event`, `executed`, `duration_ms`, and any `error`.
3. Follow `security_event_ids` to matching `security_event_id` records.
4. Follow the same `run_id` to snapshot metadata for `stata_do`.
5. Use debug checkpoints only when stage-level diagnosis is needed.

## 4. List Blocked Calls

The authoritative blocked condition is `event == "blocked"` together with
`executed == false`.

=== "macOS / Linux"

    ```bash
    jq -c 'select(.event == "blocked" and .executed == false)' \
      .statamcp/audit/stata_do.jsonl \
      .statamcp/audit/get_data_info.jsonl \
      .statamcp/audit/read_log.jsonl
    ```

=== "Windows PowerShell"

    ```powershell
    Get-ChildItem .statamcp\audit\*.jsonl | Get-Content |
      ForEach-Object { $_ | ConvertFrom-Json } |
      Where-Object { $_.event -eq 'blocked' -and $_.executed -eq $false } |
      Select-Object timestamp, tool, run_id, security_event_ids
    ```

`output.is_error` may be `false` for a normal MCP response that explains a
refusal. Never use that field alone to count security blocks.

## 5. Find Runs Without a Terminal Event

An unmatched `started` record is a lead for investigation, not proof that the
tool did or did not execute.

```bash
jq -s '
  group_by(.run_id)
  | map(select(
      any(.[]; .event == "started")
      and (any(.[];
        .event == "completed"
        or .event == "failed"
        or .event == "interrupted"
        or .event == "blocked"
        or .event == "timeout") | not)
    ))
  | .[]
' \
  .statamcp/audit/stata_do.jsonl \
  .statamcp/audit/get_data_info.jsonl \
  .statamcp/audit/read_log.jsonl \
  .statamcp/audit/help.jsonl
```

For each result, search snapshot metadata, Stata logs, checkpoints, traces, and
process logs for the same `run_id` before drawing a conclusion.

## 6. Cross-Platform Python Fallback

Use this when jq is unavailable. Save it outside `.statamcp/` as
`find_audit_run.py`:

```python
from __future__ import annotations

import json
import sys
from pathlib import Path

artifact_root = Path(sys.argv[1])
run_id = sys.argv[2]
patterns = (
    "audit/*.jsonl",
    "snapshot/metadata.jsonl",
    "debug/*.jsonl*",
)

matches: list[dict[str, object]] = []
for pattern in patterns:
    for audit_file in artifact_root.glob(pattern):
        with audit_file.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("run_id") == run_id:
                    matches.append(
                        {
                            "file": audit_file.as_posix(),
                            "line": line_number,
                            "record": record,
                        }
                    )

print(json.dumps(matches, ensure_ascii=False, indent=2))
```

Run it with:

=== "macOS / Linux"

    ```bash
    python3 find_audit_run.py .statamcp 20260830T083015123456Z_2ce5d65f457ce14a
    ```

=== "Windows"

    ```powershell
    py find_audit_run.py .statamcp 20260830T083015123456Z_2ce5d65f457ce14a
    ```

The script reads source files and prints a derived view. It does not rewrite the
evidence. When an archived artifact directory has moved, snapshot metadata can
retain its historical absolute path; relocate the object by its full `sha256`
under the archived `snapshot/objects/` directory and record that relocation in
the derived report.

## Investigation Checklist

- Confirm the artifact root and tool ledger.
- Preserve the exact `run_id`; do not join records by filename alone.
- Pair lifecycle events and read `executed`.
- Follow security IDs and snapshot metadata when present.
- Verify do-file hashes before treating an object as exact source evidence.
- Use debug records for stage diagnosis, not as durable evidence.
- Record missing files, malformed lines, or unmatched events as limitations in
  the final report.

See [Events and Correlation](events.md) for field definitions and
[Snapshots and Security Linkage](snapshots-security.md) for integrity checks.

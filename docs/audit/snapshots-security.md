# Snapshots and Security Linkage

`stata_do` has an additional evidence contract: before Stata starts,
MCP-for-Stata reads the source do-file bytes, stores a full-SHA-256 object, and
asks Stata to execute that snapshot. Later edits to the original path therefore
cannot change what the recorded run executed.

## Snapshot Layout

```text
.statamcp/snapshot/
├── objects/
│   └── <64-character-sha256>.do
└── metadata.jsonl
```

The object filename is the complete lowercase SHA-256 digest. It is not a
timestamped copy. Identical content from different paths or invocations reuses
the same object while every invocation gets its own metadata record.

## Snapshot Metadata

Each `metadata.jsonl` record contains:

| Field | Meaning |
| --- | --- |
| `schema_version` | Snapshot metadata schema version; currently `1`. |
| `run_id` | Tool invocation that created or reused this object. |
| `tool` | Normally `stata_do`. |
| `created_at` | UTC start time copied from the run. |
| `original_path` | Resolved source path at snapshot time. |
| `original_name` | Source basename. |
| `snapshot_path` | Absolute path of the content-addressed object. |
| `sha256` | Complete digest of the stored bytes. |
| `sha256_prefix` | First eight characters for display only. |
| `size_bytes` | Exact source byte length. |
| `reused` | Whether an identical verified object already existed. |

The terminal `stata_do` event also places `snapshot_path`, `snapshot_sha256`,
and `snapshot_reused` in `artifacts` when snapshotting succeeded.

## Verify a Snapshot

Choose the metadata record by exact `run_id`, not by original filename alone.

=== "macOS"

    ```bash
    RUN_ID='20260830T083015123456Z_2ce5d65f457ce14a'
    RECORD=$(jq -c --arg run_id "$RUN_ID" \
      'select(.run_id == $run_id)' .statamcp/snapshot/metadata.jsonl)
    EXPECTED=$(printf '%s\n' "$RECORD" | jq -r '.sha256')
    SNAPSHOT=$(printf '%s\n' "$RECORD" | jq -r '.snapshot_path')
    [ -f "$SNAPSHOT" ] || SNAPSHOT=".statamcp/snapshot/objects/$EXPECTED.do"

    printf '%s  %s\n' "$EXPECTED" "$SNAPSHOT" | shasum -a 256 -c -
    ```

=== "Linux"

    ```bash
    RUN_ID='20260830T083015123456Z_2ce5d65f457ce14a'
    RECORD=$(jq -c --arg run_id "$RUN_ID" \
      'select(.run_id == $run_id)' .statamcp/snapshot/metadata.jsonl)
    EXPECTED=$(printf '%s\n' "$RECORD" | jq -r '.sha256')
    SNAPSHOT=$(printf '%s\n' "$RECORD" | jq -r '.snapshot_path')
    [ -f "$SNAPSHOT" ] || SNAPSHOT=".statamcp/snapshot/objects/$EXPECTED.do"

    printf '%s  %s\n' "$EXPECTED" "$SNAPSHOT" | sha256sum -c -
    ```

=== "Windows PowerShell"

    ```powershell
    $RunId = '20260830T083015123456Z_2ce5d65f457ce14a'
    $Record = Get-Content .statamcp\snapshot\metadata.jsonl |
      ForEach-Object { $_ | ConvertFrom-Json } |
      Where-Object { $_.run_id -eq $RunId } |
      Select-Object -Last 1

    $Snapshot = $Record.snapshot_path
    if (-not (Test-Path $Snapshot)) {
      $Snapshot = ".statamcp\snapshot\objects\$($Record.sha256).do"
    }
    $Actual = (Get-FileHash $Snapshot -Algorithm SHA256).Hash.ToLower()
    if ($Actual -ne $Record.sha256) { throw 'Snapshot SHA-256 mismatch' }
    ```

A successful hash check proves that the current object bytes match the recorded
digest. It does not prove who authored the source or whether its commands were
scientifically valid.

`snapshot_path` is an absolute path recorded at execution time. If a complete
artifact bundle is later moved, the fallback above locates the object by its
full hash inside the archived bundle. Record the relocation in any derived
report; never rewrite the historical metadata just to update its path.

If an existing object has the expected filename but different bytes,
MCP-for-Stata raises an error rather than overwriting or reusing it.

## When a Snapshot Can Be Missing

A security decision can block `stata_do` before snapshot creation. For example,
a rejected source path or dangerous-command finding can produce a valid
`blocked` tool event and security record without snapshot metadata. Do not
interpret that expected absence as snapshot loss.

For a run recorded as executed, missing or invalid snapshot evidence requires
investigation. Check terminal artifacts, the Stata log, process logs, and any
storage errors.

## Security Ledger

Security decisions are written to `.statamcp/audit/security.jsonl` and linked
to the terminal tool event.

| Field | Meaning |
| --- | --- |
| `security_event_id` | Unique ID in the form `sec_<run_id>_<sequence>`. |
| `run_id` | Parent tool invocation. |
| `timestamp` | UTC decision time. |
| `tool` | Tool under review. |
| `decision` | `blocked` or `warning`. |
| `stage` | Security stage that made the decision. |
| `risk_type` | Stable risk category. |
| `executed` | Whether execution proceeded after this decision. |
| `findings` | Safe identifiers and locations: `line`, `type`, and `rule_id`. |
| `source_path` | Optional source reference after redaction. |
| `source_sha256` | Optional digest of reviewed source bytes. |

Dangerous source content is deliberately omitted from `findings`.

## Follow a Blocked Call

1. Find the terminal tool event where `event` is `blocked` and `executed` is
   `false`.
2. Copy every value in `security_event_ids`.
3. Match each value to `security_event_id` in `security.jsonl`.
4. Confirm matching `run_id` and `tool` values.
5. Report `stage`, `risk_type`, safe finding locations, and whether a snapshot
   exists. Do not reconstruct or quote dangerous commands from other files
   unless the user explicitly asks to inspect the source.

```bash
SECURITY_ID='sec_20260830T083015123456Z_2ce5d65f457ce14a_01'
jq -c --arg security_id "$SECURITY_ID" \
  'select(.security_event_id == $security_id)' \
  .statamcp/audit/security.jsonl
```

`stata_do`, `get_data_info`, and `read_log` all use this cross-ledger pattern
for supported path, URL, package, or command guard rejections.

## Persistence and Failure Semantics

- The initial tool event is persisted before the tool handler runs. If it
  cannot be written, the audited call does not proceed normally.
- `stata_do` creates and verifies the snapshot before starting Stata. Snapshot
  persistence failure prevents that Stata launch.
- A missing terminal event still requires investigation because execution may
  have progressed before terminal persistence failed.
- Debug checkpoint and trace writes are fail-open. They never replace the
  durable Audit contract and cannot block the tool result.

## Privacy and Retention

Credential-like keys are replaced with `[REDACTED]`; URL credentials, queries,
and fragments are removed. Audit evidence can still reveal local paths,
filenames, variable selections, client claims, error messages, and timing.

Audit v1 has no automatic retention, rotation, archival, replay, or recovery
policy. Back up or remove evidence only under an explicit project data policy;
never treat debug rotation settings as Audit retention settings.

See [Events and Correlation](events.md) for lifecycle fields and
[Security Guard](../security.md) for prevention policy.

# Audit Trail

MCP-for-Stata keeps local, append-only evidence for MCP tool calls. The Audit
trail is designed to answer five practical questions:

1. Which tool was requested, and when?
2. Which client and MCP protocol version were reported?
3. Did the call complete, fail, stop, or get blocked before execution?
4. Which security decision, output metadata, log, or do-file snapshot belongs
   to the call?
5. Where did a slow or stuck call last make progress?

Audit v1 covers the first four questions. The rotating local debug recorder
answers the fifth. Both use the same `run_id` when they belong to the same MCP
call, but they have different retention and trust rules.

## Evidence Layout

Files live under the configured project artifact directory, `.statamcp/` by
default:

```text
.statamcp/
├── audit/
│   ├── stata_do.jsonl
│   ├── get_data_info.jsonl
│   ├── read_log.jsonl
│   ├── help.jsonl
│   └── security.jsonl
├── snapshot/
│   ├── objects/<full-sha256>.do
│   └── metadata.jsonl
└── debug/
    ├── checkpoints.jsonl
    ├── checkpoints.jsonl.1
    ├── traces.jsonl
    └── traces.jsonl.1
```

The per-tool files, security ledger, and snapshot metadata are durable Audit
evidence. Debug files rotate by size and are operational diagnostics, not a
replacement for the evidence trail.

## Read One Run in Five Minutes

1. Start with the tool ledger that matches the call, for example
   `audit/stata_do.jsonl`.
2. Find its `run_id` and pair the `started` event with its terminal event.
3. Read the terminal `event` and `executed` fields before interpreting output
   metadata.
4. Follow `security_event_ids` into `audit/security.jsonl` when the call was
   blocked or warned.
5. For `stata_do`, use the same `run_id` in `snapshot/metadata.jsonl` to locate
   and verify the exact bytes Stata was asked to execute.
6. If a call is slow or incomplete, search the rotating debug files for the
   same `run_id` and locate the last unmatched `started` checkpoint.

See [Reading Audit Files](audit/reading.md) for read-only commands and worked
queries.

## Evidence Types

| Evidence | Primary question | Retention behavior |
| --- | --- | --- |
| Per-tool JSONL | What was requested and how did it end? | Append-only; no automatic Audit v1 retention policy |
| `security.jsonl` | Which guard decided what, and why? | Append-only |
| `snapshot/metadata.jsonl` | Which source path and full hash belong to a run? | Append-only |
| `snapshot/objects/` | What exact do-file bytes were executed? | Content-addressed and reused by full SHA-256 |
| `debug/checkpoints.jsonl*` | What was the last observed execution stage? | Rotating |
| `debug/traces.jsonl*` | Which spans ran, for how long, under which trace? | Rotating |

## Lifecycle

Each tool call normally produces one `started` event and exactly one terminal
event sharing the same `run_id`:

```text
started -> completed | failed | interrupted | blocked
```

The storage model also accepts `timeout`, but the current middleware does not
classify timeouts separately. An uncategorized timeout exception is recorded as
`failed`.

A `started` event without a terminal event is not proof that the tool never
executed. It indicates an incomplete evidence sequence that must be correlated
with snapshots, logs, debug checkpoints, and the surrounding process failure.

## Trust Boundaries

- Client name and version are self-reported. They help investigation but are
  not authentication or authorization evidence.
- `event` together with `executed` is authoritative for a security outcome.
  `output.is_error` only describes the MCP result representation.
- Credential-like input keys are replaced with `[REDACTED]`; URL credentials,
  queries, and fragments are removed. Local paths, selected variables, tool
  names, and error metadata can still be sensitive.
- Treat the complete `.statamcp/` directory as potentially sensitive and keep
  it out of Git. MCP-for-Stata creates a local `.gitignore` for the artifact
  root by default.

## Continue Reading

- [Reading Audit Files](audit/reading.md): locate files and answer common audit
  questions without modifying evidence.
- [Events and Correlation](audit/events.md): field meanings, lifecycle
  invariants, `run_id`, request metadata, traces, and checkpoints.
- [Snapshots and Security Linkage](audit/snapshots-security.md): full-hash
  do-file evidence, verification, blocked calls, and privacy boundaries.
- [Local Debug Tracing](debug-tracing.md): rotating OpenTelemetry spans,
  checkpoints, and slow-call thread snapshots.
- [Security Guard](security.md): prevention policy and guard configuration.

## Audit v1 Non-Goals

Audit v1 does not provide snapshot replay or recovery, automatic retention or
archival, verified client identity, or a standalone timeout class. Any future
replay must be explicitly requested, verify the source hash, create a new
`run_id`, and preserve the original evidence rather than rewriting it.

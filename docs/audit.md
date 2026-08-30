# Audit Trail

MCP-for-Stata writes a local, append-only audit trail for MCP tool calls. The
audit trail answers who called which tool, when it ran, which MCP protocol was
used, and whether the call completed or failed.

## Files

Audit files live under the configured project artifact directory, which is
`.statamcp/` by default:

```text
.statamcp/
├── audit/
│   ├── stata_do.jsonl
│   ├── get_data_info.jsonl
│   ├── read_log.jsonl
│   ├── help.jsonl
│   └── security.jsonl
└── snapshot/
    ├── objects/<full-sha256>.do
    └── metadata.jsonl
```

Each JSONL line is one immutable event. A tool call normally produces a
`started` event and one terminal event: `completed`, `failed`, `interrupted`,
or `blocked`. Both events share the same `run_id`. A dedicated `timeout` event
is reserved for future work and is not emitted by the current middleware.

## Run IDs

A run ID contains a readable UTC timestamp followed by a collision-resistant
digest:

```text
20260830T083015123456Z_2ce5d65f457ce14a
```

The timestamp can be recovered directly from the ID. The digest also includes
the high-resolution invocation time, tool name, source reference, and random
entropy.

## Client Identity

For MCP calls, the `started` event records the client implementation reported
by the client, the negotiated protocol version, and the request ID. Modern
2026-era requests and legacy initialize-era clients are both supported.

Client identity is self-reported and unverified. It is useful for audit and
debugging, but must never be used as authentication or authorization evidence.

## Do-file Snapshots

Before Stata starts, MCP-for-Stata stores the exact bytes that will be executed.
The snapshot metadata includes the original path, snapshot path, complete
SHA-256 digest, size, reuse state, and the shared run ID. Stata executes the
snapshot rather than the mutable source path.

Identical content always reuses one content-addressed snapshot file, regardless
of invocation time or original filename. Every invocation still gets its own
metadata record and run ID.

## Security Linkage

When a `stata_do` call is blocked by the path boundary, package-management
guard, or command guard, its terminal tool event is `blocked` rather than
`completed`. The event includes `executed: false` and one or more
`security_event_ids`.

The matching records in `audit/security.jsonl` contain the same run ID, the
security stage, decision, risk type, source SHA-256 when available, and finding
locations. Dangerous command content is never persisted in the security
ledger. This makes the tool lifecycle and the detailed security decision
independently readable while preserving a direct cross-ledger link.

`get_data_info` uses the same linkage when a strict local-path boundary or URL
guard rejects a data source. URL credentials, query strings, and fragments are
removed before persistence.

`read_log` also uses this linkage when its local-path boundary rejects a log
outside the configured allowed directories.

The terminal `event` and `executed` fields are the authoritative security
outcome. `output.is_error` only reports whether the MCP result itself was
represented as an error. A guard can return a normal MCP result while still
recording `event: "blocked"` and `executed: false`; security monitoring must
therefore select blocked events rather than relying on `output.is_error`.

## Sensitive Data

Credential-like argument keys such as `password`, `secret`, `token`,
`authorization`, and `api_key` are recursively replaced with `[REDACTED]`.
Audit files can still contain local paths, variable selections, tool names,
errors, and result metadata. Treat the entire `.statamcp/` directory as
potentially sensitive.

The directory is ignored by Git by default. No automatic audit-retention policy
is applied in the initial implementation.

## Audit vs. OpenTelemetry

The JSONL audit trail is durable research evidence. OpenTelemetry is a
candidate for debugging and performance traces, but this release does not
configure a collector or exporter and does not promise persistent traces.
Future OpenTelemetry work must remain optional and must not replace the JSONL
evidence trail.

## Deferred Work

The following items are intentionally outside Audit v1 and require a separate
design decision before implementation:

- Optional OpenTelemetry traces for debugging and performance diagnosis,
  including a safe correlation mechanism between trace/span IDs and `run_id`.
- Explicit timeout classification and tests. The current middleware records an
  uncategorized timeout exception as `failed`.
- Recovery or replay from a snapshot. Any future replay must be explicitly
  requested, verify the snapshot hash, create a new run ID, and preserve the
  original run rather than modifying its audit records.
- Audit retention, rotation, and archival policy.

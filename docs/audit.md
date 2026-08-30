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
│   └── help.jsonl
└── snapshot/
    ├── YYYYMMDDHHMM<sha256-prefix>_<dofile-name>.do
    └── metadata.jsonl
```

Each JSONL line is one immutable event. A tool call normally produces a
`started` event and one terminal event such as `completed`, `failed`,
`timeout`, or `interrupted`. Both events share the same `run_id`.

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

Repeated identical content within the same minute can reuse one snapshot file;
every invocation still gets its own metadata record and run ID.

## Sensitive Data

Credential-like argument keys such as `password`, `secret`, `token`,
`authorization`, and `api_key` are recursively replaced with `[REDACTED]`.
Audit files can still contain local paths, variable selections, tool names,
errors, and result metadata. Treat the entire `.statamcp/` directory as
potentially sensitive.

The directory is ignored by Git by default. No automatic audit-retention policy
is applied in the initial implementation.

## Audit vs. OpenTelemetry

The JSONL audit trail is durable research evidence. OpenTelemetry is the MCP 2
debugging and performance trace. OpenTelemetry can explain where time was spent;
the JSONL files preserve what was invoked and which artifacts were produced.

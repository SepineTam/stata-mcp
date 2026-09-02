# Events and Correlation

Audit v1 uses newline-delimited JSON. Each line is one event with
`schema_version: 1`; existing lines are never updated when a call progresses.

## Tool Lifecycle

For each MCP `tools/call` request, `AuditMiddleware` writes:

```text
one started event -> one terminal event
```

Both records use the same `run_id` and live in
`.statamcp/audit/<tool>.jsonl`.

| Terminal event | Meaning |
| --- | --- |
| `completed` | The tool returned a result that was not represented as an MCP error. |
| `failed` | The handler raised an exception, returned an error result, or encountered an unclassified timeout. |
| `interrupted` | Execution propagated `KeyboardInterrupt`. |
| `blocked` | A linked security decision refused execution. Read `executed` and `security_event_ids`. |
| `timeout` | Reserved by the storage model; current middleware does not emit it as a separate class. |

## Common Fields

Every tool lifecycle event contains:

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | integer | Event schema version; currently `1`. |
| `run_id` | string | Unique invocation ID with a recoverable UTC start time. |
| `event` | string | `started` or one terminal event. |
| `tool` | string | MCP tool name and ledger filename stem. |
| `timestamp` | string | UTC ISO 8601 time for this event. |

## Started-Only Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `interface` | yes | Invocation surface; MCP middleware records `mcp`. |
| `source_reference` | yes | First recognized source argument (`dofile_path`, `data_path`, or `file_path`), otherwise the tool name. |
| `input` | yes | JSON-safe, recursively redacted tool arguments. |
| `client` | no | Self-reported MCP client implementation. |
| `protocol_version` | no | Negotiated MCP protocol version when available. |
| `request_id` | no | MCP request ID converted to text. |

Synthetic example:

```json
{
  "schema_version": 1,
  "run_id": "20260830T083015123456Z_2ce5d65f457ce14a",
  "event": "started",
  "tool": "stata_do",
  "timestamp": "2026-08-30T08:30:15.123456+00:00",
  "interface": "mcp",
  "source_reference": "/project/analysis.do",
  "input": {"dofile_path": "/project/analysis.do"},
  "client": {"name": "example-client", "version": "1.0"},
  "protocol_version": "2026-07-28",
  "request_id": "42"
}
```

Client metadata is descriptive only. A client can report any name or version;
do not treat these fields as verified identity.

## Terminal-Only Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `duration_ms` | yes | Wall-clock duration from run creation to terminal persistence. |
| `artifacts` | no | Tool-produced references such as snapshot path, SHA-256, reuse state, or Stata log paths. |
| `output` | no | Result metadata; middleware currently records `is_error`. |
| `error` | no | Exception type and message when execution raised. |
| `security_event_ids` | no | IDs that join to `audit/security.jsonl`. |
| `executed` | no | Whether execution passed the security decision; middleware tool events normally include it. |

Synthetic blocked example:

```json
{
  "schema_version": 1,
  "run_id": "20260830T083015123456Z_2ce5d65f457ce14a",
  "event": "blocked",
  "tool": "stata_do",
  "timestamp": "2026-08-30T08:30:15.140000+00:00",
  "duration_ms": 16.544,
  "output": {"is_error": false},
  "security_event_ids": [
    "sec_20260830T083015123456Z_2ce5d65f457ce14a_01"
  ],
  "executed": false
}
```

This call was blocked even though `output.is_error` is `false`.

## Run ID

The format is:

```text
YYYYMMDDTHHMMSSffffffZ_<16 lowercase hex characters>
```

Example:

```text
20260830T083015123456Z_2ce5d65f457ce14a
```

The prefix directly encodes the UTC invocation time with microsecond precision.
The digest also incorporates nanosecond time, tool name, source reference, and
random entropy. It prevents practical collisions; it is not a signature and
does not authenticate the caller or source.

## Correlation Map

| Start from | Join key | Continue to | Purpose |
| --- | --- | --- | --- |
| Tool ledger | `run_id` | Same tool ledger | Pair lifecycle events. |
| Tool terminal event | `security_event_ids[]` | `security.security_event_id` | Read the exact guard decisions linked to the call. |
| Tool event | `run_id` | `security.run_id` | Find all security decisions for the run. |
| `stata_do` event | `run_id` | `snapshot/metadata.jsonl` | Locate original path, object path, hash, size, and reuse state. |
| Tool event | `run_id` | `debug/checkpoints.jsonl*` | Find immediate execution stages. |
| Tool event | `run_id` or trace attribute `statamcp.run_id` | `debug/traces.jsonl*` | Find completed spans and duration hierarchy. |
| Checkpoint | `trace_id` and `span_id` | Trace record | Connect an immediate stage event to its completed span. |

`request_id` can help compare MCP transport logs, but `run_id` is the primary
MCP-for-Stata correlation key.

## Ordering and Completeness

Writes to one JSONL file are serialized within the process. There is no single
global file that orders tool, security, snapshot, checkpoint, and trace
records. For a cross-file timeline:

1. Select one `run_id`.
2. Normalize and sort available UTC timestamps.
3. Keep file and line provenance in any derived report.
4. Mark absent terminal events, missing linked IDs, malformed JSON, or rotated
   debug records as evidence limitations.

Debug rotation can legitimately remove older checkpoints and traces. Missing
durable tool, security, or snapshot evidence requires separate investigation.

## Schema Evolution

Readers should reject or explicitly flag unsupported `schema_version` values
rather than silently treating them as v1. New optional fields may appear within
a schema version; readers should ignore unknown fields while preserving them in
derived output.

See [Reading Audit Files](reading.md) for queries and
[Snapshots and Security Linkage](snapshots-security.md) for integrity rules.

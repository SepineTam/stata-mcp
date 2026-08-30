# Local Debug Tracing

MCP-for-Stata keeps a default-on local flight recorder for `get_data_info` and
`stata_do`. It records non-blocking checkpoints around important code stages so
a slow or stuck call can be located after the fact.

Debug traces are operational diagnostics, not durable audit evidence. They live
under the project artifact directory and rotate automatically:

```text
.statamcp/debug/
├── checkpoints.jsonl
├── checkpoints.jsonl.1
├── traces.jsonl
└── traces.jsonl.1
```

`checkpoints.jsonl` is written immediately when a step starts, completes, or
fails. `traces.jsonl` contains completed OpenTelemetry spans with trace and span
IDs, durations, status, and the matching Audit `run_id` when available.

## Recorded Stages

`get_data_info` records the MCP wrapper, lazy import, runtime configuration,
path validation, handler initialization, DataFrame reads, summary generation,
the full information pipeline, and JSON serialization.

`stata_do` records request/security preparation, input validation, exact-source
snapshotting, Stata process execution, audit finalization, and result formatting.
Synchronous and asynchronous execution paths use the same stage names.

## Slow Calls

If either target tool is still running after 30 seconds, the flight recorder
writes the file name, line number, and function name for every Python thread. It
writes a second snapshot after 120 seconds. These snapshots do not pause,
cancel, or terminate the tool.

The last unmatched `started` checkpoint identifies the stage that did not
return. If all tool and serialization stages completed but the client still
waits, the remaining problem is likely in outbound transport or the client.

## Configuration

Local tracing is enabled by default. Remote OTLP export is not configured and
no trace data is sent over the network.

```toml
[DEBUG.tracing]
ENABLED = true
MAX_BYTES = 10485760
BACKUP_COUNT = 3
```

Set `ENABLED = false` to disable both local checkpoint/span files and the slow
call watchdog. The equivalent environment variables are:

```bash
export STATA_MCP__DEBUG_TRACING_ON=false
export STATA_MCP__DEBUG_TRACING_MAX_BYTES=10485760
export STATA_MCP__DEBUG_TRACING_BACKUP_COUNT=3
```

Each active file is limited independently. With the defaults, checkpoints and
traces can each retain one active file plus three backups.

## Privacy and Failure Behavior

The recorder stores stage names, timing, exception types, hashed source
references, platform metadata, thread locations, and correlation IDs. It does
not intentionally store dataset contents, variable values, do-file source, URL
queries, credentials, or exception messages.

Diagnostic write/export failures are fail-open: the tool and durable Audit v1
trail continue even when debug data cannot be persisted. Debug files rotate and
may be deleted; Audit JSONL and do-file snapshots follow their separate durable
evidence rules.

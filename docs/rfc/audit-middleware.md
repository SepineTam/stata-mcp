# MCP v2 Audit Middleware Decision

## Decision

MCP-for-Stata uses MCPServer middleware for generic `tools/call` lifecycle
auditing, an AuditStore for local append-only persistence, and tool-specific
artifact hooks for Stata do-file snapshots.

## Architecture

```text
MCP client
  -> MCPServer OpenTelemetry middleware
  -> AuditMiddleware
  -> tool handler
  -> StataDo snapshot hook when applicable
```

AuditMiddleware owns run IDs, client and protocol metadata, redacted arguments,
timing, and terminal status. StataDo owns exact source snapshots, hashes, and log
artifacts. A ContextVar carries one AuditExecutionContext through concurrent and
worker-thread execution so both layers write the same run ID.

## Alternatives

- Per-tool wrappers were rejected because every new tool would duplicate audit
  lifecycle code.
- Snapshot creation inside middleware was rejected because it would couple raw
  protocol rewriting to Stata-specific path and security behavior.
- OpenTelemetry-only auditing was rejected because traces are operational data,
  not durable, human-inspectable research evidence.

## Failure Behavior

If the initial audit event or snapshot cannot be persisted, execution fails
closed. If the terminal event cannot be persisted after a tool runs, the caller
receives the audit failure; existing artifacts remain on disk for diagnosis.

## Security

Client identity is self-reported and never authorizes access. Credential-like
argument keys are redacted recursively. Audit paths remain under the configured
project artifact root and are ignored by Git.

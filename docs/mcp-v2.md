# MCP Python SDK v2

MCP-for-Stata now uses the stable MCP Python SDK 2.x server architecture. This
is an SDK and protocol migration; it does not by itself change the Python
package version to 2.0.

## What Changed

- The high-level server class moved from `FastMCP` to `MCPServer`.
- The primary server implementation now lives in `src/stata_mcp/mcp_servers.py`.
- MCP v2 middleware wraps tool calls for durable Audit v1 records and local
  OpenTelemetry diagnostics.
- The compatibility workflow tests the real stdio server on Linux, macOS, and
  Windows with Python 3.11, 3.12, and 3.13.

The MCP concepts remain the same: servers can still expose tools, resources,
and prompts. Existing MCP-for-Stata tool names and input/output schemas remain
stable unless a feature-specific changelog entry says otherwise.

## Protocol Compatibility

The server accepts both:

- Modern MCP `2026-07-28` negotiation.
- Legacy initialize-era `2025-11-25` clients.

MCP clients can therefore upgrade independently instead of requiring every
user to replace their client and server at the same time.

## Request Pipeline

```text
MCP client
  -> MCPServer built-in OpenTelemetry span
  -> AuditMiddleware
  -> security and tool handler
  -> tool-specific artifacts
```

`AuditMiddleware` assigns the readable `run_id`, records client/protocol
metadata, and writes terminal status. `stata_do` additionally stores the exact
bytes executed by Stata as a full-SHA-256 content-addressed snapshot. Security
rejections link the tool ledger to `audit/security.jsonl` through
`security_event_ids`.

See [Audit Trail](audit.md) for durable evidence and
[Local Debug Tracing](debug-tracing.md) for rotating operational diagnostics.

## Compatibility Boundaries

- Client identity is self-reported and must not be used as authentication.
- Local OpenTelemetry files are enabled by default, stay on the user's machine,
  and can be disabled in `[DEBUG.tracing]`.
- `get_data_info` remains beta-gated on Windows by default while the historical
  client-specific hang is investigated. Cross-platform CI exercises the
  explicit opt-in path.
- Middleware is used for observation and refusal; exact Stata snapshot creation
  remains in the Stata execution layer.

## Verification

The dedicated workflow verifies:

```text
3 operating systems x 3 Python versions x modern/legacy protocol calls
```

It also runs the full pytest suite on Ubuntu and checks that `get_data_info`
returns its structured result together with matching Audit and trace records.

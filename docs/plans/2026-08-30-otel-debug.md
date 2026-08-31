# Local Debug Flight Recorder Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add default-on, local-only debug checkpoints and OpenTelemetry spans
for `get_data_info` and `stata_do` so a post-hang report shows the last
completed stage and correlates it with the durable audit run.

**Architecture:** A fail-open debug runtime writes immediate rotating JSONL
checkpoints under `.statamcp/debug/`. A reusable `debug_step` context manager
also creates child OpenTelemetry spans. MCP startup configures a local span
exporter, while AuditMiddleware attaches its `run_id` to the active MCP span.
Remote OTLP export remains disabled.

**Tech Stack:** Python 3.11+, MCP Python SDK 2.x middleware, OpenTelemetry API
and SDK, `contextvars`, standard-library JSON and rotating file handlers,
pytest, GitHub Actions.

---

### Task 1: Add the fail-open checkpoint foundation

**Files:**

- Create: `src/stata_mcp/observability/__init__.py`
- Create: `src/stata_mcp/observability/checkpoints.py`
- Create: `src/stata_mcp/observability/steps.py`
- Test: `tests/observability/test_checkpoints.py`
- Test: `tests/observability/test_steps.py`

**Steps:**

1. Write failing tests for `started`, `completed`, and `failed` checkpoint pairs.
2. Verify tests fail because the observability package does not exist.
3. Implement a rotating JSONL writer with a lock and explicit UTF-8 flushing.
4. Make writer failures return safely without changing the wrapped operation.
5. Implement `debug_step` with monotonic duration and exception-type metadata.
6. Run `uv run pytest tests/observability -q` and expect all tests to pass.
7. Commit as `feat(debug): add local diagnostic checkpoints` and push.

### Task 2: Instrument `get_data_info`

**Files:**

- Modify: `src/stata_mcp/mcp_servers.py`
- Modify: `src/stata_mcp/api/get_data_info.py`
- Modify: `src/stata_mcp/data_info/base.py`
- Test: `tests/api/test_get_data_info_logging.py`
- Test: `tests/api/test_get_data_info_mcp_stdio.py`

**Steps:**

1. Write failing tests that require named checkpoints for lazy import, runtime,
   path validation, handler setup, DataFrame read, summary, and serialization.
2. Verify the test fails on the first missing checkpoint.
3. Wrap the existing operations with `debug_step` without changing their return
   values or current diagnostic logs.
4. Assert raw paths, variable names, values, and exception messages are absent.
5. Run focused data-info and stdio tests.
6. Commit as `feat(debug): trace get_data_info stages`, push, and verify CI.

### Task 3: Instrument `stata_do`

**Files:**

- Modify: `src/stata_mcp/mcp_servers.py`
- Modify: `src/stata_mcp/stata/stata_do/do.py`
- Modify: `src/stata_mcp/stata/stata_do/async_do.py`
- Test: `tests/stata/test_do_debug_trace.py`

**Steps:**

1. Write failing tests for validation, security, snapshot, Stata execution, and
   result-formatting checkpoints.
2. Verify normal, blocked, failed, and timeout paths preserve existing results.
3. Instrument synchronous execution and the native asynchronous subprocess path.
4. Verify copied `ContextVar` state preserves the same run ID in worker threads.
5. Run focused Stata boundary, audit, and new debug tests.
6. Commit as `feat(debug): trace stata_do stages`, push, and verify CI.

### Task 4: Configure local OpenTelemetry export and Audit correlation

**Files:**

- Modify: `pyproject.toml`
- Create: `src/stata_mcp/observability/exporter.py`
- Create: `src/stata_mcp/observability/setup.py`
- Modify: `src/stata_mcp/cli/_handlers.py`
- Modify: `src/stata_mcp/audit/middleware.py`
- Test: `tests/observability/test_exporter.py`
- Test: `tests/audit/test_middleware.py`

**Steps:**

1. Write failing tests for local span JSONL, trace/span IDs, and `run_id`.
2. Add a bounded OpenTelemetry SDK dependency.
3. Implement a local JSONL `SpanExporter` using a simple processor so completed
   spans are flushed immediately rather than waiting in a batch.
4. Configure tracing only from MCP server startup; do not configure global
   tracing when the package is imported as a library.
5. Add `statamcp.run_id` to the SDK-created current MCP span.
6. Verify exporter failures do not alter tool responses and stdout stays clean.
7. Commit as `feat(debug): export local OpenTelemetry traces` and push.

### Task 5: Add the slow-call watchdog

**Files:**

- Modify: `src/stata_mcp/_diagnostic_logging.py`
- Modify: `src/stata_mcp/audit/middleware.py`
- Test: `tests/test_diagnostic_logging.py`
- Test: `tests/audit/test_middleware.py`

**Steps:**

1. Write failing tests for 30-second and 120-second privacy-safe snapshots.
2. Generalize the watchdog to both target tools and attach tool/run identifiers.
3. Start it by default for `get_data_info` and `stata_do` MCP calls.
4. Cancel it after terminal audit persistence and ensure timer threads are daemonized.
5. Verify only file names, line numbers, and function names are recorded.
6. Commit as `feat(debug): capture slow tool stack checkpoints` and push.

### Task 6: Configuration, documentation, and cross-platform acceptance

**Files:**

- Modify: `src/stata_mcp/config.py`
- Modify: `docs/audit.md`
- Modify: `docs/audit.zh.md`
- Create: `docs/debug-tracing.md`
- Create: `docs/debug-tracing.zh.md`
- Modify: `.github/workflows/mcp-v2-compat.yml`

**Steps:**

1. Add default-on local diagnostics, rotation, and watchdog configuration.
2. Document that debug records rotate and are not durable audit evidence.
3. Add Windows stdio acceptance assertions for trace/checkpoint creation.
4. Run observability, audit, data-info, and Stata tests.
5. Run `uv run mkdocs build --strict` and repository static checks.
6. Push and wait for Linux/macOS/Windows CI completion.
7. Commit as `docs(debug): document local flight recorder` and push.

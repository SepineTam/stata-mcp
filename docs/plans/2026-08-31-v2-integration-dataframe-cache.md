# MCP v2 Integration and DataFrame Reuse Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate committed master documentation into MCP v2, document the
new protocol/audit/debug architecture, merge the verified integration to
master, and then make each `get_data_info` instance parse its source into a
DataFrame only once.

**Architecture:** Preserve the dirty master checkout and perform integration in
clean worktrees. After v2 reaches remote master, create a dedicated optimization
branch. Cache the format-specific `_read_data()` result per `DataInfoBase`
instance while keeping the existing source-byte and serialized-summary caches
unchanged.

**Tech Stack:** Python 3.11–3.13, pandas, MCP Python SDK 2.x, OpenTelemetry,
pytest, MkDocs, Git worktrees, GitHub Actions.

---

### Task 1: Integrate committed master changes into MCP v2

**Files:** Git history only.

1. Confirm local master has exactly two committed changes after v1.23.1.
2. Confirm its uncommitted Audit prototype and unrelated local artifacts remain
   outside Git history.
3. Merge `master` into `codex/update-mcp-to-v2` with a merge commit.
4. Build wheel/sdist and strict bilingual documentation.
5. Push and require the full Ubuntu suite plus Linux/macOS/Windows protocol CI.

### Task 2: Complete release-facing v2 documentation

**Files:**

- Create: `docs/mcp-v2.md`
- Create: `docs/mcp-v2.zh.md`
- Modify: `docs/overview.md`
- Modify: `docs/overview.zh.md`
- Modify: `CHANGELOG.md`
- Modify: `mkdocs.yml`

1. Document `FastMCP` to `MCPServer`, modern and legacy protocol support, and
   unchanged tool/resource/prompt concepts.
2. Document Audit middleware, full-hash snapshots, security linkage, and local
   OpenTelemetry diagnostics.
3. Correct the overview architecture and `.statamcp` tree.
4. Add an Unreleased changelog entry without changing the package version.
5. Run `uv run mkdocs build --strict` and `git diff --check`.
6. Commit as `docs(v2): document migration audit and tracing` and push.

### Task 3: Merge verified v2 into remote master

**Files:** Git history only.

1. Create a temporary clean integration worktree from local committed master.
2. Merge `codex/update-mcp-to-v2` with commit message
   `Merge branch 'codex/update-mcp-to-v2' into master`.
3. Verify the merge tree and push `HEAD:master` only if remote master is still
   the expected ancestor.
4. Require master CI and verify the remote commit graph.
5. Remove the temporary integration worktree; preserve the dirty local master.

### Task 4: Create the DataFrame reuse branch

**Files:** New isolated worktree and this plan.

1. Create `codex/get-data-info-dataframe-cache` from merged `origin/master`.
2. Record a baseline test proving current repeated `_read_data()` calls.
3. Keep this optimization separate from MCP v2 integration history.

### Task 5: Implement one parse per DataInfo instance

**Files:**

- Modify: `src/stata_mcp/data_info/base.py`
- Test: `tests/data_info/test_dataframe_reuse.py`
- Test: `tests/api/test_get_data_info_logging.py`

1. Write failing tests for summary, variable filtering, and preview that expect
   `_read_data()` exactly once.
2. Add minimal per-instance caching at the shared `df` boundary.
3. Verify the cached DataFrame is not persisted across tool calls or source
   instances.
4. Verify errors are not cached as successful values.
5. Run DTA, CSV, Excel, SPSS, cache-hit/miss, head, and variable-filter tests.
6. Commit as `perf(data-info): reuse dataframe within one request` and push.

### Task 6: Cross-platform acceptance

1. Run the full Ubuntu suite.
2. Run modern and legacy MCP stdio calls on Linux, macOS, and Windows with
   Python 3.11, 3.12, and 3.13.
3. Confirm checkpoint output reports one `dataframe_read` pair per call.
4. Report results without merging the optimization branch until separately
   authorized.

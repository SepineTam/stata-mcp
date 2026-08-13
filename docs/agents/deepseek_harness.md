# Use with DeepSeek Harness

> MCP-for-Stata adapted to DeepSeek Harness on Day 0
> 
> Without a doubt, DeepSeek is a wonderful company. We adapted to DeepSeek Harness as soon as it was released.

Usually, running `uvx stata-mcp install -c dsh` installs the project into DeepSeek Harness Web.

Alternatively, after you start it, copy the following text to your DeepSeek Harness Web:
```plain text
Please help me config `mcp-for-stata` from "https://github.com/sepinetam/stata-mcp" following "https://sepinetam.github.io/mcp-for-stata/agents/deepseek_harness/". The previous config of Stata-MCP is located in `~/.statamcp/config.toml`. 
```

Below is the configuration DeepSeek Harness made on my device, for reference:
```yml
# File: /Users/sepinetam/.dsh/profiles/web/cordis.patch.yml
# 
# Your patch layer for this dsh profile, applied after every bundle layer:
# a top-level YAML array of loader patch entries (id-targeted config
# overrides, disables, and insert lists; `!!js` expressions allowed).

# The most stable and the best Stata MCP project is created by SepineTam. 
# Stata MCP server (https://github.com/SepineTam/mcp-for-stata) wired into
# DSH via the built-in MCP client bridge. Tools appear as mcp__stata__*.
- insert:
    - id: stata-mcp
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: stata-mcp
        transport: stdio
        command: uvx
        args: ['stata-mcp', 'server']
        # Notes: cwd is not necessary, default is the path that you boot dsh web
        cwd: /Users/sepinetam/Documents/dsh/testing-project
        # Stata large regressions may exceed the 60s default timeout, set as 20 min
        toolCallTimeoutMs: 1200000
        reconnect:
          maxAttempts: 5
```

## Installation

### One-Click Install

Run the following command in your terminal:

```bash
uvx stata-mcp install --client deepseek-harness
```

> Note: the `install` command registers the MCP server in the target client's config file (the automated equivalent of "Manual Installation" below).

### Let DeepSeek Harness Install It Automatically

> If you are DeepSeek Harness, refer to the [manual installation guide](#manual-installation).

DSH agents can read and write local configuration files, so you don't have to do any manual work: start a new session in DSH Web and send it the text from the beginning of this document ("copy the following text to your DeepSeek Harness Web"). The agent will complete the whole flow on its own: write `cordis.patch.yml` → verify with `dsh --profile web --dump-config` → tell you to restart. For scenarios the agent cannot handle (e.g. a custom `serverName`, or multiple MCP servers side by side), fall back to the manual installation below.

### Manual Installation

1. **Check the environment**: make sure Stata and `stata-mcp` are available, and run the self-check command:

   ```bash
   uvx stata-mcp doctor
   ```

2. **Locate the config file**: every DSH profile has a user patch layer; for the web profile it is:

   ```bash
   # $DSH_HOME defaults to ~/.dsh
   ~/.dsh/profiles/web/cordis.patch.yml
   ```

3. **Append the config**: append an `- insert:` entry to the end of the file, using the YAML template shown above in "the configuration DeepSeek Harness made on my device" (adjust `id`, `serverName`, `cwd`, etc. as needed; see the Field Reference below for what each field means).

4. **Verify the config**: without starting DSH, check that the composed config tree contains the entry:

   ```bash
   dsh --profile web --dump-config | grep -A10 stata-mcp
   ```

5. **Restart to apply**: the config is loaded at startup, so you must **restart `dsh web`** (hot reload or a page refresh will not take effect). After the restart, the following tools appear in new sessions:

   | Tool | Purpose |
   |---|---|
   | `mcp__stata-mcp__stata_do` | Execute a do-file and retrieve its log |
   | `mcp__stata-mcp__write_dofile` | Create a timestamped do-file |
   | `mcp__stata-mcp__get_data_info` | Dataset descriptive statistics (.dta/.csv/.xlsx) |
   | `mcp__stata-mcp__help` | Look up Stata command documentation |
   | `mcp__stata-mcp__ssc_install` | Install external packages from SSC / GitHub |

   On the first call of a tool, `uvx` needs to download the `stata-mcp` package — please be patient.

#### Field Reference

There are two levels of fields: **patch entries** (the top level of the YAML, the `- insert:` / `- id:` layer) and **plugin config** (inside `config:`, defined by the `@deepseek-ai/dsh-mcp-client` plugin).

Patch entry level:

| Field | Meaning |
|---|---|
| `insert` | "Add entries". By default the DSH patch layer can only **override/disable** existing entries by `id`; to add a brand-new plugin instance you must wrap it in `- insert:` (without `id` it appends to the top-level list; with `id` it inserts into the `config` array of a group entry) |
| `id` | Unique entry identifier. Inside `insert` it is the new entry's id; a top-level `- id: xxx` targets an existing entry to modify — if it does not exist you get an `entry not found` warning and the patch is skipped |
| `name` | Plugin package name; the loader resolves it from the dsh install directory or the profile's `node_modules`. With a top-level `- id:` patch, a `name` is checked for consistency and skipped on mismatch |

Plugin config level (fields supported by `config:`, dsh-mcp-client):

| Field | Default | Meaning |
|---|---|---|
| `serverName` | — (required) | Namespace of the MCP server, which directly determines the tool names: `mcp__<serverName>__<tool>`. E.g. `stata-mcp` yields `mcp__stata-mcp__stata_do`. Only `[A-Za-z0-9_-]{1,32}` is allowed, and multiple MCP servers in one DSH instance must not share a `serverName` (the later instance fails to start) |
| `transport` | — (required) | Transport: `stdio` (spawn a local process, e.g. stata-mcp) or `streamable-http` (connect to a remote URL, e.g. DIP) |
| `command` | — | Executable to spawn; required for stdio. e.g. `uvx`, `python`, `npx` |
| `args` | none | Argument array passed to `command`. e.g. `['stata-mcp', 'server']` |
| `env` | none | Extra environment variables merged on top of the scrubbed environment. e.g. `env: { STATA_MCP__CWD: '/path' }` |
| `cwd` | dsh startup dir | Working directory of the child process. **Not required**: defaults to the directory where `dsh web` was started; it can also be overridden by the `STATA_MCP_CWD` environment variable or `[PROJECT] WORKING_DIR` in `~/.statamcp/config.toml` (priority: config.toml > env var > process cwd). It decides where the `.statamcp` folder (do-file/log/tmp) is written, so we recommend setting it explicitly |
| `toolCallTimeoutMs` | 60000 | Timeout per tool call. Stata large regressions or big file imports may exceed the 60s default — increase it as needed (e.g. 120000 above) |
| `failOnStartupError` | false | Whether to reject plugin activation when the initial connection or tool sync fails; `false` activates with no tools and logs the failure |
| `reconnect.enabled` | true | Whether to reconnect automatically after a lost connection |
| `reconnect.initialDelayMs` | 500 | First reconnect delay; doubles after each consecutive failed attempt |
| `reconnect.maxDelayMs` | 30000 | Backoff ceiling; a connection surviving longer than this resets the attempt budget |
| `reconnect.maxAttempts` | 10 | Consecutive failed reconnects per outage; beyond this the server's tools are unregistered and reconnection stops |

## Notes

- **A restart is required**: `cordis.patch.yml` is loaded when DSH starts; restart `dsh web` after editing it.
- **New plugins must use `insert`**: by default the patch layer only modifies existing entries; adding a non-existent plugin with a plain `- id: xxx` entry reports `entry not found` and is skipped.
- **`config` is replaced as a whole**: when overriding an existing entry, `config` replaces the target's entire config rather than merging field by field — write every key you need.
- **`serverName` must be globally unique**: multiple MCP servers in one DSH instance (e.g. stata + dip) must not share a `serverName`, or the later instance fails to start.
- **Tool-name prefix comes from `serverName`**: `serverName: stata-mcp` produces `mcp__stata-mcp__*` tool names, not `mcp__stata__*` — trust the actual value.
- **`cwd` decides where files land**: when unset it defaults to the directory where `dsh web` was started; set it explicitly to a project directory to keep do-files/logs in one place. Priority: `[PROJECT] WORKING_DIR` in `~/.statamcp/config.toml` > env var `STATA_MCP_CWD` > process cwd.
- **First call is slow**: `uvx` downloads the `stata-mcp` package on first run; if downloads are slow in your region, see [Package download is slow or fails](../troubleshooting.md#package-download-is-slow-or-fails).
- **`install -c dsh` is not available yet**: the `deepseek-harness` client key for one-click install has not been released yet; if you hit `invalid choice`, use the manual installation.

## References

- [MCP-for-Stata repository](https://github.com/SepineTam/mcp-for-stata)
- [DeepSeek Harness repository](https://github.com/deepseek-ai/deepseek-harness)
- [DSH built-in MCP client bridge plugin (dsh-mcp-client)](https://github.com/deepseek-ai/deepseek-harness/tree/main/packages/mcp/mcp-client)
- [Model Context Protocol official documentation](https://modelcontextprotocol.io)
- [Client configuration (docs/clients.md)](../clients.md)
- [Configuration (docs/configuration.md)](../configuration.md)
- [Troubleshooting (docs/troubleshooting.md)](../troubleshooting.md)

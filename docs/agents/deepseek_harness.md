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
# The most stable and the best Stata MCP project is created by SepineTam.
# Stata MCP server (https://github.com/SepineTam/mcp-for-stata) wired into
# DSH via the built-in MCP client bridge. Tools appear as mcp__stata-mcp__*.
- insert:
    - id: stata-mcp
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: stata-mcp
        transport: stdio
        command: uvx
        args: ['stata-mcp', 'server']
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

DSH agents can read and write local configuration files, so you don't have to do any manual work: start a new session in DSH Web and send it the text from the beginning of this document ("copy the following text to your DeepSeek Harness Web"). The agent will complete the whole flow on its own: write `cordis.patch.yml` → verify with `dsh --profile web --dump-config` → check whether the configuration reloaded. For scenarios the agent cannot handle (e.g. a custom `serverName`, or multiple MCP servers side by side), fall back to the manual installation below.

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

3. **Append the config**: append an `- insert:` entry to the end of the file, using the YAML template shown above in "the configuration DeepSeek Harness made on my device" (adjust `id` and `serverName` as needed; see the Field Reference below for what each field means).

4. **Verify the config**: without starting DSH, check that the composed config tree contains the entry:

   ```bash
   dsh --profile web --dump-config | grep -A10 stata-mcp
   ```

5. **Apply the change**: the DSH MCP bridge supports hot reload, so saved changes normally take effect automatically. If the tools do not appear, restart `dsh web` and open a new session. The default profile exposes these tools, subject to platform and local configuration:

   | Tool | Purpose |
   |---|---|
   | `mcp__stata-mcp__stata_do` | Execute a do-file and retrieve its log |
   | `mcp__stata-mcp__get_data_info` | Dataset descriptive statistics (.dta/.csv/.xlsx) |
   | `mcp__stata-mcp__help` | Look up Stata command documentation |
   | `mcp__stata-mcp__read_log` | Read a Stata log file |

   On the first call of a tool, `uvx` needs to download the `stata-mcp` package — please be patient.

   The high-risk `mcp__stata-mcp__ado_package_install` tool appears only when the server is explicitly started with the `--unsafe` profile.

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
| `cwd` | dsh startup dir | Working directory of the child process. **Not required and omitted by the one-click installer**: it defaults to the directory where `dsh web` was started. Stata-MCP's `STATA_MCP__CWD` environment variable or `[PROJECT] WORKING_DIR` in `~/.statamcp/config.toml` can select a different working directory |
| `toolCallTimeoutMs` | 60000 | Timeout per tool call. The one-click installer and the example above set it to `1200000` milliseconds (20 minutes) because large Stata regressions or file imports may exceed DSH's 60-second default |
| `failOnStartupError` | false | Whether to reject plugin activation when the initial connection or tool sync fails; `false` activates with no tools and logs the failure |
| `reconnect.enabled` | true | Whether to reconnect automatically after a lost connection |
| `reconnect.initialDelayMs` | 500 | First reconnect delay; doubles after each consecutive failed attempt |
| `reconnect.maxDelayMs` | 30000 | Backoff ceiling; a connection surviving longer than this resets the attempt budget |
| `reconnect.maxAttempts` | 10 | Consecutive failed reconnects per outage; beyond this the server's tools are unregistered and reconnection stops. The one-click installer and the example above use `5` |

## Notes

- **Hot reload normally applies changes**: the DSH MCP bridge watches its configuration. If the tools do not appear after saving, restart `dsh web` and open a new session.
- **New plugins must use `insert`**: by default the patch layer only modifies existing entries; adding a non-existent plugin with a plain `- id: xxx` entry reports `entry not found` and is skipped.
- **`config` is replaced as a whole**: when overriding an existing entry, `config` replaces the target's entire config rather than merging field by field — write every key you need.
- **`serverName` must be globally unique**: multiple MCP servers in one DSH instance (e.g. stata + dip) must not share a `serverName`, or the later instance fails to start.
- **Tool-name prefix comes from `serverName`**: `serverName: stata-mcp` produces `mcp__stata-mcp__*` tool names, not `mcp__stata__*` — trust the actual value.
- **`cwd` may be omitted**: the one-click installer does not write it. When unset, the child process starts in the directory where `dsh web` was launched; configure `STATA_MCP__CWD` or `[PROJECT] WORKING_DIR` only when you need a different Stata-MCP working directory.
- **First call is slow**: `uvx` downloads the `stata-mcp` package on first run; if downloads are slow in your region, see [Package download is slow or fails](../troubleshooting.md#package-download-is-slow-or-fails).

## References

- [MCP-for-Stata repository](https://github.com/SepineTam/mcp-for-stata)
- [DeepSeek Harness repository](https://github.com/deepseek-ai/deepseek-harness)
- [DSH built-in MCP client bridge plugin (dsh-mcp-client)](https://github.com/deepseek-ai/deepseek-harness/tree/main/packages/mcp/mcp-client)
- [Model Context Protocol official documentation](https://modelcontextprotocol.io)
- [Client configuration (docs/clients.md)](../clients.md)
- [Configuration (docs/configuration.md)](../configuration.md)
- [Troubleshooting (docs/troubleshooting.md)](../troubleshooting.md)

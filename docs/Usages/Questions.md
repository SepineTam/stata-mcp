# Questions

## Cherry Studio 32000 Wrong
> (2025-04-03 Solved)

Add `USER=YOUR_COMPUTER_NAME` to config env
while if you are windows, add `USERPROFILE` to config env

If you don't know your computer name, you can run `whoami` in terminal.
it looks like the follow:
```bash
$ whoami  # YOUR_COMPUTER_NAME
```

## Cherry Studio 32000 Error
> (2025-06-04 Solved)

Cherry Studio doesn't support the `--directory` argument. Configure it with the
full path to `stata_mcp.py` instead:

```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "run",
        "/Users/sepinetam/Documents/Github/MCP_Pro/stata-mcp/stata_mcp.py"
      ]
    }
  }
}
```

This means running `uv run /the/full/path/of/stata_mcp.py`. Add `True` if you
need to specify the Stata CLI path.

_Solves [issue #1](https://github.com/sepinetam/stata-mcp/issues/1)._ 

## Windows Supports
> (2025-04-11 Added)

The windows is supported at 2025-04-11 (and it is my birthday). Thanks each of whom use Stata-MCP, it is the best gift for me.

More information you can visit the [Usage doc for Windows](Usages/Usage_Windows.md).


# Stata-MCP
Let LLM help you achieve your regression with Stata.

# Installation
```bash
git clone https://github.com/sepinetam/stata-mcp.git
cd stata-mcp

# if you use uv you can follow the offical usage, however I am not good at uv, but I commend you to use uv for the easier usage.
# else follow the following usage, but you should change that config about MCP by yourself.
# you can also use other chat servers, but you need to change it in your own mind.
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
I haven't used Windows for a long time, and I haven't purchased a license for Stata on Windows, so I have only tested it on macOS. If you have a license for Stata on Windows, you can submit a PR to add Windows support.

Then you need to config your MCP server.

For it, there is some example:
## Config for MCP Server
### [Claude](https://claude.ai/)
Follow the following config:
```json
"chat_number": {
  "command":"uv",
  "args":[
    "--directory",
    "/Users/yourname/path/to/repo/",
    "run",
    "stata_mcp.py"
  ]
}
```

### [ChatWise](https://chatwise.app/)
Open your ChatWise app and open the tab named tools (you need to subscribe it).

Then you can follow the following config:

```
type: stdio
ID: stata-mcp (or whatever you want)
command: uv --directory /Users/yourname/path/to/repo/ run stata_mcp.py
```

### Cline
```json
{
  "mcpServers": {
    "chat_number": {
      "command":"uv",
      "args":[
        "--directory",
        "/Users/yourname/path/to/repo/",
        "run",
        "stata_mcp.py"
      ]
    }
  }
}
```

# Statement
This project is only for research purpose, and I am not responsible for any damage caused by this project. 

And also please make sure you have the right to use Stata. 

More info please refer to [Statement](Statement.md).

# License
[MIT License](License)

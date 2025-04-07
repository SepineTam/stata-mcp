<h1 align="center">
  <img src="src/img/logo_with_name.jpg" alt="logo" width="300"/>
</h1>

[![en](https://img.shields.io/badge/lang-English-red.svg)](README.md)
[![fr](https://img.shields.io/badge/langue-Français-blue.svg)](docs/README/fr/README.md)
[![cn](https://img.shields.io/badge/语言-中文-yellow.svg)](docs/README/cn/README.md)
![Version](https://img.shields.io/badge/version-1.0.3-blue.svg)
[![smithery badge](https://smithery.ai/badge/@SepineTam/stata-mcp)](https://smithery.ai/server/@SepineTam/stata-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/stata-mcp/issues/new)


> Let LLM help you achieve your regression analysis with Stata.
> 
> Currently supports **macOS** only (as of 20250402)
> 
> Good News! **Windows** will be supported at the end of April 2025.

---

# 💡 Quick Start
For more detailed usage information, visit the [Usage guide](docs/Usage.md).

## Prerequisites
- [uv](https://github.com/astral-sh/uv) - Package installer and virtual environment manager
- Claude, Cline, ChatWise, or other LLM service
- Stata License
- Your API-KEY from LLM

## Installation
```bash
# Clone the repository
git clone https://github.com/sepinetam/stata-mcp.git
cd stata-mcp

# Copy example config
cp example.config.py config.py

# Using uv (recommended)
uv run stata_mcp.py 17 se  # Test run with Stata 17 SE

# Alternative setup with pip
# python3.11 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt
```

**Note:** Windows support is not currently available. If you have a Stata license for Windows and would like to contribute, please submit a PR.

# 🔧 MCP Server Configuration

## [Claude](https://claude.ai/)
```json
{
  "stata-mcp": {
    "command":"uv",
    "args":[
      "--directory",
      "/Users/yourname/path/to/repo/",
      "run",
      "stata_mcp.py",
      "17",
      "se"
    ]
  }
}
```

## [ChatWise](https://chatwise.app/)
Open ChatWise app and navigate to the tools tab (subscription required):

```
type: stdio
ID: stata-mcp
command: uv --directory /Users/yourname/path/to/repo/ run stata_mcp.py 17 se
```

## [Cline](https://github.com/cline/cline)
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command":"uv",
      "args":[
        "--directory",
        "/Users/yourname/path/to/repo/",
        "run",
        "stata_mcp.py",
        "17",
        "se"
      ]
    }
  }
}
```

# 📝 Documentation
For more detailed usage information, visit the [Usage guide](docs/Usage.md).

# 💡 Questions
- [Cherry Studio 32000 wrong](docs/Questions.md#cherry-studio-32000-wrong)

# 🚀 Roadmap
- [x] macOS support
- [ ] Windows support
- [ ] Additional LLM integrations
- [ ] Performance optimizations

# ⚠️ Disclaimer
This project is for research purposes only. I am not responsible for any damage caused by this project. Please ensure you have proper licensing to use Stata.

For more information, refer to the [Statement](docs/Statement.md).

# 🐛 Report Issues
If you encounter any bugs or have feature requests, please [open an issue](https://github.com/sepinetam/stata-mcp/issues/new).

# 📄 License
[MIT License](License)

# 📚 Citation
If you use Stata-MCP in your research, please cite this repository using one of the following formats:

## BibTeX
```bibtex
@software{sepinetam2025stata,
  author = {Song Tan},
  title = {Stata-MCP: Let LLM help you achieve your regression analysis with Stata},
  year = {2025},
  url = {https://github.com/sepinetam/stata-mcp},
  version = {1.0.3}
}
```

## APA
```
Song Tan. (2025). Stata-MCP: Let LLM help you achieve your regression analysis with Stata (Version 1.0.3) [Computer software]. https://github.com/sepinetam/stata-mcp
```

## Chicago
```
Song Tan. 2025. "Stata-MCP: Let LLM help you achieve your regression analysis with Stata." Version 1.0.3. https://github.com/sepinetam/stata-mcp.
```

# 📬 Contact
Email: [sepinetam@gmail.com](mailto:sepinetam@gmail.com)

Or contribute directly by submitting a [Pull Request](https://github.com/sepinetam/stata-mcp/pulls)! We welcome contributions of all kinds, from bug fixes to new features.

# ✨ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sepinetam/stata-mcp&type=Date)](https://www.star-history.com/#sepinetam/stata-mcp&Date)


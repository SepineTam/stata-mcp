<h1 align="center">
  <a href="https://www.statamcp.com"><img src="src/img/logo_with_name.jpg" alt="logo" width="300"/></a>
</h1>

[![en](https://img.shields.io/badge/lang-English-red.svg)](README.md)
[![cn](https://img.shields.io/badge/语言-中文-yellow.svg)](docs/README/cn/README.md)
[![fr](https://img.shields.io/badge/langue-Français-blue.svg)](docs/README/fr/README.md)
[![sp](https://img.shields.io/badge/Idioma-Español-green.svg)](docs/README/sp/README.md)
![Version](https://img.shields.io/badge/version-1.2.3-blue.svg)
[![smithery badge](https://smithery.ai/badge/@SepineTam/stata-mcp)](https://smithery.ai/server/@SepineTam/stata-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](License)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/stata-mcp/issues/new)


> Let LLM help you achieve your regression analysis with Stata.
> 
> Now Stata-MCP has been supported to find Stata CLI **automatically**.

---

> Looking for other Stata integrations or others?
>
> - A VScode or Cursor integrated [here](https://github.com/hanlulong/stata-mcp). Confused it? 💡 [Difference](docs/Difference.md)
> - Jupyter Lab Usage (Important: Stata 17+) [here](https://github.com/sepinetam/Jupyter-Stata)
> - [NBER-MCP](https://github.com/sepinetam/NBER-MCP) 🔧 under construction

## 💡 Quick Start
For more detailed usage information, visit the [Usage guide](docs/Usages/Usage.md). 

And some advanced usage, visit the [Advanced guide](docs/Usages/Advanced.md)

### Prerequisites
- [uv](https://github.com/astral-sh/uv) - Package installer and virtual environment manager
- Claude, Cline, ChatWise, or other LLM service
- Stata License
- Your API-KEY from LLM

### Installation
```bash
# Clone the repository
git clone https://github.com/sepinetam/stata-mcp.git
cd stata-mcp

# Copy example config
cp example.config.py config.py

# Using uv (recommended) to test usable
uv run usable.py

# Alternative setup with pip
# python3.11 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt
```

## 📝 Documentation
- For more detailed usage information, visit the [Usage guide](docs/Usages/Usage.md).
- Advanced Usage, visit the [Advanced](docs/Usages/Advanced.md)
- Some questions, visit the [Questions](docs/Usages/Questions.md)
- Difference with [Stata-MCP@hanlulong](https://github.com/hanlulong/stata-mcp), visit the [Difference](docs/Difference.md)

## 💡 Questions
- [Cherry Studio 32000 wrong](docs/Usages/Questions.md#cherry-studio-32000-wrong)
- [Windows Support](docs/Usages/Questions.md#windows-supports)

## 🚀 Roadmap
- [x] macOS support
- [x] Windows support
- [ ] Additional LLM integrations
- [ ] Performance optimizations

## ⚠️ Disclaimer
This project is for research purposes only. I am not responsible for any damage caused by this project. Please ensure you have proper licensing to use Stata.

For more information, refer to the [Statement](docs/Statement.md).

## 🐛 Report Issues
If you encounter any bugs or have feature requests, please [open an issue](https://github.com/sepinetam/stata-mcp/issues/new).

## 📄 License
[MIT License](License) and Extensions

## 📚 Citation
If you use Stata-MCP in your research, please cite this repository using one of the following formats:

### BibTeX
```bibtex
@software{sepinetam2025stata,
  author = {Song Tan},
  title = {Stata-MCP: Let LLM help you achieve your regression analysis with Stata},
  year = {2025},
  url = {https://github.com/sepinetam/stata-mcp},
  version = {1.2.3}
}
```

### APA
```
Song Tan. (2025). Stata-MCP: Let LLM help you achieve your regression analysis with Stata (Version 1.2.3) [Computer software]. https://github.com/sepinetam/stata-mcp
```

### Chicago
```
Song Tan. 2025. "Stata-MCP: Let LLM help you achieve your regression analysis with Stata." Version 1.2.3. https://github.com/sepinetam/stata-mcp.
```

## 📬 Contact
Email: [sepinetam@gmail.com](mailto:sepinetam@gmail.com)

Or contribute directly by submitting a [Pull Request](https://github.com/sepinetam/stata-mcp/pulls)! We welcome contributions of all kinds, from bug fixes to new features.

## ✨ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sepinetam/stata-mcp&type=Date)](https://www.star-history.com/#sepinetam/stata-mcp&Date)


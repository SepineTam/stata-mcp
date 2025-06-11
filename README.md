<h1 align="center">
  <a href="https://www.statamcp.com"><img src="src/img/logo_with_name.jpg" alt="logo" width="300"/></a>
</h1>

<h1 align="center">Stata-MCP</h1>

<p align="center"> Let LLM help you achieve your regression analysis with Stata ✨</p>

[![en](https://img.shields.io/badge/lang-English-red.svg)](README.md)
[![cn](https://img.shields.io/badge/语言-中文-yellow.svg)](source/docs/README/cn/README.md)
[![fr](https://img.shields.io/badge/langue-Français-blue.svg)](source/docs/README/fr/README.md)
[![sp](https://img.shields.io/badge/Idioma-Español-green.svg)](source/docs/README/sp/README.md)
[![PyPI version](https://img.shields.io/pypi/v/stata-mcp.svg)](https://pypi.org/project/stata-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/stata-mcp/issues/new)

---

> Looking for other Stata integrations or others?
>
> - A VScode or Cursor integrated [here](https://github.com/hanlulong/stata-mcp). Confused it? 💡 [Difference](source/docs/Difference.md)
> - Jupyter Lab Usage (Important: Stata 17+) [here](https://github.com/sepinetam/Jupyter-Stata)
> - [NBER-MCP](https://github.com/sepinetam/NBER-MCP) 🔧 under construction
> - [AER-MCP](https://github.com/sepinetam/AER-MCP)

## 💡 Quick Start
For more detailed usage information, visit the [Usage guide](source/docs/Usages/Usage.md). 

And some advanced usage, visit the [Advanced guide](source/docs/Usages/Advanced.md)

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

# Using uv (recommended) to test usable
uv run usable.py

# Alternative setup with pip
# python3.11 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt
```

## 📝 Documentation
- For more detailed usage information, visit the [Usage guide](docs/Usages/Usage.md).
- Advanced Usage, visit the [Advanced](source/docs/Usages/Advanced.md)
- Some questions, visit the [Questions](source/docs/Usages/Questions.md)
- Difference with [Stata-MCP@hanlulong](https://github.com/hanlulong/stata-mcp), visit the [Difference](source/docs/Difference.md)

## 💡 Questions
- [Cherry Studio 32000 wrong](source/docs/Usages/Questions.md#cherry-studio-32000-wrong)
- [Cherry Studio 32000 error](source/docs/Usages/Questions.md#cherry-studio-32000-error)
- [Windows Support](source/docs/Usages/Questions.md#windows-supports)
- [Network Errors When Running Stata-MCP](source/docs/Usages/Questions.md#network-errors-when-running-stata-mcp)

## 🚀 Roadmap
- [x] macOS support
- [x] Windows support
- [ ] Additional LLM integrations
- [ ] Performance optimizations

## ⚠️ Disclaimer
This project is for research purposes only. I am not responsible for any damage caused by this project. Please ensure you have proper licensing to use Stata.

For more information, refer to the [Statement](source/docs/Rights/Statement.md).

## 🐛 Report Issues
If you encounter any bugs or have feature requests, please [open an issue](https://github.com/sepinetam/stata-mcp/issues/new).

## 📄 License
[MIT License](LICENSE) and Extensions

## 📚 Citation
If you use Stata-MCP in your research, please cite this repository using one of the following formats:

### BibTeX
```bibtex
@software{sepinetam2025stata,
  author = {Song Tan},
  title = {Stata-MCP: Let LLM help you achieve your regression analysis with Stata},
  year = {2025},
  url = {https://github.com/sepinetam/stata-mcp},
  version = {1.3.7}
}
```

### APA
```
Song Tan. (2025). Stata-MCP: Let LLM help you achieve your regression analysis with Stata (Version 1.3.7) [Computer software]. https://github.com/sepinetam/stata-mcp
```

### Chicago
```
Song Tan. 2025. "Stata-MCP: Let LLM help you achieve your regression analysis with Stata." Version 1.3.7. https://github.com/sepinetam/stata-mcp.
```

## 📬 Contact
Email: [sepinetam@gmail.com](mailto:sepinetam@gmail.com)

Or contribute directly by submitting a [Pull Request](https://github.com/sepinetam/stata-mcp/pulls)! We welcome contributions of all kinds, from bug fixes to new features.

## ❤️ Acknowledgements
The author sincerely thanks the Stata official team for their support and the Stata License for authorizing the test development.

## ✨ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sepinetam/stata-mcp&type=Date)](https://www.star-history.com/#sepinetam/stata-mcp&Date)


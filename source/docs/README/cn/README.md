<h1 align="center">
  <a href="https://www.statamcp.com"><img src="../../../img/logo_with_name.jpg" alt="logo" width="300"></a>
</h1>

<h1 align="center">Stata-MCP</h1>

<p align="center"> 让大语言模型（LLM）帮助您使用Stata完成回归分析 ✨</p>

[![en](https://img.shields.io/badge/lang-English-red.svg)](../../../../README.md)
[![cn](https://img.shields.io/badge/语言-中文-yellow.svg)](README.md)
[![fr](https://img.shields.io/badge/langue-Français-blue.svg)](../fr/README.md)
[![sp](https://img.shields.io/badge/Idioma-Español-green.svg)](../sp/README.md)
[![PyPI version](https://img.shields.io/pypi/v/stata-mcp.svg)](https://pypi.org/project/stata-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../../LICENSE)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/stata-mcp/issues/new)

---

> 正在寻找其他 Stata 集成？
>
> - VScode 或 Cursor 集成 [此处](https://github.com/hanlulong/stata-mcp)。搞不清楚？️💡 [区别](../../Difference.md)
> - Jupyter Lab 使用方法（重要提示：Stata 17+）[此处](https://github.com/sepinetam/Jupyter-Stata)
> - [NBER-MCP](https://github.com/sepinetam/NBER-MCP) 🔧 建造之下
> - [AER-MCP](https://github.com/sepinetam/AER-MCP)


## 💡 快速开始
有关更详细的使用信息，请访问[使用指南](../../Usages/Usage.md)。

一些高级的功能，访问[高级指南](../../Usages/Advanced.md)

### 前提条件
- [uv](https://github.com/astral-sh/uv) - 包安装器和虚拟环境管理器
- Claude、Cline、ChatWise或其他LLM服务
- Stata许可证
- 您的LLM API密钥

### 安装
```bash
# 克隆仓库
git clone https://github.com/sepinetam/stata-mcp.git
cd stata-mcp

# 使用uv（推荐）测试可用性
uv run usable.py

# 使用pip的替代设置
# python3.11 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt
```

## 📝 文档
- 有关更详细的使用信息，请访问[使用指南](../../Usages/Usage.md)。
- 高级用法，请访问[高级指南](../../Usages/Advanced.md)
- 一些问题，请访问[问题](../../Usages/Questions.md)
- 与[Stata-MCP@hanlulong](https://github.com/hanlulong/stata-mcp)的区别，请访问[区别](../../Difference.md)

## 💡 常见问题
- [Cherry Studio 32000 wrong](../../Usages/Questions.md#cherry-studio-32000-wrong)
- [Cherry Studio 32000 error](../../Usages/Questions.md#cherry-studio-32000-error)
- [Windows 支持](../../Usages/Questions.md#windows-supports)
- [网络问题](../../Usages/Questions.md#network-errors-when-running-stata-mcp)

## 🚀 路线图
- [x] macOS支持
- [x] Windows支持
- [ ] 更多LLM集成
- [ ] 性能优化

## ⚠️ 免责声明
本项目仅用于研究目的。我对本项目造成的任何损害不承担责任。请确保您拥有使用Stata的适当许可证。

更多信息，请参阅[声明](../../Rights/Statement.md)。

## 🐛 报告问题
如果您遇到任何错误或有功能请求，请[提交问题](https://github.com/sepinetam/stata-mcp/issues/new)。

## 📄 许可证
[MIT许可证](../../../../LICENSE)和扩展

## 📚 引用
如果您在研究中使用 Stata-MCP，请使用以下格式之一引用此存储库：

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

## 📬 联系方式
电子邮件：[sepinetam@gmail.com](mailto:sepinetam@gmail.com)

或通过提交[拉取请求](https://github.com/sepinetam/stata-mcp/pulls)直接贡献！我们欢迎各种形式的贡献，从错误修复到新功能。

## ❤️ 致谢
作者诚挚感谢Stata官方团队给予的支持和授权测试开发使用的Stata License

## ✨ 历史Star

[![Star History Chart](https://api.star-history.com/svg?repos=sepinetam/stata-mcp&type=Date)](https://www.star-history.com/#sepinetam/stata-mcp&Date)
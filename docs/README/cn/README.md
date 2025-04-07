<h1 align="center">
  <img src="../../../src/img/logo_with_name.jpg" alt="logo" width="300">
</h1>

[![en](https://img.shields.io/badge/lang-English-red.svg)](../../../README.md)
[![fr](https://img.shields.io/badge/langue-Français-blue.svg)](../fr/README.md)
[![cn](https://img.shields.io/badge/语言-中文-yellow.svg)](README.md)
![Version](https://img.shields.io/badge/version-1.0.3-blue.svg)
[![smithery badge](https://smithery.ai/badge/@SepineTam/stata-mcp)](https://smithery.ai/server/@SepineTam/stata-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../License)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/stata-mcp/issues/new)

> 让大语言模型（LLM）帮助您使用Stata完成回归分析。
> 
> 目前仅支持**macOS**系统（截至20250329）
> 
> 好消息！**Windows** 将于 2025 年 4 月底获得支持。

---

# 💡 快速开始
有关更详细的使用信息，请访问[使用指南](../../Usage.md)。

## 前提条件
- [uv](https://github.com/astral-sh/uv) - 包安装器和虚拟环境管理器
- Claude、Cline、ChatWise或其他LLM服务
- Stata许可证
- 您的LLM API密钥

## 安装
```bash
# 克隆仓库
git clone https://github.com/sepinetam/stata-mcp.git
cd stata-mcp

# 复制示例配置
cp example.config.py config.py

# 使用uv（推荐）
uv run stata_mcp.py 17 se  # 使用Stata 17 SE进行测试运行

# 使用pip的替代设置
# python3.11 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt
```

**注意：** 目前不支持Windows系统。如果您拥有Windows版Stata许可证并希望做出贡献，请提交PR。

# 🔧 MCP服务器配置

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
打开ChatWise应用并导航至工具选项卡（需要订阅）：

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

# 📝 文档
有关更详细的使用信息，请访问[使用指南](../../Usage.md)。

# 💡 常见问题
- [Cherry Studio 32000 wrong](../../../docs/Questions.md#cherry-studio-32000-wrong)

# 🚀 路线图
- [x] macOS支持
- [ ] Windows支持
- [ ] 更多LLM集成
- [ ] 性能优化

# ⚠️ 免责声明
本项目仅用于研究目的。我对本项目造成的任何损害不承担责任。请确保您拥有使用Stata的适当许可证。

更多信息，请参阅[声明](../../Statement.md)。

# 🐛 报告问题
如果您遇到任何错误或有功能请求，请[提交问题](https://github.com/sepinetam/stata-mcp/issues/new)。

# 📄 许可证
[MIT许可证](../../../License)

# 📚 引用
如果您在研究中使用 Stata-MCP，请使用以下格式之一引用此存储库：

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

# 📬 联系方式
电子邮件：[sepinetam@gmail.com](mailto:sepinetam@gmail.com)

或通过提交[拉取请求](https://github.com/sepinetam/stata-mcp/pulls)直接贡献！我们欢迎各种形式的贡献，从错误修复到新功能。

# ✨ 历史Star

[![Star History Chart](https://api.star-history.com/svg?repos=sepinetam/stata-mcp&type=Date)](https://www.star-history.com/#sepinetam/stata-mcp&Date)

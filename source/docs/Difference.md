# Catalog
- [🇬🇧 English](#difference-with-stata-mcphanlulong)
- [🇨🇳 中文](#与stata-mcphanlulong的不同)

---

# Difference with Stata-MCP@hanlulong
- 🔗 [hanlulong/stata-mcp](https://github.com/hanlulong/stata-mcp)
- [Report or Request](https://github.com/SepineTam/stata-mcp/issues)

## stata-mcp@hanlulong
### Main Features
- IDE integration: Provides Stata integration for Visual Studio Code and Cursor IDE using the Model Context Protocol (MCP)
- Command execution: Allows you to run Stata commands directly from VS Code or Cursor (If you want to use it with Jupyter Lab, refer to the [documentation](https://github.com/hanlulong/stata-mcp/blob/main/jupyter-stata.md) or check [Issue](https://github.com/hanlulong/stata-mcp/issues/5))
- Syntax highlighting: Full support for Stata .do, .ado, .mata, and .doh files
- Cross-platform: Works on Windows, macOS, and Linux
- AI assistant integration: Get contextual help and code suggestions via MCP

### Installation
The Stata-MCP@hanlulong can be installed directly from the VS Code Marketplace. The first-time installation may take up to 2 minutes as dependencies are installed.

### MCP Integration
This implementation leverages the Model Context Protocol to enable AI assistants to interact with Stata, allowing:
- Running code directly from the editor
- Receiving contextual help
- Getting code suggestions

## stata-mcp@sepinetam
### Main Features
- Data Integration: Creates a bridge between Stata's statistical capabilities and AI assistants through the Model Context Protocol (MCP)
- Contextual Analysis: Allows AI systems to understand Stata datasets, commands, and statistical output
- Modular Design: Supports customizable components for different use cases and environments
- Statistical Output Parsing: Converts Stata output into structured formats that AI models can interpret
- Advanced Querying: Enables natural language interactions with Stata's statistical and data manipulation capabilities

### Installation
Installation instructions are provided in the repository [README](../../README.md) or [Usage](Usages/Usage.md). Initial setup typically requires configuring your Stata path and preferred connection settings.

### MCP Integration
This implementation uses the Model Context Protocol to create a semantic layer between Stata and AI systems:
- Statistical context awareness for more relevant AI responses
- Dataset structure understanding for better data analysis suggestions
- Command history awareness to improve workflow recommendations

## Differences
Shortly, Stata-MCP@sepinetam provides interaction with large language models to help implement dofiles, while Stata-MCP@hanlulong offers a more convenient Stata usage solution compared to using Jupyter Lab and Stata client (editing and running Stata commands in VScode).

1. Documentation and development activity: Currently, hanlulong's repository has more comprehensive documentation. This project will gradually improve its documentation, and configuration videos will be added in the future.
2. Implementation focus: Although both use MCP, they are implemented in different ways.

# 与Stata-MCP@hanlulong的不同
- 🔗 [hanlulong/stata-mcp](https://github.com/hanlulong/stata-mcp)
- [报告问题或者提出需求](https://github.com/SepineTam/stata-mcp/issues)

## stata-mcp@hanlulong
### 主要特征
- IDE集成：使用模型上下文协议(MCP)为Visual Studio Code和Cursor IDE提供Stata集成
- 命令执行：允许直接从VS Code或Cursor运行Stata命令 （如果你想通过Jupyter Lab使用，参考[文档](https://github.com/hanlulong/stata-mcp/blob/main/jupyter-stata.md)或查看[Issue](https://github.com/hanlulong/stata-mcp/issues/5)）
- 语法高亮：完全支持Stata .do、.ado、.mata和.doh文件
- 跨平台：适用于Windows、macOS和Linux
- AI助手集成：通过MCP获取上下文相关帮助和代码建议

### 安装
该Stata-MCP@hanlulong可以直接从VS Code市场安装。首次安装可能需要长达2分钟的时间，因为需要安装依赖项。

### MCP集成
此实现利用模型上下文协议使AI助手能够与Stata交互，允许：
- 直接从编辑器运行代码
- 接收上下文相关帮助
- 获取代码建议

## stata-mcp@sepinetam
### 主要特点
- 数据集成：通过模型上下文协议(MCP)在Stata的统计功能和AI助手之间建立桥梁
- 上下文分析：使AI系统能够理解Stata数据集、命令和统计输出
- 模块化设计：支持针对不同用例和环境的可定制组件
- 统计输出解析：将Stata输出转换为AI模型可以解释的结构化格式
- 高级查询：实现与Stata的统计和数据操作功能的自然语言交互

### 安装
安装说明在仓库的[README](../../README.md)或[Usage](Usages/Usage.md)中提供。初始设置通常需要配置您的Stata路径和首选连接设置。

### MCP集成
此实现使用模型上下文协议在Stata和AI系统之间创建语义层：
- 统计上下文感知，提供更相关的AI响应
- 数据集结构理解，提供更好的数据分析建议
- 命令历史感知，改进工作流程建议

## 区别
简短地说，Stata-MCP@sepinetam提供了与大语言模型交互，让其完成dofile的实现，而Stata-MCP@hanlulong提供了相比于使用Jupyter Lab和Stata客户端更方便的Stata使用方案（在VScode编辑并运行stata命令）

1. 文档和开发活动：目前hanlulong的仓库有更全面的文档，本项目将逐步完善文档，后续也会加入配置的视频。
2. 实现重点：虽然两者都使用MCP，但是是通过不同的形式来实现的。

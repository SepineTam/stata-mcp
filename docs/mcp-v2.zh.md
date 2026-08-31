# MCP Python SDK v2

MCP-for-Stata 现已使用稳定的 MCP Python SDK 2.x 服务器架构。这是 SDK 与协议层迁移，并不表示 Python 包版本已经自动变成 2.0。

## 发生了什么变化

- 高层服务器类从 `FastMCP` 迁移为 `MCPServer`。
- 主要服务器实现在 `src/stata_mcp/mcp_servers.py`。
- MCP v2 middleware 会为工具调用生成长期 Audit v1 记录和本地 OpenTelemetry 调试记录。
- 兼容性工作流会在 Linux、macOS、Windows 的 Python 3.11、3.12、3.13 上运行真实 stdio 服务器。

MCP 的基本概念没有变化：服务器仍然提供 tool、resource 和 prompt。除非某项功能在 CHANGELOG 中明确说明，MCP-for-Stata 现有工具名称和输入输出 schema 保持稳定。

## 协议兼容性

服务器同时接受：

- 现代 MCP `2026-07-28` 协商方式。
- 旧版 initialize 流程的 `2025-11-25` 客户端。

因此客户端和服务器可以分开升级，不要求所有用户同时更换两端。

## 请求流程

```text
MCP 客户端
  -> MCPServer 内置 OpenTelemetry span
  -> AuditMiddleware
  -> 安全检查和工具处理器
  -> 工具专属证据文件
```

`AuditMiddleware` 生成可读的 `run_id`，记录客户端、协议和结束状态。`stata_do` 还会把 Stata 真正执行的完整字节保存为使用完整 SHA-256 寻址的快照。安全阻拦通过 `security_event_ids` 把工具账本与 `audit/security.jsonl` 关联起来。

长期证据参见[审计记录](audit.md)，允许轮转的运行诊断参见[本地调试黑匣子](debug-tracing.md)。

## 兼容边界

- 客户端身份由客户端自行报告，不能作为认证依据。
- 本地 OpenTelemetry 默认开启，只保存在用户电脑，可通过 `[DEBUG.tracing]` 关闭。
- Windows 上的 `get_data_info` 默认仍受 beta 开关控制，因为历史上的客户端特定卡死问题仍在调查；跨平台 CI 会测试显式开启后的路径。
- Middleware 负责观察和阻拦；精确 Stata 快照仍由 Stata 执行层创建。

## 验证范围

专用工作流验证：

```text
3 个操作系统 x 3 个 Python 版本 x 现代/旧版协议调用
```

工作流还会在 Ubuntu 运行完整 pytest，并确认 `get_data_info` 返回结构化结果，同时产生可以互相关联的 Audit 和 trace 记录。

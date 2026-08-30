# 审计记录

MCP-for-Stata 会为 MCP 工具调用写入本地、只追加的审计记录，用来回答：哪个客户端在什么时间调用了什么工具、使用了哪个 MCP 协议，以及调用是否成功。

## 文件结构

审计文件位于项目产物目录中，默认是 `.statamcp/`：

```text
.statamcp/
├── audit/
│   ├── stata_do.jsonl
│   ├── get_data_info.jsonl
│   ├── help.jsonl
│   └── security.jsonl
└── snapshot/
    ├── objects/<完整SHA256>.do
    └── metadata.jsonl
```

JSONL 的每一行都是一条不可修改的事件。一次工具调用通常产生一条 `started`，以及一条 `completed`、`failed`、`timeout` 或 `interrupted` 结束事件，两条记录使用同一个 `run_id`。

## Run ID

run ID 由可直接读取的 UTC 时间和防冲突摘要组成：

```text
20260830T083015123456Z_2ce5d65f457ce14a
```

可以直接从前半部分反推出运行时间。摘要还包含高精度时间、工具名、来源引用和随机量。

## 客户端信息

对于 MCP 调用，`started` 事件会记录客户端自报的名称和版本、协商后的协议版本以及 request ID。新版 2026 协议和旧版 initialize 协议都支持。

客户端信息由客户端自行报告，可以用于审计和排错，但不能作为身份认证或权限判断依据。

## Do-file 快照

Stata 启动前，MCP-for-Stata 会保存真正要执行的完整字节。metadata 会记录原始路径、快照路径、完整 SHA-256、文件大小、复用状态和对应 run ID。Stata 实际执行快照，而不是可能继续变化的原文件。

无论运行时间和原文件名是否相同，完全相同的内容都会复用同一个内容寻址快照；每次调用仍有独立的 metadata 和 run ID。

## 安全审计联动

当 `stata_do` 被路径边界、包管理 Guard 或危险命令 Guard 阻止时，工具账本的结束事件会写成 `blocked`，而不是 `completed`。记录中包含 `executed: false` 和一个或多个 `security_event_ids`。

`audit/security.jsonl` 中对应的记录使用同一个 run ID，并保存安全阶段、判断结果、风险类型、可获得时的源码 SHA-256，以及命中规则的位置。危险命令原文不会进入安全账本。这样工具生命周期和安全判断可以分别查看，同时又能通过安全 ID 直接关联。

## 敏感信息

参数中类似 `password`、`secret`、`token`、`authorization`、`api_key` 的字段会被递归替换为 `[REDACTED]`。审计文件仍可能包含本地路径、变量选择、工具名、错误和结果信息，因此应把整个 `.statamcp/` 目录视为潜在敏感内容。

该目录默认被 Git 忽略。第一版不会自动删除审计记录。

## Audit 与 OpenTelemetry

JSONL audit 是长期保存的研究证据；OpenTelemetry 是 MCP 2 的调试和性能轨迹。OpenTelemetry 用于解释时间花在哪里，JSONL 用于保存调用了什么以及产生了哪些证据文件。

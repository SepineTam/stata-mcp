# 本地调试黑匣子

MCP-for-Stata 默认给 `get_data_info` 和 `stata_do` 开启一个只保存在本地的“黑匣子”。它在关键代码前后写入不会暂停程序的检查点，方便在调用变慢或卡住后判断最后走到了哪一步。

调试记录是可以轮转的运行诊断，不是长期保存的审计证据。文件位于项目产物目录：

```text
.statamcp/debug/
├── checkpoints.jsonl
├── checkpoints.jsonl.1
├── traces.jsonl
└── traces.jsonl.1
```

`checkpoints.jsonl` 会在每一步开始、完成或失败时立即追加。`traces.jsonl` 保存已经结束的 OpenTelemetry 记录，包括 trace ID、span ID、耗时、状态，以及可获得时对应的 Audit `run_id`。

## 记录哪些步骤

`get_data_info` 会记录：MCP 接收调用、导入组件、读取配置、路径检查、创建数据读取器、真正读取 DataFrame、计算统计信息、整理完整结果和转换 JSON。

`stata_do` 会记录：请求与安全检查、参数检查、do-file 快照、Stata 进程运行、审计收尾和返回结果整理。同步与异步执行使用相同的步骤名称。

## 运行很久时

如果这两个工具运行 30 秒仍未结束，黑匣子会记录所有 Python 线程当时停留的文件名、行号和函数名；120 秒后仍未结束，再记录一次。这个过程只观察，不暂停、不取消，也不强制结束工具。slow 记录会直接包含 MCP 根 span 的 `trace_id`、`span_id`、`run_id` 和进程 ID；没有可记录 span 时仍保留 run ID 与进程 ID。

查看时，最后一个只有 `started`、没有对应 `completed` 的步骤，就是没有返回的位置。如果工具和结果整理都显示完成，但客户端仍在等待，问题范围就会缩小到结果发出过程或客户端接收过程。

## 将缓慢调用与 Audit 关联

1. 从工具账本或 slow 检查点复制 `run_id`。
2. 先配对长期工具 `started` 和结束事件。
3. 在 `checkpoints.jsonl*` 中查找相同 `run_id`，确定最后一个没有配对的步骤 `started`。
4. 可获得时，使用 `trace_id` 和 `span_id` 在 `traces.jsonl*` 中查看对应的已完成 span。
5. 对于 `stata_do`，在判断延迟发生于 Stata 执行前、执行中还是执行后之前，应继续校验快照 metadata 和 Stata 日志。

具体命令参见[如何读取审计文件](audit/reading.md)，关联键参见[事件与关联关系](audit/events.md)。旧 debug 记录可能因为轮转而正常缺失；长期证据缺失是另一种情况。

## 配置

本地黑匣子默认开启。项目不会默认配置远程 OTLP，也不会把 trace 上传到网络。

```toml
[DEBUG.tracing]
ENABLED = true
MAX_BYTES = 10485760
BACKUP_COUNT = 3
```

设置 `ENABLED = false` 后，本地检查点、OpenTelemetry 文件和慢调用现场记录都会关闭。对应环境变量为：

```bash
export STATA_MCP__DEBUG_TRACING_ON=false
export STATA_MCP__DEBUG_TRACING_MAX_BYTES=10485760
export STATA_MCP__DEBUG_TRACING_BACKUP_COUNT=3
```

两个活动文件分别执行大小限制。默认情况下，checkpoints 和 traces 各自保留一个当前文件和三个备份文件。

## 隐私与失败处理

黑匣子保存步骤名称、时间、异常类型、来源摘要、平台信息、线程位置和关联 ID。它不会主动保存数据内容、变量值、do-file 原文、URL 查询参数、账号密码或异常消息。

调试写入失败时会放行，不能改变工具结果，也不能阻断长期 Audit v1 证据链。debug 文件允许轮转和删除；Audit JSONL 与 do-file 快照继续遵循各自的长期证据规则。

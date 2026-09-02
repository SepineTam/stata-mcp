# 事件与关联关系

Audit v1 使用 JSON Lines 格式。每一行是一条 `schema_version: 1` 事件；调用继续运行时，已有行不会被修改。

## 工具生命周期

对于每个 MCP `tools/call` 请求，`AuditMiddleware` 会写入：

```text
一条 started -> 一条结束事件
```

两条记录使用相同 `run_id`，保存在 `.statamcp/audit/<工具名>.jsonl`。

| 结束事件 | 含义 |
| --- | --- |
| `completed` | 工具返回了未被表示为 MCP 错误的结果。 |
| `failed` | 处理器抛出异常、返回错误结果，或遇到未单独分类的超时。 |
| `interrupted` | 执行向外传播了 `KeyboardInterrupt`。 |
| `blocked` | 关联的安全判断拒绝执行；应继续查看 `executed` 和 `security_event_ids`。 |
| `timeout` | 存储模型预留；当前 middleware 不会把它作为独立类别写出。 |

## 公共字段

每条工具生命周期事件都包含：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `schema_version` | 整数 | 事件 schema 版本，当前是 `1`。 |
| `run_id` | 字符串 | 唯一调用 ID，前缀可以还原 UTC 开始时间。 |
| `event` | 字符串 | `started` 或一种结束事件。 |
| `tool` | 字符串 | MCP 工具名，也是账本文件名前缀。 |
| `timestamp` | 字符串 | 该事件的 UTC ISO 8601 时间。 |

## 仅 started 事件包含的字段

| 字段 | 是否必有 | 含义 |
| --- | --- | --- |
| `interface` | 是 | 调用界面；MCP middleware 写入 `mcp`。 |
| `source_reference` | 是 | 首个可识别来源参数（`dofile_path`、`data_path` 或 `file_path`），否则为工具名。 |
| `input` | 是 | 转换为 JSON 且递归脱敏后的工具参数。 |
| `client` | 否 | MCP 客户端自报的实现信息。 |
| `protocol_version` | 否 | 可获得时的 MCP 协议协商版本。 |
| `request_id` | 否 | 转换为文本的 MCP request ID。 |

合成示例：

```json
{
  "schema_version": 1,
  "run_id": "20260830T083015123456Z_2ce5d65f457ce14a",
  "event": "started",
  "tool": "stata_do",
  "timestamp": "2026-08-30T08:30:15.123456+00:00",
  "interface": "mcp",
  "source_reference": "/project/analysis.do",
  "input": {"dofile_path": "/project/analysis.do"},
  "client": {"name": "example-client", "version": "1.0"},
  "protocol_version": "2026-07-28",
  "request_id": "42"
}
```

客户端信息只用于描述。客户端可以自报任意名称和版本，不能把这些字段当作经过验证的身份。

## 仅结束事件包含的字段

| 字段 | 是否必有 | 含义 |
| --- | --- | --- |
| `duration_ms` | 是 | 从创建 run 到保存结束事件的耗时。 |
| `artifacts` | 否 | 工具产物引用，例如快照路径、SHA-256、复用状态或 Stata 日志路径。 |
| `output` | 否 | 结果元数据；middleware 当前记录 `is_error`。 |
| `error` | 否 | 执行抛出异常时的异常类型和消息。 |
| `security_event_ids` | 否 | 与 `audit/security.jsonl` 关联的 ID。 |
| `executed` | 否 | 是否通过安全判断进入执行；middleware 的工具结束事件通常包含该字段。 |

合成的阻拦示例：

```json
{
  "schema_version": 1,
  "run_id": "20260830T083015123456Z_2ce5d65f457ce14a",
  "event": "blocked",
  "tool": "stata_do",
  "timestamp": "2026-08-30T08:30:15.140000+00:00",
  "duration_ms": 16.544,
  "output": {"is_error": false},
  "security_event_ids": [
    "sec_20260830T083015123456Z_2ce5d65f457ce14a_01"
  ],
  "executed": false
}
```

虽然 `output.is_error` 是 `false`，该调用仍然被阻止。

## Run ID

格式为：

```text
YYYYMMDDTHHMMSSffffffZ_<16位小写十六进制字符>
```

示例：

```text
20260830T083015123456Z_2ce5d65f457ce14a
```

前缀直接编码精确到微秒的 UTC 调用时间。摘要还包含纳秒时间、工具名、来源引用和随机量，用于避免实际碰撞；它不是数字签名，也不能认证调用者或来源。

## 关联关系

| 从哪里开始 | 关联键 | 继续查哪里 | 用途 |
| --- | --- | --- | --- |
| 工具账本 | `run_id` | 同一工具账本 | 配对生命周期事件。 |
| 工具结束事件 | `security_event_ids[]` | `security.security_event_id` | 读取与该调用直接关联的安全判断。 |
| 工具事件 | `run_id` | `security.run_id` | 找到该 run 的全部安全判断。 |
| `stata_do` 事件 | `run_id` | `snapshot/metadata.jsonl` | 定位原路径、对象路径、哈希、大小和复用状态。 |
| 工具事件 | `run_id` | `debug/checkpoints.jsonl*` | 查找即时执行步骤。 |
| 工具事件 | `run_id` 或 trace 属性 `statamcp.run_id` | `debug/traces.jsonl*` | 查找已完成 span 和耗时层级。 |
| 检查点 | `trace_id` 与 `span_id` | trace 记录 | 把即时步骤事件关联到对应的已完成 span。 |

`request_id` 可以辅助对照 MCP 传输日志，但 `run_id` 才是 MCP-for-Stata 的主要关联键。

## 顺序与完整性

同一个 JSONL 文件的写入会在进程内串行化，但不存在一个统一文件对工具、安全、快照、检查点和 trace 进行全局排序。构造跨文件时间线时：

1. 先选择一个 `run_id`。
2. 统一并排序已有的 UTC 时间。
3. 派生报告应保留来源文件和行号。
4. 把缺少结束事件、关联 ID 缺失、JSON 格式错误或 debug 已轮转写成证据限制。

Debug 轮转可能正常移除旧检查点和 trace；长期工具、安全或快照证据缺失则需要单独调查。

## Schema 演进

读取器遇到不支持的 `schema_version` 时应拒绝或明确标记，不能静默按 v1 解释。同一 schema 版本可以增加可选字段；读取器应忽略不认识的字段，但在派生输出中保留它们。

查询方式参见[如何读取审计文件](reading.md)，完整性规则参见[快照与安全联动](snapshots-security.md)。

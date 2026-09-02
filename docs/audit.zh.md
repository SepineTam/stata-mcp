# 审计记录

MCP-for-Stata 会为 MCP 工具调用保存本地、只追加的证据。Audit 主要回答五个实际问题：

1. 哪个工具在什么时间被调用？
2. 客户端自报的名称、版本和 MCP 协议版本是什么？
3. 调用是完成、失败、中断，还是在执行前被阻止？
4. 哪条安全判断、输出元数据、日志或 do-file 快照属于这次调用？
5. 一次缓慢或卡住的调用最后走到了哪个步骤？

Audit v1 回答前四个问题；允许轮转的本地调试黑匣子回答第五个问题。两者属于同一次 MCP 调用时会共享 `run_id`，但保存期限和证据属性不同。

## 证据目录

文件位于项目产物目录中，默认是 `.statamcp/`：

```text
.statamcp/
├── audit/
│   ├── stata_do.jsonl
│   ├── get_data_info.jsonl
│   ├── read_log.jsonl
│   ├── help.jsonl
│   └── security.jsonl
├── snapshot/
│   ├── objects/<完整SHA256>.do
│   └── metadata.jsonl
└── debug/
    ├── checkpoints.jsonl
    ├── checkpoints.jsonl.1
    ├── traces.jsonl
    └── traces.jsonl.1
```

按工具拆分的账本、安全账本和快照 metadata 属于长期 Audit 证据。Debug 文件按大小轮转，是运行诊断，不能替代证据链。

## 五分钟还原一次调用

1. 从对应工具账本开始，例如 `audit/stata_do.jsonl`。
2. 找到 `run_id`，把 `started` 与结束事件配对。
3. 先看结束事件的 `event` 和 `executed`，再解释输出元数据。
4. 遇到阻拦或警告时，根据 `security_event_ids` 联查 `audit/security.jsonl`。
5. 对于 `stata_do`，用同一 `run_id` 查询 `snapshot/metadata.jsonl`，定位并校验 Stata 被要求执行的准确字节。
6. 如果调用缓慢或记录不完整，再用同一 `run_id` 查询允许轮转的 debug 文件，寻找最后一个没有对应完成记录的 `started` 检查点。

只读命令和完整查询示例参见[如何读取审计文件](audit/reading.md)。

## 证据类型

| 证据 | 主要回答的问题 | 保存方式 |
| --- | --- | --- |
| 按工具拆分的 JSONL | 调用了什么，如何结束？ | 只追加；Audit v1 不自动清理 |
| `security.jsonl` | 哪个 Guard 作出了什么判断，原因是什么？ | 只追加 |
| `snapshot/metadata.jsonl` | 哪个来源路径和完整哈希属于某次调用？ | 只追加 |
| `snapshot/objects/` | Stata 实际被要求执行的 do-file 字节是什么？ | 使用完整 SHA-256 寻址，相同内容复用 |
| `debug/checkpoints.jsonl*` | 最后观测到哪个执行步骤？ | 允许轮转 |
| `debug/traces.jsonl*` | 哪些 span 执行了多久，属于哪个 trace？ | 允许轮转 |

## 事件生命周期

一次工具调用通常产生一条 `started` 和一条使用相同 `run_id` 的结束事件：

```text
started -> completed | failed | interrupted | blocked
```

存储层也接受 `timeout`，但当前 middleware 不会单独分类 timeout；没有专门分类的超时异常会写成 `failed`。

只有 `started`、没有结束事件，并不能证明工具从未执行。它表示证据序列不完整，需要继续结合快照、日志、debug 检查点和进程异常判断。

## 信任边界

- 客户端名称和版本由客户端自行报告，只能辅助调查，不能作为身份认证或权限依据。
- 安全结果以 `event` 和 `executed` 为准；`output.is_error` 只描述 MCP 返回值是否以错误形式表示。
- 类似密码、token、secret 的输入字段会替换为 `[REDACTED]`；URL 中的账号、密码、query 和 fragment 会被移除。路径、变量选择、工具名和错误元数据仍可能敏感。
- 应把整个 `.statamcp/` 视为潜在敏感目录，并避免提交到 Git。MCP-for-Stata 默认会在产物根目录创建本地 `.gitignore`。

## 继续阅读

- [如何读取审计文件](audit/reading.md)：只读定位文件并回答常见审计问题。
- [事件与关联关系](audit/events.md)：字段、生命周期、`run_id`、请求元数据、trace 和检查点。
- [快照与安全联动](audit/snapshots-security.md)：完整哈希快照、校验、阻拦事件和隐私边界。
- [本地调试黑匣子](debug-tracing.md)：允许轮转的 OpenTelemetry span、检查点和慢调用线程现场。
- [安全守卫](security.md)：预防规则与 Guard 配置。

## Audit v1 暂不提供

Audit v1 不提供快照重放或恢复、自动保留与归档策略、经过验证的客户端身份，以及独立 timeout 分类。未来若实现重放，必须由用户明确发起、校验来源哈希、创建新的 `run_id`，并保留原始证据不被改写。

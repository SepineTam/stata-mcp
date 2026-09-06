# 快照与安全联动

`stata_do` 还有一层证据约束：Stata 启动前，MCP-for-Stata 会读取源 do-file 的字节，保存使用完整 SHA-256 寻址的对象，并让 Stata 执行该快照。之后即使原路径内容发生变化，也不能改变这次记录对应的执行字节。

## 快照目录

```text
.statamcp/snapshot/
├── objects/
│   └── <64位SHA256>.do
└── metadata.jsonl
```

对象文件名是完整的小写 SHA-256，不是按时间命名的普通副本。不同路径或不同调用只要内容完全相同，就会复用同一个对象；每次调用仍有独立 metadata。

## 快照 metadata

`metadata.jsonl` 每条记录包含：

| 字段 | 含义 |
| --- | --- |
| `schema_version` | 快照 metadata schema 版本，当前是 `1`。 |
| `run_id` | 创建或复用该对象的工具调用。 |
| `tool` | 通常是 `stata_do`。 |
| `created_at` | 从 run 复制的 UTC 开始时间。 |
| `original_path` | 创建快照时解析后的源路径。 |
| `original_name` | 源文件名。 |
| `snapshot_path` | 内容寻址对象的绝对路径。 |
| `sha256` | 存储字节的完整摘要。 |
| `sha256_prefix` | 只用于显示的前8位。 |
| `size_bytes` | 源字节的准确长度。 |
| `reused` | 是否已经存在内容相同且校验通过的对象。 |

快照成功后，`stata_do` 结束事件的 `artifacts` 还会包含 `snapshot_path`、`snapshot_sha256` 和 `snapshot_reused`。

## 校验快照

必须根据完整 `run_id` 选择 metadata，不能只根据原文件名。

=== "macOS"

    ```bash
    RUN_ID='20260830T083015123456Z_2ce5d65f457ce14a'
    RECORD=$(jq -c --arg run_id "$RUN_ID" \
      'select(.run_id == $run_id)' .statamcp/snapshot/metadata.jsonl)
    EXPECTED=$(printf '%s\n' "$RECORD" | jq -r '.sha256')
    SNAPSHOT=$(printf '%s\n' "$RECORD" | jq -r '.snapshot_path')
    [ -f "$SNAPSHOT" ] || SNAPSHOT=".statamcp/snapshot/objects/$EXPECTED.do"

    printf '%s  %s\n' "$EXPECTED" "$SNAPSHOT" | shasum -a 256 -c -
    ```

=== "Linux"

    ```bash
    RUN_ID='20260830T083015123456Z_2ce5d65f457ce14a'
    RECORD=$(jq -c --arg run_id "$RUN_ID" \
      'select(.run_id == $run_id)' .statamcp/snapshot/metadata.jsonl)
    EXPECTED=$(printf '%s\n' "$RECORD" | jq -r '.sha256')
    SNAPSHOT=$(printf '%s\n' "$RECORD" | jq -r '.snapshot_path')
    [ -f "$SNAPSHOT" ] || SNAPSHOT=".statamcp/snapshot/objects/$EXPECTED.do"

    printf '%s  %s\n' "$EXPECTED" "$SNAPSHOT" | sha256sum -c -
    ```

=== "Windows PowerShell"

    ```powershell
    $RunId = '20260830T083015123456Z_2ce5d65f457ce14a'
    $Record = Get-Content .statamcp\snapshot\metadata.jsonl |
      ForEach-Object { $_ | ConvertFrom-Json } |
      Where-Object { $_.run_id -eq $RunId } |
      Select-Object -Last 1

    $Snapshot = $Record.snapshot_path
    if (-not (Test-Path $Snapshot)) {
      $Snapshot = ".statamcp\snapshot\objects\$($Record.sha256).do"
    }
    $Actual = (Get-FileHash $Snapshot -Algorithm SHA256).Hash.ToLower()
    if ($Actual -ne $Record.sha256) { throw 'Snapshot SHA-256 mismatch' }
    ```

哈希校验通过，只能证明当前对象字节与记录的摘要一致；不能证明谁编写了源文件，也不能证明命令在科研意义上正确。

`snapshot_path` 是执行时记录的绝对路径。如果完整产物包后来被移动，以上备用路径会根据完整哈希在归档包内部定位对象。派生报告应记录这次路径迁移，不能为了更新路径而改写历史 metadata。

如果预期文件名的对象已经存在，但对象字节计算出的哈希不同，MCP-for-Stata 会报错，不会覆盖或复用它。

## 哪些情况可以没有快照

安全判断可能在创建快照之前阻止 `stata_do`。例如来源路径被拒绝或命中危险命令时，可以产生有效的 `blocked` 工具事件和安全记录，但没有快照 metadata。这种预期缺失不代表快照丢失。

对于记录为已经执行的 run，快照缺失或校验失败需要调查。应继续查看结束事件 artifacts、Stata 日志、进程日志和存储错误。

## 安全账本

安全判断写入 `.statamcp/audit/security.jsonl`，并与工具结束事件关联。

| 字段 | 含义 |
| --- | --- |
| `security_event_id` | 形如 `sec_<run_id>_<序号>` 的唯一 ID。 |
| `run_id` | 父工具调用。 |
| `timestamp` | UTC 判断时间。 |
| `tool` | 被检查的工具。 |
| `decision` | `blocked` 或 `warning`。 |
| `stage` | 作出判断的安全阶段。 |
| `risk_type` | 稳定风险类别。 |
| `executed` | 该判断后是否继续执行。 |
| `findings` | 安全标识和位置：`line`、`type`、`rule_id`。 |
| `source_path` | 可选的脱敏来源引用。 |
| `source_sha256` | 可选的被检查来源字节摘要。 |

`findings` 会故意省略危险源码原文。

## 追踪一次阻拦

1. 找到 `event` 为 `blocked` 且 `executed` 为 `false` 的工具结束事件。
2. 复制 `security_event_ids` 中的全部值。
3. 在 `security.jsonl` 中匹配每个 `security_event_id`。
4. 确认 `run_id` 和 `tool` 一致。
5. 报告 `stage`、`risk_type`、安全位置以及是否存在快照。除非用户明确要求检查源码，否则不要从其他文件还原或引用危险命令。

```bash
SECURITY_ID='sec_20260830T083015123456Z_2ce5d65f457ce14a_01'
jq -c --arg security_id "$SECURITY_ID" \
  'select(.security_event_id == $security_id)' \
  .statamcp/audit/security.jsonl
```

`stata_do`、`get_data_info` 和 `read_log` 会为支持的路径、URL、包或命令 Guard 拒绝使用同样的跨账本关联方式。

## 保存失败与执行语义

- 工具处理器运行前先保存 started 事件；如果该记录无法写入，审计调用不会正常继续。
- `stata_do` 在启动 Stata 前创建并校验快照；快照保存失败会阻止该次 Stata 启动。
- 缺少结束事件仍然需要调查，因为在保存结束事件失败前，执行可能已经继续推进。
- Debug 检查点和 trace 写入采用 fail-open，不会替代长期 Audit 约束，也不能阻断工具结果。

## 隐私与保留

类似密码、token、secret 的字段会替换成 `[REDACTED]`；URL 的账号、密码、query 和 fragment 会被移除。审计证据仍可能暴露本地路径、文件名、变量选择、客户端自报信息、错误消息和时间。

Audit v1 没有自动保留、轮转、归档、重放或恢复策略。只有在项目明确的数据策略下才能备份或删除证据；不能把 debug 轮转配置当作 Audit 保留策略。

生命周期字段参见[事件与关联关系](events.md)，预防规则参见[安全守卫](../security.md)。

# 如何读取审计文件

本页使用只读命令回答常见审计问题。如果 `PROJECT.FOLDER_TAG` 指向其他产物目录，请把示例中的 `.statamcp` 替换成真实目录。

!!! warning "不要改动源证据"

    不要编辑、截断、轮转、原地排序或重放 `.statamcp/` 中的文件。查询原文件，派生报告写入其他目录。即使账号密码已经脱敏，审计文件仍可能包含敏感的本地路径和研究元数据。

## 1. 找到证据目录

在项目工作目录中运行：

=== "macOS / Linux"

    ```bash
    find .statamcp/audit -maxdepth 1 -type f -name '*.jsonl' -print
    find .statamcp/snapshot -maxdepth 2 -type f -print
    ```

=== "Windows PowerShell"

    ```powershell
    Get-ChildItem .statamcp\audit\*.jsonl
    Get-ChildItem .statamcp\snapshot -Recurse -File
    ```

如果目录不存在，先确认 MCP 服务器的 `WORKING_DIR` 和 `FOLDER_TAG`，然后调用一次工具。产物根目录会在首次保存证据时按需创建。

## 2. 查看最近记录

每个非空行都是一个完整 JSON 对象。

=== "macOS / Linux"

    ```bash
    tail -n 5 .statamcp/audit/stata_do.jsonl
    tail -n 1 .statamcp/audit/stata_do.jsonl | jq .
    ```

=== "Windows PowerShell"

    ```powershell
    Get-Content .statamcp\audit\stata_do.jsonl -Tail 5
    Get-Content .statamcp\audit\stata_do.jsonl -Tail 1 |
      ConvertFrom-Json | ConvertTo-Json -Depth 10
    ```

一个文件的最后一行不一定是整个系统最新的事件。跨文件调查应根据 `run_id` 关联，并比较 UTC `timestamp`。

## 3. 还原一次调用

从工具事件中复制完整 `run_id`：

```text
20260830T083015123456Z_2ce5d65f457ce14a
```

=== "macOS / Linux 与 jq"

    ```bash
    RUN_ID='20260830T083015123456Z_2ce5d65f457ce14a'

    find .statamcp/audit .statamcp/snapshot .statamcp/debug \
      -type f \( -name '*.jsonl' -o -name '*.jsonl.[0-9]*' \) \
      -print 2>/dev/null |
      while IFS= read -r audit_file; do
        jq -c --arg run_id "$RUN_ID" \
          'select(.run_id == $run_id)' "$audit_file"
      done
    ```

=== "Windows PowerShell"

    ```powershell
    $RunId = '20260830T083015123456Z_2ce5d65f457ce14a'
    $Files = @(
      Get-ChildItem .statamcp\audit\*.jsonl
      Get-Item .statamcp\snapshot\metadata.jsonl -ErrorAction SilentlyContinue
      Get-ChildItem .statamcp\debug\*.jsonl* -ErrorAction SilentlyContinue
    )

    $Files | Get-Content | ForEach-Object { $_ | ConvertFrom-Json } |
      Where-Object { $_.run_id -eq $RunId } |
      Sort-Object timestamp |
      ConvertTo-Json -Depth 10
    ```

按以下顺序解释结果：

1. 将工具的 `started` 与结束事件配对。
2. 查看结束事件的 `event`、`executed`、`duration_ms` 和 `error`。
3. 根据 `security_event_ids` 联查对应 `security_event_id`。
4. 对于 `stata_do`，根据同一 `run_id` 联查快照 metadata。
5. 只有需要定位具体步骤时，才继续读取 debug 检查点。

## 4. 列出被阻止的调用

权威阻拦条件是 `event == "blocked"` 且 `executed == false`。

=== "macOS / Linux"

    ```bash
    jq -c 'select(.event == "blocked" and .executed == false)' \
      .statamcp/audit/stata_do.jsonl \
      .statamcp/audit/get_data_info.jsonl \
      .statamcp/audit/read_log.jsonl
    ```

=== "Windows PowerShell"

    ```powershell
    Get-ChildItem .statamcp\audit\*.jsonl | Get-Content |
      ForEach-Object { $_ | ConvertFrom-Json } |
      Where-Object { $_.event -eq 'blocked' -and $_.executed -eq $false } |
      Select-Object timestamp, tool, run_id, security_event_ids
    ```

Guard 可以用正常 MCP 结果解释拒绝，此时 `output.is_error` 可能仍是 `false`。不能只根据该字段统计安全阻拦。

## 5. 查找没有结束事件的 run

没有配对结束事件的 `started` 是调查线索，不能单独证明工具执行过或没有执行。

```bash
jq -s '
  group_by(.run_id)
  | map(select(
      any(.[]; .event == "started")
      and (any(.[];
        .event == "completed"
        or .event == "failed"
        or .event == "interrupted"
        or .event == "blocked"
        or .event == "timeout") | not)
    ))
  | .[]
' \
  .statamcp/audit/stata_do.jsonl \
  .statamcp/audit/get_data_info.jsonl \
  .statamcp/audit/read_log.jsonl \
  .statamcp/audit/help.jsonl
```

对于每条结果，必须继续根据相同 `run_id` 查询快照 metadata、Stata 日志、检查点、trace 和进程日志后再下结论。

## 6. 跨平台 Python 备用方案

没有 jq 时，可把下面脚本保存在 `.statamcp/` 之外，文件名例如 `find_audit_run.py`：

```python
from __future__ import annotations

import json
import sys
from pathlib import Path

artifact_root = Path(sys.argv[1])
run_id = sys.argv[2]
patterns = (
    "audit/*.jsonl",
    "snapshot/metadata.jsonl",
    "debug/*.jsonl*",
)

matches: list[dict[str, object]] = []
for pattern in patterns:
    for audit_file in artifact_root.glob(pattern):
        with audit_file.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("run_id") == run_id:
                    matches.append(
                        {
                            "file": audit_file.as_posix(),
                            "line": line_number,
                            "record": record,
                        }
                    )

print(json.dumps(matches, ensure_ascii=False, indent=2))
```

运行方式：

=== "macOS / Linux"

    ```bash
    python3 find_audit_run.py .statamcp 20260830T083015123456Z_2ce5d65f457ce14a
    ```

=== "Windows"

    ```powershell
    py find_audit_run.py .statamcp 20260830T083015123456Z_2ce5d65f457ce14a
    ```

该脚本只读取源文件并输出派生视图，不会改写证据。如果整个产物目录被移动到归档位置，快照 metadata 可能仍保留历史绝对路径；此时应根据完整 `sha256` 在归档包自己的 `snapshot/objects/` 下重新定位对象，并在派生报告中记录该路径迁移。

## 调查检查表

- 确认产物根目录和工具账本。
- 保留完整 `run_id`，不要只按文件名关联。
- 配对生命周期事件并查看 `executed`。
- 根据安全 ID 和快照 metadata 继续关联。
- 把 do-file 对象当作准确源码证据前先校验 SHA-256。
- Debug 用于定位步骤，不属于长期证据。
- 最终报告应明确记录缺失文件、格式错误行和未配对事件等限制。

字段说明参见[事件与关联关系](events.md)，完整性检查参见[快照与安全联动](snapshots-security.md)。

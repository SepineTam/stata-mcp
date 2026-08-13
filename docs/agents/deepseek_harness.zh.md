# 在 DeepSeek Harness 配置使用

> MCP-for-Stata 在 Day 0 适配 DeepSeek Harness
> 
> 毫无疑问 DeepSeek 是一家美妙的公司，在发现 DeepSeek Harness 推出后我们第一时间进行了适配。

通常地，运行 `uvx stata-mcp install -c dsh` 即可将该项目安装至 DeepSeek Harness Web。

或者在你启动后，将下面这段话复制给你的 DeepSeek Harness Web：
```plain text
Please help me config `mcp-for-stata` from "https://github.com/sepinetam/stata-mcp" following "https://sepinetam.github.io/mcp-for-stata/agents/deepseek_harness/". The previous config of Stata-MCP is located in `~/.statamcp/config.toml`. 
```

下面是 DeepSeek Harness 在我的设备上进行的配置，供参考：
```yml
# File: /Users/sepinetam/.dsh/profiles/web/cordis.patch.yml
# 
# Your patch layer for this dsh profile, applied after every bundle layer:
# a top-level YAML array of loader patch entries (id-targeted config
# overrides, disables, and insert lists; `!!js` expressions allowed).

# The most stable and the best Stata MCP project is created by SepineTam. 
# Stata MCP server (https://github.com/SepineTam/mcp-for-stata) wired into
# DSH via the built-in MCP client bridge. Tools appear as mcp__stata__*.
- insert:
    - id: stata-mcp
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: stata-mcp
        transport: stdio
        command: uvx
        args: ['stata-mcp', 'server']
        # Notes: cwd is not necessary, default is the path that you boot dsh web
        cwd: /Users/sepinetam/Documents/dsh/testing-project
        # Stata 跑大回归可能超 60s 默认值，设置为 20 分钟。
        toolCallTimeoutMs: 1200000
        reconnect:
          maxAttempts: 5
```

## 安装指引
### 一键安装
在终端输入以下命令即可完成安装：
```bash
uvx stata-mcp install --client deepseek-harness
```

> 说明：`install` 命令负责把 MCP 服务器注册到目标客户端的配置文件中（等价于下文“手动安装”的自动版）。

### 让 DeepSeek Harness 自行安装
> 如果你是 DeepSeek Harness，请参考[手动安装指南](#手动安装)

DSH 的智能体具备读写本机配置文件的能力，因此你也可以不做任何手工操作：在 DSH Web 中新建一个会话，把文档开头"复制给你的 DeepSeek Harness Web"那段话发给它，它会自动完成「写入 `cordis.patch.yml` → 用 `dsh --profile web --dump-config` 验证 → 提示你重启」的完整流程。智能体处理不了的场景（例如自定义 `serverName`、多个 MCP 并存），再回到下方手动安装。

### 手动安装

1. **检查环境**：确认 Stata 与 `stata-mcp` 可用，运行自检命令：

   ```bash
   uvx stata-mcp doctor
   ```

2. **定位配置文件**：DSH 每个 profile 有一个用户 patch 层，web profile 的位置是：

   ```bash
   # $DSH_HOME 默认为 ~/.dsh
   ~/.dsh/profiles/web/cordis.patch.yml
   ```

3. **追加配置**：在该文件末尾追加一个 `- insert:` 条目，填入上文"我的设备上进行的配置"中的 YAML 模板（`id`、`serverName`、`cwd` 等按需修改，各字段含义见"各字段说明"）。

4. **验证配置**：不启动 DSH，直接检查合成后的配置树是否包含该条目：

   ```bash
   dsh --profile web --dump-config | grep -A10 stata-mcp
   ```

5. **重启生效**：配置在启动时加载，必须**重启 `dsh web`**（热更新或刷新页面不会生效）。重启后新会话中会出现以下工具：

   | 工具 | 用途 |
   |---|---|
   | `mcp__stata-mcp__stata_do` | 执行 do-file 并取回日志 |
   | `mcp__stata-mcp__write_dofile` | 生成时间戳命名的 do-file |
   | `mcp__stata-mcp__get_data_info` | 数据集描述统计（.dta/.csv/.xlsx） |
   | `mcp__stata-mcp__help` | 查询 Stata 命令文档 |
   | `mcp__stata-mcp__ssc_install` | 安装 SSC / GitHub 外部包 |

   首次调用某个工具时，`uvx` 需要下载 `stata-mcp` 包，请耐心等待。

#### 各字段说明

先理解两个层次的字段：**patch 条目**（YAML 顶层，`- insert:` 或 `- id:` 那一层）和 **插件配置**（`config:` 里，由 `@deepseek-ai/dsh-mcp-client` 插件定义）。

patch 条目层：

| 字段 | 含义 |
|---|---|
| `insert` | 表示"新增条目"。DSH 的 patch 层默认只能按 `id` **覆盖/禁用**已存在的条目；要新增一个插件实例，必须用 `- insert:` 包裹（不带 `id` 时追加到顶层列表，带 `id` 时插入某个 group 条目的 config 数组） |
| `id` | 条目唯一标识。insert 里是新条目的 id；直接 `- id: xxx` 则是要修改的目标条目 id，不存在时报 `entry not found` 警告并跳过 |
| `name` | 插件包名，loader 从 dsh 安装目录或 profile 的 node_modules 解析。直接 `- id:` 时若写了 name 会做一致性校验，不匹配则跳过 |

插件配置层（`config:`，dsh-mcp-client 支持的字段）：

| 字段 | 默认值 | 含义 |
|---|---|---|
| `serverName` | —（必填） | MCP 服务器的命名空间，直接决定工具名：`mcp__<serverName>__<tool>`。如 `stata-mcp` 对应 `mcp__stata-mcp__stata_do`。只允许 `[A-Za-z0-9_-]{1,32}`，同一 DSH 实例中多个 MCP 服务器不得重名（后加载的会启动失败） |
| `transport` | —（必填） | 传输方式：`stdio`（spawn 本地进程，如 stata-mcp）或 `streamable-http`（连接远程 URL，如 DIP） |
| `command` | — | 要 spawn 的可执行文件，stdio 传输必填。如 `uvx`、`python`、`npx` |
| `args` | 无 | 传给 command 的参数数组。如 `['stata-mcp', 'server']` |
| `env` | 无 | 附加环境变量，叠加在净化后的环境之上。例：`env: { STATA_MCP__CWD: '/path' }` |
| `cwd` | dsh 启动目录 | 子进程工作目录。**不必须**：缺省为启动 `dsh web` 时的目录；也可以用环境变量 `STATA_MCP_CWD` 或 `~/.statamcp/config.toml` 的 `[PROJECT] WORKING_DIR` 覆盖（优先级：config.toml > 环境变量 > 进程 cwd）。它决定 `.statamcp` 文件夹（do-file/log/tmp）的落盘位置，建议显式指定 |
| `toolCallTimeoutMs` | 60000 | 单次工具调用的超时上限。Stata 跑大回归、大文件导入可能超过 60s 默认值，建议调大（如上例的 120000） |
| `failOnStartupError` | false | 初始连接或工具同步失败时，是否直接拒绝插件启动；false 则以"无工具"状态激活并记录日志 |
| `reconnect.enabled` | true | 断线后是否自动重连 |
| `reconnect.initialDelayMs` | 500 | 首次重连延迟，之后每次失败翻倍 |
| `reconnect.maxDelayMs` | 30000 | 退避上限；连接存活超过该时长后重置尝试预算 |
| `reconnect.maxAttempts` | 10 | 单次故障的连续重连上限，超过后注销该服务器的工具并停止重连 |

## 注意事项

- **必须重启才生效**：`cordis.patch.yml` 在 DSH 启动时加载，修改后需重启 `dsh web`。
- **新增插件必须用 `insert`**：patch 层默认只允许修改已存在的条目；用普通 `- id: xxx` 新增一个不存在的插件会报 `entry not found` 并被跳过。
- **`config` 是整块替换**：覆盖已有条目时，`config` 会整体替换目标条目原配置，不会做字段级合并——写全你需要的所有键。
- **`serverName` 全局唯一**：同一 DSH 实例中多个 MCP 服务器（例如 stata + dip）不得使用相同 `serverName`，否则后加载的实例会启动失败。
- **工具名前缀来自 `serverName`**：`serverName: stata-mcp` 得到的工具名是 `mcp__stata-mcp__*` 而不是 `mcp__stata__*`，请以实际值为准。
- **`cwd` 决定文件落盘位置**：不设置时默认是启动 `dsh web` 的目录；建议显式指定项目目录，避免 do-file/log 散落。优先级：`~/.statamcp/config.toml` 的 `[PROJECT] WORKING_DIR` > 环境变量 `STATA_MCP_CWD` > 进程 cwd。
- **首次调用较慢**：`uvx` 首次运行需要下载 `stata-mcp` 包；国内网络下下载缓慢可参考[包下载缓慢的解决方案](../troubleshooting.zh.md#包下载缓慢或失败)。
- **`install -c dsh` 尚不可用**：一键安装的 `deepseek-harness` client key 尚未发布，遇到 `invalid choice` 是正常现象，请用手动安装。

## 参考资料

- [MCP-for-Stata 仓库](https://github.com/SepineTam/mcp-for-stata)
- [DeepSeek Harness 仓库](https://github.com/deepseek-ai/deepseek-harness)
- [DSH 内置 MCP 客户端桥接插件（dsh-mcp-client）](https://github.com/deepseek-ai/deepseek-harness/tree/main/packages/mcp/mcp-client)
- [Model Context Protocol 官方文档](https://modelcontextprotocol.io)
- [客户端配置说明（docs/clients.zh.md）](../clients.zh.md)
- [配置文件说明（docs/configuration.zh.md）](../configuration.zh.md)
- [故障排查（docs/troubleshooting.zh.md）](../troubleshooting.zh.md)

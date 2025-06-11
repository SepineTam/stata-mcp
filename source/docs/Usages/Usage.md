# Usage Catalog
- [中文](#使用指南中文)
  - [macOS](#macos)
  - [Windows](#windows)
- [English](#usage-guide-english)
  - [macOS](#macos-1)
  - [Windows](#windows-1)

# 使用指南（中文）
## macOS
### 视频演示

* YouTube
* bilibili
* 官方网站

### 准备工作
#### 必需品

* **Stata 17+**
* **Python 3.11+**（低版本可能可行，但本项目未经过测试）
* **uv** 和 **uvx**（推荐使用，以避免不必要的配置问题）
* 任意支持 MCP 的客户端，如 Claude 桌面版、Cursor、Cherry Studio 等

#### 获取项目

```bash
git clone https://www.github.com/sepinetam/stata-mcp.git
cd stata-mcp
```

#### 环境配置

1. 确保已安装 Stata 软件，并具有有效许可证；如使用非官方授权，请阅读本项目的[开源许可](../../../LICENSE)。
2. 在项目目录下运行：

```bash
uvx stata-mcp --usable
```

* 若所有检查通过，则可使用默认配置。
* 若 `stata_cli` 项显示 **FAILED**，则需在配置中指定 Stata 可执行文件路径。

3. （可选）可直接通过以下命令确认：

```bash
/usr/local/bin/stata-se  # 或者 stata-mp、stata-ci 等，视安装版本而定
```

### Stata-MCP 配置

#### 通用配置

> Stata-MCP 支持自动查找本地 Stata 路径，无需手动指定版本号。

```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": ["stata-mcp"]
    }
  }
}
```

> 若需指定 Stata 可执行文件路径或自定义文档保存目录，可添加 `env`：

```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": ["stata-mcp"],
      "env": {
        "stata_cli": "/usr/local/bin/stata-se",
        "documents_path": "~/Documents/stata-mcp"
      }
    }
  }
}
```

#### Claude 配置

同通用配置。若需指定 Stata CLI 路径，只需在 `env` 中添加 `stata_cli`（可选：`documents_path`）。

#### Cherry Studio 配置

通过 GUI 填写：

```text
name: Stata-MCP
command: uvx
args:
  - stata-mcp
envs:
  stata_cli="/usr/local/bin/stata-se"
  documents_path="~/Documents/stata-mcp"
```

#### ChatWise 配置

支持剪贴板 JSON 导入，或直接输入：

```bash
uvx stata-mcp
```

如需指定 CLI 路径：

```bash
uvx stata-mcp --env stata_cli="/usr/local/bin/stata-se"
```

---

## Windows

### 视频演示

* YouTube
* bilibili
* 官方网站

### 准备工作

#### 必需品

* **Stata 17+**
* **Python 3.11+**（低版本可能可行，但本项目未经过测试）
* **uv** 和 **uvx**（推荐使用，以避免不必要的配置问题）
* 任意支持 MCP 的客户端，如 Claude 桌面版、Cursor、Cherry Studio 等

#### 获取项目

```bash
git clone https://www.github.com/sepinetam/stata-mcp.git
cd stata-mcp
```

#### 环境配置

1. 安装 Stata，并确保可通过命令行（CMD 或 PowerShell）启动（如 `Stata.exe`、`StataMP.exe`、`StataSE.exe`）。
2. 在项目目录下运行：

```bash
uvx stata-mcp --usable
```

* 全部检查通过后，可使用默认配置。
* 若 `stata_cli` 显示 **FAILED**，请记录 Stata 可执行文件的完整路径，并在配置中指定。

### Stata-MCP 配置

#### 通用配置

> 若 Stata 安装在默认位置（仅盘符不同），可使用以下简单配置：

```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": ["stata-mcp"]
    }
  }
}
```

> 若需指定自定义 Stata 路径或文档目录，添加 `env`：

```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": ["stata-mcp"],
      "env": {
        "stata_cli": "C:\\Program Files\\Stata18\\StataSE.exe",
        "documents_path": "C:\\Users\\YourUser\\Documents\\stata-mcp"
      }
    }
  }
}
```

#### Claude 配置

同通用配置，将 `stata_cli`（及可选的 `documents_path`）添加至 `env`。

#### Cherry Studio 配置

在 GUI 中填写：

```text
name: Stata-MCP
command: uvx
args:
  - stata-mcp
envs:
  stata_cli="C:\\Program Files\\Stata18\\StataSE.exe"
  documents_path="C:\\Users\\YourUser\\Documents\\stata-mcp"
```

#### ChatWise 配置

可粘贴 JSON 或直接在命令行输入：

```bash
uvx stata-mcp
```

指定 CLI 路径：

```bash
uvx stata-mcp --env stata_cli="C:\\Program Files\\Stata18\\StataSE.exe"
```

---

更多信息请参阅 [Advanced](Advanced.md#高级功能)。


# Usage Guide (English)
## macOS
### Video Demonstration
- [YouTube]()
- [bilibili]()
- [Official Website]()

### Prerequisites
#### Requirements
- Stata 17+
- Python 3.11+ (lower versions might work, but this project has not been tested with lower versions)
- uv and uvx(recommended for setup to avoid unnecessary configuration issues)
- Any client that supports MCP, such as Claude desktop app, Cursor, Cherry Studio, etc.

#### Check your environments
```bash
uvx stata-mcp --usable
```
If all of them are PASSED, it means you can use it directory with the default config, if you find the stata_cli FAILED, you can config your env-variable in your shell, or you can config it in your MCP client later.

#### Environment Setup
1. Ensure that you have Stata software installed on your computer (with a valid Stata license. If you're using a non-official Stata license, please make sure to read the [open source license](../../../LICENSE) of this project)
2. Install Stata terminal tools: In Stata's menu bar, click on Stata, then select "Install Terminal Tools..." (as shown in the image below)

![](../../img/usage_01.png)

Then, 

![](../../img/macOS_cli.png)

3. Verify Stata CLI installation by running `uv run usable.py` in the project directory. If no exceptions are thrown, it means the usability test has passed.
4. Alternatively, you can check if it's available by using `/usr/local/bin/stata-se` directly in the terminal (replace "se" with your Stata version). You should see a return similar to the one shown below:

![](../../img/usage_02.png)

### Stata-MCP Configuration
#### General Configuration
> Currently, Stata-MCP supports automatically finding the Stata path, so users don't need to provide version numbers. The configuration below allows for quick setup.
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": [
        "stata-mcp"
      ]
    }
  }
}
```

> If you want to specify the path to the Stata executable, or you want to make the certain file saving path, use the following configuration:
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": [
        "stata-mcp"
      ],
      "env": {
        "stata_cli": "/path/to/your/stata-cli",
        "documents_path": "~/Documents/stata-mcp"
      }
    }
  }
}
```

> Notes: <br>
> for Windows, you should find the exe file if you want to use the certain version of your Stata if there are lots of different version on your computer;<br>
> for macOS, you could not use the two different `stata-mp` because it is a cli tool, but if you have a StataSE 17 and a StataMP 19, you can use both of them. 

#### Claude Configuration
Same as the general configuration. To specify the Stata CLI path, and add `stata_cli` to the `env`.
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": [
        "stata-mcp"
      ],
      "env": {
        "stata_cli": "/path/to/your/stata-cli",
        "documents_path": "~/Documents/stata-mcp"
      }
    }
  }
}
```

#### Cherry Studio Configuration
In Cherry Studio, it's recommended to use the GUI to fill in:
```text
name: Stata-MCP
command: uvx
args:
  stata-mcp
envs:
  stata_cli="/path/to/your/stata-cli"
  documents_path=~/Documents/stata-mcp
```

If you need to specify the Stata CLI path, add `stata_cli` to the `env`.

> Notes:<br>
> Maybe there is something wrong on CherryStudio, here is an alternative method to config it:
> you can con down the source code and use it or download it via pip
```bash
# for first download it
pip install stata-mcp

# for upgrade it
pip install --upgrade stata-mcp
```
Then you can config it like this:
```text
name: Stata-MCP
command: stata-mcp
(no args)
envs:
  stata_cli="/path/to/your/stata-cli"
  documents_path=~/Documents/stata-mcp
```

#### ChatWise Configuration
ChatWise not only supports JSON import via clipboard (in which case you can directly copy the general configuration after modifying the repo path),
but you can also directly type the command:
```bash
uvx stata-mcp
```

Similarly, if you need to specify the Stata CLI path, add `stata_cli` to the `env`:

### More
Refer to [Advanced](Advanced.md#advanced)


## Windows
## Windows

### Video Demonstration

* [YouTube]()
* [bilibili]()
* [Official Website]()

### Prerequisites

#### Requirements

* **Stata 17+**
* **Python 3.11+** (lower versions might work, but this project has not been tested with them)
* **uv and uvx** (recommended for setup to avoid unnecessary configuration issues)
* Any MCP-compatible client (e.g., Claude desktop app, Cursor, Cherry Studio)

### Check Your Environment

```bash
uvx stata-mcp --usable
```

If all checks pass, you can proceed with the default configuration. If `stata_cli` shows **FAILED**, you’ll need to specify its path in your config (see below).

### Environment Setup

1. **Install Stata** on your Windows machine (ensure you have a valid license; if using an unofficial license, please review this project’s [open-source license](../../../LICENSE)).
2. **No terminal tools** are required on Windows—just verify you can launch Stata from Command Prompt or PowerShell.
3. If `uvx stata-mcp --usable` does not open Stata, locate your Stata executable (`Stata.exe`, `StataMP.exe`, or `StataSE.exe`) and note its full path for the configuration step.

---

### Stata-MCP Configuration

#### General Configuration

> If Stata is installed in the **default location** (e.g., only the drive letter differs), use the simple setup below.
> On Windows, avoid Chinese characters and spaces in paths; be mindful of `\\` vs `/`.

```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": [
        "stata-mcp"
      ]
    }
  }
}
```

> To specify a **custom Stata path** or set a **documents directory**, add an `env` section:

```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": [
        "stata-mcp"
      ],
      "env": {
        "stata_cli": "C:\\Program Files\\Stata18\\StataSE.exe",
        "documents_path": "C:\\Users\\YourUser\\Documents\\stata-mcp"
      }
    }
  }
}
```

#### Claude Configuration

Same as General Configuration. To override the Stata executable path, include the `stata_cli` (and optionally `documents_path`) in the `env`.

#### Cherry Studio Configuration

Use the GUI in Cherry Studio:

```text
name: Stata-MCP
command: uvx
args:
  - stata-mcp
envs:
  stata_cli="C:\\Program Files\\Stata18\\StataSE.exe"
  documents_path="C:\\Users\\YourUser\\Documents\\stata-mcp"
```

#### ChatWise Configuration

You can import JSON via clipboard or type the command directly:

```bash
uvx stata-mcp
```

To specify the Stata path:

```bash
uvx stata-mcp --env stata_cli="C:\\Program Files\\Stata18\\StataSE.exe"
```

---

### More

Refer to [Advanced](Advanced.md#advanced) for additional features and customization.

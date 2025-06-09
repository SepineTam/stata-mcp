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
- [YouTube]()
- [bilibili]()
- [Official Website]()

### 准备工作
#### 必需品
- Stata 17+
- python 3.11+（相对较低的版本或许可行，但是本项目并没有在低版本下进行测试）
- uv（推荐使用uv进行配置以避免在配置上不必要的麻烦）
- 任一支持MCP的客户端，如Claude桌面版、Cursor、Cherry Studio等

#### 获取项目
```bash
git clone https://www.github.com/sepinetam/stata-mcp.git
cd stata-mcp
```

#### 环境配置
1. 请确保你的计算机已经安装 Stata 软件（并具有有效的 Stata 许可证，如您使用非正版授权的 Stata 请务必阅读本项目的[开源许可](../../../LICENSE)）
2. 安装Stata终端工具，具体流程为：在Stata的菜单栏中点击Stata，选择"安装终端工具..."（如下图所示）

![](../../img/usage_01.png)

3. 验证 Stata cli 的安装，在该项目目录下运行 `uv run usable.py` ，如未抛出异常则代表可用性通过。
4. 或者你可以在终端中使用 `/usr/local/bin/stata-se` 直接判断是否可用（其中se换成你的stata版本），你将会看到下面的这样的返回

![](../../img/usage_02.png)

### Stata-MCP 配置
#### 通用配置
> 目前，Stata-MCP已支持自动去寻找Stata的路径，不需要用户提供版本号，如下的配置即可快速使用。
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/the/repo/",
        "run",
        "__init__.py"
      ]
    }
  }
}
```

> 如果你想要指定Stata可执行文件的路径，按照如下配置：
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/the/repo/",
        "run",
        "__init__.py",
        "True"
      ],
      "env": {
        "stata_cli": "/usr/local/bin/stata-se"
      }
    }
  }
}
```
#### Claude
与通用配置相同，如要指定Stata CLI的路径在 `args` 中添加 `True` 并添加 `stata_cli` 在 `env` 中。
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/the/repo/",
        "run",
        "__init__.py"
      ]
    }
  }
}
```

#### Cherry Studio配置
Cherry Studio中推荐使用GUI填写
```text
name: Stata-MCP
command: uv
args:
  run
  /path/to/the/repo/stata_mcp.py
```

如果你要指定Stata CLI的路径，同样地在参数中加入 `True`，并在 `env` 中加入 `stata_cli`

#### ChatWise 配置
ChatWise不仅支持通过剪切板的json导入（这种情况下你可以在修改了repo的路径后直接复制通用配置），
这里建议可以在命令里直接键入
```bash
uv run /path/to/the/repo/__init__.py
```

同样，如果你要指定Stata CLI的路径，换成如下命令，并在 `env` 中加入 `stata_cli`
```bash
uv run /path/to/the/repo/__init__.py True
```

### 更多
参考[Advanced](Advanced.md#高级功能)


## Windows
> ~~作者的瞎逼逼：如果可以，这边建议您更换一台macOS的电脑~~

### 视频演示
- [YouTube]()
- [bilibili]()
- [Official Website]()

### 准备工作
#### 必需品
- Stata 17+
- python 3.11+（相对较低的版本或许可行，但是本项目并没有在低版本下进行测试）
- uv（推荐使用uv进行配置以避免在配置上不必要的麻烦）
- 任一支持MCP的客户端，如Claude桌面版、Cursor、Cherry Studio等

#### 获取项目
```bash
git clone https://www.github.com/sepinetam/stata-mcp.git
cd stata-mcp
```

#### 环境配置
1. 确保你的Windows电脑上有 Stata 软件（并具有有效的 Stata 许可证，如果您使用非正版 Stata 许可，请务必阅读本项目的[开源许可](../../../LICENSE)）
2. Windows和macOS不同，不需要安装终端工具，而只需要确保你可以在终端或者Power Shell里确保能通过命令行打开Stata即可。
3. 你可以运行 `uv run usable.py`，如果打开了Stata则代表测试通过。如果未能正确打开，请手动寻找Stata.exe文件（或StataMP.exe、StataSE.exe等，这是依据你的版本而定的）

### Stata-MCP配置
#### 通用配置
> 如果你的Stata安装在**默认路径**或者是在默认路径下只改变了盘符，请直接按照默认配置以避免不必要的麻烦
> 
> Windows 系统下请注意避免在路径中出现中文和空格，同时请注意`/` 和 `\\`的使用

```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\the\\repo",
        "run",
        "__init__.py"
      ]
    }
  }
}
```

> 如果你是自定义的Stata安装路径，请按照如下配置：
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\the\\repo",
        "run",
        "__init__.py",
        "True"
      ],
      "env": {
        "stata_cli": "C:\\Program Files\\Stata18\\StataSE.exe"
      }
    }
  }
}
```
其中stata_cli为你的Stata可执行文件(`.exe`文件)的绝对路径。如果你有任何疑问请提交[PR](https://github.com/sepinetam/stata-mcp/pulls)

#### Claude
与通用配置相同，如要指定Stata可执行文件路径，在 `args` 中添加 `True` 并添加 `stata_cli` 在 `env` 中。
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\the\\repo",
        "run",
        "__init__.py"
      ]
    }
  }
}
```

#### Cherry Studio配置
Cherry Studio中推荐使用GUI填写
```text
name: Stata-MCP
command: uv
args:
  run
  "C:\\path\\to\\the\\repo\\stata_mcp.py"
```
如果你要指定Stata可执行文件的路径，同样地在参数中加入 `True`，并在 `env` 中加入 `stata_cli`

#### ChatWise 配置
ChatWise不仅支持通过剪切板的json导入（这种情况下你可以在修改了repo的路径后直接复制通用配置），
这里建议可以在命令里直接键入
```bash
uv run "C:\\path\\to\\the\\repo\\stata_mcp.py"
```

同样，如果你要指定Stata可执行文件的路径，换成如下命令，并在 `env` 中加入 `stata_cli`
```bash
uv run "C:\\path\\to\\the\\repo\\stata_mcp.py" True
```

### 更多
参考[Advanced](Advanced.md#高级功能)


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
- uv (recommended for setup to avoid unnecessary configuration issues)
- Any client that supports MCP, such as Claude desktop app, Cursor, Cherry Studio, etc.

#### Getting the Project
```bash
git clone https://www.github.com/sepinetam/stata-mcp.git
cd stata-mcp
```

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
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/the/repo/",
        "run",
        "__init__.py"
      ]
    }
  }
}
```

> If you want to specify the path to the Stata executable, use the following configuration:
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/the/repo/",
        "run",
        "__init__.py",
        "True"
      ],
      "env": {
        "stata_cli": "/usr/local/bin/stata-se"
      }
    }
  }
}
```

#### Claude Configuration
Same as the general configuration. To specify the Stata CLI path, add `True` to the `args` and add `stata_cli` to the `env`.
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/the/repo/",
        "run",
        "__init__.py"
      ]
    }
  }
}
```

#### Cherry Studio Configuration
In Cherry Studio, it's recommended to use the GUI to fill in:
```text
name: Stata-MCP
command: uv
args:
  run
  /path/to/the/repo/stata_mcp.py
```

If you need to specify the Stata CLI path, add `True` to the parameters and add `stata_cli` to the `env`.

#### ChatWise Configuration
ChatWise not only supports JSON import via clipboard (in which case you can directly copy the general configuration after modifying the repo path),
but you can also directly type the command:
```bash
uv run /path/to/the/repo/__init__.py
```

Similarly, if you need to specify the Stata CLI path, use the command below and add `stata_cli` to the `env`:
```bash
uv run /path/to/the/repo/__init__.py True
```

### More
Refer to [Advanced](Advanced.md#advanced)


## Windows
> ~~Author's note: If possible, we recommend using a macOS computer instead~~

### Video Demonstration
- [YouTube]()
- [bilibili]()
- [Official Website]()

### Prerequisites
#### Requirements
- Stata 17+
- Python 3.11+ (lower versions might work, but this project has not been tested with lower versions)
- uv (recommended for setup to avoid unnecessary configuration issues)
- Any client that supports MCP, such as Claude desktop app, Cursor, Cherry Studio, etc.

#### Getting the Project
```bash
git clone https://www.github.com/sepinetam/stata-mcp.git
cd stata-mcp
```

#### Environment Setup
1. Ensure that you have Stata software installed on your Windows computer (with a valid Stata license. If you're using a non-official Stata license, please make sure to read the [open source license](../../../LICENSE) of this project)
2. Unlike macOS, Windows doesn't require installing terminal tools. You only need to ensure that you can open Stata via command line in Terminal or PowerShell.
3. You can run `uv run usable.py` - if Stata opens, the test has passed. If it doesn't open correctly, manually look for the Stata.exe file (or StataMP.exe, StataSE.exe, etc., depending on your version)

### Stata-MCP Configuration
#### General Configuration
> If Stata is installed in the **default path** or if you only changed the drive letter in the default path, please use the default configuration to avoid unnecessary issues.
> 
> On Windows, please avoid using Chinese characters and spaces in paths, and pay attention to the use of `/` and `\\`.

```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\the\\repo",
        "run",
        "__init__.py"
      ]
    }
  }
}
```

> If you have a custom Stata installation path, use the following configuration:
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\the\\repo",
        "run",
        "__init__.py",
        "True"
      ],
      "env": {
        "stata_cli": "C:\\Program Files\\Stata18\\StataSE.exe"
      }
    }
  }
}
```
Where `stata_cli` is the absolute path to your Stata executable (`.exe` file). If you have any questions, please submit a [PR](https://github.com/sepinetam/stata-mcp/pulls).

#### Claude Configuration
Same as the general configuration. To specify the Stata executable path, add `True` to the `args` and add `stata_cli` to the `env`.
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\the\\repo",
        "run",
        "__init__.py"
      ]
    }
  }
}
```

#### Cherry Studio Configuration
In Cherry Studio, it's recommended to use the GUI to fill in:
```text
name: Stata-MCP
command: uv
args:
  run
  "C:\\path\\to\\the\\repo\\stata_mcp.py"
```
If you need to specify the Stata executable path, add `True` to the parameters and add `stata_cli` to the `env`.

#### ChatWise Configuration
ChatWise not only supports JSON import via clipboard (in which case you can directly copy the general configuration after modifying the repo path),
but you can also directly type the command:
```bash
uv run "C:\\path\\to\\the\\repo\\stata_mcp.py"
```

Similarly, if you need to specify the Stata executable path, use the command below and add `stata_cli` to the `env`:
```bash
uv run "C:\\path\\to\\the\\repo\\stata_mcp.py" True
```

### More
Refer to [Advanced](Advanced.md#advanced)

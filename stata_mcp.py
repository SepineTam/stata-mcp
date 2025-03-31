from typing import List, Optional, Union
import subprocess
import sys
import os
import platform
import tempfile
from datetime import datetime

from mcp.server.fastmcp import FastMCP

from config import *

mcp = FastMCP('stata-mcp')

args = sys.argv[1:]
if len(args) < 2:
    sys.exit("错误：必须提供版本号和版本类型，如uv run stata_mcp.py 17 se")

version_number = args[0]  # 第一个参数是版本号（如17）
version_type = args[1]  # 第二个参数是版本类型（如se）

# 初始化可选参数（默认为None）
stata_cli_path = None
log_file_path = None
operating_system = None
dofile_base_path = None
result_doc_path = None

for arg in args[2:]:
    if arg.startswith("stata_cli_path="):
        stata_cli_path = arg.split("=", 1)[1]  # 提取路径部分
    elif arg.startswith("log_file_path="):
        log_file_path = arg.split("=", 1)[1]  # 提取日志路径
    elif arg.startswith("operating_system="):
        operating_system = arg.split("=", 1)[1].lower()
    elif arg.startswith("dofile_base_path="):
        dofile_base_path = arg.split("=", 1)[1]
    elif arg.startswith("result_doc_path="):
        result_doc_path = arg.split("=", 1)[1]
    else:
        print(f"警告：未知参数 `{arg}`，已忽略")

if operating_system is None:
    os_name = platform.system()  # 返回 'Windows', 'Linux', 'Darwin'(macOS) 等
    if os_name == "Windows":
        operating_system = "windows"
    elif os_name == "Darwin":
        operating_system = "macos"
    elif os_name == "Linux":
        operating_system = "lunix"
    else:
        operating_system = None
        print("未知操作系统")

if operating_system != "macos":
    sys.exit("目前仅支持macOS，如确定你的电脑是macOS，请加上参数operating_system=macos")

if stata_cli_path is None:
    if operating_system == "macos":
        stata_cli_path = f"/Applications/Stata/StataSE.app/Contents/MacOS/stata-{version_type}"
        # stata_cli_path = f"/usr/local/bin/stata-{version_type}"
    elif operating_system == "windows":
        pass  # 目前手头没有Windows电脑去看stata-cli的配置

if log_file_path is None:
    if operating_system == "macos":
        # _name = os.environ['USER']
        _home = os.getenv('HOME')
        log_file_path = f"{_home}/Documents/stata-mcp-log/"
        # 创建目录（如果不存在）
        os.makedirs(log_file_path, exist_ok=True)
    elif operating_system == "windows":
        pass

if dofile_base_path is None:
    if operating_system == "macos":
        # _name = os.environ['USER']
        _home = os.getenv('HOME')
        dofile_base_path = f"{_home}/Documents/stata-mcp-dofile/"
        # 创建目录（如果不存在）
        os.makedirs(dofile_base_path, exist_ok=True)

if result_doc_path is None:
    if operating_system == "macos":
        # _name = os.environ['USER']
        _home = os.getenv('HOME')
        result_doc_path = f"{_home}/Documents/stata-mcp-result_doc/"
        # 创建目录（如果不存在）
        os.makedirs(result_doc_path, exist_ok=True)
    elif operating_system == "windows":
        pass

# README文件路径
readme_path = os.path.join(log_file_path, "README.md")
metadata = os.path.join(log_file_path, "metadata")

# 检查并创建README文件
if not os.path.exists(readme_path):
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
if not os.path.exists(metadata):
    with open(metadata, 'w', encoding='utf-8') as f:
        f.write("Using Log Serve...")


class StataCommandGenerator:
    """Stata代码生成器"""

    # def __init__(self): pass

    @staticmethod
    @mcp.tool(name="use", description="生成并返回 Stata 的 'use' 命令（加载数据集的命令）")
    def use(data_path: str, is_clear: bool = True) -> str:
        """
        Use data in Stata

        Args:
            data_path: the data which will be used.
            is_clear: whether clear the history data in Stata, default is True, and also suggest to set default.

        Returns:
            the stata-code of using the data whose path is data_path
        """
        options = ", clear" if is_clear else ""
        return f"use {data_path}{options}"

    @staticmethod
    @mcp.tool(name="save", description="生成并返回 Stata 的 'save' 命令（保存数据集的命令）")
    def save(data_path: str, is_replace: bool = False) -> str:
        """
        Save data from stata

        Args:
            data_path: the data which will be saved.
            is_replace: whether replace the data for the ori-data, default is False,
                        and also suggest keep False(and use the another path difference to the ori-data)

        Returns:
            the stata-code of saving the data to the path data_path
        """
        options = ", replace" if is_replace else ""
        return f"save {data_path}{options}"

    @staticmethod
    @mcp.tool(name="summarize", description="生成并返回 Stata 的 'summarize' 命令（数据的描述性统计命令）")
    def summarize(varlist: Optional[List[str]] = None, if_condition: Optional[str] = None,
                  in_range: Optional[str] = None,
                  weight: Optional[str] = None,
                  detail: bool = False,
                  meanonly: bool = False,
                  fmt: bool = False,
                  separator: Optional[int] = None,
                  **display_options) -> str:
        """
        Generate Stata's summarize command with various options.

        This function constructs a Stata summarize command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            varlist: List of variables to summarize. If None, summarizes all variables.
            if_condition: Stata if condition as string (e.g., "foreign == 1").
            in_range: Stata in range specification (e.g., "1/100").
            weight: Weight specification (aweights, fweights, or iweights).
            detail: Whether to include detailed statistics.
            meanonly: Whether to calculate only the mean (programmer's option).
            fmt: Use variable's display format instead of default g format.
            separator: Draw separator line after specified number of variables.
            **display_options: Additional display options (vsquish, noemptycells, etc.).

        Returns:
            A complete Stata summarize command string.

        Raises:
            ValueError: If invalid parameter combinations are provided.

        Examples:
            >>> summarize(["mpg", "weight"])
            'summarize mpg weight'

            >>> summarize(["price"], if_condition="foreign", detail=True, separator=10)
            'summarize price if foreign, detail separator(10)'
        """
        # Validate incompatible options
        if detail and meanonly:
            raise ValueError("detail and meanonly options cannot be used together")
        if weight and "iweights" in weight and detail:
            raise ValueError("iweights may not be used with the detail option")

        # Start building the command
        cmd_parts = ["summarize"]

        # Add variable list if specified
        if varlist is not None:
            if not all(isinstance(v, str) for v in varlist):
                raise ValueError("varlist must contain only strings")
            cmd_parts.extend(varlist)

        # Add if condition
        if if_condition is not None:
            cmd_parts.append(f"if {if_condition}")

        # Add in range
        if in_range is not None:
            cmd_parts.append(f"in {in_range}")

        # Add weights
        if weight is not None:
            valid_weights = ["aweights", "fweights", "iweights"]
            if not any(w in weight for w in valid_weights):
                raise ValueError(f"weight must be one of {valid_weights}")
            cmd_parts.append(f"[{weight}]")

        # Process options
        options = []

        # Main options
        if detail:
            options.append("detail")
        if meanonly:
            options.append("meanonly")
        if fmt:
            options.append("format")
        if separator is not None:
            options.append(f"separator({separator})")

        # Display options
        valid_display_opts = {
            'vsquish', 'noemptycells', 'baselevels', 'allbaselevels',
            'nofvlabel', 'fvwrap', 'fvwrapon'
        }

        for opt, value in display_options.items():
            if opt not in valid_display_opts:
                raise ValueError(f"Invalid display option: {opt}")

            if isinstance(value, bool) and value:
                options.append(opt)
            elif isinstance(value, int):
                options.append(f"{opt}({value})")
            elif isinstance(value, str):
                options.append(f"{opt}({value})")

        # Combine options if any exist
        if options:
            cmd_parts.append(",")
            cmd_parts.extend(options)

        # Join all parts with single spaces
        return " ".join(cmd_parts)

    # @staticmethod
    # @mcp.tool(name="generate")
    # def generate(): pass


@mcp.tool()
def read_log(log_path: str) -> str:
    """
    Read the log file and return its content.

    Args:
        log_path (str): The path to the log file.

    Returns:
        str: The content of the log file.
    """
    with open(log_path, 'r') as file:
        log = file.read()
    return log


@mcp.tool(name="results_doc_path", description="Stata中`outreg2`等命令的返回文件存储路径")
def results_doc_path() -> str:
    """
    生成并返回一个基于当前时间戳的结果文档存储路径。

    该函数执行以下操作：
    1. 获取当前系统时间并格式化为'%Y%m%d%H%M%S'格式的时间戳字符串
    2. 将该时间戳字符串与预设的result_doc_path基础路径拼接，形成完整路径
    3. 创建该路径对应的目录（如果目录已存在不会报错）
    4. 返回新创建的完整路径字符串

    Returns:
        str: 新创建的结果文档目录的完整路径，路径格式为：
            `<result_doc_path>/<YYYYMMDDHHMMSS>`，其中时间戳部分由函数执行时的系统时间生成

    Notes:
        （以下内容对于LLM来说不需要懂）
        - 使用`exist_ok=True`参数，当目标目录已存在时不会引发异常
        - 函数使用了Python 3.8+的海象运算符(:=)在表达式内进行变量赋值
        - 返回的路径适合用作Stata的`outreg2`等命令的输出目录
    """
    os.makedirs(
        (path := os.path.join(result_doc_path, datetime.strftime(datetime.now(), "%Y%m%d%H%M%S"))),
        exist_ok=True
    )
    return path


@mcp.tool(name="write_dofile", description="write the stata-code to dofile")
def write_dofile(content: str) -> str:
    """
    Write stata code to a dofile.
    Args:
        content: The stata code content which will be writen to the designated do-file.

    Returns:
        the do-file path

    Notes:
        Please avoid writing any code that draws graphics or requires human intervention for uncertainty bug.
    """
    file_path = os.path.join(dofile_base_path,  datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")+".do")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path


@mcp.tool(name="stata_do", description="Run a stata-code via Stata")
def stata_do(dofile_path: str) -> str:
    """
    Execute a Stata do-file and return the path to its log file.

    Args:
        dofile_path: Path to the Stata do-file to be executed.

    Returns:
        str: Path to the generated Stata log file.

    Note:
        Requires StataSE to be installed at the default macOS location.
        The log file will be created in a temporary directory.
    """
    nowtime: str = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
    log_file = os.path.join(log_file_path, f"{nowtime}.log")

    # 启动 Stata 进程（交互模式）
    proc = subprocess.Popen(
        [stata_cli_path],  # 启动 Stata 命令行
        stdin=subprocess.PIPE,  # 准备输入命令
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True  # 如果路径有空格需要 shell=True
    )

    # 在 Stata 中依次执行命令
    commands = f"""
    log using "{log_file}", replace
    do "{dofile_path}"
    log close
    exit, STATA
    """
    proc.communicate(input=commands)  # 发送命令并等待结束

    return log_file


if __name__ == "__main__":
    mcp.run(transport="stdio")

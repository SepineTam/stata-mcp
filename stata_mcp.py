from typing import List, Optional, Union, Dict, Any
import subprocess
import sys
import os
import platform

import dotenv
from mcp.server.fastmcp import FastMCP

from utils import StataFinder
from config import *

dotenv.load_dotenv()
mcp = FastMCP(name='stata-mcp')

# 初始化可选参数（默认为None）
stata_cli_path = None
operating_system = None

output_base_path = None

log_file_path = None
dofile_base_path = None
result_doc_path = None

sys_os = platform.system()

if sys_os == "Darwin" or sys_os == "Windows":
    args = sys.argv[1:]
    if len(args) == 0:
        is_env_stata_cli = False
    else:
        is_env_stata_cli = eval(args[0])
        if type(is_env_stata_cli) is not bool:
            is_env_stata_cli = True
else:
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit("错误：必须提供版本号和版本类型，如uv run stata_mcp.py 17 se")

    version_number = args[0]  # 第一个参数是版本号（如17）
    version_type = args[1]  # 第二个参数是版本类型（如se）

for arg in args[1:]:
    if arg.startswith("stata_cli_path="):
        stata_cli_path = arg.split("=", 1)[1]  # 提取路径部分
    elif arg.startswith("operating_system="):
        operating_system = arg.split("=", 1)[1].lower()
    elif arg.startswith("output_base_path="):
        output_base_path = arg.split("=", 1)[1]
    else:
        print(f"警告：未知参数 `{arg}`，已忽略")

if operating_system is None:
    os_name = platform.system()  # 返回 'Windows', 'Linux', 'Darwin'(macOS) 等
    if os_name == "Windows":
        operating_system = "windows"
    elif os_name == "Darwin":
        operating_system = "macos"
    elif os_name == "Linux":
        operating_system = "linux"
    else:
        operating_system = None
        sys.exit("未知操作系统")

if operating_system == "macos":
    if stata_cli_path is None:
        stata_cli_path = StataFinder._find_stata_macos(is_env=is_env_stata_cli)
    # check the output base path
    if output_base_path is None:
        _user_name = os.getenv("USER")
        output_base_path = f"/Users/{_user_name}/Documents/stata-mcp-folder"
        os.makedirs(output_base_path, exist_ok=True)
elif operating_system == "windows":
    if stata_cli_path is None:
        stata_cli_path = StataFinder._find_stata_windows(is_env=is_env_stata_cli)
        if stata_cli_path is None:
            exit_msg = ('Missing Stata.exe, you could config your Stata.exe abspath in your env\n'
                        r'e.g. stata_cli="C:\\Program Files\\Stata19\StataMP.exe"')
            sys.exit(exit_msg)

    if output_base_path is None:
        # there is something wrong on cherry studio, so you should config the env as `USERPROFILE=YOU_RNAME`
        _user_name = os.getenv("USERPROFILE").split("\\")[-1]
        output_base_path = f"C:\\Users\\{_user_name}\\Documents\\stata-mcp-folder"
        os.makedirs(output_base_path, exist_ok=True)
elif operating_system == "linux":
    sys.exit("目前仅支持macOS和Windows，如确定你的电脑是macOS，请加上参数operating_system=macos")
else:
    sys.exit("未知操作系统")

# Create a series of folder
log_file_path = os.path.join(output_base_path, "stata-mcp-log")
os.makedirs(log_file_path, exist_ok=True)
dofile_base_path = os.path.join(output_base_path, "stata-mcp-dofile")
os.makedirs(dofile_base_path, exist_ok=True)
result_doc_path = os.path.join(output_base_path, "stata-mcp-result")
os.makedirs(result_doc_path, exist_ok=True)

# output_base_path/README文件
readme_path = os.path.join(output_base_path, "README.md")
metadata = os.path.join(output_base_path, "metadata")

# 检查并创建README文件
if not os.path.exists(readme_path):
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
if not os.path.exists(metadata):
    with open(metadata, 'w', encoding='utf-8') as f:
        f.write("Using Log Serve...")

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


@mcp.tool(name="get_data_info", description="获取数据文件的描述性统计信息")
def get_data_info(data_path: str, vars_list: Optional[List[str]] = None) -> str:
    """
    分析数据文件并返回描述性统计信息。支持多种文件格式，包括Stata数据文件(.dta)、
    CSV文件(.csv)和Excel文件(.xlsx, .xls)。
    如果AI要查看数据的情况，不能使用 `use` ，而应该使用 `get_data_info` 。

    Args:
        data_path: 数据文件的路径，支持.dta、.csv、.xlsx和.xls格式。
        vars_list: 可选的变量列表。如果提供，则仅返回这些变量的统计信息。
                  如果为None，则返回所有变量的统计信息。

    Returns:
        str: 包含数据描述性统计信息的字符串，包括：
             - 文件基本信息（格式、大小、变量数量、观测数量等）
             - 变量类型统计
             - 数值变量的统计摘要（均值、标准差、最小值、最大值等）
             - 分类变量的频率分布
             - 缺失值分析
             - 如果是面板数据，还包括面板结构信息

    Raises:
        ValueError: 如果文件格式不支持或文件不存在
        ImportError: 如果缺少处理特定文件格式所需的包

    Examples:
        >>> get_data_info("example.dta")
        '文件信息：
         格式：Stata数据文件(.dta)
         文件大小：1.2 MB
         观测数：1000
         变量数：15
         ...'

        >>> get_data_info("sales.csv", vars_list=["price", "quantity", "date"])
        '文件信息：
         格式：CSV文件(.csv)
         文件大小：0.5 MB
         观测数：500
         变量数：3 (从原始变量中选择)
         ...'
    """
    # 导入必要的库
    import os
    import pandas as pd
    import numpy as np
    from pathlib import Path
    import tempfile

    # 检查文件是否存在
    if not os.path.exists(data_path):
        raise ValueError(f"文件不存在：{data_path}")

    # 获取文件信息
    file_size = os.path.getsize(data_path) / (1024 * 1024)  # 转换为MB
    file_extension = os.path.splitext(data_path)[1].lower()

    # 根据文件扩展名读取数据
    if file_extension == '.dta':
        try:
            # 尝试读取Stata文件
            df = pd.read_stata(data_path)
            file_type = "Stata数据文件(.dta)"
        except ImportError:
            raise ImportError("缺少读取Stata文件所需的包。请安装pandas: pip install pandas")
    elif file_extension == '.csv':
        try:
            # 尝试读取CSV文件，处理可能的编码问题
            try:
                df = pd.read_csv(data_path)
            except UnicodeDecodeError:
                # 尝试不同的编码
                df = pd.read_csv(data_path, encoding='latin1')
            file_type = "CSV文件(.csv)"
        except ImportError:
            raise ImportError("缺少读取CSV文件所需的包。请安装pandas: pip install pandas")
    elif file_extension in ['.xlsx', '.xls']:
        try:
            # 尝试读取Excel文件
            df = pd.read_excel(data_path)
            file_type = f"Excel文件({file_extension})"
        except ImportError:
            raise ImportError("缺少读取Excel文件所需的包。请安装openpyxl: pip install openpyxl")
    else:
        raise ValueError(f"不支持的文件格式：{file_extension}。支持的格式包括.dta、.csv、.xlsx和.xls")

    # 如果提供了变量列表，则仅保留这些变量
    if vars_list is not None:
        # 检查所有请求的变量是否存在
        missing_vars = [var for var in vars_list if var not in df.columns]
        if missing_vars:
            raise ValueError(f"以下变量在数据集中不存在：{', '.join(missing_vars)}")

        # 选择指定的变量
        df = df[vars_list]

    # 创建输出字符串
    output = []

    # 1. 文件基本信息
    output.append("文件信息：")
    output.append(f"格式：{file_type}")
    output.append(f"文件大小：{file_size:.2f} MB")
    output.append(f"观测数：{df.shape[0]}")

    if vars_list is not None:
        output.append(f"变量数：{len(vars_list)} (从原始变量中选择)")
    else:
        output.append(f"变量数：{df.shape[1]}")

    # 2. 变量类型统计
    num_numeric = sum(pd.api.types.is_numeric_dtype(df[col]) for col in df.columns)
    num_categorical = sum(pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == 'object' for col in df.columns)
    num_datetime = sum(pd.api.types.is_datetime64_dtype(df[col]) for col in df.columns)
    num_boolean = sum(pd.api.types.is_bool_dtype(df[col]) for col in df.columns)

    output.append("\n变量类型统计：")
    output.append(f"数值型变量：{num_numeric}")
    output.append(f"分类型变量：{num_categorical}")
    output.append(f"日期时间型变量：{num_datetime}")
    output.append(f"布尔型变量：{num_boolean}")

    # 3. 缺失值分析
    total_missing = df.isna().sum().sum()
    missing_percent = (total_missing / (df.shape[0] * df.shape[1])) * 100

    output.append("\n缺失值分析：")
    output.append(f"总缺失值数量：{total_missing}")
    output.append(f"缺失值占比：{missing_percent:.2f}%")

    # 获取每个变量的缺失值数量和百分比
    if df.shape[1] <= 30:  # 如果变量数量不多，则显示每个变量的缺失值情况
        output.append("\n各变量缺失值情况：")
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_percent = (missing_count / df.shape[0]) * 100
            if missing_count > 0:
                output.append(f"  {col}: {missing_count} ({missing_percent:.2f}%)")
    else:
        # 如果变量太多，只显示有缺失值的前10个变量
        missing_cols = df.isna().sum().sort_values(ascending=False)
        missing_cols = missing_cols[missing_cols > 0]
        if len(missing_cols) > 0:
            output.append("\n缺失值最多的10个变量：")
            for col, count in missing_cols.head(10).items():
                missing_percent = (count / df.shape[0]) * 100
                output.append(f"  {col}: {count} ({missing_percent:.2f}%)")

    # 4. 数值变量的统计摘要
    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) > 0:
        output.append("\n数值变量统计摘要：")

        # 计算统计量
        desc_stats = df[numeric_cols].describe().T

        # 添加额外的统计量
        if df.shape[0] > 0:  # 确保有数据
            desc_stats['缺失值'] = df[numeric_cols].isna().sum()
            desc_stats['缺失值比例'] = df[numeric_cols].isna().sum() / df.shape[0]

            # 可选：添加更多统计量
            desc_stats['偏度'] = df[numeric_cols].skew()
            desc_stats['峰度'] = df[numeric_cols].kurtosis()

        # 格式化并添加到输出
        for col in desc_stats.index:
            output.append(f"\n  {col}:")
            output.append(f"    计数: {desc_stats.loc[col, 'count']:.0f}")
            output.append(f"    均值: {desc_stats.loc[col, 'mean']:.4f}")
            output.append(f"    标准差: {desc_stats.loc[col, 'std']:.4f}")
            output.append(f"    最小值: {desc_stats.loc[col, 'min']:.4f}")
            output.append(f"    25%分位数: {desc_stats.loc[col, '25%']:.4f}")
            output.append(f"    中位数: {desc_stats.loc[col, '50%']:.4f}")
            output.append(f"    75%分位数: {desc_stats.loc[col, '75%']:.4f}")
            output.append(f"    最大值: {desc_stats.loc[col, 'max']:.4f}")
            output.append(f"    缺失值: {desc_stats.loc[col, '缺失值']:.0f} ({desc_stats.loc[col, '缺失值比例']:.2%})")
            output.append(f"    偏度: {desc_stats.loc[col, '偏度']:.4f}")
            output.append(f"    峰度: {desc_stats.loc[col, '峰度']:.4f}")

    # 5. 分类变量的频率分布
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns

    if len(categorical_cols) > 0:
        output.append("\n分类变量频率分布：")

        for col in categorical_cols:
            # 获取唯一值的数量
            unique_count = df[col].nunique()

            output.append(f"\n  {col}:")
            output.append(f"    唯一值数量: {unique_count}")

            # 如果唯一值数量合理（不超过10个），则显示频率分布
            if unique_count <= 10 and unique_count > 0:
                value_counts = df[col].value_counts().head(10)
                value_percent = df[col].value_counts(normalize=True).head(10) * 100

                for i, (value, count) in enumerate(value_counts.items()):
                    percent = value_percent[i]
                    output.append(f"    {value}: {count} ({percent:.2f}%)")
            elif unique_count > 10:
                # 如果唯一值太多，只显示前5个
                output.append("    前5个最常见值:")
                value_counts = df[col].value_counts().head(5)
                value_percent = df[col].value_counts(normalize=True).head(5) * 100

                for i, (value, count) in enumerate(value_counts.items()):
                    percent = value_percent[i]
                    output.append(f"    {value}: {count} ({percent:.2f}%)")

    # 6. 检测是否为面板数据并分析面板结构
    # 通常面板数据具有ID和时间两个维度
    potential_id_cols = [col for col in df.columns if 'id' in str(col).lower() or
                         'code' in str(col).lower() or 'key' in str(col).lower()]
    potential_time_cols = [col for col in df.columns if 'time' in str(col).lower() or
                           'date' in str(col).lower() or 'year' in str(col).lower() or
                           'month' in str(col).lower() or 'day' in str(col).lower()]

    # 如果存在可能的ID列和时间列，则尝试分析面板结构
    if potential_id_cols and potential_time_cols:
        for id_col in potential_id_cols[:1]:  # 只尝试第一个ID列
            for time_col in potential_time_cols[:1]:  # 只尝试第一个时间列
                # 计算面板结构
                try:
                    n_ids = df[id_col].nunique()
                    n_times = df[time_col].nunique()
                    n_obs = df.shape[0]

                    output.append("\n潜在面板数据结构检测：")
                    output.append(f"  ID变量: {id_col} (唯一值数量: {n_ids})")
                    output.append(f"  时间变量: {time_col} (唯一值数量: {n_times})")
                    output.append(f"  总观测数: {n_obs}")

                    # 检查面板是否平衡
                    cross_table = pd.crosstab(df[id_col], df[time_col])
                    is_balanced = (cross_table == 1).all().all()

                    if is_balanced and n_ids * n_times == n_obs:
                        output.append("  面板状态: 强平衡面板 (每个ID在每个时间点都有一个观测值)")
                    elif df.groupby(id_col)[time_col].count().var() == 0:
                        output.append("  面板状态: 弱平衡面板 (每个ID有相同数量的观测值，但可能不在相同的时间点)")
                    else:
                        output.append("  面板状态: 非平衡面板 (不同ID有不同数量的观测值)")

                    # 计算每个ID的平均观测数
                    avg_obs_per_id = df.groupby(id_col).size().mean()
                    output.append(f"  每个ID的平均观测数: {avg_obs_per_id:.2f}")

                    # 计算时间跨度
                    if pd.api.types.is_datetime64_dtype(df[time_col]):
                        min_time = df[time_col].min()
                        max_time = df[time_col].max()
                        output.append(f"  时间跨度: {min_time} 至 {max_time}")
                except:
                    # 如果计算出错，跳过面板分析
                    pass

    # 返回格式化的输出
    return "\n".join(output)


@mcp.tool(name="results_doc_path", description="Stata中`outreg2`等命令的返回文件存储路径（方便统一管理结果）")
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
        - 在具体地Stata代码中可以在前面设置文件输出路径。
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
        Please be careful about the first command in dofile should be use data.
        For avoiding make mistake, you can generate stata-code with the function from `StataCommandGenerator` class.
        Please avoid writing any code that draws graphics or requires human intervention for uncertainty bug.
        If you find something went wrong about the code, you can use the function from `StataCommandGenerator` class.

    Enhancement:
        If you have `outreg2`, `esttab` command for output the result,
        you should use the follow command to get the output path.
        `results_doc_path`, and use `local output_path path` the path is the return of the function `results_doc_path`.
        If you want to use the function `write_dofile`, please use `results_doc_path` before which is necessary.

    """
    file_path = os.path.join(dofile_base_path,  datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")+".do")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path


@mcp.tool(name="append_dofile", description="append stata-code to an existing dofile or create a new one")
def append_dofile(original_dofile_path: str, content: str) -> str:
    """
    Append stata code to an existing dofile or create a new one if the original doesn't exist.

    Args:
        original_dofile_path: Path to the original dofile to append to. If empty or invalid, a new file will be created.
        content: The stata code content which will be appended to the designated do-file.

    Returns:
        The new do-file path (either the modified original or a newly created file)

    Notes:
        When appending to an existing file, the content will be added at the end of the file.
        If the original file doesn't exist or path is empty, a new file will be created with the content.
        Please be careful about the syntax coherence when appending code to an existing file.
        For avoiding mistakes, you can generate stata-code with the function from `StataCommandGenerator` class.
        Please avoid writing any code that draws graphics or requires human intervention for uncertainty bug.
        If you find something went wrong about the code, you can use the function from `StataCommandGenerator` class.

    Enhancement:
        If you have `outreg2`, `esttab` command for output the result,
        you should use the follow command to get the output path.
        `results_doc_path`, and use `local output_path path` the path is the return of the function `results_doc_path`.
        If you want to use the function `append_dofile`, please use `results_doc_path` before which is necessary.
    """
    # Create a new file path for the output
    new_file_path = os.path.join(dofile_base_path, datetime.strftime(datetime.now(), "%Y%m%d%H%M%S") + ".do")

    # Check if original file exists and is valid
    original_exists = False
    original_content = ""
    if original_dofile_path and os.path.exists(original_dofile_path):
        try:
            with open(original_dofile_path, "r", encoding="utf-8") as f:
                original_content = f.read()
            original_exists = True
        except Exception:
            # If there's any error reading the file, we'll create a new one
            original_exists = False

    # Write to the new file (either copying original content + new content, or just new content)
    with open(new_file_path, "w", encoding="utf-8") as f:
        if original_exists:
            f.write(original_content)
            # Add a newline if the original file doesn't end with one
            if original_content and not original_content.endswith("\n"):
                f.write("\n")
        f.write(content)

    return new_file_path


@mcp.tool(name="stata_do", description="Run a stata-code via Stata")
def stata_do(dofile_path: str) -> str:
    """
    Execute a Stata do-file and return the path to its log file.

    Args:
        dofile_path: Path to the Stata do-file to be executed.

    Returns:
        str: Path to the generated Stata log file.

    Note:
        Supports multiple operating systems (macOS, Windows, Linux).
        The log file will be created in the log_file_path directory.
    """
    nowtime: str = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
    log_file = os.path.join(log_file_path, f"{nowtime}.log")

    # 针对不同操作系统使用不同的执行方式
    if operating_system == "macos" or operating_system == "linux":
        # macOS/Linux 方式
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

    elif operating_system == "windows":
        # Windows 方式 - 使用 /e 参数执行批处理命令
        # 创建临时批处理文件
        batch_file = os.path.join(dofile_base_path, f"{nowtime}_batch.do")
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(f'log using "{log_file}", replace\n')
            f.write(f'do "{dofile_path}"\n')
            f.write('log close\n')
            f.write('exit, STATA\n')

        # 在Windows上执行Stata，使用/e参数运行批处理文件
        # 使用双引号处理路径中的空格
        cmd = f'"{stata_cli_path}" /e do "{batch_file}"'
        subprocess.run(cmd, shell=True)

    else:
        raise ValueError(f"不支持的操作系统: {operating_system}")

    return log_file


if __name__ == "__main__":
    mcp.run(transport="stdio")

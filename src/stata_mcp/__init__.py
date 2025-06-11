from typing import List, Optional, Union, Dict, Any

import subprocess
import sys
import os
import platform
from datetime import datetime

import pandas as pd

import dotenv
from mcp.server.fastmcp import FastMCP

from .utils import StataFinder
from .utils.Prompt import pmp

from .usable import main as usable

dotenv.load_dotenv()
mcp = FastMCP(name='stata-mcp')

# Initialize optional parameters (defaults to None)
stata_cli_path = None

output_base_path = None

log_file_path = None
dofile_base_path = None
result_doc_path = None

sys_os = platform.system()
is_env_stata_cli: bool = True

if sys_os == "Darwin" or sys_os == "Windows" or sys_os == "Linux":
    args = sys.argv[1:]
    if len(args) == 0:
        is_env_stata_cli = True
    else:
        if args[0].lower() == "true":
            is_env_stata_cli = True
        elif args[0].lower() == "false":
            is_env_stata_cli = False
        else:
            is_env_stata_cli = True
else:
    sys.exit("Unknown OS")
try:
    for arg in args[1:]:
        if arg.startswith("stata_cli_path="):
            stata_cli_path = arg.split("=", 1)[1]  # Extract the path part
        elif arg.startswith("output_base_path="):
            output_base_path = arg.split("=", 1)[1]
        else:
            print(f"Warning: Unknown arg `{arg}`")
except Exception as e:
    print(e)

if output_base_path is None:
    documents_path = os.path.expanduser("~/Documents")
    output_base_path = os.path.join(documents_path, "stata-mcp-folder/")
os.makedirs(output_base_path, exist_ok=True)

if sys_os == "Darwin":
    if stata_cli_path is None:
        stata_cli_path = StataFinder.find_stata(is_env=is_env_stata_cli)
    # check the output base path
elif sys_os == "Windows":
    if stata_cli_path is None:
        stata_cli_path = StataFinder.find_stata(is_env=is_env_stata_cli)
        if stata_cli_path is None:
            exit_msg = ('Missing Stata.exe, you could config your Stata.exe abspath in your env\n'
                        r'e.g. stata_cli="C:\\Program Files\\Stata19\StataMP.exe"')
            sys.exit(exit_msg)
    # not sure whether windows could use `documents_path = os.path.expanduser("~/Documents")`
    # if output_base_path is None:  # need to be tested
    #     # there is something wrong on cherry studio, so you should config the env as `USERPROFILE=YOU_RNAME`
    #     _user_name = os.getenv("USERPROFILE").split("\\")[-1]
    #     output_base_path = f"C:\\Users\\{_user_name}\\Documents\\stata-mcp-folder"
    #     os.makedirs(output_base_path, exist_ok=True)
elif sys_os == "Linux":
    if stata_cli_path is None:
        stata_cli_path = StataFinder.find_stata()
else:
    sys.exit("Unknown OS")

# Create a series of folder
log_file_path = os.path.join(output_base_path, "stata-mcp-log")
os.makedirs(log_file_path, exist_ok=True)
dofile_base_path = os.path.join(output_base_path, "stata-mcp-dofile")
os.makedirs(dofile_base_path, exist_ok=True)
result_doc_path = os.path.join(output_base_path, "stata-mcp-result")
os.makedirs(result_doc_path, exist_ok=True)

# output_base_path/README file
readme_path = os.path.join(output_base_path, "README.md")
metadata = os.path.join(output_base_path, "metadata")

# # Check and make README file and metadata future it would be used.
# if not os.path.exists(readme_path):
#     with open(readme_path, 'w', encoding='utf-8') as f:
#         f.write(readme_content)
# if not os.path.exists(metadata):
#     with open(metadata, 'w', encoding='utf-8') as f:
#         f.write("Using Log Serve...")

pmp.set_lang(os.getenv("lang", "en"))


@mcp.prompt()
def stata_assistant_role(lang: str = None) -> str:
    """
    Return the Stata assistant role prompt content.

    This function retrieves a predefined prompt that defines the role and capabilities
    of a Stata analysis assistant. The prompt helps set expectations and context for
    the assistant's behavior when handling Stata-related tasks.

    Args:
        lang (str, optional): Language code for localization of the prompt content.
            If None, returns the default language version. Defaults to None.
            Examples: "en" for English, "cn" for Chinese.

    Returns:
        str: The Stata assistant role prompt text in the requested language.

    Examples:
        >>> stata_assistant_role()  # Returns default language version
        "I am a Stata analysis assistant..."

        >>> stata_assistant_role(lang="en")  # Returns English version
        "I am a Stata analysis assistant..."

        >>> stata_assistant_role(lang="cn")  # Returns Chinese version
        "我是一个Stata分析助手..."
    """
    return pmp.get_prompt(prompt_id="stata_assistant_role", lang=lang)

@mcp.prompt()
def stata_analysis_strategy(lang: str = None) -> str:
    """
    Return the Stata analysis strategy prompt content.

    This function retrieves a predefined prompt that outlines the recommended
    strategy for conducting data analysis using Stata. The prompt includes
    guidelines for data preparation, code generation, results management,
    reporting, and troubleshooting.

    Args:
        lang (str, optional): Language code for localization of the prompt content.
            If None, returns the default language version. Defaults to None.
            Examples: "en" for English, "cn" for Chinese.

    Returns:
        str: The Stata analysis strategy prompt text in the requested language.

    Examples:
        >>> stata_analysis_strategy()  # Returns default language version
        "When conducting data analysis using Stata..."

        >>> stata_analysis_strategy(lang="en")  # Returns English version
        "When conducting data analysis using Stata..."

        >>> stata_analysis_strategy(lang="cn")  # Returns Chinese version
        "使用Stata进行数据分析时，请遵循以下策略..."
    """
    return pmp.get_prompt(prompt_id="stata_analysis_strategy", lang=lang)

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

# @mcp.tool(name="get_data_info", description="Get descriptive statistics for the data file")
def get_data_info(data_path: str, vars_list: Optional[List[str]] = None, encoding: str = 'utf-8') -> str:
    """
    Analyze the data file and return descriptive statistics. Supports various file formats,
    including Stata data files (.dta), CSV files (.csv), and Excel files (.xlsx, .xls).
    If the AI wants to examine the data situation, it should not use `use`, but should use
    `get_data_info` instead.

    Args:
        data_path: Path to the data file, supporting .dta, .csv, .xlsx, and .xls formats.
        vars_list: Optional list of variables. If provided, returns statistics only for these variables.
                  If None, returns statistics for all variables.
        encoding: The data file encoding method, supporting "utf-8", "gbk" and so on. (Only works when the data is csv)

    Returns:
        str: A string containing descriptive statistics of the data, including:
             - Basic file information (format, size, number of variables, number of observations, etc.)
             - Variable type statistics
             - Statistical summary of numerical variables (mean, standard deviation, min, max, etc.)
             - Frequency distribution of categorical variables
             - Missing value analysis
             - Panel structure information, if it is panel data

    Raises:
        ValueError: If the file format is not supported or the file does not exist
        ImportError: If packages required for processing specific file formats are missing

    Examples:
        >>> get_data_info("example.dta")
        'File Information:
         Format: Stata data file (.dta)
         File size: 1.2 MB
         Observations: 1000
         Variables: 15
         ...'

        >>> get_data_info("sales.csv", vars_list=["price", "quantity", "date"])
        'File Information:
         Format: CSV file (.csv)
         File size: 0.5 MB
         Observations: 500
         Variables: 3 (selected from original variables)
         ...'
    """
    # Check if the file exists
    if not os.path.exists(data_path):
        raise ValueError(f"File does not exist: {data_path}")

    # Get file information
    file_size = os.path.getsize(data_path) / (1024 * 1024)  # Convert to MB
    file_extension = os.path.splitext(data_path)[1].lower()

    # Read data according to file extension
    if file_extension == '.dta':
        try:
            # Try to read Stata file
            df = pd.read_stata(data_path)
            file_type = "Stata data file (.dta)"
        except ImportError:
            raise ImportError("Missing package required to read Stata files. Please install pandas: pip install pandas")
    elif file_extension == '.csv':
        try:
            # Try to read CSV file, handle potential encoding issues
            try:
                df = pd.read_csv(data_path, encoding=encoding)
            except UnicodeDecodeError:
                # Try different encoding
                df = pd.read_csv(data_path, encoding='latin1')
            file_type = "CSV file (.csv)"
        except ImportError:
            raise ImportError("Missing package required to read CSV files. Please install pandas: pip install pandas")
    elif file_extension in ['.xlsx', '.xls']:
        try:
            # Try to read Excel file
            df = pd.read_excel(data_path)
            file_type = f"Excel file ({file_extension})"
        except ImportError:
            raise ImportError("Missing package required to read Excel files. Please install openpyxl: pip install openpyxl")
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. Supported formats include .dta, .csv, .xlsx, and .xls")

    # If variable list is provided, only keep these variables
    if vars_list is not None:
        # Check if all requested variables exist
        missing_vars = [var for var in vars_list if var not in df.columns]
        if missing_vars:
            raise ValueError(f"The following variables do not exist in the dataset: {', '.join(missing_vars)}")

        # Select specified variables
        df = df[vars_list]

    # Create output string
    output: list = []

    # 1. Basic file information
    output.append("File Information:")
    output.append(f"Format: {file_type}")
    output.append(f"File size: {file_size:.2f} MB")
    output.append(f"Observations: {df.shape[0]}")

    if vars_list is not None:
        output.append(f"Variables: {len(vars_list)} (selected from original variables)")
    else:
        output.append(f"Variables: {df.shape[1]}")

    # 2. Variable type statistics
    num_numeric = sum(pd.api.types.is_numeric_dtype(df[col]) for col in df.columns)
    num_categorical = sum(pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == 'object' for col in df.columns)
    num_datetime = sum(pd.api.types.is_datetime64_dtype(df[col]) for col in df.columns)
    num_boolean = sum(pd.api.types.is_bool_dtype(df[col]) for col in df.columns)

    output.append("\nVariable Type Statistics:")
    output.append(f"Numeric variables: {num_numeric}")
    output.append(f"Categorical variables: {num_categorical}")
    output.append(f"Datetime variables: {num_datetime}")
    output.append(f"Boolean variables: {num_boolean}")

    # 3. Missing value analysis
    total_missing = df.isna().sum().sum()
    missing_percent = (total_missing / (df.shape[0] * df.shape[1])) * 100

    output.append("\nMissing Value Analysis:")
    output.append(f"Total missing values: {total_missing}")
    output.append(f"Missing value percentage: {missing_percent:.2f}%")

    # Get missing value count and percentage for each variable
    if df.shape[1] <= 30:  # If there aren't many variables, show missing values for each
        output.append("\nMissing values by variable:")
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_percent = (missing_count / df.shape[0]) * 100
            if missing_count > 0:
                output.append(f"  {col}: {missing_count} ({missing_percent:.2f}%)")
    else:
        # If there are too many variables, only show the top 10 with missing values
        missing_cols = df.isna().sum().sort_values(ascending=False)
        missing_cols = missing_cols[missing_cols > 0]
        if len(missing_cols) > 0:
            output.append("\nTop 10 variables with most missing values:")
            for col, count in missing_cols.head(10).items():
                missing_percent = (count / df.shape[0]) * 100
                output.append(f"  {col}: {count} ({missing_percent:.2f}%)")

    # 4. Statistical summary of numerical variables
    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) > 0:
        output.append("\nNumerical Variable Statistics:")

        # Calculate statistics
        desc_stats = df[numeric_cols].describe().T

        # Add additional statistics
        if df.shape[0] > 0:  # Ensure there is data
            desc_stats['Missing'] = df[numeric_cols].isna().sum()
            desc_stats['Missing Ratio'] = df[numeric_cols].isna().sum() / df.shape[0]

            # Optional: Add more statistics
            desc_stats['Skewness'] = df[numeric_cols].skew()
            desc_stats['Kurtosis'] = df[numeric_cols].kurtosis()

        # Format and add to output
        for col in desc_stats.index:
            output.append(f"\n  {col}:")
            output.append(f"    Count: {desc_stats.loc[col, 'count']:.0f}")
            output.append(f"    Mean: {desc_stats.loc[col, 'mean']:.4f}")
            output.append(f"    Std Dev: {desc_stats.loc[col, 'std']:.4f}")
            output.append(f"    Min: {desc_stats.loc[col, 'min']:.4f}")
            output.append(f"    25th Percentile: {desc_stats.loc[col, '25%']:.4f}")
            output.append(f"    Median: {desc_stats.loc[col, '50%']:.4f}")
            output.append(f"    75th Percentile: {desc_stats.loc[col, '75%']:.4f}")
            output.append(f"    Max: {desc_stats.loc[col, 'max']:.4f}")
            output.append(f"    Missing Values: {desc_stats.loc[col, 'Missing']:.0f} ({desc_stats.loc[col, 'Missing Ratio']:.2%})")
            output.append(f"    Skewness: {desc_stats.loc[col, 'Skewness']:.4f}")
            output.append(f"    Kurtosis: {desc_stats.loc[col, 'Kurtosis']:.4f}")

    # 5. Frequency distribution of categorical variables
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns

    if len(categorical_cols) > 0:
        output.append("\nCategorical Variable Frequency Distribution:")

        for col in categorical_cols:
            # Get number of unique values
            unique_count = df[col].nunique()

            output.append(f"\n  {col}:")
            output.append(f"    Unique values: {unique_count}")

            # If number of unique values is reasonable (not more than 10), show frequency distribution
            if unique_count <= 10 and unique_count > 0:
                value_counts = df[col].value_counts().head(10)
                value_percent = df[col].value_counts(normalize=True).head(10) * 100

                for i, (value, count) in enumerate(value_counts.items()):
                    percent = value_percent[i]
                    output.append(f"    {value}: {count} ({percent:.2f}%)")
            elif unique_count > 10:
                # If too many unique values, only show top 5
                output.append("    Top 5 most common values:")
                value_counts = df[col].value_counts().head(5)
                value_percent = df[col].value_counts(normalize=True).head(5) * 100

                for i, (value, count) in enumerate(value_counts.items()):
                    percent = value_percent[i]
                    output.append(f"    {value}: {count} ({percent:.2f}%)")

    # 6. Detect if it's panel data and analyze panel structure
    # Typically panel data has ID and time dimensions
    potential_id_cols = [col for col in df.columns if 'id' in str(col).lower() or
                         'code' in str(col).lower() or 'key' in str(col).lower()]
    potential_time_cols = [col for col in df.columns if 'time' in str(col).lower() or
                           'date' in str(col).lower() or 'year' in str(col).lower() or
                           'month' in str(col).lower() or 'day' in str(col).lower()]

    # If there are potential ID columns and time columns, try to analyze panel structure
    if potential_id_cols and potential_time_cols:
        for id_col in potential_id_cols[:1]:  # Only try the first ID column
            for time_col in potential_time_cols[:1]:  # Only try the first time column
                # Calculate panel structure
                try:
                    n_ids = df[id_col].nunique()
                    n_times = df[time_col].nunique()
                    n_obs = df.shape[0]

                    output.append("\nPotential Panel Data Structure Detection:")
                    output.append(f"  ID variable: {id_col} (unique values: {n_ids})")
                    output.append(f"  Time variable: {time_col} (unique values: {n_times})")
                    output.append(f"  Total observations: {n_obs}")

                    # Check if panel is balanced
                    cross_table = pd.crosstab(df[id_col], df[time_col])
                    is_balanced = (cross_table == 1).all().all()

                    if is_balanced and n_ids * n_times == n_obs:
                        output.append("  Panel status: Strongly balanced panel (each ID has one observation at each time point)")
                    elif df.groupby(id_col)[time_col].count().var() == 0:
                        output.append("  Panel status: Weakly balanced panel (each ID has the same number of observations, but possibly not at the same time points)")
                    else:
                        output.append("  Panel status: Unbalanced panel (different IDs have different numbers of observations)")

                    # Calculate average observations per ID
                    avg_obs_per_id = df.groupby(id_col).size().mean()
                    output.append(f"  Average observations per ID: {avg_obs_per_id:.2f}")

                    # Calculate time span
                    if pd.api.types.is_datetime64_dtype(df[time_col]):
                        min_time = df[time_col].min()
                        max_time = df[time_col].max()
                        output.append(f"  Time span: {min_time} to {max_time}")
                except:
                    # If calculation fails, skip panel analysis
                    pass

    # Return formatted output
    return "\n".join(output)

# @mcp.tool(name="results_doc_path", description="Storage path for Stata `outreg2` and other command return files (for convenient result management)")
def results_doc_path() -> str:
    """
    Generate and return a result document storage path based on the current timestamp.

    This function performs the following operations:
    1. Gets the current system time and formats it as a '%Y%m%d%H%M%S' timestamp string
    2. Concatenates this timestamp string with the preset result_doc_path base path to form a complete path
    3. Creates the directory corresponding to that path (no error if directory already exists)
    4. Returns the complete path string of the newly created directory

    Returns:
        str: The complete path of the newly created result document directory, formatted as:
            `<result_doc_path>/<YYYYMMDDHHMMSS>`, where the timestamp portion is generated from the system time when the function is executed

    Notes:
        (The following content is not needed for LLM to understand)
        - Using the `exist_ok=True` parameter, no exception will be raised when the target directory already exists
        - The function uses the walrus operator (:=) in Python 3.8+ to assign a variable within an expression
        - The returned path is suitable for use as the output directory for Stata commands such as `outreg2`
        - In specific Stata code, you can set the file output path at the beginning.
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
    if sys_os == "Darwin" or sys_os == "Linux":
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

    elif sys_os == "Windows":
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
        raise ValueError(f"不支持的操作系统: {sys_os}")

    return log_file


def main() -> None:
    """Entry point for the command line interface."""
    if "--usable" in sys.argv[1:]:
        usable()
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

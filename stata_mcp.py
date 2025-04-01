from typing import List, Optional, Union, Dict, Any
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
    def use(filename: str,
            varlist: Optional[List[str]] = None,
            if_condition: Optional[str] = None,
            in_range: Optional[str] = None,
            clear: bool = False,
            nolabel: bool = False) -> str:
        """
        Generate Stata's use command with various options.

        This function constructs a Stata use command string based on provided parameters,
        matching the official Stata documentation specifications for loading datasets.

        Args:
            filename: Path to the Stata dataset file (.dta) to be loaded.
            varlist: Optional list of variables to load (subset of the dataset).
            if_condition: Stata if condition as string (e.g., "foreign == 1").
            in_range: Stata in range specification (e.g., "1/100").
            clear: Whether to replace the data in memory, even if current data have not been saved.
            nolabel: Whether to prevent value labels in the saved data from being loaded.

        Returns:
            A complete Stata use command string.

        Raises:
            ValueError: If invalid parameter combinations are provided.

        Examples:
            >>> use("auto.dta")
            'use auto.dta'

            >>> use("auto.dta", clear=True)
            'use auto.dta, clear'

            >>> use("myauto.dta", varlist=["make", "rep78", "foreign"])
            'use make rep78 foreign using myauto.dta'

            >>> use("myauto.dta", if_condition="foreign == 1")
            'use if foreign == 1 using myauto.dta'
        """
        # Input validation
        if not filename or not isinstance(filename, str):
            raise ValueError("filename must be a non-empty string")

        # Start building the command
        cmd_parts = []

        # Handle the two different syntax forms:
        # 1. use filename [, options]
        # 2. use [varlist] [if] [in] using filename [, options]

        if varlist or if_condition or in_range:
            # Second syntax form with subset loading
            cmd_parts.append("use")

            # Add variable list if specified
            if varlist:
                if not all(isinstance(v, str) for v in varlist):
                    raise ValueError("varlist must contain only strings")
                cmd_parts.extend(varlist)

            # Add if condition
            if if_condition:
                cmd_parts.append(f"if {if_condition}")

            # Add in range
            if in_range:
                cmd_parts.append(f"in {in_range}")

            # Add "using" with filename
            cmd_parts.append(f"using {filename}")
        else:
            # First syntax form - direct file loading
            cmd_parts.extend(["use", filename])

        # Process options
        options = []

        # Add options based on flags
        if clear:
            options.append("clear")
        if nolabel:
            options.append("nolabel")

        # Combine options if any exist
        if options:
            cmd_parts.append(",")
            cmd_parts.extend(options)

        # Join all parts with single spaces
        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="save", description="生成并返回 Stata 的 'save' 命令（保存数据集的命令）")
    def save(filename: Optional[str] = None,
             nolabel: bool = False,
             replace: bool = False,
             all: bool = False,
             orphans: bool = False,
             emptyok: bool = False) -> str:
        """
        Generate Stata's save command with various options.

        This function constructs a Stata save command string based on provided parameters,
        matching the official Stata documentation specifications for saving datasets.

        Args:
            filename: The path where the dataset will be saved. If None, the dataset is saved
                     under the name it was last known to Stata.
            nolabel: Whether to omit value labels from the saved dataset.
            replace: Whether to overwrite an existing dataset.
            all: Programmer's option to save e(sample) with the dataset.
            orphans: Whether to save all value labels, including those not attached to any variable.
            emptyok: Programmer's option to save the dataset even if it has zero observations and variables.

        Returns:
            A complete Stata save command string.

        Examples:
            >>> save("mydata")
            'save mydata'

            >>> save("mydata", replace=True)
            'save mydata, replace'

            >>> save("mydata", replace=True, nolabel=True)
            'save mydata, nolabel replace'

            >>> save()
            'save'
        """
        # Start building the command
        cmd_parts = ["save"]

        # Add filename if specified
        if filename is not None:
            cmd_parts.append(filename)

        # Process options
        options = []

        # Add options based on flags
        if nolabel:
            options.append("nolabel")
        if replace:
            options.append("replace")
        if all:
            options.append("all")
        if orphans:
            options.append("orphans")
        if emptyok:
            options.append("emptyok")

        # Combine options if any exist
        if options:
            cmd_parts.append(",")
            cmd_parts.extend(options)

        # Join all parts with single spaces
        return " ".join(cmd_parts)

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

    @staticmethod
    @mcp.tool(name="regress", description="Generate and return Stata's 'regress' command (linear regression)")
    def regress(depvar: str, indepvars: Optional[List[str]] = None,
                if_condition: Optional[str] = None,
                in_range: Optional[str] = None,
                weight: Optional[str] = None,
                noconstant: bool = False,
                hascons: bool = False,
                tsscons: bool = False,
                vce: Optional[str] = None,
                level: Optional[int] = None,
                beta: bool = False,
                eform: Optional[str] = None,
                depname: Optional[str] = None,
                noheader: bool = False,
                notable: bool = False,
                plus: bool = False,
                mse1: bool = False,
                coeflegend: bool = False,
                **display_options) -> str:
        """
        Generate Stata's regress command with various options.

        This function constructs a Stata regress command string based on provided parameters,
        matching the official Stata documentation specifications for linear regression.

        Args:
            depvar: The dependent variable name.
            indepvars: List of independent variables. If None, only the dependent variable is included.
            if_condition: Stata if condition as string (e.g., "foreign == 1").
            in_range: Stata in range specification (e.g., "1/100").
            weight: Weight specification (aweights, fweights, iweights, or pweights).
            noconstant: Suppress constant term in the model.
            hascons: Indicate that a user-defined constant is specified among the independent variables.
            tsscons: Compute total sum of squares with constant (used with noconstant).
            vce: Variance-covariance estimation type (ols, robust, cluster clustvar, bootstrap, jackknife, hc2, or hc3).
            level: Set confidence level (default is 95 in Stata).
            beta: Report standardized beta coefficients instead of confidence intervals.
            eform: Report exponentiated coefficients and label as the provided string.
            depname: Substitute dependent variable name (programmer's option).
            noheader: Suppress output header.
            notable: Suppress coefficient table.
            plus: Make table extendable.
            mse1: Force mean squared error to 1.
            coeflegend: Display legend instead of statistics.
            **display_options: Additional display options (noci, nopvalues, noomitted, vsquish, etc.).

        Returns:
            A complete Stata regress command string.

        Raises:
            ValueError: If invalid parameter combinations are provided.

        Examples:
            >>> regress("mpg", ["weight", "foreign"])
            'regress mpg weight foreign'

            >>> regress("gp100m", ["weight", "foreign"], vce="robust", beta=True)
            'regress gp100m weight foreign, vce(robust) beta'

            >>> regress("weight", ["length"], noconstant=True)
            'regress weight length, noconstant'
        """
        # Input validation
        if not isinstance(depvar, str) or not depvar:
            raise ValueError("depvar must be a non-empty string")

        if indepvars is not None and not all(isinstance(v, str) for v in indepvars):
            raise ValueError("indepvars must contain only strings")

        # Validate incompatible options
        if noconstant and hascons:
            raise ValueError("noconstant and hascons options cannot be used together")

        if beta and vce and "cluster" in vce:
            raise ValueError("beta may not be used with vce(cluster)")

        # Start building the command
        cmd_parts = ["regress", depvar]

        # Add independent variables if specified
        if indepvars:
            cmd_parts.extend(indepvars)

        # Add if condition
        if if_condition:
            cmd_parts.append(f"if {if_condition}")

        # Add in range
        if in_range:
            cmd_parts.append(f"in {in_range}")

        # Add weights
        if weight:
            valid_weights = ["aweights", "fweights", "iweights", "pweights"]
            if not any(w in weight for w in valid_weights):
                raise ValueError(f"weight must be one of {valid_weights}")
            cmd_parts.append(f"[{weight}]")

        # Process options
        options = []

        # Model options
        if noconstant:
            options.append("noconstant")
        if hascons:
            options.append("hascons")
        if tsscons:
            options.append("tsscons")

        # SE/Robust options
        if vce:
            valid_vce = ["ols", "robust", "bootstrap", "jackknife", "hc2", "hc3"]
            # For cluster, we check if it starts with "cluster " to allow for the cluster variable
            if not (vce in valid_vce or vce.startswith("cluster ")):
                raise ValueError(f"vce must be one of {valid_vce} or 'cluster clustvar'")
            options.append(f"vce({vce})")

        # Reporting options
        if level:
            if not isinstance(level, int) or level <= 0 or level >= 100:
                raise ValueError("level must be an integer between 1 and 99")
            options.append(f"level({level})")
        if beta:
            options.append("beta")
        if eform:
            options.append(f"eform({eform})")
        if depname:
            options.append(f"depname({depname})")

        # Additional reporting options that don't appear in dialog box
        if noheader:
            options.append("noheader")
        if notable:
            options.append("notable")
        if plus:
            options.append("plus")
        if mse1:
            options.append("mse1")
        if coeflegend:
            options.append("coeflegend")

        # Display options
        valid_display_opts = {
            'noci', 'nopvalues', 'noomitted', 'vsquish', 'noemptycells',
            'baselevels', 'allbaselevels', 'nofvlabel', 'fvwrap', 'fvwrapon',
            'cformat', 'pformat', 'sformat', 'nolstretch'
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

    @staticmethod
    @mcp.tool(name="generate",
              description="Generate and return Stata's 'generate' command (create or change variable contents)")
    def generate(newvar: str, exp: str,
                 type: Optional[str] = None,
                 lblname: Optional[str] = None,
                 if_condition: Optional[str] = None,
                 in_range: Optional[str] = None,
                 before: Optional[str] = None,
                 after: Optional[str] = None) -> str:
        """
        Generate Stata's generate command to create a new variable.

        This function constructs a Stata generate command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            newvar: Name of the new variable to create.
            exp: Expression defining the contents of the new variable.
            type: Optional storage type for the new variable (byte, int, long, float, double, str, str1, ..., str2045).
            lblname: Optional value label name to be associated with the new variable.
            if_condition: Stata if condition as string (e.g., "age > 30").
            in_range: Stata in range specification (e.g., "1/100").
            before: Place the new variable before the specified variable in the dataset.
            after: Place the new variable after the specified variable in the dataset.

        Returns:
            A complete Stata generate command string.

        Raises:
            ValueError: If invalid parameter combinations or values are provided.

        Examples:
            >>> generate("age2", "age^2")
            'generate age2 = age^2'

            >>> generate("age2", "age^2", type="int", if_condition="age > 30")
            'generate int age2 = age^2 if age > 30'

            >>> generate("lastname", "word(name,2)")
            'generate lastname = word(name,2)'

            >>> generate("posttran", "(_n==2)", type="byte", lblname="yesno")
            'generate byte posttran:yesno = (_n==2)'
        """
        # Input validation
        if not newvar or not isinstance(newvar, str):
            raise ValueError("newvar must be a non-empty string")

        if not exp or not isinstance(exp, str):
            raise ValueError("exp must be a non-empty string")

        # Validate storage type if provided
        valid_types = {"byte", "int", "long", "float", "double", "str"}
        str_types = {f"str{i}" for i in range(1, 2046)}
        valid_types.update(str_types)

        if type and type not in valid_types:
            raise ValueError(f"type must be one of: byte, int, long, float, double, str, str1, ..., str2045")

        # Validate incompatible options
        if before and after:
            raise ValueError("before and after options cannot be used together")

        # Start building the command
        cmd_parts = ["generate"]

        # Add type if specified
        if type:
            cmd_parts.append(type)

        # Add new variable name with optional label name
        if lblname:
            cmd_parts.append(f"{newvar}:{lblname}")
        else:
            cmd_parts.append(newvar)

        # Add expression
        cmd_parts.append(f"= {exp}")

        # Add if condition
        if if_condition:
            cmd_parts.append(f"if {if_condition}")

        # Add in range
        if in_range:
            cmd_parts.append(f"in {in_range}")

        # Add placement options
        options = []
        if before:
            options.append(f"before({before})")
        if after:
            options.append(f"after({after})")

        # Combine options if any exist
        if options:
            cmd_parts.append(",")
            cmd_parts.extend(options)

        # Join all parts with single spaces
        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="replace",
              description="Generate and return Stata's 'replace' command (replace contents of existing variable)")
    def replace(oldvar: str, exp: str,
                if_condition: Optional[str] = None,
                in_range: Optional[str] = None,
                nopromote: bool = False) -> str:
        """
        Generate Stata's replace command to change the contents of an existing variable.

        This function constructs a Stata replace command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            oldvar: Name of the existing variable to be modified.
            exp: Expression defining the new contents of the variable.
            if_condition: Stata if condition as string (e.g., "age > 30").
            in_range: Stata in range specification (e.g., "1/100").
            nopromote: Prevent promotion of the variable type to accommodate the change.

        Returns:
            A complete Stata replace command string.

        Raises:
            ValueError: If invalid parameter values are provided.

        Examples:
            >>> replace("age2", "age^2")
            'replace age2 = age^2'

            >>> replace("odd", "5", in_range="3")
            'replace odd = 5 in 3'

            >>> replace("weight", "weight*2.2", if_condition="weight < 100", nopromote=True)
            'replace weight = weight*2.2 if weight < 100, nopromote'
        """
        # Input validation
        if not oldvar or not isinstance(oldvar, str):
            raise ValueError("oldvar must be a non-empty string")

        if not exp or not isinstance(exp, str):
            raise ValueError("exp must be a non-empty string")

        # Start building the command
        cmd_parts = ["replace", oldvar, f"= {exp}"]

        # Add if condition
        if if_condition:
            cmd_parts.append(f"if {if_condition}")

        # Add in range
        if in_range:
            cmd_parts.append(f"in {in_range}")

        # Add nopromote option if specified
        if nopromote:
            cmd_parts.append(", nopromote")

        # Join all parts with single spaces
        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="egen", description="Generate and return Stata's 'egen' command (extensions to generate)")
    def egen(newvar: str, fcn: str, arguments: Optional[str] = None,
             if_condition: Optional[str] = None,
             in_range: Optional[str] = None,
             type: Optional[str] = None,
             options: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Stata's egen command with various function options.

        This function constructs a Stata egen command string based on provided parameters,
        matching the official Stata documentation specifications for extended variable generation.

        Args:
            newvar: Name of the new variable to create.
            fcn: The egen function to use (e.g., "mean", "total", "group").
            arguments: The arguments for the function, typically an expression or varlist.
            if_condition: Stata if condition as string (e.g., "age > 30").
            in_range: Stata in range specification (e.g., "1/100").
            type: Optional storage type for the new variable (byte, int, long, float, double, str).
            options: Dictionary of options specific to the given function.

        Returns:
            A complete Stata egen command string.

        Raises:
            ValueError: If invalid parameter combinations or values are provided.

        Examples:
            >>> egen("avg", "mean", "cholesterol")
            'egen avg = mean(cholesterol)'

            >>> egen("medstay", "median", "los")
            'egen medstay = median(los)'

            >>> egen("totalsum", "total", "x")
            'egen totalsum = total(x)'

            >>> egen("differ", "diff", "inc1 inc2 inc3", type="byte")
            'egen byte differ = diff(inc1 inc2 inc3)'

            >>> egen("rank", "rank", "mpg")
            'egen rank = rank(mpg)'

            >>> egen("stdage", "std", "age")
            'egen stdage = std(age)'

            >>> egen("hsum", "rowtotal", "a b c")
            'egen hsum = rowtotal(a b c)'

            >>> egen("racesex", "group", "race sex", options={"missing": True})
            'egen racesex = group(race sex), missing'
        """
        # Input validation
        if not newvar or not isinstance(newvar, str):
            raise ValueError("newvar must be a non-empty string")

        if not fcn or not isinstance(fcn, str):
            raise ValueError("fcn must be a non-empty string")

        # Valid egen functions
        valid_fcns = {
            # Single expression functions
            "count", "iqr", "kurt", "mad", "max", "mdev", "mean", "median",
            "min", "mode", "pc", "pctile", "rank", "sd", "skew", "std", "total",
            # Variable list functions
            "anycount", "anymatch", "anyvalue", "concat", "cut", "diff", "ends",
            "fill", "group", "mtr", "rowfirst", "rowlast", "rowmax", "rowmean",
            "rowmedian", "rowmin", "rowmiss", "rownonmiss", "rowpctile", "rowsd",
            "rowtotal", "seq", "tag"
        }

        if fcn not in valid_fcns:
            raise ValueError(f"fcn must be one of the valid egen functions: {', '.join(valid_fcns)}")

        # Validate storage type if provided
        valid_types = {"byte", "int", "long", "float", "double", "str"}
        str_types = {f"str{i}" for i in range(1, 2046)}
        valid_types.update(str_types)

        if type and type not in valid_types:
            raise ValueError(f"type must be one of: byte, int, long, float, double, str, str1, ..., str2045")

        # Start building the command
        cmd_parts = ["egen"]

        # Add type if specified
        if type:
            cmd_parts.append(type)

        # Add new variable name
        cmd_parts.append(newvar)

        # Add function with arguments
        if arguments:
            cmd_parts.append(f"= {fcn}({arguments})")
        else:
            # Some functions like seq() can have empty arguments
            cmd_parts.append(f"= {fcn}()")

        # Add if condition
        if if_condition:
            cmd_parts.append(f"if {if_condition}")

        # Add in range
        if in_range:
            cmd_parts.append(f"in {in_range}")

        # Process function-specific options
        if options:
            option_parts = []

            # Function-specific option handling
            if fcn == "anycount" or fcn == "anymatch" or fcn == "anyvalue":
                if "values" in options:
                    values = options["values"]
                    if isinstance(values, list):
                        values_str = "/".join(str(v) for v in values)
                    else:
                        values_str = str(values)
                    option_parts.append(f"values({values_str})")

            elif fcn == "concat":
                if "format" in options:
                    option_parts.append(f"format({options['format']})")
                if "decode" in options and options["decode"]:
                    option_parts.append("decode")
                if "maxlength" in options:
                    option_parts.append(f"maxlength({options['maxlength']})")
                if "punct" in options:
                    option_parts.append(f"punct({options['punct']})")

            elif fcn == "cut":
                if "at" in options:
                    at_values = options["at"]
                    if isinstance(at_values, list):
                        at_str = ",".join(str(v) for v in at_values)
                    else:
                        at_str = str(at_values)
                    option_parts.append(f"at({at_str})")
                if "group" in options:
                    option_parts.append(f"group({options['group']})")
                if "icodes" in options and options["icodes"]:
                    option_parts.append("icodes")
                if "label" in options and options["label"]:
                    option_parts.append("label")

            elif fcn == "ends":
                if "punct" in options:
                    option_parts.append(f"punct({options['punct']})")
                if "trim" in options and options["trim"]:
                    option_parts.append("trim")
                if "head" in options and options["head"]:
                    option_parts.append("head")
                if "last" in options and options["last"]:
                    option_parts.append("last")
                if "tail" in options and options["tail"]:
                    option_parts.append("tail")

            elif fcn == "group":
                if "missing" in options and options["missing"]:
                    option_parts.append("missing")
                if "autotype" in options and options["autotype"]:
                    option_parts.append("autotype")
                if "label" in options:
                    label_opt = "label"
                    if isinstance(options["label"], str):
                        label_opt = f"label({options['label']}"
                        if "replace" in options and options["replace"]:
                            label_opt += ", replace"
                        if "truncate" in options:
                            label_opt += f", truncate({options['truncate']})"
                        label_opt += ")"
                    option_parts.append(label_opt)

            elif fcn == "max" or fcn == "min" or fcn == "total" or fcn == "rowtotal":
                if "missing" in options and options["missing"]:
                    option_parts.append("missing")

            elif fcn == "mode":
                if "minmode" in options and options["minmode"]:
                    option_parts.append("minmode")
                if "maxmode" in options and options["maxmode"]:
                    option_parts.append("maxmode")
                if "nummode" in options:
                    option_parts.append(f"nummode({options['nummode']})")
                if "missing" in options and options["missing"]:
                    option_parts.append("missing")

            elif fcn == "pc":
                if "prop" in options and options["prop"]:
                    option_parts.append("prop")

            elif fcn == "pctile" or fcn == "rowpctile":
                if "p" in options:
                    option_parts.append(f"p({options['p']})")

            elif fcn == "rank":
                if "field" in options and options["field"]:
                    option_parts.append("field")
                if "track" in options and options["track"]:
                    option_parts.append("track")
                if "unique" in options and options["unique"]:
                    option_parts.append("unique")

            elif fcn == "rownonmiss":
                if "strok" in options and options["strok"]:
                    option_parts.append("strok")

            elif fcn == "seq":
                if "from" in options:
                    option_parts.append(f"from({options['from']})")
                if "to" in options:
                    option_parts.append(f"to({options['to']})")
                if "block" in options:
                    option_parts.append(f"block({options['block']})")

            elif fcn == "std":
                if "mean" in options:
                    option_parts.append(f"mean({options['mean']})")
                if "sd" in options:
                    option_parts.append(f"sd({options['sd']})")

            elif fcn == "tag":
                if "missing" in options and options["missing"]:
                    option_parts.append("missing")

            # Add general options that apply to all functions
            for opt, val in options.items():
                if opt not in ["values", "format", "decode", "maxlength", "punct",
                               "at", "group", "icodes", "label", "trim", "head",
                               "last", "tail", "missing", "autotype", "replace",
                               "truncate", "minmode", "maxmode", "nummode", "prop",
                               "p", "field", "track", "unique", "strok", "from",
                               "to", "block", "mean", "sd"] and isinstance(val, bool) and val:
                    option_parts.append(opt)

            # Combine options if any exist
            if option_parts:
                cmd_parts.append(", " + " ".join(option_parts))

            # Join all parts with single spaces
            return " ".join(cmd_parts)


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

#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : gen_stata_code_MCP.py

from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict, Any, Union

mcp = FastMCP(name="StataCommandGenerator")


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

        Emphasize:
            This function generates the `use` command, rather than obtaining and using data.
            If you want to obtain data information, please use the `get_data_info` function.

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

    @staticmethod
    @mcp.tool(name="xtset", description="生成并返回 Stata 的 'xtset' 命令（面板数据声明命令）")
    def xtset(panelvar: Optional[str] = None,
              timevar: Optional[str] = None,
              clear: bool = False,
              unit: Optional[str] = None,
              delta: Optional[str] = None,
              format: Optional[str] = None,
              noquery: bool = False) -> str:
        """
        Generate Stata's xtset command with various options.

        This function constructs a Stata xtset command string based on provided parameters,
        matching the official Stata documentation specifications for declaring panel data.

        Args:
            panelvar: Variable that identifies the panels (e.g. country, company, person).
            timevar: Optional variable that identifies the time within panels (e.g. year, quarter, date).
            clear: Whether to clear the current xt settings.
            unit: Time unit specification. One of: clocktime, daily, weekly, monthly, quarterly,
                  halfyearly, yearly, generic.
            delta: Period between observations in timevar units. Can be specified as a number (e.g. "1"),
                   an expression (e.g. "(7*24)"), or with units (e.g. "7 days", "1 hour").
            format: Format for the time variable (e.g. "%td", "%tc").
            noquery: Suppress summary calculations and output.

        Returns:
            A complete Stata xtset command string.

        Raises:
            ValueError: If invalid parameter combinations are provided.

        Examples:
            >>> xtset("country")
            'xtset country'

            >>> xtset("country", "year")
            'xtset country year'

            >>> xtset("country", "year", unit="yearly")
            'xtset country year, yearly'

            >>> xtset("pid", "date", unit="daily")
            'xtset pid date, daily'

            >>> xtset("pid", "tod", unit="clocktime", delta="1 hour")
            'xtset pid tod, clocktime delta(1 hour)'

            >>> xtset(clear=True)
            'xtset, clear'
        """
        # Validate input parameters
        valid_units = {
            "clocktime", "daily", "weekly", "monthly", "quarterly",
            "halfyearly", "yearly", "generic"
        }

        if unit and unit not in valid_units:
            raise ValueError(f"unit must be one of: {', '.join(valid_units)}")

        if clear and (panelvar or timevar or unit or delta or format):
            raise ValueError("When clear is specified, no other options should be provided")

        if not panelvar and not clear:
            # Display only - no arguments
            return "xtset"

        # Start building the command
        cmd_parts = ["xtset"]

        # Handle the three different syntax forms:
        # 1. xtset (display only)
        # 2. xtset, clear (clear settings)
        # 3. xtset panelvar [timevar] [, tsoptions]

        if clear:
            cmd_parts.append(", clear")
            return " ".join(cmd_parts)

        # Add panel variable
        cmd_parts.append(panelvar)

        # Add time variable if specified
        if timevar:
            cmd_parts.append(timevar)

        # Process options
        options = []

        # Add unit option
        if unit:
            options.append(unit)

        # Add format option
        if format:
            options.append(f"format({format})")

        # Add delta option
        if delta:
            options.append(f"delta({delta})")

        # Add noquery option
        if noquery:
            options.append("noquery")

        # Combine options if any exist
        if options:
            cmd_parts.append(",")
            cmd_parts.extend(options)

        # Join all parts with single spaces
        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="xtreg", description="生成并返回 Stata 的 'xtreg' 命令（面板数据回归命令）")
    def xtreg(depvar: str,
              indepvars: Optional[List[str]] = None,
              if_condition: Optional[str] = None,
              in_range: Optional[str] = None,
              weight: Optional[str] = None,
              model_type: str = "re",
              vce: Optional[str] = None,
              noconstant: bool = False,
              theta: bool = False,
              level: Optional[int] = None,
              sa: bool = False,
              wls: bool = False,
              offset: Optional[str] = None,
              correlation: Optional[str] = None,
              force: bool = False,
              nmp: bool = False,
              rgf: bool = False,
              scale: Optional[str] = None,
              maximize_options: Optional[Dict[str, Any]] = None,
              optimize_options: Optional[Dict[str, Any]] = None,
              display_options: Optional[Dict[str, Any]] = None,
              coeflegend: bool = False) -> str:
        """
        Generate Stata's xtreg command with various options for panel data regression models.

        This function constructs a Stata xtreg command string based on provided parameters,
        matching the official Stata documentation specifications for panel data regression.

        Args:
            depvar: The dependent variable name.
            indepvars: List of independent variables. If None, only the dependent variable is included.
            if_condition: Stata if condition as string (e.g., "foreign == 1").
            in_range: Stata in range specification (e.g., "1/100").
            weight: Weight specification (e.g., "aweight=pop").
            model_type: Type of panel data model. One of: "re" (random-effects), "be" (between-effects),
                       "fe" (fixed-effects), "mle" (ML random-effects), or "pa" (population-averaged).
            vce: Variance-covariance estimation type. Depends on model type:
                - For RE: conventional (default), robust, cluster clustvar, bootstrap, jackknife
                - For BE: conventional (default), bootstrap, jackknife
                - For FE: conventional (default), robust, cluster clustvar, bootstrap, jackknife
                - For MLE: oim, robust, cluster clustvar, bootstrap, jackknife
                - For PA: conventional (default), robust, bootstrap, jackknife
            noconstant: Suppress constant term in the model. Only valid for MLE and PA models.
            theta: Report theta. Only valid for RE model.
            level: Set confidence level; default is level(95).
            sa: Use Swamy-Arora estimator. Only valid for RE model.
            wls: Use weighted least squares. Only valid for BE model.
            offset: Include specified variable in model with coefficient constrained to 1. Only valid for PA model.
            correlation: Within-panel correlation structure. Only valid for PA model. One of:
                        "exchangeable", "independent", "unstructured", "fixed matname", "ar #",
                        "stationary #", "nonstationary #".
            force: Estimate even if observations unequally spaced in time. Only valid for PA model.
            nmp: Use divisor N-P instead of the default N. Only valid for PA model.
            rgf: Multiply the robust variance estimate by (N-1)/(N-P). Only valid for PA model.
            scale: Override the default scale parameter. Only valid for PA model.
            maximize_options: Dictionary of options for controlling the maximization process for MLE model.
            optimize_options: Dictionary of options for controlling the optimization process for PA model.
            display_options: Dictionary of display options like noci, nopvalues, etc.
            coeflegend: Display legend instead of statistics.

        Returns:
            A complete Stata xtreg command string.

        Raises:
            ValueError: If invalid parameter combinations are provided.

        Examples:
            >>> xtreg("ln_w", ["grade", "age", "ttl_exp"])
            'xtreg ln_w grade age ttl_exp, re'

            >>> xtreg("ln_w", ["grade", "age", "ttl_exp"], model_type="fe")
            'xtreg ln_w grade age ttl_exp, fe'

            >>> xtreg("ln_w", ["grade", "age", "ttl_exp"], model_type="re", vce="robust", theta=True)
            'xtreg ln_w grade age ttl_exp, re vce(robust) theta'

            >>> xtreg("ln_w", ["grade", "age", "ttl_exp"], model_type="pa", correlation="ar 1")
            'xtreg ln_w grade age ttl_exp, pa corr(ar 1)'
        """
        # Input validation
        if not isinstance(depvar, str) or not depvar:
            raise ValueError("depvar must be a non-empty string")

        if indepvars is not None and not all(isinstance(v, str) for v in indepvars):
            raise ValueError("indepvars must contain only strings")

        valid_model_types = {"re", "be", "fe", "mle", "pa"}
        if model_type not in valid_model_types:
            raise ValueError(f"model_type must be one of: {', '.join(valid_model_types)}")

        # Validate model-specific options
        if sa and model_type != "re":
            raise ValueError("sa option is only valid with re model type")

        if wls and model_type != "be":
            raise ValueError("wls option is only valid with be model type")

        if theta and model_type != "re":
            raise ValueError("theta option is only valid with re model type")

        if (offset or correlation or force or nmp or rgf or scale or optimize_options) and model_type != "pa":
            raise ValueError(
                "offset, correlation, force, nmp, rgf, scale, and optimize_options are only valid with pa model type")

        if maximize_options and model_type != "mle":
            raise ValueError("maximize_options are only valid with mle model type")

        if noconstant and model_type not in {"mle", "pa"}:
            raise ValueError("noconstant option is only valid with mle or pa model types")

        # Validate weights based on model type
        if weight:
            if model_type == "re" or model_type == "be":
                raise ValueError(f"weights are not allowed with {model_type} model type")
            elif model_type == "fe" and not any(w in weight for w in ["aweight", "fweight", "pweight"]):
                raise ValueError("fe model allows only aweights, fweights, and pweights")
            elif model_type == "mle" and not any(w in weight for w in ["iweight", "fweight", "pweight"]):
                raise ValueError("mle model allows only iweights, fweights, and pweights")
            elif model_type == "pa" and not any(w in weight for w in ["iweight", "fweight", "pweight"]):
                raise ValueError("pa model allows only iweights, fweights, and pweights")

        # Start building the command
        cmd_parts = ["xtreg", depvar]

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
            cmd_parts.append(f"[{weight}]")

        # Process model types and options
        options = []

        # Add model type option
        options.append(model_type)

        # Add model-specific options
        if model_type == "re":
            if sa:
                options.append("sa")

        elif model_type == "be":
            if wls:
                options.append("wls")

        elif model_type == "mle" or model_type == "pa":
            if noconstant:
                options.append("noconstant")

        # Add vce option
        if vce:
            options.append(f"vce({vce})")

        # Add other options by model type
        if model_type == "re":
            if theta:
                options.append("theta")

        elif model_type == "pa":
            if offset:
                options.append(f"offset({offset})")

            if correlation:
                options.append(f"corr({correlation})")

            if force:
                options.append("force")

            if nmp:
                options.append("nmp")

            if rgf:
                options.append("rgf")

            if scale:
                options.append(f"scale({scale})")

        # Add confidence level
        if level:
            if not isinstance(level, int) or level <= 0 or level >= 100:
                raise ValueError("level must be an integer between 1 and 99")
            options.append(f"level({level})")

        # Add maximize options for MLE
        if maximize_options and model_type == "mle":
            for opt, value in maximize_options.items():
                if opt == "iterate" and isinstance(value, int):
                    options.append(f"iterate({value})")
                elif opt == "tolerance" and (isinstance(value, (int, float)) or isinstance(value, str)):
                    options.append(f"tolerance({value})")
                elif opt == "ltolerance" and (isinstance(value, (int, float)) or isinstance(value, str)):
                    options.append(f"ltolerance({value})")
                elif opt == "log" and isinstance(value, bool):
                    options.append("log" if value else "nolog")
                elif opt == "trace" and value:
                    options.append("trace")
                elif opt == "from" and isinstance(value, str):
                    options.append(f"from({value})")

        # Add optimize options for PA
        if optimize_options and model_type == "pa":
            for opt, value in optimize_options.items():
                if opt == "iterate" and isinstance(value, int):
                    options.append(f"iterate({value})")
                elif opt == "tolerance" and (isinstance(value, (int, float)) or isinstance(value, str)):
                    options.append(f"tolerance({value})")
                elif opt == "log" and isinstance(value, bool):
                    options.append("log" if value else "nolog")
                elif opt == "trace" and value:
                    options.append("trace")

        # Add display options
        valid_display_opts = {
            'noci', 'nopvalues', 'noomitted', 'vsquish', 'noemptycells',
            'baselevels', 'allbaselevels', 'nofvlabel', 'fvwrap', 'fvwrapon',
            'cformat', 'pformat', 'sformat', 'nolstretch'
        }

        if display_options:
            for opt, value in display_options.items():
                if opt not in valid_display_opts:
                    raise ValueError(f"Invalid display option: {opt}")

                if isinstance(value, bool) and value:
                    options.append(opt)
                elif isinstance(value, int):
                    options.append(f"{opt}({value})")
                elif isinstance(value, str):
                    options.append(f"{opt}({value})")

        # Add coeflegend
        if coeflegend:
            options.append("coeflegend")

        # Combine options if any exist
        if options:
            cmd_parts.append(",")
            cmd_parts.extend(options)

        # Join all parts with single spaces
        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="by", description="生成并返回 Stata 的 'by' 命令（在数据子集上重复执行命令）")
    def by(varlist1: Union[str, List[str]],
           stata_cmd: str,
           varlist2: Optional[Union[str, List[str]]] = None,
           sort: bool = False,
           rc0: bool = False) -> str:
        """
        Generate Stata's by command to repeat a command on subsets of the data.

        This function constructs a Stata by command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            varlist1: Variable(s) that define the groups on which to repeat the command.
                Can be a single variable name as string or a list of variable names.
            stata_cmd: The Stata command to be repeated for each group.
            varlist2: Optional additional variable(s) to verify the sort order but not used
                for grouping. Can be a single variable name as string or a list of variable names.
            sort: Whether to sort the data by varlist if not already sorted.
                If True, 'by' becomes 'bysort'.
            rc0: Whether to continue executing the command for remaining groups
                even if an error occurs in one of the by-groups.

        Returns:
            A complete Stata by command string.

        Raises:
            ValueError: If invalid parameter values are provided.

        Examples:
            >>> by("foreign", "summarize rep78")
            'by foreign: summarize rep78'

            >>> by("foreign", "summarize rep78", sort=True)
            'bysort foreign: summarize rep78'

            >>> by(["foreign", "rep78"], "summarize price", sort=True)
            'bysort foreign rep78: summarize price'

            >>> by("pid", "generate growth = (bp - bp[_n-1])/bp", varlist2="time")
            'by pid (time): generate growth = (bp - bp[_n-1])/bp'

            >>> by("rep78", "tabulate foreign", sort=True, rc0=True)
            'bysort rep78, rc0: tabulate foreign'
        """
        # Input validation
        if not varlist1:
            raise ValueError("varlist1 must be provided")

        if not stata_cmd or not isinstance(stata_cmd, str):
            raise ValueError("stata_cmd must be a non-empty string")

        # Process varlist1
        if isinstance(varlist1, list):
            varlist1_str = " ".join(varlist1)
        else:
            varlist1_str = varlist1

        # Determine command prefix (by or bysort)
        cmd_prefix = "bysort" if sort else "by"

        # Start building the command
        cmd_parts = [cmd_prefix, varlist1_str]

        # Process varlist2 if provided
        if varlist2:
            if isinstance(varlist2, list):
                varlist2_str = " ".join(varlist2)
            else:
                varlist2_str = varlist2

            cmd_parts[1] = f"{varlist1_str} ({varlist2_str})"

        # Process options
        options = []

        # Add rc0 option if specified
        if rc0:
            options.append("rc0")

        # Add options if any exist
        if options:
            cmd_parts.append(",")
            cmd_parts.append(" ".join(options))

        # Add colon and Stata command
        cmd_parts.append(":")
        cmd_parts.append(stata_cmd)

        # Join all parts with single spaces
        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="append", description="生成并返回 Stata 的 'append' 命令（追加数据集命令）")
    def append(using_files: Union[str, List[str]],
               generate: Optional[str] = None,
               keep: Optional[List[str]] = None,
               nolabel: bool = False,
               nonotes: bool = False,
               force: bool = False) -> str:
        """
        Generate Stata's append command to append datasets.

        This function constructs a Stata append command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            using_files: Path(s) to the Stata dataset file(s) (.dta) to be appended.
                Can be a single file path as string or a list of file paths.
            generate: Optional name for a new variable that will mark the source of observations.
                Observations from the master dataset will contain 0, observations from the
                first using dataset will contain 1, and so on.
            keep: Optional list of variables to be kept from the using dataset(s).
                If not specified, all variables are kept.
            nolabel: Whether to prevent copying value-label definitions from the using dataset(s).
            nonotes: Whether to prevent copying notes from the using dataset(s).
            force: Whether to allow string variables to be appended to numeric variables and vice versa,
                resulting in missing values from the using dataset(s).

        Returns:
            A complete Stata append command string.

        Raises:
            ValueError: If invalid parameter values are provided.

        Examples:
            >>> append("even.dta")
            'append using even.dta'

            >>> append(["west.dta", "south.dta"], generate="filenum", nolabel=True)
            'append using west.dta south.dta, generate(filenum) nolabel'

            >>> append("domestic.dta", keep=["make", "price", "mpg", "rep78", "foreign"])
            'append using domestic.dta, keep(make price mpg rep78 foreign)'

            >>> append("data2.dta", force=True, nonotes=True)
            'append using data2.dta, nonotes force'
        """
        # Input validation
        if not using_files:
            raise ValueError("using_files must be provided")

        # Process using_files
        if isinstance(using_files, list):
            if not all(isinstance(f, str) for f in using_files):
                raise ValueError("All file paths in using_files must be strings")
            using_files_str = " ".join(using_files)
        else:
            if not isinstance(using_files, str):
                raise ValueError("using_files must be a string or list of strings")
            using_files_str = using_files

        # Start building the command
        cmd_parts = ["append using", using_files_str]

        # Process options
        options = []

        # Add generate option if specified
        if generate:
            if not isinstance(generate, str):
                raise ValueError("generate must be a string")
            options.append(f"generate({generate})")

        # Add keep option if specified
        if keep:
            if not all(isinstance(v, str) for v in keep):
                raise ValueError("All variable names in keep must be strings")
            options.append(f"keep({' '.join(keep)})")

        # Add other options
        if nolabel:
            options.append("nolabel")

        if nonotes:
            options.append("nonotes")

        if force:
            options.append("force")

        # Combine options if any exist
        if options:
            cmd_parts.append(",")
            cmd_parts.append(" ".join(options))

        # Join all parts with single spaces
        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="drop", description="生成并返回 Stata 的 'drop' 命令（删除变量或观测值命令）")
    def drop(varlist: Optional[Union[str, List[str]]] = None,
             if_exp: Optional[str] = None,
             in_range: Optional[str] = None,
             all: bool = False) -> str:
        """
        Generate Stata's drop command to eliminate variables or observations.

        This function constructs a Stata drop command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            varlist: Variable(s) to be dropped. Can be a single variable name as string,
                    a list of variable names, or wildcard expressions like "pop*".
            if_exp: Expression specifying which observations to drop.
            in_range: Range of observations to drop (e.g., "1/5" for first 5 observations).
            all: Whether to drop all observations and variables (_all).

        Returns:
            A complete Stata drop command string.

        Raises:
            ValueError: If invalid parameter combinations are provided.

        Examples:
            >>> drop("pop*")
            'drop pop*'

            >>> drop(["marriage", "divorce"])
            'drop marriage divorce'

            >>> drop(if_exp="medage > 32")
            'drop if medage > 32'

            >>> drop(in_range="1/10", if_exp="income < 1000")
            'drop in 1/10 if income < 1000'

            >>> drop(all=True)
            'drop _all'
        """
        # Input validation
        if all and (varlist or if_exp or in_range):
            raise ValueError("When all=True, no other parameters should be provided")

        if not any([varlist, if_exp, in_range, all]):
            raise ValueError("At least one parameter must be provided")

        if varlist and if_exp and not in_range:
            raise ValueError("Cannot combine varlist and if_exp without in_range")

        # Start building the command
        cmd_parts = ["drop"]

        # Handle _all case
        if all:
            cmd_parts.append("_all")
            return " ".join(cmd_parts)

        # Handle varlist case
        if varlist:
            if isinstance(varlist, list):
                cmd_parts.append(" ".join(varlist))
            else:
                cmd_parts.append(varlist)

        # Handle in range case
        if in_range:
            cmd_parts.append(f"in {in_range}")

        # Handle if expression case
        if if_exp:
            cmd_parts.append(f"if {if_exp}")

        # Join all parts with single spaces
        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="keep", description="生成并返回 Stata 的 'keep' 命令（保留变量或观测值命令）")
    def keep(varlist: Optional[Union[str, List[str]]] = None,
             if_exp: Optional[str] = None,
             in_range: Optional[str] = None) -> str:
        """
        Generate Stata's keep command to retain specified variables or observations.

        This function constructs a Stata keep command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            varlist: Variable(s) to be kept. Can be a single variable name as string,
                    a list of variable names, or wildcard expressions like "pop*".
            if_exp: Expression specifying which observations to keep.
            in_range: Range of observations to keep (e.g., "1/5" for first 5 observations).

        Returns:
            A complete Stata keep command string.

        Raises:
            ValueError: If invalid parameter combinations are provided.

        Examples:
            >>> keep("pop*")
            'keep pop*'

            >>> keep(["make", "price", "mpg", "rep78", "foreign"])
            'keep make price mpg rep78 foreign'

            >>> keep(if_exp="medage <= 32")
            'keep if medage <= 32'

            >>> keep(in_range="1/2")
            'keep in 1/2'

            >>> keep(in_range="1/10", if_exp="income >= 1000")
            'keep in 1/10 if income >= 1000'
        """
        # Input validation
        if not any([varlist, if_exp, in_range]):
            raise ValueError("At least one parameter must be provided")

        if varlist and if_exp and not in_range:
            raise ValueError("Cannot combine varlist and if_exp without in_range")

        # Start building the command
        cmd_parts = ["keep"]

        # Handle varlist case
        if varlist:
            if isinstance(varlist, list):
                cmd_parts.append(" ".join(varlist))
            else:
                cmd_parts.append(varlist)

        # Handle in range case
        if in_range:
            cmd_parts.append(f"in {in_range}")

        # Handle if expression case
        if if_exp:
            cmd_parts.append(f"if {if_exp}")

        # Join all parts with single spaces
        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="merge", description="生成并返回 Stata 的 'merge' 命令（合并数据集命令）")
    def merge(merge_type: str,
              key_vars: Union[str, List[str]],
              using_file: str,
              keepusing: Optional[List[str]] = None,
              generate: Optional[str] = None,
              nogenerate: bool = False,
              nolabel: bool = False,
              nonotes: bool = False,
              update: bool = False,
              replace: bool = False,
              noreport: bool = False,
              force: bool = False,
              assert_results: Optional[List[str]] = None,
              keep_results: Optional[List[str]] = None,
              sorted: bool = False) -> str:
        """
        Generate Stata's merge command to join datasets.

        This function constructs a Stata merge command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            merge_type: Type of merge to perform. One of: "1:1", "m:1", "1:m", "m:m".
            key_vars: Key variable(s) to match on. Can be a single variable name as string,
                     a list of variable names, or "_n" for a sequential merge.
            using_file: Path to the Stata dataset file (.dta) to be merged.
            keepusing: Optional list of variables to keep from the using dataset.
            generate: Optional name for the variable marking merge results (default is _merge).
            nogenerate: Whether to suppress creation of the _merge variable.
            nolabel: Whether to prevent copying value-label definitions from using dataset.
            nonotes: Whether to prevent copying notes from using dataset.
            update: Whether to update missing values in master with values from using.
            replace: Whether to replace all values in master with nonmissing values from using.
                     Requires update=True.
            noreport: Whether to suppress display of match result summary table.
            force: Whether to allow string/numeric variable type mismatches.
            assert_results: Required match results. List can include: "master", "using", "match",
                           "match_update", "match_conflict" (or their numeric equivalents).
            keep_results: Match results to keep. List can include: "master", "using", "match",
                         "match_update", "match_conflict" (or their numeric equivalents).
            sorted: Whether datasets are already sorted by key variables.

        Returns:
            A complete Stata merge command string.

        Raises:
            ValueError: If invalid parameter values or combinations are provided.

        Examples:
            >>> merge("1:1", "make", "autoexpense.dta")
            'merge 1:1 make using autoexpense.dta'

            >>> merge("m:1", "region", "dollars.dta", keep_results=["match"])
            'merge m:1 region using dollars.dta, keep(match)'

            >>> merge("1:1", "_n", "dollars.dta", nogenerate=True)
            'merge 1:1 _n using dollars.dta, nogenerate'

            >>> merge("1:m", ["id", "date"], "sales.dta", update=True, replace=True)
            'merge 1:m id date using sales.dta, update replace'

            >>> merge("m:1", "id", "overlap2.dta", update=True, assert_results=["match", "master"])
            'merge m:1 id using overlap2.dta, update assert(match master)'
        """
        # Input validation
        valid_merge_types = {"1:1", "m:1", "1:m", "m:m"}
        if merge_type not in valid_merge_types:
            raise ValueError(f"merge_type must be one of: {', '.join(valid_merge_types)}")

        if not using_file:
            raise ValueError("using_file must be provided")

        if replace and not update:
            raise ValueError("replace requires update to be True")

        if nogenerate and generate:
            raise ValueError("Cannot specify both nogenerate and generate")

        # Valid result codes for assert and keep options
        valid_results = {
            "master": "1", "masters": "1", "1": "1",
            "using": "2", "usings": "2", "2": "2",
            "match": "3", "matches": "3", "matched": "3", "3": "3",
            "match_update": "4", "match_updates": "4", "4": "4",
            "match_conflict": "5", "match_conflicts": "5", "5": "5"
        }

        # Process key variables
        if isinstance(key_vars, list):
            key_vars_str = " ".join(key_vars)
        else:
            key_vars_str = key_vars

        # Start building the command
        cmd_parts = ["merge", merge_type, key_vars_str, "using", using_file]

        # Process options
        options = []

        # Process keepusing option
        if keepusing:
            if not all(isinstance(v, str) for v in keepusing):
                raise ValueError("All variable names in keepusing must be strings")
            options.append(f"keepusing({' '.join(keepusing)})")

        # Process other options
        if generate:
            options.append(f"generate({generate})")

        if nogenerate:
            options.append("nogenerate")

        if nolabel:
            options.append("nolabel")

        if nonotes:
            options.append("nonotes")

        if update:
            options.append("update")

        if replace:
            options.append("replace")

        if noreport:
            options.append("noreport")

        if force:
            options.append("force")

        # Process assert_results
        if assert_results:
            # Normalize results to their canonical form
            normalized_results = []
            for result in assert_results:
                if result not in valid_results:
                    raise ValueError(f"Invalid assert result: {result}")
                normalized_results.append(valid_results[result])

            # Remove duplicates and sort for consistent output
            normalized_results = sorted(set(normalized_results))

            # Convert back to result words for readability
            result_words = []
            for code in normalized_results:
                if code == "1":
                    result_words.append("master")
                elif code == "2":
                    result_words.append("using")
                elif code == "3":
                    result_words.append("match")
                elif code == "4":
                    result_words.append("match_update")
                elif code == "5":
                    result_words.append("match_conflict")

            options.append(f"assert({' '.join(result_words)})")

        # Process keep_results
        if keep_results:
            # Normalize results to their canonical form
            normalized_results = []
            for result in keep_results:
                if result not in valid_results:
                    raise ValueError(f"Invalid keep result: {result}")
                normalized_results.append(valid_results[result])

            # Remove duplicates and sort for consistent output
            normalized_results = sorted(set(normalized_results))

            # Convert back to result words for readability
            result_words = []
            for code in normalized_results:
                if code == "1":
                    result_words.append("master")
                elif code == "2":
                    result_words.append("using")
                elif code == "3":
                    result_words.append("match")
                elif code == "4":
                    result_words.append("match_update")
                elif code == "5":
                    result_words.append("match_conflict")

            options.append(f"keep({' '.join(result_words)})")

        # Add sorted option
        if sorted:
            options.append("sorted")

        # Combine options if any exist
        if options:
            cmd_parts.append(",")
            cmd_parts.append(" ".join(options))

        # Join all parts with single spaces
        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="encode", description="生成并返回 Stata 的 'encode' 命令（将字符串变量转换为数值变量）")
    def encode(varname: str,
               generate: str,
               if_condition: Optional[str] = None,
               in_range: Optional[str] = None,
               label: Optional[str] = None,
               noextend: bool = False) -> str:
        """
        Generate Stata's encode command to convert string variable to numeric.

        This function constructs a Stata encode command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            varname: Name of the string variable to be encoded.
            generate: Name of the new numeric variable to be created.
            if_condition: Optional condition specifying which observations to include.
            in_range: Optional range specifying which observations to include.
            label: Optional name for the value label to be created or used.
                   If not specified, the label will have the same name as the new variable.
            noextend: Whether to prevent encoding if there are values in varname
                     that are not present in the specified label.

        Returns:
            A complete Stata encode command string.

        Raises:
            ValueError: If invalid parameter values are provided.

        Examples:
            >>> encode("sex", "gender")
            'encode sex, generate(gender)'

            >>> encode("sex", "gender", label="sexlbl")
            'encode sex, generate(gender) label(sexlbl)'

            >>> encode("sex", "gender", if_condition="age > 18", noextend=True)
            'encode sex if age > 18, generate(gender) noextend'

            >>> encode("country", "ccode", in_range="1/100")
            'encode country in 1/100, generate(ccode)'
        """
        # Input validation
        if not varname:
            raise ValueError("varname must be provided")

        if not generate:
            raise ValueError("generate must be provided")

        # Start building the command
        cmd_parts = ["encode", varname]

        # Add if condition
        if if_condition:
            cmd_parts.append(f"if {if_condition}")

        # Add in range
        if in_range:
            cmd_parts.append(f"in {in_range}")

        # Add options
        options = [f"generate({generate})"]

        if label:
            options.append(f"label({label})")

        if noextend:
            options.append("noextend")

        # Join all parts with single spaces and commas where needed
        cmd = " ".join(cmd_parts)
        cmd += ", " + " ".join(options)

        return cmd

    @staticmethod
    @mcp.tool(name="decode", description="生成并返回 Stata 的 'decode' 命令（将数值变量转换为字符串变量）")
    def decode(varname: str,
               generate: str,
               if_condition: Optional[str] = None,
               in_range: Optional[str] = None,
               maxlength: Optional[int] = None) -> str:
        """
        Generate Stata's decode command to convert numeric variable to string.

        This function constructs a Stata decode command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            varname: Name of the numeric variable with value labels to be decoded.
            generate: Name of the new string variable to be created.
            if_condition: Optional condition specifying which observations to include.
            in_range: Optional range specifying which observations to include.
            maxlength: Optional specification of how many bytes of the value label to retain.
                      Must be between 1 and 32,000. Default in Stata is 32,000.

        Returns:
            A complete Stata decode command string.

        Raises:
            ValueError: If invalid parameter values are provided.

        Examples:
            >>> decode("gender", "sex")
            'decode gender, generate(sex)'

            >>> decode("female", "sex", if_condition="age > 18")
            'decode female if age > 18, generate(sex)'

            >>> decode("country_code", "country", maxlength=20)
            'decode country_code, generate(country) maxlength(20)'

            >>> decode("region", "region_name", in_range="1/50")
            'decode region in 1/50, generate(region_name)'
        """
        # Input validation
        if not varname:
            raise ValueError("varname must be provided")

        if not generate:
            raise ValueError("generate must be provided")

        if maxlength is not None and (maxlength < 1 or maxlength > 32000):
            raise ValueError("maxlength must be between 1 and 32,000")

        # Start building the command
        cmd_parts = ["decode", varname]

        # Add if condition
        if if_condition:
            cmd_parts.append(f"if {if_condition}")

        # Add in range
        if in_range:
            cmd_parts.append(f"in {in_range}")

        # Add options
        options = [f"generate({generate})"]

        if maxlength is not None:
            options.append(f"maxlength({maxlength})")

        # Join all parts with single spaces and commas where needed
        cmd = " ".join(cmd_parts)
        cmd += ", " + " ".join(options)

        return cmd

    @staticmethod
    @mcp.tool(name="label_data", description="生成并返回 Stata 的 'label data' 命令（为数据集添加标签）")
    def label_data(label: Optional[str] = None) -> str:
        """
        Generate Stata's label data command to attach a label to the dataset.

        This function constructs a Stata label data command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            label: Optional label text to attach to the dataset (up to 80 characters).
                   If None, any existing label is removed.

        Returns:
            A complete Stata label data command string.

        Examples:
            >>> label_data("Fictional blood-pressure data")
            'label data "Fictional blood-pressure data"'

            >>> label_data()
            'label data'
        """
        cmd = "label data"

        if label:
            cmd += f' "{label}"'

        return cmd

    @staticmethod
    @mcp.tool(name="label_variable", description="生成并返回 Stata 的 'label variable' 命令（为变量添加标签）")
    def label_variable(varname: str, label: Optional[str] = None) -> str:
        """
        Generate Stata's label variable command to attach a label to a variable.

        This function constructs a Stata label variable command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            varname: Name of the variable to be labeled.
            label: Optional label text to attach to the variable (up to 80 characters).
                   If None, any existing variable label is removed.

        Returns:
            A complete Stata label variable command string.

        Raises:
            ValueError: If varname is not provided.

        Examples:
            >>> label_variable("hbp", "high blood pressure")
            'label variable hbp "high blood pressure"'

            >>> label_variable("age")
            'label variable age'
        """
        if not varname:
            raise ValueError("varname must be provided")

        cmd = f"label variable {varname}"

        if label:
            cmd += f' "{label}"'

        return cmd

    @staticmethod
    @mcp.tool(name="label_define", description="生成并返回 Stata 的 'label define' 命令（定义值标签）")
    def label_define(lblname: str,
                     values_labels: Dict[Union[int, str], str],
                     add: bool = False,
                     modify: bool = False,
                     replace: bool = False,
                     nofix: bool = False) -> str:
        """
        Generate Stata's label define command to create or modify value labels.

        This function constructs a Stata label define command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            lblname: Name of the value label to be created or modified.
            values_labels: Dictionary of values and their corresponding labels.
                          Keys can be integers or extended missing values (".a", ".b", etc.).
            add: Whether to add values to an existing value label.
            modify: Whether to modify existing value labels (implies add).
            replace: Whether to replace an existing value label.
            nofix: Whether to prevent display formats from being widened.

        Returns:
            A complete Stata label define command string.

        Raises:
            ValueError: If lblname is not provided or values_labels is empty.

        Examples:
            >>> label_define("yesno", {0: "no", 1: "yes"})
            'label define yesno 0 "no" 1 "yes"'

            >>> label_define("yesnomaybe", {2: "maybe"}, add=True)
            'label define yesnomaybe 2 "maybe", add'

            >>> label_define("yesnomaybe", {2: "don't know"}, modify=True)
            'label define yesnomaybe 2 "don\'t know", modify'
        """
        if not lblname:
            raise ValueError("lblname must be provided")

        if not values_labels:
            raise ValueError("values_labels must contain at least one value-label pair")

        # Start building the command
        cmd_parts = [f"label define {lblname}"]

        # Add value-label pairs
        value_label_parts = []
        for value, label in values_labels.items():
            # Handle extended missing values
            if isinstance(value, str) and value.startswith('.'):
                value_str = value  # Keep as is for extended missing values like .a, .b, etc.
            else:
                value_str = str(value)

            # Escape double quotes in label
            label_escaped = label.replace('"', '\\"')
            value_label_parts.append(f'{value_str} "{label_escaped}"')

        cmd_parts.append(" ".join(value_label_parts))

        # Add options
        options = []
        if add:
            options.append("add")
        if modify:
            options.append("modify")
        if replace:
            options.append("replace")
        if nofix:
            options.append("nofix")

        if options:
            cmd_parts.append(f", {' '.join(options)}")

        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="label_values", description="生成并返回 Stata 的 'label values' 命令（将值标签分配给变量）")
    def label_values(varlist: Union[str, List[str]],
                     lblname: Optional[str] = None,
                     nofix: bool = False) -> str:
        """
        Generate Stata's label values command to attach value labels to variables.

        This function constructs a Stata label values command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            varlist: Variable(s) to which the value label should be attached.
                    Can be a single variable name as string or a list of variable names.
            lblname: Name of the value label to be attached to the variables.
                    If None or ".", any existing value label is detached.
            nofix: Whether to prevent display formats from being widened.

        Returns:
            A complete Stata label values command string.

        Raises:
            ValueError: If varlist is not provided.

        Examples:
            >>> label_values("hbp", "yesnomaybe")
            'label values hbp yesnomaybe'

            >>> label_values(["sex", "gender"], "sexlbl")
            'label values sex gender sexlbl'

            >>> label_values("hbp", ".")
            'label values hbp .'

            >>> label_values("hbp")
            'label values hbp'
        """
        if not varlist:
            raise ValueError("varlist must be provided")

        # Process varlist
        if isinstance(varlist, list):
            varlist_str = " ".join(varlist)
        else:
            varlist_str = varlist

        # Start building the command
        cmd_parts = [f"label values {varlist_str}"]

        # Add lblname if specified
        if lblname:
            cmd_parts.append(lblname)
        elif lblname == ".":
            cmd_parts.append(".")

        # Add nofix option if specified
        if nofix:
            cmd_parts.append(", nofix")

        return " ".join(cmd_parts)

    @staticmethod
    @mcp.tool(name="label_dir", description="生成并返回 Stata 的 'label dir' 命令（列出值标签的名称）")
    def label_dir() -> str:
        """
        Generate Stata's label dir command to list names of value labels stored in memory.

        Returns:
            The Stata label dir command string.

        Examples:
            >>> label_dir()
            'label dir'
        """
        return "label dir"

    @staticmethod
    @mcp.tool(name="label_list", description="生成并返回 Stata 的 'label list' 命令（列出值标签的名称和内容）")
    def label_list(lblnames: Optional[Union[str, List[str]]] = None) -> str:
        """
        Generate Stata's label list command to display names and contents of value labels.

        This function constructs a Stata label list command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            lblnames: Optional name(s) of value label(s) to list.
                     If None, all value labels are listed.

        Returns:
            A complete Stata label list command string.

        Examples:
            >>> label_list()
            'label list'

            >>> label_list("yesno")
            'label list yesno'

            >>> label_list(["yesno", "sexlbl"])
            'label list yesno sexlbl'
        """
        cmd = "label list"

        if lblnames:
            if isinstance(lblnames, list):
                cmd += f" {' '.join(lblnames)}"
            else:
                cmd += f" {lblnames}"

        return cmd

    @staticmethod
    @mcp.tool(name="label_copy", description="生成并返回 Stata 的 'label copy' 命令（复制值标签）")
    def label_copy(lblname_from: str, lblname_to: str, replace: bool = False) -> str:
        """
        Generate Stata's label copy command to copy value labels.

        This function constructs a Stata label copy command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            lblname_from: Name of the existing value label to copy from.
            lblname_to: Name of the new value label to create.
            replace: Whether to replace lblname_to if it already exists.

        Returns:
            A complete Stata label copy command string.

        Raises:
            ValueError: If either lblname_from or lblname_to is not provided.

        Examples:
            >>> label_copy("yesno", "yesnomaybe")
            'label copy yesno yesnomaybe'

            >>> label_copy("sexlbl", "gender", replace=True)
            'label copy sexlbl gender, replace'
        """
        if not lblname_from or not lblname_to:
            raise ValueError("Both lblname_from and lblname_to must be provided")

        cmd = f"label copy {lblname_from} {lblname_to}"

        if replace:
            cmd += ", replace"

        return cmd

    @staticmethod
    @mcp.tool(name="label_drop", description="生成并返回 Stata 的 'label drop' 命令（删除值标签）")
    def label_drop(lblnames: Union[str, List[str], bool] = False) -> str:
        """
        Generate Stata's label drop command to eliminate value labels.

        This function constructs a Stata label drop command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            lblnames: Name(s) of value label(s) to drop, or True for _all (to drop all value labels).
                     Can be a single value label name as string or a list of value label names.

        Returns:
            A complete Stata label drop command string.

        Raises:
            ValueError: If lblnames is not provided or is an empty list.

        Examples:
            >>> label_drop("yesno")
            'label drop yesno'

            >>> label_drop(["yesno", "sexlbl"])
            'label drop yesno sexlbl'

            >>> label_drop(True)
            'label drop _all'
        """
        if not lblnames:
            raise ValueError("lblnames must be provided")

        cmd = "label drop"

        if lblnames is True:
            cmd += " _all"
        elif isinstance(lblnames, list):
            if not lblnames:
                raise ValueError("lblnames list cannot be empty")
            cmd += f" {' '.join(lblnames)}"
        else:
            cmd += f" {lblnames}"

        return cmd

    @staticmethod
    @mcp.tool(name="label_save", description="生成并返回 Stata 的 'label save' 命令（将值标签保存为do文件）")
    def label_save(lblnames: Optional[Union[str, List[str]]],
                   filename: str,
                   replace: bool = False) -> str:
        """
        Generate Stata's label save command to save value labels to a do-file.

        This function constructs a Stata label save command string based on provided parameters,
        matching the official Stata documentation specifications.

        Args:
            lblnames: Optional name(s) of value label(s) to save.
                     If None, all value labels are saved.
                     Can be a single value label name as string or a list of value label names.
            filename: Path where the do-file will be saved.
            replace: Whether to replace the file if it already exists.

        Returns:
            A complete Stata label save command string.

        Raises:
            ValueError: If filename is not provided.

        Examples:
            >>> label_save("sexlbl", "mylabel")
            'label save sexlbl using mylabel'

            >>> label_save(["yesno", "sexlbl"], "mylabels", replace=True)
            'label save yesno sexlbl using mylabels, replace'

            >>> label_save(None, "alllabels")
            'label save using alllabels'
        """
        if not filename:
            raise ValueError("filename must be provided")

        cmd_parts = ["label save"]

        # Add lblnames if specified
        if lblnames:
            if isinstance(lblnames, list):
                cmd_parts.append(" ".join(lblnames))
            else:
                cmd_parts.append(lblnames)

        # Add filename
        cmd_parts.append(f"using {filename}")

        # Add replace option if specified
        if replace:
            cmd_parts.append(", replace")

        return " ".join(cmd_parts)


if __name__ == "__main__":
    mcp.run(transport="stdio")

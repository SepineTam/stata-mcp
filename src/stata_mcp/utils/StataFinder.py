#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : StataFinder.py

import os
import glob
import dotenv

import platform
from typing import Dict, Callable, Any

from .windows import *

dotenv.load_dotenv()

def _stata_version_macos():
    stata_dir = "/Applications/Stata"
    stata_apps = []
    for item in os.listdir(stata_dir):
        full_path = os.path.join(stata_dir, item)
        if os.path.isdir(full_path) and item.endswith(".app"):
            stata_apps.append(item)
    stata_app = stata_apps[0]
    stata_type = stata_app.split(".")[0].split("Stata")[-1]
    if stata_type == "":
        stata_type = None
    return stata_type.lower()

def _stata_version_windows(driver: str = "C:\\"):
    stata_paths = []
    common_patterns = [
        os.path.join(driver, "Program Files", "Stata*", "*.exe"),
        os.path.join(driver, "Program Files(x86)", "Stata*", "*.exe")
    ]
    for pattern in common_patterns:
        try:
            matches = glob.glob(pattern)
            for match in matches:
                if "stata" in match.lower() and match.lower().endswith(".exe"):
                    stata_paths.append(match)

            if not stata_paths:
                for root, dirs, files in os.walk(driver):
                    if root.count(os.sep) - driver.count(os.sep) > 3:
                        dirs.clear()
                        continue

                    for file in files:
                        if file.lower().endswith(".exe") and "stata" in file.lower():
                            stata_paths.append(os.path.join(root, file))

        except Exception as e:
            pass

    return stata_paths

def _find_stata_macos(is_env: bool = False) -> str:
    """
    For macOS, there is not important for the number version but the version type.

    Args:
        is_env (bool): whether to use the env config of the path of stata cli

    Returns:
        The path of stata cli
    """
    stata_type = _stata_version_macos()
    __default_cli_path = f"/Applications/Stata/Stata{stata_type.upper()}.app/Contents/MacOS/stata-{stata_type}"
    if is_env:
        import dotenv
        dotenv.load_dotenv()
        _stata_cli = os.getenv("stata_cli", __default_cli_path)
    else:
        _stata_cli = __default_cli_path
    return _stata_cli

def __default_stata_cli_path_windows() -> Any | None:
    drives: list = get_available_drives()
    stata_cli_path_list: list = []
    for drive in drives:
        stata_cli_path_list += _stata_version_windows(drive)
    if len(stata_cli_path_list) == 0:
        return None
    elif len(stata_cli_path_list) == 1:
        return stata_cli_path_list[0]
    else:
        for path in stata_cli_path_list:
            if windows_stata_match(path):
                return path
            else:
                pass
        return stata_cli_path_list[0]

def _find_stata_windows(is_env: bool = False) -> str:
    _stata_cli_path = None
    __default_cli_path = __default_stata_cli_path_windows()
    if is_env:
        import dotenv
        dotenv.load_dotenv()

        _stata_cli_path = os.getenv("stata_cli", __default_cli_path)
    else:
        _stata_cli_path = __default_cli_path
    return _stata_cli_path

def __default_stata_cli_path_linux() -> Any | None:
    pass


def _find_stata_linux(is_env: bool = False) -> str:
    """
    Find the Stata CLI path on Linux systems.

    For Linux users, this function attempts to locate the Stata CLI executable.
    If is_env is True, it will check the "stata_cli" environment variable.

    Args:
        is_env: Boolean flag to determine whether to check environment variables
                for the Stata path. Defaults to False.

    Returns:
        The path to the Stata CLI executable, or None if not found.
    """
    # Get default path
    default_path = __default_stata_cli_path_linux()

    # If using environment variables, check "stata_cli" env var with default as fallback
    if is_env:
        return os.getenv("stata_cli", default_path)

    # Otherwise just return the default path
    return default_path

def find_stata(os_name: str = None, is_env: bool = True):
    if os_name is None:
        os_name = platform.system()
    if os_name == "Darwin":
        return _find_stata_macos(is_env=is_env)
    elif os_name == "Windows":
        return _find_stata_windows(is_env=is_env)
    elif os_name == "Linux":
        return _find_stata_linux(is_env=is_env)


if __name__ == "__main__":
    sys_os = platform.system()
    if sys_os == "Darwin":
        stata_cli = _find_stata_macos(False)
        print(stata_cli)
    elif sys_os == "Windows":
        _stata_version_windows()
    else:
        print("Hello Stata-MCP, Install it please~")

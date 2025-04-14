#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : StataFinder.py

import os
from typing import Dict, Callable


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

def _find_stata_macos(is_env: bool = False) -> str:
    """
    For macOS, there is not important for the number version but the version type.

    Args:
        is_env (bool): whether

    Return:
        The path of stata cli
    """
    stata_type = _stata_version_macos()
    default_path = f"/Applications/Stata/Stata{stata_type.upper()}.app/Contents/MacOS/stata-{stata_type}"
    if is_env:
        import dotenv
        dotenv.load_dotenv()
        _stata_cli = os.getenv("stata_cli", default_path)
    else:
        _stata_cli = default_path
    return _stata_cli

def _find_stata_windows() -> str:
    pass

def _find_stata_linux() -> str:
    pass


if __name__ == "__main__":
    stata_cli = _find_stata_macos(False)
    print(stata_cli)

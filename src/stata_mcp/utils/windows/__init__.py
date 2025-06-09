#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : __init__.py

import os
import string

import re


def get_available_drives():
    drives = []
    for letter in string.ascii_uppercase:
        if os.path.exists(f"{letter}:\\"):
            drives.append(f"{letter}:\\")
    return drives


def windows_stata_match(path: str) -> bool:
    """
    检查路径是否匹配Windows Stata可执行文件的模式

    参数:
        path: 要检查的路径字符串

    返回:
        bool: 如果路径匹配Stata可执行文件模式，则返回True，否则返回False
    """
    # 正则表达式匹配 Stata\d+\\Stata(MP|SE|BE|IC)?.exe
    # \d+ 匹配一个或多个数字（版本号）
    # (MP|SE|BE|IC)? 匹配可选的版本类型（可以不存在）
    pattern = r'Stata\d+\\\\Stata(MP|SE|BE|IC)?\.exe$'

    if re.search(pattern, path):
        return True
    return False

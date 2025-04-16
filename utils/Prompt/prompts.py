#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : Prompt.py

from utils import Prompt
from utils.Prompt.string import frame


def filter_system_vars(dictionary):
    exclude_prefixes = ['__']
    exclude_vars = ['inspect', 'frame']

    filtered_dict = {}
    for key, value in dictionary.items():
        if not any(key.startswith(prefix) for prefix in exclude_prefixes) and key not in exclude_vars:
            filtered_dict[key] = value
    return filtered_dict


prompts_dict: dict = filter_system_vars(frame.f_locals)

pmp = Prompt.Prompt()
pmp.auto_extract(prompts_dict)

if __name__ == "__main__":
    print(pmp.prompts)

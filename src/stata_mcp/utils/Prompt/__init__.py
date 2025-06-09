#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : __init__.py

from .string import frame

class Prompt:
    def __init__(self):
        self.prompts = {}
        self.lang = "en"

    def set_lang(self, lang):
        self.lang = lang

    def add_prompt(self, prompt_id: str, lang: str, prompt: str):
        if prompt_id not in self.prompts:
            self.prompts[prompt_id] = {}
        self.prompts[prompt_id][lang] = prompt

    def get_prompt(self, prompt_id: str, lang: str = None):
        if lang is None:
            lang = self.lang

        if prompt_id not in self.prompts:
            return ""

        if lang not in self.prompts[prompt_id]:
            lang = "en"
            if lang not in self.prompts[prompt_id]:
                return ""
        return self.prompts[prompt_id][lang]

    @staticmethod
    def extract(var_name: str):
        name_list = var_name.split("_")
        lang = name_list[-1]
        prompt_id = "_".join(name_list[:-1])
        return prompt_id, lang

    def auto_extract(self, prompts_dict: dict):
        for key, prompt in prompts_dict.items():
            prompt_id, lang = Prompt.extract(key)
            self.add_prompt(prompt_id=prompt_id, lang=lang, prompt=prompt)

def filter_system_vars(dictionary):
    exclude_prefixes = ['__']
    exclude_vars = ['inspect', 'frame']

    filtered_dict = {}
    for key, value in dictionary.items():
        if not any(key.startswith(prefix) for prefix in exclude_prefixes) and key not in exclude_vars:
            filtered_dict[key] = value
    return filtered_dict


prompts_dict: dict = filter_system_vars(frame.f_locals)

pmp = Prompt()
pmp.auto_extract(prompts_dict)

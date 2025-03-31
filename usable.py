#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : usable.py

"""
Stata MCP配置检查脚本
用于检查用户的Stata MCP配置是否正确
"""

import os
import platform
import subprocess
import sys
import argparse
from typing import Dict, List, Optional, Tuple


def print_status(message: str, status: bool) -> None:
    """打印带有状态的消息"""
    status_str = "✅ 通过" if status else "❌ 失败"
    print(f"{message}: {status_str}")


def check_os() -> Tuple[str, bool]:
    """检查操作系统类型"""
    os_name = platform.system()
    os_mapping = {
        "Darwin": "macos",
        "Windows": "windows",
        "Linux": "linux"
    }
    detected_os = os_mapping.get(os_name, "unknown")
    is_supported = detected_os == "macos"  # 目前仅支持macOS

    return detected_os, is_supported


def check_stata_cli(version_number: str, version_type: str, stata_cli_path: Optional[str] = None) -> Tuple[str, bool]:
    """检查Stata CLI路径是否存在且可执行"""
    if stata_cli_path is None:
        # 尝试使用默认路径
        detected_os, _ = check_os()
        if detected_os == "macos":
            stata_cli_path = f"/Applications/Stata/StataSE.app/Contents/MacOS/stata-{version_type}"
        elif detected_os == "windows":
            # Windows路径可能需要根据实际情况调整
            stata_cli_path = f"C:\\Program Files\\Stata{version_number}\\StataMP-{version_type}.exe"
        else:
            return "", False

    # 检查文件是否存在
    exists = os.path.exists(stata_cli_path)

    # 检查是否可执行
    is_executable = False
    if exists:
        if os.name == 'posix':  # macOS/Linux
            is_executable = os.access(stata_cli_path, os.X_OK)
        else:  # Windows
            is_executable = stata_cli_path.endswith('.exe')

    return stata_cli_path, exists and is_executable


def check_directories(dofile_base_path: Optional[str] = None,
                      log_file_path: Optional[str] = None,
                      result_doc_path: Optional[str] = None) -> Dict[str, Tuple[str, bool]]:
    """检查必要的目录是否存在"""
    detected_os, _ = check_os()
    home_dir = os.path.expanduser("~")

    # 初始化默认路径
    if detected_os == "macos":
        if dofile_base_path is None:
            dofile_base_path = f"{home_dir}/Documents/stata-mcp-dofile/"
        if log_file_path is None:
            log_file_path = f"{home_dir}/Documents/stata-mcp-log/"
        if result_doc_path is None:
            result_doc_path = f"{home_dir}/Documents/stata-mcp-result_doc/"

    # 检查目录是否存在
    results = {}
    for name, path in [
        ("dofile_base_path", dofile_base_path),
        ("log_file_path", log_file_path),
        ("result_doc_path", result_doc_path)
    ]:
        if path:
            exists = os.path.exists(path)
            is_dir = os.path.isdir(path) if exists else False
            is_writable = os.access(path, os.W_OK) if exists else False
            results[name] = (path, exists and is_dir and is_writable)
        else:
            results[name] = ("未指定", False)

    return results


def check_mcp_installation() -> bool:
    """检查MCP库是否安装"""
    try:
        import mcp.server.fastmcp
        return True
    except ImportError:
        return False


def test_stata_execution(stata_cli_path: str) -> bool:
    """测试运行Stata命令"""
    if not os.path.exists(stata_cli_path):
        return False

    try:
        # 创建临时文件
        temp_do_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_test.do")
        with open(temp_do_file, "w") as f:
            f.write("display \"Stata MCP test successful\"\nexit, STATA")

        # 运行Stata命令
        result = subprocess.run(
            [stata_cli_path, "-b", "do", temp_do_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10  # 设置超时时间
        )

        # 清理临时文件
        if os.path.exists(temp_do_file):
            os.remove(temp_do_file)

        return result.returncode == 0
    except Exception as e:
        print(f"测试Stata执行时出错: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="检查Stata MCP配置")
    parser.add_argument("version_number", help="Stata版本号，例如: 17")
    parser.add_argument("version_type", help="Stata版本类型，例如: se")
    parser.add_argument("--stata-cli-path", help="Stata CLI路径")
    parser.add_argument("--log-file-path", help="日志文件路径")
    parser.add_argument("--dofile-base-path", help="do文件基础路径")
    parser.add_argument("--result-doc-path", help="结果文档路径")

    args = parser.parse_args()

    print("\n===== Stata MCP 配置检查 =====\n")

    # 检查操作系统
    detected_os, os_supported = check_os()
    print_status(f"操作系统检查 (当前: {detected_os})", os_supported)
    if not os_supported:
        print("  警告: 目前仅支持macOS。如果您确定是在macOS上运行，请添加参数 operating_system=macos")

    # 检查Stata CLI
    stata_cli_path, stata_cli_exists = check_stata_cli(
        args.version_number,
        args.version_type,
        args.stata_cli_path
    )
    print_status(f"Stata CLI检查 (路径: {stata_cli_path})", stata_cli_exists)
    if not stata_cli_exists:
        print("  提示: 如果Stata已安装但路径不同，请使用 --stata-cli-path 参数指定正确路径")

    # 检查目录
    directories = check_directories(
        args.dofile_base_path,
        args.log_file_path,
        args.result_doc_path
    )
    for name, (path, exists) in directories.items():
        print_status(f"{name}检查 (路径: {path})", exists)
        if not exists:
            print(f"  提示: 此目录不存在或无写入权限，请创建目录或使用 --{name.replace('_', '-')} 参数指定有效路径")

    # 检查MCP库
    mcp_installed = check_mcp_installation()
    print_status("MCP库安装检查", mcp_installed)
    if not mcp_installed:
        print("  提示: 请安装MCP库，可以使用: pip install mcp")

    # 如果Stata CLI存在，测试执行
    if stata_cli_exists:
        stata_exec_works = test_stata_execution(stata_cli_path)
        print_status("Stata执行测试", stata_exec_works)
        if not stata_exec_works:
            print("  警告: Stata执行测试失败，可能是权限问题或Stata安装有问题")

    # 总结
    all_passed = (os_supported and stata_cli_exists and
                  all(exists for _, exists in directories.values()) and
                  mcp_installed)

    print("\n===== 检查结果 =====")
    if all_passed:
        print("✅ 所有检查通过！Stata MCP可以正常运行。")
    else:
        print("❌ 部分检查未通过。请解决上述问题后再次尝试运行Stata MCP。")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

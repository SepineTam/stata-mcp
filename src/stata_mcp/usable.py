#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : usable.py

"""
Stata MCP Configuration Check Script
This script automatically checks if your Stata MCP configuration is correct
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple

from .utils import StataFinder


def print_status(message: str, status: bool) -> None:
    """Print a message with status indicator"""
    status_str = "✅ PASSED" if status else "❌ FAILED"
    print(f"{message}: {status_str}")


def check_os() -> Tuple[str, bool]:
    """Check current operating system"""
    os_name = platform.system()
    os_mapping = {
        "Darwin": "macOS",
        "Windows": "Windows",
        "Linux": "Linux"
    }
    detected_os = os_mapping.get(os_name, "unknown")
    is_supported = detected_os in ["macOS", "Windows", "Linux"]  # All three are now supported

    return detected_os, is_supported


def check_python_version() -> Tuple[str, bool]:
    """Check if the Python version is compatible"""
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    is_compatible = sys.version_info.major == 3 and sys.version_info.minor >= 11

    return current_version, is_compatible


def test_stata_execution(stata_cli_path: str) -> bool:
    """Test if Stata can be executed"""
    if not stata_cli_path or not os.path.exists(stata_cli_path):
        return False

    sys_os = platform.system()

    try:
        if sys_os == "Darwin" or sys_os == "Linux":  # macOS or Linux
            proc = subprocess.Popen(
                [stata_cli_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            # Send a simple command and exit
            commands = """
            display "Stata-MCP test successful"
            exit, STATA
            """
            proc.communicate(input=commands, timeout=10)
            return proc.returncode == 0

        elif sys_os == "Windows":  # Windows
            # Create a temporary do-file for testing
            temp_dir = os.path.dirname(os.path.abspath(__file__))
            temp_do_file = os.path.join(temp_dir, "temp_test.do")

            with open(temp_do_file, "w") as f:
                f.write('display "Stata-MCP test successful"\nexit, STATA\n')

            # Run Stata with the temp do-file
            cmd = f'"{stata_cli_path}" /e do "{temp_do_file}"'
            result = subprocess.run(cmd, shell=True, timeout=10)

            # Clean up
            if os.path.exists(temp_do_file):
                os.remove(temp_do_file)

            return result.returncode == 0

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
        print(f"  Error testing Stata: {e}")
        return False

    return False


def check_directories() -> Dict[str, Tuple[str, bool]]:
    """Check if required directories exist and create them if needed"""
    home_dir = os.path.expanduser("~")
    documents_path = os.path.join(home_dir, "Documents")

    # Define directories that should exist
    base_path = os.path.join(documents_path, "stata-mcp-folder")
    dirs = {
        "base_dir": (base_path, False),
        "log_dir": (os.path.join(base_path, "stata-mcp-log"), False),
        "dofile_dir": (os.path.join(base_path, "stata-mcp-dofile"), False),
        "result_dir": (os.path.join(base_path, "stata-mcp-result"), False),
    }

    # Check and create directories if they don't exist
    for name, (path, _) in dirs.items():
        exists = os.path.exists(path)
        if not exists:
            try:
                os.makedirs(path, exist_ok=True)
                exists = True
                print(f"  Created directory: {path}")
            except Exception as e:
                print(f"  Error creating directory {path}: {e}")

        is_writable = os.access(path, os.W_OK) if exists else False
        dirs[name] = (path, exists and is_writable)

    return dirs


def check_mcp_installation() -> bool:
    """Check if MCP library is installed"""
    try:
        import mcp.server.fastmcp
        return True
    except ImportError:
        return False


def animate_loading(seconds: int) -> None:
    """Display an animated loading spinner"""
    chars = "|/-\\"
    for _ in range(seconds * 5):
        for char in chars:
            sys.stdout.write(f"\r  Finding Stata CLI {char} ")
            sys.stdout.flush()
            time.sleep(0.05)
    sys.stdout.write("\r" + " " * 20 + "\r")
    sys.stdout.flush()


def main():
    """Main function to check Stata MCP configuration"""
    print("\n===== Stata MCP Configuration Check =====\n")

    # Check operating system
    detected_os, os_supported = check_os()
    print_status(f"Operating system (Current: {detected_os})", os_supported)
    if not os_supported:
        print("  Warning: Your operating system may not be fully supported by Stata-MCP.")

    # Check Python version
    python_version, python_compatible = check_python_version()
    print_status(f"Python version (Current: {python_version})", python_compatible)
    if not python_compatible:
        print("  Warning: Python 3.11+ is recommended for Stata-MCP.")

    # Check MCP library
    mcp_installed = check_mcp_installation()
    print_status("MCP library installation", mcp_installed)
    if not mcp_installed:
        print("  Please install MCP library: pip install mcp[cli]")

    # Find Stata CLI
    print("Locating Stata CLI...")
    animate_loading(2)  # Show loading animation for 2 seconds
    stata_cli_path = StataFinder.find_stata(is_env=True)

    stata_found = bool(stata_cli_path and os.path.exists(stata_cli_path))
    print_status(f"Stata CLI (Path: {stata_cli_path or 'Not found'})", stata_found)

    # Test Stata execution if found
    stata_works = False
    if stata_found:
        print("Testing Stata execution...")
        stata_works = test_stata_execution(stata_cli_path)
        print_status("Stata execution test", stata_works)
        if not stata_works:
            print("  Warning: Stata was found but could not be executed properly.")
            print("  You may need to specify the path manually in config.py or as an environment variable.")

    # Check and create necessary directories
    print("\nChecking required directories...")
    directories = check_directories()
    all_dirs_ok = True
    for name, (path, exists) in directories.items():
        dir_name = name.replace("_", " ").title()
        print_status(f"{dir_name} (Path: {path})", exists)
        if not exists:
            all_dirs_ok = False
            print(f"  Warning: Could not create or access {path}")

    # Overall summary
    print("\n===== Summary =====")
    all_passed = os_supported and python_compatible and mcp_installed and stata_found and stata_works and all_dirs_ok

    if all_passed:
        print("\n✅ Success! Your Stata-MCP setup is ready to use.")
        print("You can now use Stata-MCP with your preferred MCP client (Claude, Cherry Studio, etc.)")
    else:
        print("\n⚠️ Some checks failed. Please address the issues above to use Stata-MCP.")
        if not stata_found or not stata_works:
            print("\nTo manually specify your Stata path, add this to your MCP configuration:")
            print('  "env": {')
            print('    "stata_cli": "/path/to/your/stata/executable"')
            print('  }')

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

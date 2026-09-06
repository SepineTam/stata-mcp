"""Validate binary build inputs before starting an expensive compilation."""

from __future__ import annotations

import importlib
import importlib.util
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_binary_entry_points_exist():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    options = project["tool"]["nuitka"]

    if "main" in options:
        assert (ROOT / options["main"]).is_file()

    scripts = project["project"]["scripts"]
    assert scripts
    for entry_point in scripts.values():
        module_name, function_name = entry_point.split(":", 1)
        module = importlib.import_module(module_name)
        assert callable(getattr(module, function_name))


def test_explicit_binary_packages_are_installed():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    for package in project["tool"]["nuitka"].get("include-package", []):
        assert importlib.util.find_spec(package) is not None, package

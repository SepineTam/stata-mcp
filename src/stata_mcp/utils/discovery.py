"""Read-only Stata discovery, independent of server and configuration imports."""

from __future__ import annotations

import os
import platform
import re
from pathlib import Path

from ..core.types import OSNotSupported

_UNIX_NAME = re.compile(r"(?:x?stata)(?:-?(?:mp|se|be|ic))?", re.IGNORECASE)
_WINDOWS_NAME = re.compile(r"stata(?:mp|se|be|ic)?(?:-64)?\.exe", re.IGNORECASE)
_APP_NAME = re.compile(r"stata(?:mp|se|be|ic)?\.app", re.IGNORECASE)
_DISPLAY_NAME = re.compile(
    r"^stata(?:now)?(?:mp|se|be|ic)?(?:$|[\s/\d-])", re.IGNORECASE
)


def _children(directory: Path) -> list[Path]:
    """Skip missing or inaccessible directories."""
    try:
        return list(directory.iterdir())
    except OSError:
        return []


def _application_candidates(system: str) -> list[Path]:
    """Filter the OS application inventory before inspecting installation files."""
    if system == "Darwin":
        from app_scanner import get_installed_apps

        return [
            Path(path)
            for app in get_installed_apps()
            if (path := app.get("path")) and _APP_NAME.fullmatch(Path(path).name)
        ]

    import winapps

    candidates = []
    for app in winapps.list_installed():
        if _DISPLAY_NAME.match(app.name or "") and app.install_location:
            candidates.extend(_children(Path(app.install_location)))
    return candidates


def _windows_roots() -> list[Path]:
    """Cover standard installs whose registry entry has no installation location."""
    return [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
        Path(os.environ.get("ProgramW6432", r"C:\Program Files")),
        Path("C:/"),
        Path("D:/"),
        Path("D:/Program Files"),
        Path("D:/Program Files (x86)"),
    ]


def _executable(path: Path, system: str) -> bool:
    pattern = _WINDOWS_NAME if system == "Windows" else _UNIX_NAME
    return bool(
        pattern.fullmatch(path.name)
        and path.is_file()
        and (system == "Windows" or os.access(path, os.X_OK))
    )


def _installation_path(path: Path, system: str) -> Path | None:
    """Validate a candidate and normalize macOS binaries to their app bundle."""
    try:
        path = path.expanduser().resolve()
        if system == "Darwin":
            bundle = next(
                (
                    parent
                    for parent in (path, *path.parents)
                    if _APP_NAME.fullmatch(parent.name)
                ),
                None,
            )
            if bundle is not None:
                if any(
                    _executable(binary, system)
                    for binary in _children(bundle / "Contents" / "MacOS")
                ):
                    return bundle
                return None
        if system == "Windows" and _executable(path, system):
            return path
    except (OSError, RuntimeError):
        return None
    return None


def discover_stata() -> list[str]:
    """List macOS/Windows installations without launching them or changing config.

    Results are absolute, deduplicated, and sorted. An empty search returns [].
    """
    system = platform.system()
    if system not in {"Darwin", "Windows"}:
        raise OSNotSupported()

    candidates = _application_candidates(system)
    if system == "Windows":
        for root in _windows_roots():
            for child in _children(root):
                if child.name.lower().startswith("stata"):
                    candidates.extend(_children(child))

    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if directory:
            candidates.extend(_children(Path(directory).expanduser()))

    for variable in ("STATA_CLI", "stata_cli"):
        value = os.environ.get(variable)
        if value:
            candidate = Path(value).expanduser()
            candidates.append(candidate)
            if not candidate.is_absolute():
                for directory in os.environ.get("PATH", "").split(os.pathsep):
                    if directory:
                        candidates.append(Path(directory) / candidate)

    found = {}
    for candidate in candidates:
        installation = _installation_path(candidate, system)
        if installation is not None:
            path = str(installation)
            key = path.casefold() if system == "Windows" else path
            found.setdefault(key, path)
    return sorted(found.values())

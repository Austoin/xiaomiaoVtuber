"""Helpers for loading trimmed third-party tool sources from this repository."""

from __future__ import annotations

import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path | None:
    """Find the repository root from either tool/core or compatibility wrappers."""
    for directory in (start, *start.parents):
        if (directory / "package.json").exists() and (directory / "xiaomiaoAgent").exists():
            return directory
    return None


def prefer_repo_tool_source(package_name: str, relative_source: tuple[str, ...]) -> None:
    """Prefer the repository copy of a third-party tool if it is available."""
    if package_name in sys.modules:
        return

    repo_root = _find_repo_root(Path(__file__).resolve().parent)
    if repo_root is None:
        return

    source_path = repo_root.joinpath(*relative_source)
    if not source_path.exists():
        return

    source = str(source_path)
    if source in sys.path:
        sys.path.remove(source)
    sys.path.insert(0, source)

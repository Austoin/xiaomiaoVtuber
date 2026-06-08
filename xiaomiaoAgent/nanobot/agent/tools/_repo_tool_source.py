"""Helpers for loading trimmed third-party tool sources from this repository."""

from __future__ import annotations

import sys
from pathlib import Path


def prefer_repo_tool_source(package_name: str, relative_source: tuple[str, ...]) -> None:
    """Prefer the repository copy of a third-party tool if it is available."""
    if package_name in sys.modules:
        return

    try:
        repo_root = Path(__file__).resolve().parents[4]
    except IndexError:
        return

    source_path = repo_root.joinpath(*relative_source)
    if not source_path.exists():
        return

    source = str(source_path)
    if source in sys.path:
        sys.path.remove(source)
    sys.path.insert(0, source)

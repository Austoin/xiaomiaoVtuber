"""
nanobot - A lightweight AI agent framework
"""

import tomllib
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from pathlib import Path


def _read_pyproject_version() -> str | None:
    """Read the source-tree version when package metadata is unavailable."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if not pyproject.exists():
        return None
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return data.get("project", {}).get("version")


def _resolve_version() -> str:
    try:
        return _pkg_version("nanobot-ai")
    except PackageNotFoundError:
        # Source checkouts often import nanobot without installed dist-info.
        return _read_pyproject_version() or "0.1.5.post3"


__version__ = _resolve_version()
__logo__ = "🐈"

# Import the public API only after package metadata is resolved.  Some source-tree
# consumers import ``__version__`` while ``nanobot.nanobot`` is still loading.
from nanobot.nanobot import Nanobot, RunResult  # noqa: E402

__all__ = ["Nanobot", "RunResult"]

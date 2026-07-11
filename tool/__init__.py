"""xiaomiaoVirtual unified tool layer."""

from __future__ import annotations

import sys
from pathlib import Path


def _prefer_repo_agent_source() -> None:
    """Expose the in-repository nanobot package when running from repo root."""
    repo_root = Path(__file__).resolve().parents[1]
    agent_dir = repo_root / "xiaomiaoAgent"
    if not (agent_dir / "nanobot").exists():
        return

    source = str(agent_dir)
    if source not in sys.path:
        sys.path.insert(0, source)


_prefer_repo_agent_source()

__version__ = "1.0.0"
__all__ = ["core", "xiaomiao", "memory", "vendor", "adapters"]

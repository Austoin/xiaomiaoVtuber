from __future__ import annotations

import sys
import types
from pathlib import Path

from nanobot.agent.tools._repo_tool_source import prefer_repo_tool_source


def test_prefer_repo_tool_source_adds_trimmed_source_path(monkeypatch):
    repo_root = Path(__file__).resolve().parents[3]
    source = repo_root / "tool" / "markitdown" / "packages" / "markitdown" / "src"
    monkeypatch.delitem(sys.modules, "markitdown", raising=False)
    monkeypatch.setattr(sys, "path", [item for item in sys.path if item != str(source)])

    prefer_repo_tool_source(
        "markitdown",
        ("tool", "markitdown", "packages", "markitdown", "src"),
    )

    assert sys.path[0] == str(source)


def test_prefer_repo_tool_source_keeps_loaded_module(monkeypatch):
    repo_root = Path(__file__).resolve().parents[3]
    source = repo_root / "tool" / "Scrapling"
    fake_module = types.ModuleType("scrapling")
    monkeypatch.setitem(sys.modules, "scrapling", fake_module)
    monkeypatch.setattr(sys, "path", [item for item in sys.path if item != str(source)])

    prefer_repo_tool_source("scrapling", ("tool", "Scrapling"))

    assert str(source) not in sys.path

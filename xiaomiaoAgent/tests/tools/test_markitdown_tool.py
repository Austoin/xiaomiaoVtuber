from __future__ import annotations

import sys
import types

import pytest

from nanobot.agent.tools import markitdown_tool
from nanobot.agent.tools.markitdown_tool import MarkItDownConvertTool


def test_default_resource_workspace_uses_repository_qq_cache(tmp_path, monkeypatch):
    module_path = tmp_path / "xiaomiaoAgent" / "nanobot" / "agent" / "tools" / "markitdown_tool.py"
    resource_workspace = tmp_path / ".cache" / "xiaomiao" / "qq_workspace"
    module_path.parent.mkdir(parents=True)
    resource_workspace.mkdir(parents=True)

    monkeypatch.delenv("XIAOMIAO_RESOURCE_WORKSPACE", raising=False)
    monkeypatch.setattr(markitdown_tool, "__file__", str(module_path))

    assert markitdown_tool._default_resource_workspace() == resource_workspace.resolve()


@pytest.mark.asyncio
async def test_markitdown_convert_rejects_uri_input(tmp_path):
    tool = MarkItDownConvertTool(workspace=tmp_path)

    result = await tool.execute(path="https://example.com/file.pdf")

    assert result.startswith("Error:")
    assert "workspace-local" in result


@pytest.mark.asyncio
async def test_markitdown_convert_rejects_outside_workspace(tmp_path):
    outside = tmp_path.parent / "outside-markitdown.txt"
    outside.write_text("secret", encoding="utf-8")
    tool = MarkItDownConvertTool(workspace=tmp_path, extra_allowed_dirs=[])

    result = await tool.execute(path=str(outside))

    assert result.startswith("Error:")
    assert "outside allowed directory" in result


@pytest.mark.asyncio
async def test_markitdown_convert_accepts_extra_resource_workspace(tmp_path, monkeypatch):
    agent_workspace = tmp_path / "agent"
    resource_workspace = tmp_path / "resource"
    agent_workspace.mkdir()
    resource_workspace.mkdir()
    source = resource_workspace / "upload.txt"
    source.write_text("hello", encoding="utf-8")

    class FakeMarkItDown:
        def __init__(self, **kwargs):
            assert kwargs == {"enable_plugins": False}

        def convert(self, fp):
            assert fp == source
            return types.SimpleNamespace(markdown="converted")

    fake_module = types.SimpleNamespace(MarkItDown=FakeMarkItDown)
    monkeypatch.setitem(sys.modules, "markitdown", fake_module)

    tool = MarkItDownConvertTool(
        workspace=agent_workspace,
        extra_allowed_dirs=[resource_workspace],
    )
    result = await tool.execute(path=str(source))

    assert "(Converted with MarkItDown from: upload.txt)" in result
    assert "converted" in result


@pytest.mark.asyncio
async def test_markitdown_convert_returns_truncated_markdown(tmp_path, monkeypatch):
    source = tmp_path / "sample.txt"
    source.write_text("hello", encoding="utf-8")

    class FakeMarkItDown:
        def __init__(self, **kwargs):
            assert kwargs == {"enable_plugins": False}

        def convert(self, fp):
            assert fp == source
            return types.SimpleNamespace(markdown="x" * 120)

    fake_module = types.SimpleNamespace(MarkItDown=FakeMarkItDown)
    monkeypatch.setitem(sys.modules, "markitdown", fake_module)

    tool = MarkItDownConvertTool(workspace=tmp_path)
    result = await tool.execute(path="sample.txt", max_chars=100)

    assert "(Converted with MarkItDown from: sample.txt)" in result
    assert f"\n\n{'x' * 100}\n\n" in result
    assert "truncated at 100 characters" in result


@pytest.mark.asyncio
async def test_markitdown_convert_missing_dependency_is_explicit(tmp_path, monkeypatch):
    source = tmp_path / "sample.txt"
    source.write_text("hello", encoding="utf-8")

    monkeypatch.delitem(sys.modules, "markitdown", raising=False)
    tool = MarkItDownConvertTool(workspace=tmp_path)

    def _raise_import_error(_fp):
        raise ImportError()

    monkeypatch.setattr(tool, "_convert_file", _raise_import_error)

    result = await tool.execute(path="sample.txt")

    assert result == "Error: markitdown is not installed in this environment."

from __future__ import annotations

import json
import socket
from types import SimpleNamespace

import pytest

from nanobot.agent.tools.scrapling_tool import ScraplingGetTool


def _fake_resolve_private(hostname, port, family=0, type_=0):
    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 0))]


def _fake_resolve_public(hostname, port, family=0, type_=0):
    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 0))]


@pytest.mark.asyncio
async def test_scrapling_get_blocks_internal_targets(monkeypatch):
    tool = ScraplingGetTool()
    monkeypatch.setattr("nanobot.security.network.socket.getaddrinfo", _fake_resolve_private)

    result = await tool.execute(url="http://localhost/admin")

    data = json.loads(result)
    assert "error" in data
    assert "private" in data["error"].lower() or "blocked" in data["error"].lower()


@pytest.mark.asyncio
async def test_scrapling_get_returns_untrusted_structured_content(monkeypatch):
    tool = ScraplingGetTool()
    monkeypatch.setattr("nanobot.security.network.socket.getaddrinfo", _fake_resolve_public)

    async def _fake_scrapling_get(**kwargs):
        assert kwargs == {
            "url": "https://example.com/page",
            "css_selector": "main",
            "extraction_type": "markdown",
        }
        return SimpleNamespace(
            status=200,
            url="https://example.com/page",
            content=["# Title", "Body"],
        )

    monkeypatch.setattr(tool, "_scrapling_get", _fake_scrapling_get)

    result = await tool.execute(
        url="https://example.com/page",
        css_selector="main",
        extraction_type="markdown",
        max_chars=1000,
    )

    data = json.loads(result)
    assert data["status"] == 200
    assert data["extractor"] == "scrapling_get"
    assert data["untrusted"] is True
    assert "[External content" in data["text"]
    assert "# Title" in data["text"]


@pytest.mark.asyncio
async def test_scrapling_get_missing_dependency_is_explicit(monkeypatch):
    tool = ScraplingGetTool()
    monkeypatch.setattr("nanobot.security.network.socket.getaddrinfo", _fake_resolve_public)

    async def _raise_import_error(**kwargs):
        raise ImportError()

    monkeypatch.setattr(tool, "_scrapling_get", _raise_import_error)

    result = await tool.execute(url="https://example.com")

    data = json.loads(result)
    assert data == {
        "error": "scrapling is not installed in this environment.",
        "url": "https://example.com",
    }


@pytest.mark.asyncio
async def test_scrapling_get_blocks_private_redirect(monkeypatch):
    tool = ScraplingGetTool()
    monkeypatch.setattr("nanobot.security.network.socket.getaddrinfo", _fake_resolve_public)

    async def _fake_scrapling_get(**kwargs):
        return SimpleNamespace(
            status=200,
            url="http://127.0.0.1/secret",
            content=["secret"],
        )

    monkeypatch.setattr(tool, "_scrapling_get", _fake_scrapling_get)

    result = await tool.execute(url="https://example.com")

    data = json.loads(result)
    assert "error" in data
    assert "Redirect blocked" in data["error"]

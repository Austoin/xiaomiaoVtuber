from __future__ import annotations

from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.agent.tools.registry import ToolRegistry


class _FakeTool(Tool):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return f"{self._name} tool"

    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, **kwargs: Any) -> Any:
        return kwargs


def _tool_names(definitions: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    for definition in definitions:
        fn = definition.get("function", {})
        names.append(fn.get("name", ""))
    return names


def test_get_definitions_orders_builtins_then_mcp_tools() -> None:
    registry = ToolRegistry()
    registry.register(_FakeTool("mcp_git_status"))
    registry.register(_FakeTool("write_file"))
    registry.register(_FakeTool("mcp_fs_list"))
    registry.register(_FakeTool("read_file"))

    assert _tool_names(registry.get_definitions()) == [
        "read_file",
        "write_file",
        "mcp_fs_list",
        "mcp_git_status",
    ]


def test_prepare_call_read_file_rejects_non_object_params_with_actionable_hint() -> None:
    registry = ToolRegistry()
    registry.register(_FakeTool("read_file"))

    tool, params, error = registry.prepare_call("read_file", ["foo.txt"])

    assert tool is None
    assert params == ["foo.txt"]
    assert error is not None
    assert "must be a JSON object" in error
    assert "Use named parameters" in error


def test_prepare_call_other_tools_keep_generic_object_validation() -> None:
    registry = ToolRegistry()
    registry.register(_FakeTool("grep"))

    tool, params, error = registry.prepare_call("grep", ["TODO"])

    assert tool is not None
    assert params == ["TODO"]
    assert error == "Error: Invalid parameters for tool 'grep': parameters must be an object, got list"


def test_get_definitions_returns_cached_result() -> None:
    registry = ToolRegistry()
    registry.register(_FakeTool("read_file"))
    first = registry.get_definitions()
    assert registry._cached_definitions is not None
    second = registry.get_definitions()
    assert first == second


def test_register_invalidates_cache() -> None:
    registry = ToolRegistry()
    registry.register(_FakeTool("read_file"))
    first = registry.get_definitions()
    registry.register(_FakeTool("write_file"))
    second = registry.get_definitions()
    assert first is not second
    assert len(second) == 2


def test_unregister_invalidates_cache() -> None:
    registry = ToolRegistry()
    registry.register(_FakeTool("read_file"))
    registry.register(_FakeTool("write_file"))
    first = registry.get_definitions()
    registry.unregister("write_file")
    second = registry.get_definitions()
    assert first is not second
    assert len(second) == 1


def test_low_risk_policy_exposes_only_safe_tools() -> None:
    from nanobot.agent.tools.context import RequestContext

    registry = ToolRegistry()
    registry.register(_FakeTool("read_file"))
    registry.register(_FakeTool("grep"))
    registry.register(_FakeTool("write_file"))
    registry.register(_FakeTool("exec"))
    registry.register(_FakeTool("mcp_server_tool"))
    registry.register(_FakeTool("markitdown_convert"))
    registry.register(_FakeTool("scrapling_get"))
    registry.register(_FakeTool("xiaomiaobot_status"))
    registry.register(_FakeTool("xiaomiaobot_action"))

    registry.set_context(
        RequestContext(
            channel="qq-group",
            chat_id="10001",
            metadata={"channel_policy": "low_risk"},
        )
    )

    assert _tool_names(registry.get_definitions()) == [
        "grep",
        "markitdown_convert",
        "read_file",
        "scrapling_get",
        "xiaomiaobot_status",
    ]


def test_low_risk_policy_blocks_hidden_tool_execution() -> None:
    from nanobot.agent.tools.context import RequestContext

    registry = ToolRegistry()
    registry.register(_FakeTool("write_file"))
    registry.set_context(
        RequestContext(
            channel="qq-group",
            chat_id="10001",
            metadata={"channel_policy": "low_risk"},
        )
    )

    tool, params, error = registry.prepare_call("write_file", {})

    assert tool is None
    assert params == {}
    assert error is not None
    assert "blocked by channel policy" in error


def test_trusted_pending_policy_exposes_high_risk_tools_but_requires_confirmation() -> None:
    from nanobot.agent.tools.context import RequestContext

    registry = ToolRegistry()
    registry.register(_FakeTool("read_file"))
    registry.register(_FakeTool("exec"))
    registry.register(_FakeTool("write_file"))
    registry.register(_FakeTool("mcp_computer_use"))

    registry.set_context(
        RequestContext(
            channel="qq-group",
            chat_id="10001",
            metadata={"channel_policy": "trusted_pending"},
        )
    )

    assert _tool_names(registry.get_definitions()) == [
        "exec",
        "read_file",
        "write_file",
        "mcp_computer_use",
    ]

    tool, params, error = registry.prepare_call("exec", {"command": "dir"})

    assert tool is None
    assert params == {"command": "dir"}
    assert error is not None
    assert "requires confirmation" in error


def test_trusted_pending_policy_allows_low_risk_tools() -> None:
    from nanobot.agent.tools.context import RequestContext

    registry = ToolRegistry()
    registry.register(_FakeTool("read_file"))
    registry.set_context(
        RequestContext(
            channel="qq-group",
            chat_id="10001",
            metadata={"channel_policy": "trusted_pending"},
        )
    )

    tool, params, error = registry.prepare_call("read_file", {"path": "README.md"})

    assert tool is not None
    assert params == {"path": "README.md"}
    assert error is None


def test_restricted_policy_allows_only_explicit_low_risk_mcp_tools() -> None:
    from nanobot.agent.tools.context import RequestContext

    registry = ToolRegistry()
    registry.register(_FakeTool("mcp_computer_use_desktop_get_capabilities"))
    registry.register(_FakeTool("mcp_computer_use_desktop_get_state"))
    registry.register(_FakeTool("mcp_computer_use_desktop_list_pending_actions"))
    registry.register(_FakeTool("mcp_computer_use_desktop_screenshot"))
    registry.register(_FakeTool("mcp_computer_use_terminal_get_state"))
    registry.register(_FakeTool("mcp_computer_use_terminal_exec"))
    registry.register(_FakeTool("mcp_computer_use_desktop_click"))
    registry.register(_FakeTool("mcp_computer_use_browser_dom_get_active_tab"))
    registry.register(_FakeTool("mcp_computer_use_browser_dom_read_page"))
    registry.register(_FakeTool("mcp_computer_use_browser_dom_click"))
    registry.register(_FakeTool("mcp_computer_use_clipboard_read_text"))
    registry.register(_FakeTool("mcp_twitter_search_tweets"))
    registry.register(_FakeTool("mcp_twitter_search"))
    registry.register(_FakeTool("mcp_twitter_refresh-timeline"))
    registry.register(_FakeTool("mcp_twitter_get-my-profile"))
    registry.register(_FakeTool("mcp_twitter_post_tweet"))
    registry.register(_FakeTool("mcp_twitter_post-tweet"))
    registry.register(_FakeTool("mcp_twitter_like-tweet"))
    registry.register(_FakeTool("mcp_minecraft_get_state"))
    registry.register(_FakeTool("mcp_minecraft_get_logs"))
    registry.register(_FakeTool("mcp_minecraft_get_last_prompt"))
    registry.register(_FakeTool("mcp_minecraft_get_llm_trace"))
    registry.register(_FakeTool("mcp_minecraft_inject_chat"))
    registry.register(_FakeTool("mcp_minecraft_execute_repl"))

    registry.set_context(
        RequestContext(
            channel="qq-group",
            chat_id="10001",
            metadata={"channel_policy": "low_risk"},
        )
    )

    assert _tool_names(registry.get_definitions()) == [
        "mcp_computer_use_browser_dom_get_active_tab",
        "mcp_computer_use_browser_dom_read_page",
        "mcp_computer_use_desktop_get_capabilities",
        "mcp_computer_use_desktop_get_state",
        "mcp_computer_use_desktop_list_pending_actions",
        "mcp_computer_use_desktop_screenshot",
        "mcp_computer_use_terminal_get_state",
        "mcp_minecraft_get_last_prompt",
        "mcp_minecraft_get_llm_trace",
        "mcp_minecraft_get_logs",
        "mcp_minecraft_get_state",
        "mcp_twitter_get-my-profile",
        "mcp_twitter_refresh-timeline",
        "mcp_twitter_search",
        "mcp_twitter_search_tweets",
    ]

    for tool_name in [
        "mcp_computer_use_terminal_exec",
        "mcp_computer_use_desktop_click",
        "mcp_computer_use_browser_dom_click",
        "mcp_computer_use_clipboard_read_text",
        "mcp_twitter_post_tweet",
        "mcp_twitter_post-tweet",
        "mcp_twitter_like-tweet",
        "mcp_minecraft_inject_chat",
        "mcp_minecraft_execute_repl",
    ]:
        tool, params, error = registry.prepare_call(tool_name, {})
        assert tool is None
        assert params == {}
        assert error is not None
        assert "blocked by channel policy" in error


def test_trusted_confirmed_policy_exposes_high_risk_tools() -> None:
    from nanobot.agent.tools.context import RequestContext

    registry = ToolRegistry()
    registry.register(_FakeTool("read_file"))
    registry.register(_FakeTool("exec"))
    registry.register(_FakeTool("write_file"))
    registry.register(_FakeTool("mcp_computer_use"))

    registry.set_context(
        RequestContext(
            channel="qq-group",
            chat_id="10001",
            metadata={
                "channel_policy": "trusted_confirmed",
                "confirmation_id": "ABC123",
            },
        )
    )

    assert _tool_names(registry.get_definitions()) == [
        "exec",
        "read_file",
        "write_file",
        "mcp_computer_use",
    ]

    tool, params, error = registry.prepare_call("exec", {"command": "dir"})

    assert tool is not None
    assert params == {"command": "dir"}
    assert error is None

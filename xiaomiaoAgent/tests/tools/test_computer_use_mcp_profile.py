from __future__ import annotations

from nanobot.agent.tools.context import RequestContext
from nanobot.agent.tools.registry import ToolRegistry
from nanobot.config.schema import (
    COMPUTER_USE_CONFIRMED_TOOLS,
    COMPUTER_USE_LOW_RISK_TOOLS,
    MINECRAFT_CONFIRMED_TOOLS,
    MINECRAFT_LOW_RISK_TOOLS,
    TWITTER_CONFIRMED_TOOLS,
    TWITTER_LOW_RISK_TOOLS,
    ComputerUseMCPProfileConfig,
    Config,
    MinecraftMCPProfileConfig,
    MCPServerConfig,
    TwitterMCPProfileConfig,
)

from tests.tools.test_tool_registry import _FakeTool, _tool_names


def test_computer_use_profile_is_opt_in_by_default() -> None:
    config = Config.model_validate({})

    assert config.tools.computer_use_mcp.enable is False
    assert config.tools.twitter_mcp.enable is False
    assert config.tools.minecraft_mcp.enable is False
    assert config.tools.effective_mcp_servers() == {}


def test_computer_use_profile_builds_explicit_confirmed_allowlist() -> None:
    profile = ComputerUseMCPProfileConfig(enable=True)
    server = profile.build_server_config()

    assert server.type == "stdio"
    assert server.command == "pnpm"
    assert server.args == ["-F", "@proj-airi/computer-use-mcp", "start"]
    assert "*" not in server.enabled_tools
    assert "desktop_get_capabilities" in server.enabled_tools
    assert "browser_dom_read_page" in server.enabled_tools
    assert "terminal_exec" in server.enabled_tools
    assert "clipboard_read_text" in server.enabled_tools


def test_computer_use_profile_low_risk_mode_omits_mutating_tools() -> None:
    profile = ComputerUseMCPProfileConfig(enable=True, mode="low_risk")
    server = profile.build_server_config()

    assert list(COMPUTER_USE_LOW_RISK_TOOLS) == server.enabled_tools
    assert "desktop_get_capabilities" in server.enabled_tools
    assert "browser_dom_read_page" in server.enabled_tools
    assert "terminal_get_state" in server.enabled_tools
    assert "terminal_exec" not in server.enabled_tools
    assert "desktop_click" not in server.enabled_tools
    assert "clipboard_read_text" not in server.enabled_tools


def test_effective_mcp_servers_merges_computer_use_profile() -> None:
    config = Config.model_validate(
        {
            "tools": {
                "mcpServers": {
                    "existing": {
                        "command": "existing-command",
                        "enabledTools": ["status"],
                    }
                },
                "computerUseMcp": {
                    "enable": True,
                    "serverName": "computer_use",
                    "mode": "low_risk",
                    "extraEnabledTools": ["desktop_wait", "desktop_wait"],
                },
            }
        }
    )

    servers = config.tools.effective_mcp_servers()

    assert set(servers) == {"existing", "computer_use"}
    assert isinstance(servers["existing"], MCPServerConfig)
    assert servers["existing"].enabled_tools == ["status"]
    assert servers["computer_use"].enabled_tools.count("desktop_wait") == 1
    assert "terminal_exec" not in servers["computer_use"].enabled_tools


def test_twitter_profile_builds_explicit_confirmed_allowlist() -> None:
    profile = TwitterMCPProfileConfig(enable=True)
    server = profile.build_server_config()

    assert server.type == "sse"
    assert server.url == "http://127.0.0.1:8080/sse"
    assert "*" not in server.enabled_tools
    assert list(TWITTER_CONFIRMED_TOOLS) == server.enabled_tools
    assert "search" in server.enabled_tools
    assert "refresh-timeline" in server.enabled_tools
    assert "get-my-profile" in server.enabled_tools
    assert "post-tweet" in server.enabled_tools


def test_twitter_profile_low_risk_mode_omits_account_actions() -> None:
    profile = TwitterMCPProfileConfig(enable=True, mode="low_risk")
    server = profile.build_server_config()

    assert list(TWITTER_LOW_RISK_TOOLS) == server.enabled_tools
    assert "search" in server.enabled_tools
    assert "refresh-timeline" in server.enabled_tools
    assert "get-my-profile" in server.enabled_tools
    assert "post-tweet" not in server.enabled_tools
    assert "like-tweet" not in server.enabled_tools
    assert "retweet" not in server.enabled_tools
    assert "login" not in server.enabled_tools


def test_minecraft_profile_builds_explicit_confirmed_allowlist() -> None:
    profile = MinecraftMCPProfileConfig(enable=True)
    server = profile.build_server_config()

    assert server.type == "streamableHttp"
    assert server.url == "http://127.0.0.1:3001/sse"
    assert "*" not in server.enabled_tools
    assert list(MINECRAFT_CONFIRMED_TOOLS) == server.enabled_tools
    assert "get_state" in server.enabled_tools
    assert "get_logs" in server.enabled_tools
    assert "execute_repl" in server.enabled_tools
    assert "inject_chat" in server.enabled_tools


def test_minecraft_profile_low_risk_mode_omits_injection_tools() -> None:
    profile = MinecraftMCPProfileConfig(enable=True, mode="low_risk")
    server = profile.build_server_config()

    assert list(MINECRAFT_LOW_RISK_TOOLS) == server.enabled_tools
    assert "get_state" in server.enabled_tools
    assert "get_last_prompt" in server.enabled_tools
    assert "get_logs" in server.enabled_tools
    assert "get_llm_trace" in server.enabled_tools
    assert "execute_repl" not in server.enabled_tools
    assert "inject_chat" not in server.enabled_tools
    assert "inject_event" not in server.enabled_tools


def test_effective_mcp_servers_merges_xiaomiaobot_service_profiles() -> None:
    config = Config.model_validate(
        {
            "tools": {
                "mcpServers": {
                    "existing": {
                        "command": "existing-command",
                        "enabledTools": ["status"],
                    }
                },
                "computerUseMcp": {
                    "enable": True,
                    "mode": "low_risk",
                },
                "twitterMcp": {
                    "enable": True,
                    "mode": "low_risk",
                    "extraEnabledTools": ["search", "search"],
                },
                "minecraftMcp": {
                    "enable": True,
                    "mode": "low_risk",
                    "extraEnabledTools": ["get_logs", "get_logs"],
                },
            }
        }
    )

    servers = config.tools.effective_mcp_servers()

    assert set(servers) == {"existing", "computer_use", "twitter", "minecraft"}
    assert servers["twitter"].enabled_tools.count("search") == 1
    assert "post-tweet" not in servers["twitter"].enabled_tools
    assert servers["minecraft"].enabled_tools.count("get_logs") == 1
    assert "inject_chat" not in servers["minecraft"].enabled_tools


def test_computer_use_profile_tools_still_obey_low_risk_policy() -> None:
    registry = ToolRegistry()
    for name in COMPUTER_USE_CONFIRMED_TOOLS:
        registry.register(_FakeTool(f"mcp_computer_use_{name}"))

    registry.set_context(
        RequestContext(
            channel="qq-group",
            chat_id="10001",
            metadata={"channel_policy": "low_risk"},
        )
    )

    names = _tool_names(registry.get_definitions())
    assert "mcp_computer_use_desktop_get_capabilities" in names
    assert "mcp_computer_use_browser_dom_read_page" in names
    assert "mcp_computer_use_terminal_get_state" in names
    assert "mcp_computer_use_terminal_exec" not in names
    assert "mcp_computer_use_desktop_click" not in names
    assert "mcp_computer_use_clipboard_read_text" not in names


def test_computer_use_profile_tools_visible_after_confirmation() -> None:
    registry = ToolRegistry()
    for name in ("desktop_get_capabilities", "terminal_exec", "desktop_click"):
        registry.register(_FakeTool(f"mcp_computer_use_{name}"))

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
        "mcp_computer_use_desktop_click",
        "mcp_computer_use_desktop_get_capabilities",
        "mcp_computer_use_terminal_exec",
    ]

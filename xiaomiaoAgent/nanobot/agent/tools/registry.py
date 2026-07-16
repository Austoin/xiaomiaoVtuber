"""Tool registry for dynamic tool management."""

from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.agent.tools.context import RequestContext

LOW_RISK_CHANNEL_POLICY = "low_risk"
RESTRICTED_TOOL_POLICIES = frozenset({
    LOW_RISK_CHANNEL_POLICY,
})
LOW_RISK_ALLOWED_TOOLS = frozenset({
    "read_file",
    "list_dir",
    "grep",
    "glob",
    "markitdown_convert",
    "scrapling_get",
    "web_search",
    "web_fetch",
    "xiaomiaobot_status",
})
LOW_RISK_MCP_TOOL_SUFFIXES = frozenset({
    "browser_cdp_status",
    "browser_dom_find_elements",
    "browser_dom_get_active_tab",
    "browser_dom_get_bridge_status",
    "browser_dom_get_computed_styles",
    "browser_dom_get_element_attributes",
    "browser_dom_read_input_value",
    "browser_dom_read_page",
    "browser_dom_wait_for_element",
    "desktop_get_capabilities",
    "desktop_get_session_trace",
    "desktop_get_state",
    "desktop_list_pending_actions",
    "desktop_observe_windows",
    "desktop_screenshot",
    "desktop_wait",
    "get_last_prompt",
    "get_llm_trace",
    "get_logs",
    "get_my_profile",
    "get_profile",
    "get_state",
    "get_status",
    "get_timeline",
    "get_tweet",
    "list",
    "list_tabs",
    "list_windows",
    "read_profile",
    "read_page",
    "read_tweet",
    "refresh-timeline",
    "refresh_timeline",
    "screenshot",
    "search",
    "search_tweets",
    "get-my-profile",
    "status",
    "terminal_get_state",
    "tool_directory",
    "tool_search",
})


class ToolRegistry:
    """
    Registry for agent tools.

    Allows dynamic registration and execution of tools.
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._cached_definitions: list[dict[str, Any]] | None = None
        self._request_context: RequestContext | None = None

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        self._cached_definitions = None

    def unregister(self, name: str) -> None:
        """Unregister a tool by name."""
        self._tools.pop(name, None)
        self._cached_definitions = None

    def set_context(self, ctx: RequestContext) -> None:
        """Set per-request context for policy-aware tool filtering."""
        self._request_context = ctx

    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def has(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    @staticmethod
    def _schema_name(schema: dict[str, Any]) -> str:
        """Extract a normalized tool name from either OpenAI or flat schemas."""
        fn = schema.get("function")
        if isinstance(fn, dict):
            name = fn.get("name")
            if isinstance(name, str):
                return name
        name = schema.get("name")
        return name if isinstance(name, str) else ""

    def _is_tool_allowed(self, name: str) -> bool:
        policy = self._active_policy()
        if policy not in RESTRICTED_TOOL_POLICIES:
            return True
        return name in LOW_RISK_ALLOWED_TOOLS or _is_low_risk_mcp_tool(name)

    def _active_policy(self) -> str:
        if self._request_context is not None:
            return str(self._request_context.metadata.get("channel_policy") or "")
        return ""

    def _policy_error(self, name: str) -> str | None:
        if self._is_tool_allowed(name):
            return None
        ctx = self._request_context
        channel = ctx.channel if ctx else "unknown"
        return (
            f"Error: Tool '{name}' is blocked by channel policy "
            f"'{LOW_RISK_CHANNEL_POLICY}' for channel '{channel}'."
        )

    def get_definitions(self) -> list[dict[str, Any]]:
        """Get tool definitions with stable ordering for cache-friendly prompts.

        Built-in tools are sorted first as a stable prefix, then MCP tools are
        sorted and appended.  The result is cached until the next
        register/unregister call.
        """
        if self._cached_definitions is None:
            definitions = [tool.to_schema() for tool in self._tools.values()]
            builtins: list[dict[str, Any]] = []
            mcp_tools: list[dict[str, Any]] = []
            for schema in definitions:
                name = self._schema_name(schema)
                if name.startswith("mcp_"):
                    mcp_tools.append(schema)
                else:
                    builtins.append(schema)

            builtins.sort(key=self._schema_name)
            mcp_tools.sort(key=self._schema_name)
            self._cached_definitions = builtins + mcp_tools

        if self._active_policy() != LOW_RISK_CHANNEL_POLICY:
            return self._cached_definitions

        return [
            schema for schema in self._cached_definitions
            if self._is_tool_allowed(self._schema_name(schema))
        ]

    def prepare_call(
        self,
        name: str,
        params: dict[str, Any],
    ) -> tuple[Tool | None, dict[str, Any], str | None]:
        """Resolve, cast, and validate one tool call."""
        # Guard against invalid parameter types (e.g., list instead of dict)
        if not isinstance(params, dict) and name in ('write_file', 'read_file'):
            return None, params, (
                f"Error: Tool '{name}' parameters must be a JSON object, got {type(params).__name__}. "
                "Use named parameters: tool_name(param1=\"value1\", param2=\"value2\")"
            )

        tool = self._tools.get(name)
        if not tool:
            return None, params, (
                f"Error: Tool '{name}' not found. Available: {', '.join(self.tool_names)}"
            )
        if policy_error := self._policy_error(name):
            return None, params, policy_error

        cast_params = tool.cast_params(params)
        errors = tool.validate_params(cast_params)
        if errors:
            return tool, cast_params, (
                f"Error: Invalid parameters for tool '{name}': " + "; ".join(errors)
            )
        return tool, cast_params, None

    async def execute(self, name: str, params: dict[str, Any]) -> Any:
        """Execute a tool by name with given parameters."""
        hint = "\n\n[Analyze the error above and try a different approach.]"
        tool, params, error = self.prepare_call(name, params)
        if error:
            return error + hint

        try:
            assert tool is not None  # guarded by prepare_call()
            result = await tool.execute(**params)
            if isinstance(result, str) and result.startswith("Error"):
                return result + hint
            return result
        except Exception as e:
            return f"Error executing {name}: {str(e)}" + hint

    @property
    def tool_names(self) -> list[str]:
        """Get list of registered tool names."""
        return list(self._tools.keys())

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools


def _is_low_risk_mcp_tool(name: str) -> bool:
    if not name.startswith("mcp_"):
        return False

    for suffix in LOW_RISK_MCP_TOOL_SUFFIXES:
        if name == f"mcp_{suffix}" or name.endswith(f"_{suffix}"):
            return True

    parts = name.split("_")
    for index in range(1, len(parts)):
        candidate = "_".join(parts[index:])
        if candidate in LOW_RISK_MCP_TOOL_SUFFIXES:
            return True

    return False

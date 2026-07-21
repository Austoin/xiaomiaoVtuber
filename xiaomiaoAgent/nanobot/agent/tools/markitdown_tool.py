"""MarkItDown document conversion tool."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

from nanobot.agent.tools._repo_tool_source import prefer_repo_tool_source
from nanobot.agent.tools.base import Tool, tool_parameters
from nanobot.agent.tools.filesystem import _resolve_path
from nanobot.agent.tools.schema import IntegerSchema, StringSchema, tool_parameters_schema

_DEFAULT_MAX_CHARS = 120_000
_MAX_CHARS = 300_000
_URI_PREFIXES = ("http:", "https:", "file:", "data:")


def _default_resource_workspace() -> Path | None:
    configured = os.environ.get("XIAOMIAO_RESOURCE_WORKSPACE", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()

    # Source-tree layout: xiaomiaoAgent/nanobot/agent/tools/markitdown_tool.py
    # -> repository root is parents[4]. QQ resources share the repository cache.
    try:
        root_workspace = (
            Path(__file__).resolve().parents[4]
            / ".cache"
            / "xiaomiao"
            / "qq_workspace"
        )
    except IndexError:
        return None
    return root_workspace.resolve() if root_workspace.exists() else None


def _truncate(text: str, max_chars: int) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars], True


@tool_parameters(
    tool_parameters_schema(
        path=StringSchema(
            "Workspace-local file path to convert to Markdown. URI inputs are not accepted.",
            min_length=1,
            max_length=4096,
        ),
        max_chars=IntegerSchema(
            _DEFAULT_MAX_CHARS,
            description="Maximum output characters to return.",
            minimum=100,
            maximum=_MAX_CHARS,
        ),
        required=["path"],
    )
)
class MarkItDownConvertTool(Tool):
    """Convert a workspace-local document to Markdown."""

    _scopes = {"core", "subagent"}

    def __init__(
        self,
        workspace: str | Path | None = None,
        extra_allowed_dirs: list[str | Path] | None = None,
    ):
        self._workspace = Path(workspace or Path.cwd()).resolve()
        extras = [Path(path).expanduser().resolve() for path in (extra_allowed_dirs or [])]
        default_extra = _default_resource_workspace()
        if default_extra is not None:
            extras.append(default_extra)
        self._extra_allowed_dirs = tuple(dict.fromkeys(extras))

    @classmethod
    def create(cls, ctx: Any) -> Tool:
        return cls(workspace=ctx.workspace)

    @property
    def name(self) -> str:
        return "markitdown_convert"

    @property
    def description(self) -> str:
        return (
            "Convert a workspace-local file to Markdown using MarkItDown. "
            "Only local files under the Agent workspace or the project resource workspace are allowed; "
            "URLs and file/data URIs are blocked."
        )

    @property
    def read_only(self) -> bool:
        return True

    async def execute(
        self,
        path: str,
        max_chars: int | None = None,
        **kwargs: Any,
    ) -> str:
        if not path:
            return "Error: markitdown_convert requires a workspace-local file path."
        if path.strip().lower().startswith(_URI_PREFIXES) or "://" in path:
            return "Error: markitdown_convert only accepts workspace-local file paths, not URI inputs."

        limit = min(max(max_chars or _DEFAULT_MAX_CHARS, 100), _MAX_CHARS)
        try:
            fp = _resolve_path(
                path,
                workspace=self._workspace,
                allowed_dir=self._workspace,
                extra_allowed_dirs=list(self._extra_allowed_dirs),
            )
        except PermissionError as exc:
            return f"Error: {exc}"

        if not fp.exists():
            return f"Error: File not found: {path}"
        if not fp.is_file():
            return f"Error: Not a file: {path}"

        try:
            markdown = await asyncio.to_thread(self._convert_file, fp)
        except ImportError:
            return "Error: markitdown is not installed in this environment."
        except Exception as exc:
            return f"Error converting file with MarkItDown: {exc}"

        markdown = markdown.strip()
        if not markdown:
            return f"(MarkItDown produced no extractable Markdown for: {path})"

        trimmed, truncated = _truncate(markdown, limit)
        rel = self._display_path(fp)
        header = f"(Converted with MarkItDown from: {rel})"
        if truncated:
            return f"{header}\n\n{trimmed}\n\n(MarkItDown output truncated at {limit} characters)"
        return f"{header}\n\n{trimmed}"

    def _convert_file(self, fp: Path) -> str:
        prefer_repo_tool_source(
            "markitdown",
            ("xiaomiaoAgent", "vendor", "markitdown", "packages", "markitdown", "src"),
        )
        from markitdown import MarkItDown

        result = MarkItDown(enable_plugins=False).convert(fp)
        markdown = getattr(result, "markdown", None)
        if markdown is None:
            markdown = getattr(result, "text_content", "")
        return str(markdown or "")

    def _display_path(self, fp: Path) -> str:
        for root in (self._workspace, *self._extra_allowed_dirs):
            try:
                return str(fp.relative_to(root))
            except ValueError:
                continue
        return str(fp)

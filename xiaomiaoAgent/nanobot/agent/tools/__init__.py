"""Compatibility exports for the canonical tool.core package."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if (_REPO_ROOT / "tool").exists() and _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from tool.core import (
    ArraySchema,
    BooleanSchema,
    IntegerSchema,
    NumberSchema,
    ObjectSchema,
    Schema,
    StringSchema,
    Tool,
    ToolRegistry,
    tool_parameters,
    tool_parameters_schema,
)

__all__ = [
    "ArraySchema",
    "BooleanSchema",
    "IntegerSchema",
    "NumberSchema",
    "ObjectSchema",
    "Schema",
    "StringSchema",
    "Tool",
    "ToolRegistry",
    "tool_parameters",
    "tool_parameters_schema",
]

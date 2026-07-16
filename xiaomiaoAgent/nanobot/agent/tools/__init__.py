"""Canonical xiaomiaoAgent tool contracts and registry exports."""

from nanobot.agent.tools.base import Schema, Tool, tool_parameters
from nanobot.agent.tools.registry import ToolRegistry
from nanobot.agent.tools.schema import (
    ArraySchema,
    BooleanSchema,
    IntegerSchema,
    NumberSchema,
    ObjectSchema,
    StringSchema,
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

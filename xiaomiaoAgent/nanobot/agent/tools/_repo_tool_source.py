"""Compatibility alias for :mod:`tool.core._repo_tool_source`."""

from importlib import import_module
import sys

_source = import_module("tool.core._repo_tool_source")
sys.modules[__name__] = _source
globals().update(_source.__dict__)

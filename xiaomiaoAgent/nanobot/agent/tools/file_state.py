"""Compatibility alias for :mod:`tool.core.file_state`."""

from importlib import import_module
import sys

_source = import_module("tool.core.file_state")
sys.modules[__name__] = _source
globals().update(_source.__dict__)

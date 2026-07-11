"""Compatibility alias for :mod:`tool.core.runtime_state`."""

from importlib import import_module
import sys

_source = import_module("tool.core.runtime_state")
sys.modules[__name__] = _source
globals().update(_source.__dict__)

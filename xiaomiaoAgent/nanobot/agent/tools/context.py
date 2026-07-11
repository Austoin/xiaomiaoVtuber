"""Compatibility alias for :mod:`tool.core.context`."""

from importlib import import_module
import sys

_source = import_module("tool.core.context")
sys.modules[__name__] = _source
globals().update(_source.__dict__)

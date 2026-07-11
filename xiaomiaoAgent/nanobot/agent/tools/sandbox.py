"""Compatibility alias for :mod:`tool.core.sandbox`."""

from importlib import import_module
import sys

_source = import_module("tool.core.sandbox")
sys.modules[__name__] = _source
globals().update(_source.__dict__)

"""Compatibility alias for :mod:`tool.core.base`."""

from importlib import import_module
import sys

_source = import_module("tool.core.base")
sys.modules[__name__] = _source
globals().update(_source.__dict__)

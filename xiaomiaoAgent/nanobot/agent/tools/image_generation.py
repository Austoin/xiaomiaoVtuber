"""Compatibility alias for :mod:`tool.core.image_generation`."""

from importlib import import_module
import sys

_source = import_module("tool.core.image_generation")
sys.modules[__name__] = _source
globals().update(_source.__dict__)

"""Compatibility alias for :mod:`tool.core.cron`."""

from importlib import import_module
import sys

_source = import_module("tool.core.cron")
sys.modules[__name__] = _source
globals().update(_source.__dict__)

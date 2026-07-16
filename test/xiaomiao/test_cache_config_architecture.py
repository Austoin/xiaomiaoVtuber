"""Architecture guards for the unified QQ and xiaomiaoAgent cache layout."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_cache_config():
    path = Path(__file__).resolve().parents[2] / "cache_config.py"
    spec = importlib.util.spec_from_file_location("architecture_cache_config", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cache_config_has_no_removed_service_paths() -> None:
    cache_config = _load_cache_config()
    removed_names = {
        "BOT_CACHE",
        "TOOL_CACHE",
        "BRIDGE_EVENTS_CACHE",
        "BRIDGE_EVENTS_FILE",
        "NANOBOT_BRIDGE",
        "TOOL_LOG",
        "LEGACY_PATHS",
        "get_legacy_path",
    }

    assert removed_names.isdisjoint(vars(cache_config))


def test_menu_has_no_removed_cache_migration_entry() -> None:
    project_root = Path(__file__).resolve().parents[2]
    menu_source = (project_root / "menu.cmd").read_text(encoding="utf-8")

    assert "migrate_cache.py" not in menu_source

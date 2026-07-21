"""Architecture guards for the unified QQ and xiaomiaoAgent cache layout."""

from __future__ import annotations

import importlib.util
import json
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


def test_xiaomiaobot_lint_cache_uses_root_cache() -> None:
    project_root = Path(__file__).resolve().parents[2]
    package = json.loads(
        (project_root / "xiaomiaobot" / "package.json").read_text(encoding="utf-8")
    )
    cache_args = "--cache --cache-location ../.cache/eslint/xiaomiaobot/.eslintcache"

    assert cache_args in package["scripts"]["lint"]
    assert cache_args in package["scripts"]["lint:fix"]

    staged_commands = package["nano-staged"]["*"]
    assert isinstance(staged_commands, list)
    assert any(cache_args in command for command in staged_commands)


def test_xiaomiaobot_lint_ignores_generated_artifacts() -> None:
    project_root = Path(__file__).resolve().parents[2]
    package = json.loads(
        (project_root / "xiaomiaobot" / "package.json").read_text(encoding="utf-8")
    )
    eslint_config = (
        project_root / "xiaomiaobot" / "eslint.config.js"
    ).read_text(encoding="utf-8")
    oxlint_ignore_args = (
        "--ignore-pattern '**/.wxt/**' "
        "--ignore-pattern '**/tasks/assets/wasm/**'"
    )

    assert "'**/.wxt/**'" in eslint_config
    assert "'**/tasks/assets/wasm/**'" in eslint_config
    assert oxlint_ignore_args in package["scripts"]["lint"]
    assert oxlint_ignore_args in package["scripts"]["lint:fix"]

    staged_commands = package["nano-staged"]["*"]
    assert isinstance(staged_commands, list)
    assert any(oxlint_ignore_args in command for command in staged_commands)


def test_xiaomiaobot_build_waits_for_workspace_dependencies() -> None:
    project_root = Path(__file__).resolve().parents[2]
    turbo_config = json.loads(
        (project_root / "xiaomiaobot" / "turbo.json").read_text(encoding="utf-8")
    )

    build_task = turbo_config["tasks"]["build"]
    assert "^build" in build_task["dependsOn"]
    assert "out/**" in build_task["outputs"]

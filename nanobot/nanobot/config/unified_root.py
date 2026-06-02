"""Merge root-level Xiaomiao config into nanobot config data."""

import json
import os
from pathlib import Path
from typing import Any

UNIFIED_CONFIG_ENV = "XIAOMIAO_UNIFIED_CONFIG"


def apply_unified_config_overrides(
    data: dict[str, Any],
    config_path: Path,
) -> dict[str, Any]:
    unified_path = _find_unified_config_path(config_path)
    if unified_path is None:
        return data

    with unified_path.open("r", encoding="utf-8") as f:
        unified = json.load(f)
    if not isinstance(unified, dict):
        raise ValueError(f"Unified config must be a JSON object: {unified_path}")

    override = _build_nanobot_override(unified)
    if not override:
        return data
    return _merge_non_empty(data, override)


def _find_unified_config_path(config_path: Path) -> Path | None:
    explicit_path = os.environ.get(UNIFIED_CONFIG_ENV)
    if explicit_path:
        path = Path(explicit_path)
        if not path.exists():
            raise FileNotFoundError(f"Unified config not found: {path}")
        return path

    resolved_config = config_path.resolve()
    for parent in resolved_config.parents:
        candidate = parent / "config.json"
        if candidate == resolved_config:
            continue
        if candidate.exists():
            return candidate
    return None


def _build_nanobot_override(unified: dict[str, Any]) -> dict[str, Any]:
    nanobot = _optional_dict(unified.get("nanobot"), "config.json.nanobot")
    override: dict[str, Any] = {}
    defaults = _build_agent_defaults_override(unified, nanobot)
    providers = _build_providers_override(unified, nanobot, defaults)

    if defaults:
        override["agents"] = {"defaults": defaults}
    if providers:
        override["providers"] = providers
    return override


def _build_agent_defaults_override(
    unified: dict[str, Any],
    nanobot: dict[str, Any],
) -> dict[str, Any]:
    defaults = _optional_dict(nanobot.get("defaults"), "config.json.nanobot.defaults")
    defaults = dict(defaults)
    nanobot_agent = _optional_dict(unified.get("nanobot_agent"), "config.json.nanobot_agent")

    provider = _first_text(
        nanobot.get("provider"),
        nanobot.get("chatProvider"),
        nanobot.get("chat_provider"),
    )
    model = _first_text(nanobot.get("model"), nanobot_agent.get("model"))
    if provider:
        defaults["provider"] = provider
    if model:
        defaults["model"] = model
    return defaults


def _build_providers_override(
    unified: dict[str, Any],
    nanobot: dict[str, Any],
    defaults: dict[str, Any],
) -> dict[str, Any]:
    providers: dict[str, Any] = {}
    _merge_provider_section(providers, unified.get("providers"), "config.json.providers")
    _merge_provider_section(providers, nanobot.get("providers"), "config.json.nanobot.providers")

    provider_name = defaults.get("provider")
    if isinstance(provider_name, str):
        selected = providers.get(provider_name)
        if isinstance(selected, dict):
            model = _first_text(selected.pop("model", None))
            if model and not defaults.get("model"):
                defaults["model"] = model
    return providers


def _merge_provider_section(
    target: dict[str, Any],
    value: Any,
    name: str,
) -> None:
    section = _optional_dict(value, name)
    for provider_name, provider_value in section.items():
        provider_config = _optional_dict(provider_value, f"{name}.{provider_name}")
        normalized = _normalize_provider_config(provider_config)
        if normalized:
            target[provider_name] = _merge_non_empty(target.get(provider_name, {}), normalized)


def _normalize_provider_config(provider_config: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    aliases = {
        "apiKey": ("apiKey", "api_key"),
        "apiBase": ("apiBase", "api_base", "baseUrl", "base_url"),
        "extraHeaders": ("extraHeaders", "extra_headers"),
        "extraBody": ("extraBody", "extra_body"),
        "model": ("model",),
    }
    for target_key, source_keys in aliases.items():
        value = _first_existing(provider_config, source_keys)
        if value is not None and value != "":
            normalized[target_key] = value
    return normalized


def _optional_dict(value: Any, name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _first_existing(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return None


def _first_text(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _merge_non_empty(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if value is None or value == "":
            continue
        current = result.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            result[key] = _merge_non_empty(current, value)
            continue
        result[key] = value
    return result

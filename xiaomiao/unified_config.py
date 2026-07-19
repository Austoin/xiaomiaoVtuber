import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

UNIFIED_CONFIG_ENV = "XIAOMIAO_UNIFIED_CONFIG"
XIAOMIAO_AGENT_SECTION = "xiaomiaoAgent"
CUSTOM_PROVIDER = "custom"


def default_unified_config_path() -> Path:
    return Path(__file__).resolve().parents[1] / "config.json"


def resolve_unified_config_path() -> Path:
    explicit_path = os.environ.get(UNIFIED_CONFIG_ENV)
    return Path(explicit_path) if explicit_path else default_unified_config_path()


def load_unified_config() -> dict[str, Any]:
    explicit_path = os.environ.get(UNIFIED_CONFIG_ENV)
    config_path = resolve_unified_config_path()
    if not config_path.exists():
        if explicit_path:
            raise FileNotFoundError(f"Unified config not found: {config_path}")
        return {}

    with config_path.open("r", encoding="utf-8") as config_file:
        data = json.load(config_file)

    if not isinstance(data, dict):
        raise ValueError("Unified config must be a JSON object")
    return data


def merge_unified_config_section(
    section_name: str,
    local_section: Any,
) -> dict[str, Any]:
    local_config = _section_to_dict(local_section, f"Others.{section_name}")
    root_section = load_unified_config().get(section_name, {})
    root_config = _section_to_dict(root_section, f"config.json.{section_name}")
    return _merge_non_empty_values(local_config, root_config)


def load_xiaomiao_agent_config_status() -> dict[str, Any]:
    config = _load_config_or_empty(resolve_unified_config_path())
    return _build_xiaomiao_agent_config_status(config)


def save_xiaomiao_agent_custom_config(update: dict[str, Any]) -> dict[str, Any]:
    api_key = _require_non_empty_text(update, "apiKey")
    base_url = _require_url_text(update, "baseUrl")
    model = _require_non_empty_text(update, "model")
    config_path = resolve_unified_config_path()
    config = _load_config_or_empty(config_path)

    xiaomiao_agent_config = _section_to_dict(
        config.get(XIAOMIAO_AGENT_SECTION, {}),
        "config.json.xiaomiaoAgent",
    )
    providers = _section_to_dict(
        xiaomiao_agent_config.get("providers", {}),
        "config.json.xiaomiaoAgent.providers",
    )
    custom_provider = _section_to_dict(
        providers.get(CUSTOM_PROVIDER, {}),
        "config.json.xiaomiaoAgent.providers.custom",
    )

    custom_provider["apiKey"] = api_key
    custom_provider["baseUrl"] = base_url
    providers[CUSTOM_PROVIDER] = custom_provider
    xiaomiao_agent_config["provider"] = CUSTOM_PROVIDER
    xiaomiao_agent_config["model"] = model
    xiaomiao_agent_config["providers"] = providers
    config[XIAOMIAO_AGENT_SECTION] = xiaomiao_agent_config

    _save_unified_config(config_path, config)
    return _build_xiaomiao_agent_config_status(config)


def _section_to_dict(value: Any, name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _load_config_or_empty(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}

    with config_path.open("r", encoding="utf-8") as config_file:
        data = json.load(config_file)

    if not isinstance(data, dict):
        raise ValueError("Unified config must be a JSON object")
    return data


def _save_unified_config(config_path: Path, config: dict[str, Any]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(config, ensure_ascii=False, indent=2)
    config_path.write_text(f"{content}\n", encoding="utf-8")


def _build_xiaomiao_agent_config_status(config: dict[str, Any]) -> dict[str, Any]:
    xiaomiao_agent_config = _section_to_dict(
        config.get(XIAOMIAO_AGENT_SECTION, {}),
        "config.json.xiaomiaoAgent",
    )
    provider = _text_or_empty(xiaomiao_agent_config.get("provider"))
    providers = _section_to_dict(
        xiaomiao_agent_config.get("providers", {}),
        "config.json.xiaomiaoAgent.providers",
    )
    provider_config = _section_to_dict(
        providers.get(CUSTOM_PROVIDER, {}),
        "config.json.xiaomiaoAgent.providers.custom",
    )
    model = _text_or_empty(xiaomiao_agent_config.get("model"))
    base_url = _text_or_empty(provider_config.get("baseUrl"))
    has_api_key = _has_non_empty_text(provider_config.get("apiKey"))

    return {
        "ok": True,
        "configured": provider == CUSTOM_PROVIDER
        and bool(model and base_url and has_api_key),
        "provider": provider,
        "model": model,
        "baseUrl": base_url,
        "hasApiKey": has_api_key,
    }


def _require_non_empty_text(data: dict[str, Any], name: str) -> str:
    value = data.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _require_url_text(data: dict[str, Any], name: str) -> str:
    value = _require_non_empty_text(data, name)
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{name} must be an absolute http(s) URL")
    return value


def _text_or_empty(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _has_non_empty_text(value: Any) -> bool:
    return bool(_text_or_empty(value))


def _merge_non_empty_values(
    base: dict[str, Any],
    override: dict[str, Any],
) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if value is None or value == "":
            continue
        current = result.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            result[key] = _merge_non_empty_values(current, value)
            continue
        result[key] = value
    return result

import json
from pathlib import Path

import pytest

from nanobot.config.loader import UNIFIED_CONFIG_ENV, load_config


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_root_nanobot_provider_uses_aubot_style_api_fields(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv(UNIFIED_CONFIG_ENV, raising=False)
    root_config = tmp_path / "config.json"
    nanobot_config = tmp_path / "nanobot" / ".nanobot" / "config.json"
    _write_json(
        root_config,
        {
            "nanobot": {
                "provider": "custom",
                "model": "relay-chat",
                "providers": {
                    "custom": {
                        "apiKey": "root-key",
                        "baseUrl": "https://relay.example/v1",
                    }
                },
            }
        },
    )
    _write_json(
        nanobot_config,
        {
            "agents": {"defaults": {"provider": "deepseek", "model": "deepseek-chat"}},
            "providers": {
                "custom": {
                    "apiKey": "old-key",
                    "apiBase": "https://old.example/v1",
                }
            },
        },
    )

    config = load_config(nanobot_config)

    assert config.agents.defaults.provider == "custom"
    assert config.agents.defaults.model == "relay-chat"
    assert config.providers.custom.api_key == "root-key"
    assert config.providers.custom.api_base == "https://relay.example/v1"


def test_root_xiaomiao_agent_sections_override_agent_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv(UNIFIED_CONFIG_ENV, raising=False)
    root_config = tmp_path / "config.json"
    nanobot_config = tmp_path / "xiaomiaoAgent" / ".nanobot" / "config.json"
    _write_json(
        root_config,
        {
            "xiaomiao_agent": {"model": "runtime-chat"},
            "xiaomiaoAgent": {
                "provider": "custom",
                "model": "deepseek-v4-flash",
                "providers": {
                    "custom": {
                        "apiKey": "root-key",
                        "baseUrl": "https://relay.example/v1",
                    }
                },
            },
        },
    )
    _write_json(
        nanobot_config,
        {
            "agents": {"defaults": {"provider": "deepseek", "model": "deepseek-chat"}},
            "providers": {"custom": {"apiKey": "old-key"}},
        },
    )

    config = load_config(nanobot_config)

    assert config.agents.defaults.provider == "custom"
    assert config.agents.defaults.model == "deepseek-v4-flash"
    assert config.providers.custom.api_key == "root-key"
    assert config.providers.custom.api_base == "https://relay.example/v1"


def test_root_xiaomiao_agent_runtime_model_fills_missing_agent_model(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv(UNIFIED_CONFIG_ENV, raising=False)
    root_config = tmp_path / "config.json"
    nanobot_config = tmp_path / "xiaomiaoAgent" / ".nanobot" / "config.json"
    _write_json(
        root_config,
        {
            "xiaomiao_agent": {"model": "runtime-chat"},
            "xiaomiaoAgent": {
                "provider": "custom",
                "providers": {"custom": {"apiKey": "root-key"}},
            },
        },
    )
    _write_json(nanobot_config, {})

    config = load_config(nanobot_config)

    assert config.agents.defaults.provider == "custom"
    assert config.agents.defaults.model == "runtime-chat"
    assert config.providers.custom.api_key == "root-key"


def test_root_top_level_provider_supports_snake_case_placeholders(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv(UNIFIED_CONFIG_ENV, raising=False)
    root_config = tmp_path / "config.json"
    nanobot_config = tmp_path / "nanobot" / ".nanobot" / "config.json"
    _write_json(
        root_config,
        {
            "nanobot": {"provider": "openai"},
            "providers": {
                "openai": {
                    "api_key": "snake-key",
                    "base_url": "https://snake.example/v1",
                    "model": "snake-chat",
                }
            },
        },
    )
    _write_json(nanobot_config, {})

    config = load_config(nanobot_config)

    assert config.agents.defaults.provider == "openai"
    assert config.agents.defaults.model == "snake-chat"
    assert config.providers.openai.api_key == "snake-key"
    assert config.providers.openai.api_base == "https://snake.example/v1"


def test_empty_root_values_do_not_override_existing_nanobot_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv(UNIFIED_CONFIG_ENV, raising=False)
    root_config = tmp_path / "config.json"
    nanobot_config = tmp_path / "nanobot" / ".nanobot" / "config.json"
    _write_json(
        root_config,
        {
            "nanobot": {
                "provider": "",
                "model": "",
                "providers": {"custom": {"apiKey": "", "baseUrl": ""}},
            }
        },
    )
    _write_json(
        nanobot_config,
        {
            "agents": {"defaults": {"provider": "custom", "model": "existing-chat"}},
            "providers": {
                "custom": {
                    "apiKey": "existing-key",
                    "apiBase": "https://existing.example/v1",
                }
            },
        },
    )

    config = load_config(nanobot_config)

    assert config.agents.defaults.provider == "custom"
    assert config.agents.defaults.model == "existing-chat"
    assert config.providers.custom.api_key == "existing-key"
    assert config.providers.custom.api_base == "https://existing.example/v1"


def test_unified_config_env_path_is_honored(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    explicit_root = tmp_path / "explicit" / "config.json"
    nanobot_config = tmp_path / "nanobot" / ".nanobot" / "config.json"
    _write_json(
        explicit_root,
        {
            "nanobot": {
                "provider": "custom",
                "providers": {"custom": {"apiKey": "env-key"}},
            }
        },
    )
    _write_json(tmp_path / "config.json", {"nanobot": {"provider": "openai"}})
    _write_json(nanobot_config, {})
    monkeypatch.setenv(UNIFIED_CONFIG_ENV, str(explicit_root))

    config = load_config(nanobot_config)

    assert config.agents.defaults.provider == "custom"
    assert config.providers.custom.api_key == "env-key"


def test_missing_unified_config_env_path_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    nanobot_config = tmp_path / "nanobot" / ".nanobot" / "config.json"
    _write_json(nanobot_config, {})
    monkeypatch.setenv(UNIFIED_CONFIG_ENV, str(tmp_path / "missing.json"))

    with pytest.raises(FileNotFoundError, match="Unified config not found"):
        load_config(nanobot_config)

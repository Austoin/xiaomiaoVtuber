"""Runtime path helpers derived from the active config context."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from nanobot.utils.helpers import ensure_dir


def _find_repo_root() -> Path | None:
    """Find the repository root when running from the source tree."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "cache_config.py").exists() and (parent / "xiaomiaoAgent").exists():
            return parent
    return None


def _load_repo_cache_config() -> object | None:
    """Load the root cache config when available."""
    repo_root = _find_repo_root()
    if repo_root is None:
        return None

    cache_config_path = repo_root / "cache_config.py"
    spec = importlib.util.spec_from_file_location("xiaomiao_root_cache_config", cache_config_path)
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ROOT_CACHE_CONFIG = _load_repo_cache_config()


def _default_nanobot_root() -> Path:
    """Return the default nanobot runtime root."""
    if _ROOT_CACHE_CONFIG is not None:
        return Path(_ROOT_CACHE_CONFIG.NANOBOT_CACHE)
    return Path.home() / ".nanobot"


def get_default_config_path() -> Path:
    """Return the default config file path."""
    if _ROOT_CACHE_CONFIG is not None:
        return Path(_ROOT_CACHE_CONFIG.NANOBOT_CONFIG_FILE)
    return _default_nanobot_root() / "config.json"


def get_config_path() -> Path:
    """Get the configuration file path (lazy import to break circular dependency).

    Delegates to ``nanobot.config.loader.get_config_path`` at call time so
    that importing this module never triggers a circular import during startup.
    """
    from nanobot.config.loader import get_config_path as _loader_get_config_path
    return _loader_get_config_path()


def get_data_dir() -> Path:
    """Return the instance-level runtime data directory."""
    return ensure_dir(get_config_path().parent)


def get_runtime_subdir(name: str) -> Path:
    """Return a named runtime subdirectory under the instance data dir."""
    return ensure_dir(get_data_dir() / name)


def get_media_dir(channel: str | None = None) -> Path:
    """Return the media directory, optionally namespaced per channel.

    Follows the active config instance directory (``get_config_path().parent``)
    so per-instance media isolation works. Falls back to the project default
    cache root when no config instance is active.
    """
    base = get_runtime_subdir("media")
    return ensure_dir(base / channel) if channel else base


def get_cron_dir() -> Path:
    """Return the cron storage directory, following the active config instance."""
    return get_runtime_subdir("cron")


def get_logs_dir() -> Path:
    """Return the logs directory, following the active config instance."""
    return get_runtime_subdir("logs")


def get_workspace_path(workspace: str | None = None) -> Path:
    """Resolve and ensure the agent workspace path."""
    path = Path(workspace).expanduser() if workspace else _default_nanobot_root() / "workspace"
    return ensure_dir(path)


def is_default_workspace(workspace: str | Path | None) -> bool:
    """Return whether a workspace resolves to nanobot's default workspace path."""
    current = Path(workspace).expanduser() if workspace is not None else _default_nanobot_root() / "workspace"
    default = _default_nanobot_root() / "workspace"
    return current.resolve(strict=False) == default.resolve(strict=False)


def get_cli_history_path() -> Path:
    """Return the shared CLI history file path."""
    return ensure_dir(_default_nanobot_root() / "history") / "cli_history"


def get_bridge_install_dir() -> Path:
    """Return the shared WhatsApp bridge installation directory."""
    return ensure_dir(_default_nanobot_root() / "bridge")


def get_legacy_sessions_dir() -> Path:
    """Return the legacy global session directory used for migration fallback."""
    return ensure_dir(_default_nanobot_root() / "sessions")


def get_tool_results_dir(workspace: str | Path | None = None) -> Path:
    """Return the shared tool-result persistence directory."""
    if workspace is not None:
        workspace_path = Path(workspace).expanduser().resolve(strict=False)
        if not is_default_workspace(workspace_path):
            return ensure_dir(workspace_path / ".cache" / "tool-results")
    return ensure_dir(_default_nanobot_root() / "tool-results")

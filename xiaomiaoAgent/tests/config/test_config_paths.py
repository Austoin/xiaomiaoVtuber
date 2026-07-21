import configparser
import tomllib
from pathlib import Path

from nanobot.config.paths import (
    get_bridge_install_dir,
    get_cli_history_path,
    get_cron_dir,
    get_data_dir,
    get_default_config_path,
    get_legacy_sessions_dir,
    get_logs_dir,
    get_media_dir,
    get_runtime_subdir,
    get_tool_results_dir,
    get_workspace_path,
    is_default_workspace,
)
from nanobot.config.schema import Config


def test_repo_default_paths_use_project_cache() -> None:
    config_path = get_default_config_path()

    assert config_path.as_posix().endswith("/.cache/agent/nanobot/config.json")
    assert get_workspace_path().as_posix().endswith("/.cache/agent/nanobot/workspace")
    assert get_cli_history_path().as_posix().endswith("/.cache/agent/nanobot/history/cli_history")
    assert get_bridge_install_dir().as_posix().endswith("/.cache/agent/nanobot/bridge")
    assert get_tool_results_dir().as_posix().endswith("/.cache/agent/nanobot/tool-results")


def test_pytest_caches_stay_in_project_cache() -> None:
    project_root = Path(__file__).resolve().parents[3]
    cache_root = (project_root / ".cache").resolve()

    root_config = configparser.ConfigParser()
    root_config.read(project_root / "pytest.ini", encoding="utf-8")
    root_options = root_config["pytest"]

    agent_config = tomllib.loads(
        (project_root / "xiaomiaoAgent" / "pyproject.toml").read_text(encoding="utf-8")
    )
    agent_options = agent_config["tool"]["pytest"]["ini_options"]

    project_cache_paths = (
        (project_root, root_options["cache_dir"]),
        (project_root, root_options["addopts"].removeprefix("--basetemp=")),
        (project_root / "xiaomiaoAgent", agent_options["cache_dir"]),
        (
            project_root / "xiaomiaoAgent",
            agent_options["addopts"].removeprefix("--basetemp="),
        ),
    )

    for config_dir, configured_path in project_cache_paths:
        resolved_path = (config_dir / configured_path).resolve()
        assert resolved_path.is_relative_to(cache_root)


def test_runtime_dirs_follow_config_path(monkeypatch, tmp_path: Path) -> None:
    config_file = tmp_path / "instance-a" / "config.json"
    monkeypatch.setattr("nanobot.config.paths.get_config_path", lambda: config_file)

    assert get_data_dir() == config_file.parent
    assert get_runtime_subdir("cron") == config_file.parent / "cron"
    assert get_cron_dir() == config_file.parent / "cron"
    assert get_logs_dir() == config_file.parent / "logs"


def test_media_dir_supports_channel_namespace(monkeypatch, tmp_path: Path) -> None:
    config_file = tmp_path / "instance-b" / "config.json"
    monkeypatch.setattr("nanobot.config.paths.get_config_path", lambda: config_file)

    assert get_media_dir() == config_file.parent / "media"
    assert get_media_dir("telegram") == config_file.parent / "media" / "telegram"


def test_shared_and_legacy_paths_follow_default_runtime_root() -> None:
    runtime_root = get_default_config_path().parent

    assert get_cli_history_path() == runtime_root / "history" / "cli_history"
    assert get_bridge_install_dir() == runtime_root / "bridge"
    assert get_legacy_sessions_dir() == runtime_root / "sessions"


def test_workspace_path_is_explicitly_resolved() -> None:
    assert get_workspace_path() == get_default_config_path().parent / "workspace"
    assert get_workspace_path("~/custom-workspace") == Path.home() / "custom-workspace"


def test_config_workspace_path_returns_expanded_path(tmp_path: Path) -> None:
    config = Config(agents={"defaults": {"workspace": str(tmp_path)}})

    assert config.workspace_path == tmp_path


def test_is_default_workspace_distinguishes_default_and_custom_paths() -> None:
    assert is_default_workspace(None) is True
    assert is_default_workspace(get_default_config_path().parent / "workspace") is True
    assert is_default_workspace("~/custom-workspace") is False


def test_tool_results_dir_uses_custom_workspace_cache(tmp_path: Path) -> None:
    custom_workspace = tmp_path / "workspace"

    assert get_tool_results_dir(custom_workspace) == custom_workspace / ".cache" / "tool-results"

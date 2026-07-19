import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
XIAOMIAO_DIR = PROJECT_ROOT / "xiaomiao"


def test_main_imports_without_legacy_model_module() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import main"],
        cwd=XIAOMIAO_DIR,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_qq_entry_does_not_own_desktop_bridge() -> None:
    source = (XIAOMIAO_DIR / "main.py").read_text(encoding="utf-8")

    assert "from desktop_bridge" not in source
    assert "start_desktop_bridge" not in source
    assert "publish_qq_agent_reply" not in source
    assert "http://127.0.0.1:5519" not in source

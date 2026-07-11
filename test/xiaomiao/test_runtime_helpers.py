import asyncio
import io
import sys
import tempfile
from pathlib import Path

from PIL import Image

project_root = Path(__file__).resolve().parents[2]
xiaomiao_path = project_root / "xiaomiao"
if str(xiaomiao_path) not in sys.path:
    sys.path.insert(0, str(xiaomiao_path))

from utils.runtime_helpers import (
    SettingsStore,
    deal_image,
    download_and_compress_image,
    seconds_to_hms,
    verfiy_pixiv,
)


def _create_image_bytes(size=(3000, 2000), color=(255, 0, 0)) -> bytes:
    image = Image.new("RGB", size, color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_seconds_to_hms_formats_duration():
    assert seconds_to_hms(3661) == "1h, 1m, 1s"


def _workspace_temp_dir() -> str:
    temp_dir = project_root / ".pytest-tmp-xiaomiao"
    temp_dir.mkdir(exist_ok=True)
    return str(temp_dir)


def test_verfiy_pixiv_accepts_valid_image():
    with tempfile.TemporaryDirectory(dir=_workspace_temp_dir()) as temp_dir:
        image_path = Path(temp_dir) / "image.png"
        image_path.write_bytes(_create_image_bytes(size=(32, 32)))

        assert verfiy_pixiv(image_path) is True


def test_verfiy_pixiv_rejects_invalid_image():
    with tempfile.TemporaryDirectory(dir=_workspace_temp_dir()) as temp_dir:
        image_path = Path(temp_dir) / "broken.png"
        image_path.write_text("not-an-image", encoding="utf-8")

        assert verfiy_pixiv(image_path) is False


def test_deal_image_resizes_and_converts_to_jpeg():
    compressed = deal_image(
        _create_image_bytes(),
        max_width=800,
        max_height=600,
        max_size_mb=1,
    )

    image = Image.open(io.BytesIO(compressed))
    assert image.format == "JPEG"
    assert image.width <= 800
    assert image.height <= 600


class _FakeResponse:
    def __init__(self, body: bytes, status: int = 200):
        self._body = body
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def read(self):
        return self._body


class _FakeSession:
    def __init__(self, body: bytes, status: int = 200):
        self._body = body
        self._status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def get(self, url, timeout):
        return _FakeResponse(self._body, self._status)


def test_download_and_compress_image_returns_base64(monkeypatch):
    image_bytes = _create_image_bytes()

    import utils.runtime_helpers as runtime_helpers

    monkeypatch.setattr(
        runtime_helpers.aiohttp,
        "ClientSession",
        lambda: _FakeSession(image_bytes),
    )

    result = asyncio.run(
        download_and_compress_image(
            "https://example.com/image.png",
            max_width=800,
            max_height=600,
            max_size_mb=1,
        )
    )

    assert isinstance(result, str)
    assert len(result) > 0


def test_settings_store_reads_and_writes_files():
    with tempfile.TemporaryDirectory(dir=_workspace_temp_dir()) as temp_dir:
        temp_path = Path(temp_dir)
        super_user_file = temp_path / "super.txt"
        manage_user_file = temp_path / "manage.txt"
        sisters_file = temp_path / "sisters.txt"
        jhq_file = temp_path / "jhq.txt"
        programmers_file = temp_path / "programmers.txt"

        super_user_file.write_text("10001\n10002\n", encoding="utf-8")
        manage_user_file.write_text("20001\n", encoding="utf-8")
        sisters_file.write_text("30001\n", encoding="utf-8")
        jhq_file.write_text("40001\n", encoding="utf-8")

        store = SettingsStore(
            super_user_file=super_user_file,
            manage_user_file=manage_user_file,
            sisters_file=sisters_file,
            jhq_file=jhq_file,
            programmers_file=programmers_file,
        )

        settings = store.read_settings()
        assert settings["super_users"] == ["10001", "10002", ""]
        assert settings["manage_users"] == ["20001", ""]
        assert settings["sisters"] == ["30001", ""]
        assert settings["jhq"] == ["40001", ""]
        assert settings["programmers"] == []

        assert store.write_settings(["50001", "", "50002"], ["60001", ""]) is True
        assert super_user_file.read_text(encoding="utf-8") == "50001\n50002"
        assert manage_user_file.read_text(encoding="utf-8") == "60001"

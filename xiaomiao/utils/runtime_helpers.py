import base64
import io
from dataclasses import dataclass
from pathlib import Path

import aiohttp
from PIL import Image

from prerequisites import update_role_lists


@dataclass
class SettingsStore:
    super_user_file: Path
    manage_user_file: Path
    sisters_file: Path
    jhq_file: Path
    programmers_file: Path

    @staticmethod
    def _read_lines(path: Path) -> list[str]:
        with open(path, "r", encoding="utf-8") as file:
            return file.read().split("\n")

    def read_settings(self) -> dict[str, list[str]]:
        settings = {
            "super_users": self._read_lines(self.super_user_file),
            "manage_users": self._read_lines(self.manage_user_file),
            "sisters": self._read_lines(self.sisters_file),
            "jhq": self._read_lines(self.jhq_file),
        }
        try:
            settings["programmers"] = self._read_lines(self.programmers_file)
        except FileNotFoundError:
            settings["programmers"] = []
        return settings

    def write_roles(
        self,
        role: str,
        user_id: int,
        sisters: list[str],
        jhq: list[str],
        programmers: list[str],
    ) -> tuple[bool, list[str], list[str], list[str]]:
        next_sisters, next_jhq, next_programmers = update_role_lists(
            str(user_id), role, sisters, jhq, programmers
        )
        try:
            with open(self.sisters_file, "w", encoding="utf-8") as file:
                file.write("\n".join(next_sisters))
            with open(self.jhq_file, "w", encoding="utf-8") as file:
                file.write("\n".join(next_jhq))
            with open(self.programmers_file, "w", encoding="utf-8") as file:
                file.write("\n".join(next_programmers))
            return True, next_sisters, next_jhq, next_programmers
        except Exception:
            return False, sisters, jhq, programmers

    def write_settings(self, super_users: list[str], manage_users: list[str]) -> bool:
        normalized_super_users = [item for item in super_users if item]
        normalized_manage_users = [item for item in manage_users if item]
        try:
            with open(self.super_user_file, "w", encoding="utf-8") as file:
                file.write("\n".join(normalized_super_users))
            with open(self.manage_user_file, "w", encoding="utf-8") as file:
                file.write("\n".join(normalized_manage_users))
            return True
        except Exception:
            return False


def seconds_to_hms(total_seconds):
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    return f"{hours}h, {minutes}m, {seconds}s"


def verfiy_pixiv(file_path):
    try:
        img = Image.open(file_path)
        img.verify()
        img.close()
        return True
    except (IOError, SyntaxError) as exc:
        print(f"Error: {exc}")
        return False


def deal_image(i, max_width=1920, max_height=1920, max_size_mb=5):
    img = Image.open(io.BytesIO(i))

    if img.mode in ("RGBA", "P", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    width, height = img.size
    if width > max_width or height > max_height:
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"图片尺寸调整: {width}x{height} -> {new_width}x{new_height}")

    buffer = io.BytesIO()
    max_size = max_size_mb * 1024 * 1024
    quality = 95

    while quality >= 10:
        buffer.seek(0)
        buffer.truncate()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        if buffer.tell() < max_size:
            break
        quality -= 10

    print(f"图片压缩完成: {buffer.tell() / 1024:.1f}KB, quality={quality}")
    return buffer.getvalue()


async def download_and_compress_image(
    url, max_width=1920, max_height=1920, max_size_mb=5
):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    original_size = len(image_data) / 1024
                    print(f"下载图片成功: {original_size:.1f}KB")

                    compressed = deal_image(
                        image_data, max_width, max_height, max_size_mb
                    )
                    compressed_size = len(compressed) / 1024
                    print(
                        f"压缩后: {compressed_size:.1f}KB (节省 {(1 - compressed_size / original_size) * 100:.1f}%)"
                    )

                    return base64.b64encode(compressed).decode("utf-8")
                else:
                    print(f"下载图片失败: HTTP {resp.status}")
                    return None
    except Exception as exc:
        print(f"下载图片异常: {exc}")
        return None

"""Quote image generation for QQ reply messages."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import httpx
from PIL import Image, ImageDraw, ImageFont

from cache_config import QQ_TMP


_ASSET_DIR = Path(__file__).resolve().parent / "assets"
QUOTE_IMAGE_PATH = QQ_TMP / "quote.png"


def open_from_url(url: str) -> Image.Image:
    """Load an image from a URL and fail loudly on HTTP errors."""
    response = httpx.get(url, timeout=15.0)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))


def square_scale(image: Image.Image, height: int) -> Image.Image:
    old_width, old_height = image.size
    scale = height / old_height
    width = int(old_width * scale)
    return image.resize((width, height))


def wrap_text(text: str, chars_per_line: int = 13) -> str:
    return "\n".join(text[i : i + chars_per_line] for i in range(0, len(text), chars_per_line))


def _font(filename: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(_ASSET_DIR / filename), size=size)


def _is_emoji(char: str) -> bool:
    codepoint = ord(char)
    return 0x1F300 <= codepoint <= 0x1FAFF


async def get_image(quote: str, ava_url: str, name: str, uin: int | str) -> None:
    """Generate a quote image and write it to ``QUOTE_IMAGE_PATH``.

    ``uin`` is kept for compatibility with the historical call signature.
    """
    _ = uin
    mask = Image.open(_ASSET_DIR / "quote" / "mask.png").convert("RGBA")
    background = Image.new("RGBA", mask.size, (255, 255, 255, 255))
    head = open_from_url(ava_url).convert("RGBA")

    title_font = _font("t.ttf", size=36)
    desc_font = _font("n.ttf", size=30)
    digit_font = _font("sz.ttf", size=36)
    emoji_font = _font("e.ttf", size=36)

    background.paste(square_scale(head, 640), (0, 0))
    background.paste(mask, (0, 0), mask)

    draw = ImageDraw.Draw(background)
    text = wrap_text(quote)

    mask_circle = Image.new("L", head.size, 0)
    draw_circle = ImageDraw.Draw(mask_circle)
    draw_circle.ellipse((0, 0, head.size[0], head.size[1]), fill=255)
    head.putalpha(mask_circle)

    x_offset = 640
    y_offset = 165
    for char in text:
        if char.isdigit() or char == ".":
            font = digit_font
            fill_color = (255, 0, 0)
        elif _is_emoji(char):
            font = emoji_font
            fill_color = (255, 255, 255)
        else:
            font = title_font
            fill_color = (255, 255, 255)

        char_width = font.getlength(char)
        if x_offset + char_width > mask.size[0]:
            x_offset = 640
            y_offset += 40

        draw.text((x_offset, y_offset), char, font=font, fill=fill_color)
        x_offset += char_width
        if char == "\n":
            x_offset = 640
            y_offset += 40

    draw.text((862 if len(name) >= 7 else 1000, 465), f"——{name}", font=desc_font, fill=(112, 112, 112))

    output = Image.new("RGB", mask.size, (0, 0, 0))
    output.paste(background, (0, 0))
    QUOTE_IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.save(QUOTE_IMAGE_PATH)


async def handle(message: list[Any], actions: Any, images: str | None = None) -> Any:
    """Handle a QQ reply message and return a Hyper image segment."""
    from Hyper import Segments
    from Hyper.Events import gen_message

    if not message or not isinstance(message[0], Segments.Reply):
        return None

    content = await actions.get_msg(message[0].id)
    sender = content.data["sender"]
    name = sender["nickname"] if not sender.get("card") else sender["card"]
    uin = sender["user_id"]
    quoted_message = gen_message({"message": content.data["message"]})
    text = str(quoted_message).replace("[图片]", "")

    avatar_url = images or f"http://q2.qlogo.cn/headimg_dl?dst_uin={uin}&spec=640"
    await get_image(text, avatar_url, name, uin)

    return Segments.Image(f"file://{QUOTE_IMAGE_PATH.resolve()}")


__all__ = ["QUOTE_IMAGE_PATH", "get_image", "handle", "open_from_url", "square_scale", "wrap_text"]

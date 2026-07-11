"""
图片服务

封装图片生成、下载、压缩等功能
"""

import logging
import aiohttp
import base64
from PIL import Image
import io
from typing import Optional, Literal

logger = logging.getLogger(__name__)

ImageType = Literal["二次元", "风景", "妹子", "随机"]


class ImageService:
    """图片服务"""

    def __init__(self):
        self.api_urls = {
            "二次元": "https://api.mossia.top/duckMo",
            "风景": "https://api.mossia.top/duckMo",
            "妹子": "https://api.mossia.top/duckMo",
            "随机": "https://api.mossia.top/duckMo",
        }

    async def generate(
        self,
        img_type: str = "二次元",
        max_width: int = 1920,
        max_height: int = 1920,
        max_size_mb: int = 5,
    ) -> Optional[str]:
        """
        生成图片

        Args:
            img_type: 图片类型 (二次元, 风景, 妹子, 随机)
            max_width: 最大宽度
            max_height: 最大高度
            max_size_mb: 最大文件大小 (MB)

        Returns:
            图片 URL,失败返回 None
        """
        # 映射快捷输入
        type_mapping = {
            "二次元": "二次元",
            "acg": "二次元",
            "anime": "二次元",
            "风景": "风景",
            "landscape": "风景",
            "妹子": "妹子",
            "girl": "妹子",
            "随机": "随机",
            "random": "随机",
        }

        normalized_type = type_mapping.get(img_type.lower(), "二次元")
        api_url = self.api_urls.get(normalized_type, self.api_urls["二次元"])

        try:
            async with aiohttp.ClientSession() as session:
                # 根据类型构建请求
                params = self._build_params(normalized_type)

                async with session.get(
                    api_url, params=params, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        # API 返回的是图片 URL 或者直接是图片
                        content_type = resp.headers.get('content-type', '')

                        if 'image' in content_type:
                            # 直接返回图片数据,需要转换为 URL
                            image_data = await resp.read()
                            return await self._upload_or_encode(image_data)
                        else:
                            # 返回的是 JSON 或 URL
                            try:
                                data = await resp.json()
                                return data.get('url') or data.get('data', {}).get('url')
                            except:
                                # 可能直接返回 URL 文本
                                text = await resp.text()
                                if text.startswith('http'):
                                    return text

                    logger.error(f"图片生成失败: HTTP {resp.status}")
                    return None

        except Exception as e:
            logger.error(f"图片生成异常: {e}", exc_info=True)
            return None

    def _build_params(self, img_type: str) -> dict:
        """构建 API 请求参数"""
        params = {}

        if img_type == "二次元":
            params['type'] = 'acg'
        elif img_type == "风景":
            params['type'] = 'landscape'
        elif img_type == "妹子":
            params['type'] = 'girl'
        elif img_type == "随机":
            params['type'] = 'random'

        return params

    async def _upload_or_encode(self, image_data: bytes) -> str:
        """
        上传图片或转为 base64

        这里简化为直接返回一个占位符
        实际应用中可以上传到图床
        """
        # TODO: 实现图片上传到图床
        # 目前返回 base64 编码 (不推荐用于大图)
        return f"data:image/png;base64,{base64.b64encode(image_data).decode()}"

    async def get_avatar(self, qq: int, size: int = 640) -> str:
        """
        获取 QQ 头像

        Args:
            qq: QQ 号
            size: 头像大小 (默认 640)

        Returns:
            头像 URL
        """
        return f"http://q2.qlogo.cn/headimg_dl?dst_uin={qq}&spec={size}"

    def compress_image(
        self,
        image_data: bytes,
        max_width: int = 1920,
        max_height: int = 1920,
        max_size_mb: int = 5,
    ) -> bytes:
        """
        压缩图片

        Args:
            image_data: 原始图片数据
            max_width: 最大宽度
            max_height: 最大高度
            max_size_mb: 最大文件大小 (MB)

        Returns:
            压缩后的图片数据
        """
        try:
            img = Image.open(io.BytesIO(image_data))

            # 调整尺寸
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # 压缩质量
            quality = 95
            while quality > 10:
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality)
                size_mb = len(buffer.getvalue()) / (1024 * 1024)

                if size_mb <= max_size_mb:
                    return buffer.getvalue()

                quality -= 10

            return buffer.getvalue()

        except Exception as e:
            logger.error(f"图片压缩失败: {e}")
            return image_data


# 全局图片服务实例
image_service = ImageService()

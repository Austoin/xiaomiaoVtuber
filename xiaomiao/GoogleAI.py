"""
GoogleAI.py - 使用 OpenAI SDK 调用 Gemini 模型（支持中转站）

通过 OpenAI 兼容接口调用 Gemini，支持：
- 多轮对话
- 图片理解（base64 编码）
- 自定义 base_url（中转站支持）
"""

from typing import Union
from openai import OpenAI
import httpx
import base64


class Parts:
    """消息内容部件"""

    @staticmethod
    class File:
        """图片文件部件"""

        def __init__(self, image_data: str, mime_type: str = "image/jpeg"):
            self.image_data = image_data  # base64 编码的图片数据
            self.mime_type = mime_type

        @classmethod
        def upload_from_file(cls, path: str):
            """从本地文件加载图片"""
            with open(path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            mime_type = "image/png" if "png" in path else "image/jpeg"
            return cls(image_data, mime_type)

        @classmethod
        def upload_from_url(cls, url: str):
            """从 URL 下载并加载图片"""
            print(url)
            # 增加超时时间，QQ 多媒体服务器响应较慢
            response = httpx.get(url, timeout=30.0, follow_redirects=True)
            image_data = base64.b64encode(response.content).decode("utf-8")
            # 根据 URL 判断 MIME 类型
            if "gif" in url.lower():
                mime_type = "image/gif"
            elif "png" in url.lower():
                mime_type = "image/png"
            else:
                mime_type = "image/jpeg"
            return cls(image_data, mime_type)

        def to_raw(self) -> dict:
            """转换为 OpenAI API 格式"""
            return {
                "type": "image_url",
                "image_url": {"url": f"data:{self.mime_type};base64,{self.image_data}"},
            }

    @staticmethod
    class Text:
        """文本部件"""

        def __init__(self, text: str):
            self.text = text

        def to_raw(self) -> dict:
            """转换为 OpenAI API 格式"""
            return {"type": "text", "text": self.text}


class BaseRole:
    """消息角色基类"""

    def __init__(self, *args: Union[Parts.File, Parts.Text]):
        self.content = list(args)
        self.tag = "none"

    def res(self) -> dict:
        """转换为 OpenAI API 消息格式"""
        return {"role": self.tag, "content": [i.to_raw() for i in self.content]}


class Roles:
    """消息角色定义"""

    @staticmethod
    class User(BaseRole):
        """用户消息"""

        def __init__(self, *args: Union[Parts.File, Parts.Text]):
            super().__init__(*args)
            self.tag = "user"

    @staticmethod
    class Model(BaseRole):
        """模型回复"""

        def __init__(self, *args: Union[Parts.File, Parts.Text]):
            super().__init__(*args)
            self.tag = "assistant"


class Context:
    """对话上下文管理器"""

    def __init__(self, api_key: str, model, base_url: str = None, tools: list = None):
        """
        初始化上下文

        Args:
            api_key: API 密钥
            model: GenerativeModel 实例
            base_url: 中转站地址（可选）
            tools: 工具列表（暂未实现）
        """
        # 优先使用传入的 base_url，其次使用全局配置
        actual_base_url = (
            base_url
            or _GenAI._base_url
            or "https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        self.client = OpenAI(api_key=api_key, base_url=actual_base_url)
        self.model = model
        self.model_name = getattr(
            model, "model_name", "gemini-2.0-flash-thinking-exp-01-21"
        )
        self.system_instruction = getattr(model, "_system_instruction", None)
        self.generation_config = getattr(model, "generation_config", {})
        self.tools = tools
        self.history = []

    def __gen_content(self, new: Roles.User) -> list:
        """生成消息列表"""
        content = []
        content += self.history
        if len(content) > 0 and isinstance(content[-1], Roles.User):
            raise ValueError("消息角色重复")

        content.append(new)
        self.history = content
        return [i.res() for i in content]

    def gen_content(self, content: Roles.User) -> str:
        """
        生成回复内容

        Args:
            content: 用户消息

        Returns:
            模型回复文本
        """
        try:
            messages = self.__gen_content(content)

            # 添加系统提示词
            if self.system_instruction:
                messages = [
                    {"role": "system", "content": self.system_instruction}
                ] + messages

            print(content.res())

            # 构建请求参数
            request_params = {
                "model": self.model_name,
                "messages": messages,
            }

            # 添加生成配置
            if self.generation_config:
                if "temperature" in self.generation_config:
                    request_params["temperature"] = self.generation_config[
                        "temperature"
                    ]
                if "top_p" in self.generation_config:
                    request_params["top_p"] = self.generation_config["top_p"]
                if "max_output_tokens" in self.generation_config:
                    request_params["max_tokens"] = self.generation_config[
                        "max_output_tokens"
                    ]

            response = self.client.chat.completions.create(**request_params)

            result = response.choices[0].message.content
            self.history.append(Roles.Model(Parts.Text(str(result))))
            return result
        except Exception as e:
            if len(self.history) > 0:
                self.history = self.history[: len(self.history) - 1]
            raise e


class _GenAI:
    """
    genai 模块兼容层

    模拟 google.generativeai 的接口，使 main.py 无需大幅修改
    """

    _api_key = None
    _base_url = None

    @staticmethod
    def configure(api_key: str, base_url: str = None):
        """
        配置 API 密钥和中转站地址

        Args:
            api_key: API 密钥
            base_url: 中转站地址（可选）
        """
        _GenAI._api_key = api_key
        _GenAI._base_url = base_url

    class GenerativeModel:
        """生成模型配置"""

        def __init__(
            self,
            model_name: str = "gemini-2.0-flash-thinking-exp-01-21",
            generation_config: dict = None,
            system_instruction: str = None,
            **kwargs,
        ):
            """
            初始化模型配置

            Args:
                model_name: 模型名称
                generation_config: 生成配置
                system_instruction: 系统提示词
            """
            self.model_name = model_name
            self.generation_config = generation_config or {}
            self._system_instruction = system_instruction


# 导出兼容接口
genai = _GenAI()

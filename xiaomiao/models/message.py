"""
消息模型 - 统一的消息数据结构
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """消息类型"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    VOICE = "voice"
    VIDEO = "video"
    AT = "at"
    REPLY = "reply"
    FORWARD = "forward"


class MessageSource(Enum):
    """消息来源"""
    GROUP = "group"
    PRIVATE = "private"
    DESKTOP = "desktop"
    WEB = "web"


@dataclass
class User:
    """用户信息"""
    user_id: int
    nickname: str
    role: str = "user"  # user, admin, owner, root
    group_id: Optional[int] = None


@dataclass
class MessageSegment:
    """消息片段"""
    type: MessageType
    data: Dict[str, Any]


@dataclass
class Message:
    """统一消息模型"""
    # 基本信息
    message_id: str
    user: User
    source: MessageSource
    timestamp: datetime = field(default_factory=datetime.now)

    # 消息内容
    text: str = ""
    segments: List[MessageSegment] = field(default_factory=list)
    raw_message: Optional[Any] = None

    # 上下文信息
    reply_to: Optional[str] = None
    group_id: Optional[int] = None
    session_id: Optional[str] = None

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_text(self) -> bool:
        """是否包含文本"""
        return bool(self.text.strip())

    def has_image(self) -> bool:
        """是否包含图片"""
        return any(seg.type == MessageType.IMAGE for seg in self.segments)

    def has_file(self) -> bool:
        """是否包含文件"""
        return any(seg.type == MessageType.FILE for seg in self.segments)

    def has_at(self) -> bool:
        """是否包含 @ 提及"""
        return any(seg.type == MessageType.AT for seg in self.segments)

    def get_images(self) -> List[Dict[str, Any]]:
        """获取所有图片"""
        return [seg.data for seg in self.segments if seg.type == MessageType.IMAGE]

    def get_files(self) -> List[Dict[str, Any]]:
        """获取所有文件"""
        return [seg.data for seg in self.segments if seg.type == MessageType.FILE]

    def is_command(self, prefix: str = "") -> bool:
        """
        判断是否为命令

        Args:
            prefix: 命令前缀，默认为空（任意命令）

        Returns:
            是否为命令
        """
        if not self.has_text():
            return False

        text = self.text.strip()
        if not prefix:
            # 检查是否以常见命令前缀开头
            return text.startswith(('/', '!', '.', '#'))

        return text.startswith(prefix)

    def extract_command(self, prefix: str = "") -> Optional[tuple[str, str]]:
        """
        提取命令和参数

        Args:
            prefix: 命令前缀

        Returns:
            (命令, 参数) 或 None
        """
        if not self.is_command(prefix):
            return None

        text = self.text.strip()
        if prefix:
            text = text[len(prefix):]

        parts = text.split(maxsplit=1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        return command, args


@dataclass
class Response:
    """响应消息"""
    text: str = ""
    images: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    at_sender: bool = False
    reply_to: Optional[str] = None

    # 元数据
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_text(self, text: str) -> 'Response':
        """添加文本"""
        if self.text:
            self.text += "\n" + text
        else:
            self.text = text
        return self

    def add_image(self, image_url: str) -> 'Response':
        """添加图片"""
        self.images.append(image_url)
        return self

    def add_file(self, file_path: str) -> 'Response':
        """添加文件"""
        self.files.append(file_path)
        return self

    def set_error(self, error: str) -> 'Response':
        """设置错误"""
        self.success = False
        self.error_message = error
        return self

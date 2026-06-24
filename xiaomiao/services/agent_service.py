"""
Agent 服务 - 封装与 xiaomiaoAgent 的交互

整合自:
- agent_backend.py
- main.py 中的 Agent 调用逻辑
"""
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

try:
    from ..models import Message, Response
except ImportError:
    from models import Message, Response

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Agent 配置"""
    base_url: str = "http://127.0.0.1:8900/v1/chat/completions"
    model: str = ""
    session_id: str = "xiaomiao-unified"
    timeout_seconds: int = 30
    enabled: bool = True


class AgentService:
    """Agent 服务"""

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        初始化 Agent 服务

        Args:
            config: Agent 配置
        """
        self.config = config or AgentConfig()
        self._sessions: Dict[str, List[Dict]] = {}
        logger.info(f"Agent 服务初始化: {self.config.base_url}")

    async def request_agent(
        self,
        message: Message,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
    ) -> Response:
        """
        请求 Agent 处理消息

        Args:
            message: 消息对象
            system_prompt: 系统提示词
            tools: 可用工具列表

        Returns:
            Agent 响应
        """
        if not self.config.enabled:
            logger.warning("Agent 服务未启用")
            return Response(text="Agent 服务未启用").set_error("disabled")

        # 获取会话历史
        session_id = message.session_id or self.config.session_id
        history = self._get_session_history(session_id)

        # 构建请求
        request_data = self._build_request(
            message=message,
            history=history,
            system_prompt=system_prompt,
            tools=tools,
        )

        try:
            # 调用 Agent API
            response_text = await self._call_agent_api(request_data)

            # 更新会话历史
            self._update_session_history(session_id, message.text, response_text)

            return Response(text=response_text, success=True)

        except Exception as e:
            logger.error(f"Agent 请求失败: {e}", exc_info=True)
            return Response(text="处理失败，请稍后重试").set_error(str(e))

    async def stream_agent(
        self,
        message: Message,
        system_prompt: Optional[str] = None,
    ):
        """
        流式请求 Agent（生成器）

        Args:
            message: 消息对象
            system_prompt: 系统提示词

        Yields:
            响应片段
        """
        # TODO: 实现流式响应
        yield "流式响应暂未实现"

    def get_session_history(self, session_id: str) -> List[Dict]:
        """获取会话历史"""
        return self._get_session_history(session_id)

    def clear_session(self, session_id: str) -> None:
        """清除会话历史"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"清除会话: {session_id}")

    def _get_session_history(self, session_id: str) -> List[Dict]:
        """获取会话历史"""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        return self._sessions[session_id]

    def _update_session_history(
        self, session_id: str, user_msg: str, assistant_msg: str
    ) -> None:
        """更新会话历史"""
        history = self._get_session_history(session_id)
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": assistant_msg})

        # 限制历史长度
        max_history = 20
        if len(history) > max_history:
            self._sessions[session_id] = history[-max_history:]

    def _build_request(
        self,
        message: Message,
        history: List[Dict],
        system_prompt: Optional[str],
        tools: Optional[List[Dict]],
    ) -> Dict[str, Any]:
        """构建 Agent 请求"""
        messages = []

        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 添加历史消息
        messages.extend(history)

        # 添加当前消息
        messages.append({"role": "user", "content": message.text})

        request = {
            "model": self.config.model or "default",
            "messages": messages,
        }

        # 添加工具
        if tools:
            request["tools"] = tools

        return request

    async def _call_agent_api(self, request_data: Dict[str, Any]) -> str:
        """
        调用 Agent API

        Args:
            request_data: 请求数据

        Returns:
            响应文本
        """
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.base_url,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds),
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"API 错误 {resp.status}: {error_text}")

                    data = await resp.json()

                    # 解析响应
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
                    else:
                        raise Exception("API 响应格式错误")

        except aiohttp.ClientError as e:
            logger.error(f"网络请求失败: {e}")
            raise Exception(f"无法连接到 Agent 服务: {e}")
        except Exception as e:
            logger.error(f"API 调用失败: {e}")
            raise


# 全局 Agent 服务实例
agent_service = AgentService()

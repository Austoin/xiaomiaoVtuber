"""
桥接服务 - 桌面应用桥接和事件管理

整合自:
- desktop_bridge.py
- bridge_event_store.py
"""
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json

from cache_config import BRIDGE_EVENTS_FILE

logger = logging.getLogger(__name__)


@dataclass
class BridgeEvent:
    """桥接事件"""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: Optional[str] = None


class BridgeService:
    """桥接服务"""

    def __init__(self, event_store_path: Optional[Path] = None):
        """
        初始化桥接服务

        Args:
            event_store_path: 事件存储路径
        """
        if event_store_path is None:
            event_store_path = BRIDGE_EVENTS_FILE

        self.event_store_path = event_store_path
        self.event_store_path.parent.mkdir(parents=True, exist_ok=True)

        self._subscribers: Dict[str, List[Callable]] = {}
        self._state: Dict[str, Any] = {}

        logger.info(f"桥接服务初始化: {self.event_store_path}")

    async def publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
    ) -> None:
        """
        发布事件

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        event = BridgeEvent(type=event_type, data=data)

        # 存储事件
        self._store_event(event)

        # 通知订阅者
        await self._notify_subscribers(event)

        logger.debug(f"发布事件: {event_type}")

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[BridgeEvent], None],
    ) -> None:
        """
        订阅事件

        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(callback)
        logger.info(f"订阅事件: {event_type}")

    def get_state(self, key: str) -> Any:
        """获取状态"""
        return self._state.get(key)

    def set_state(self, key: str, value: Any) -> None:
        """设置状态"""
        self._state[key] = value
        logger.debug(f"设置状态: {key} = {value}")

    def sync_state(self, state: Dict[str, Any]) -> None:
        """同步状态"""
        self._state.update(state)
        logger.debug(f"同步状态: {len(state)} 个键")

    def get_recent_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[BridgeEvent]:
        """
        获取最近的事件

        Args:
            event_type: 事件类型筛选
            limit: 最大数量

        Returns:
            事件列表
        """
        if not self.event_store_path.exists():
            return []

        events = []
        try:
            with open(self.event_store_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue

                    event_data = json.loads(line)

                    # 类型筛选
                    if event_type and event_data.get('type') != event_type:
                        continue

                    event = BridgeEvent(
                        type=event_data['type'],
                        data=event_data['data'],
                        timestamp=datetime.fromisoformat(event_data['timestamp']),
                        event_id=event_data.get('event_id'),
                    )
                    events.append(event)

            # 返回最近的 N 个
            return events[-limit:]

        except Exception as e:
            logger.error(f"读取事件失败: {e}")
            return []

    def _store_event(self, event: BridgeEvent) -> None:
        """存储事件到文件"""
        try:
            with open(self.event_store_path, 'a', encoding='utf-8') as f:
                event_data = {
                    'type': event.type,
                    'data': event.data,
                    'timestamp': event.timestamp.isoformat(),
                    'event_id': event.event_id,
                }
                f.write(json.dumps(event_data, ensure_ascii=False) + '\n')

        except Exception as e:
            logger.error(f"存储事件失败: {e}")

    async def _notify_subscribers(self, event: BridgeEvent) -> None:
        """通知订阅者"""
        subscribers = self._subscribers.get(event.type, [])

        for callback in subscribers:
            try:
                # 如果是异步回调
                if hasattr(callback, '__call__'):
                    result = callback(event)
                    # 如果返回协程，await 它
                    if hasattr(result, '__await__'):
                        await result
            except Exception as e:
                logger.error(f"订阅者回调失败: {e}", exc_info=True)


# 全局桥接服务实例
bridge_service = BridgeService()

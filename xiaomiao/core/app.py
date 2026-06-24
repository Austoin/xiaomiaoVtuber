"""
xiaomiao 核心模块 - 应用配置和生命周期管理
"""
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class XiaomiaoApp:
    """xiaomiao 应用主类"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化应用

        Args:
            config_path: 配置文件路径，默认为 xiaomiao/config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.json"

        self.config_path = config_path
        self.config = None
        self._initialized = False
        self._bot_name = "小喵"
        self._bot_name_en = "XiaoMiao"

    def initialize(self) -> None:
        """初始化应用配置和日志"""
        if self._initialized:
            return

        # 尝试加载配置
        try:
            from Hyper import Configurator
            Configurator.cm = Configurator.ConfigManager(
                Configurator.Config(file=str(self.config_path)).load_from_file()
            )
            self.config = Configurator.cm.get_cfg()
            self._bot_name = self.config.others.get("bot_name", "小喵")
            self._bot_name_en = self.config.others.get("bot_name_en", "XiaoMiao")
            logger.info(f"配置加载成功: {self.config_path}")
        except Exception as e:
            logger.warning(f"配置加载失败，使用默认配置: {e}")

        self._initialized = True
        logger.info(f"xiaomiao 应用已初始化")

    @property
    def bot_name(self) -> str:
        """获取 Bot 名称"""
        return self._bot_name

    @property
    def bot_name_en(self) -> str:
        """获取 Bot 英文名称"""
        return self._bot_name_en

    @property
    def version(self) -> str:
        """获取版本号"""
        return "2.0"

    def shutdown(self) -> None:
        """关闭应用"""
        logger.info("xiaomiao 应用正在关闭...")
        self._initialized = False


# 全局应用实例
app = XiaomiaoApp()

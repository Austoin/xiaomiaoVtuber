"""角色管理器

支持多角色切换，每个角色有独立的人格、身份和记忆。

功能：
- 角色列表管理
- 角色切换
- 人格定义加载
- 记忆隔离

使用示例：
```python
from tool.xiaomiao.character_manager import CharacterManager

# 列出所有角色
characters = CharacterManager.list_characters()

# 加载角色
character = CharacterManager.load_character("natsume")
print(character["soul"])      # 人格定义
print(character["identity"])  # 身份定义

# 切换角色
CharacterManager.switch_character("atri")

# 获取当前角色
current = CharacterManager.get_current()
```
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# 角色目录
CHARACTERS_DIR = Path(__file__).parents[2] / "characters"
CONFIG_FILE = CHARACTERS_DIR / "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "current_character": "xiaomiao",
    "characters": {
        "xiaomiao": {
            "name": "小喵",
            "description": "默认 AI 助手",
            "enabled": True
        },
        "natsume": {
            "name": "四季夏目",
            "description": "高岭之花，外冷内热",
            "enabled": True
        },
        "atri": {
            "name": "亚托莉",
            "description": "元气天使，天真烂漫",
            "enabled": True
        }
    }
}


class CharacterManager:
    """角色管理器"""

    @staticmethod
    def _ensure_config():
        """确保配置文件存在"""
        if not CONFIG_FILE.exists():
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _load_config() -> dict:
        """加载配置"""
        CharacterManager._ensure_config()
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return DEFAULT_CONFIG.copy()

    @staticmethod
    def _save_config(config: dict):
        """保存配置"""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    @staticmethod
    def list_characters() -> list[dict]:
        """
        列出所有可用角色

        Returns:
            角色列表，每个角色包含 name, description, enabled, is_current
        """
        config = CharacterManager._load_config()
        current = config.get("current_character", "xiaomiao")

        characters = []
        for char_id, char_info in config.get("characters", {}).items():
            char_dir = CHARACTERS_DIR / char_id
            if not char_dir.exists():
                continue

            characters.append({
                "id": char_id,
                "name": char_info.get("name", char_id),
                "description": char_info.get("description", ""),
                "enabled": char_info.get("enabled", True),
                "is_current": char_id == current,
                "has_soul": (char_dir / "SOUL.md").exists(),
                "has_identity": (char_dir / "IDENTITY.md").exists(),
            })

        return characters

    @staticmethod
    def load_character(character_id: str) -> Optional[dict[str, Any]]:
        """
        加载指定角色的完整信息

        Args:
            character_id: 角色 ID

        Returns:
            {
                "id": str,
                "name": str,
                "description": str,
                "soul": str,          # SOUL.md 内容
                "identity": str,      # IDENTITY.md 内容
                "memory_dir": str     # 记忆目录路径
            }
        """
        char_dir = CHARACTERS_DIR / character_id
        if not char_dir.exists():
            logger.error(f"角色不存在: {character_id}")
            return None

        config = CharacterManager._load_config()
        char_info = config.get("characters", {}).get(character_id, {})

        # 读取 SOUL.md
        soul_file = char_dir / "SOUL.md"
        soul = ""
        if soul_file.exists():
            try:
                with open(soul_file, "r", encoding="utf-8") as f:
                    soul = f.read()
            except Exception as e:
                logger.error(f"读取 SOUL.md 失败: {e}")

        # 读取 IDENTITY.md
        identity_file = char_dir / "IDENTITY.md"
        identity = ""
        if identity_file.exists():
            try:
                with open(identity_file, "r", encoding="utf-8") as f:
                    identity = f.read()
            except Exception as e:
                logger.error(f"读取 IDENTITY.md 失败: {e}")

        # 记忆目录
        memory_dir = char_dir / "memory"
        memory_dir.mkdir(exist_ok=True)

        return {
            "id": character_id,
            "name": char_info.get("name", character_id),
            "description": char_info.get("description", ""),
            "soul": soul,
            "identity": identity,
            "memory_dir": str(memory_dir),
        }

    @staticmethod
    def switch_character(character_id: str) -> bool:
        """
        切换到指定角色

        Args:
            character_id: 角色 ID

        Returns:
            是否切换成功
        """
        # 检查角色是否存在
        character = CharacterManager.load_character(character_id)
        if not character:
            logger.error(f"切换失败：角色不存在 {character_id}")
            return False

        # 更新配置
        config = CharacterManager._load_config()
        config["current_character"] = character_id
        CharacterManager._save_config(config)

        logger.info(f"已切换到角色: {character['name']} ({character_id})")
        return True

    @staticmethod
    def get_current() -> Optional[dict[str, Any]]:
        """
        获取当前激活的角色

        Returns:
            当前角色的完整信息，格式同 load_character
        """
        config = CharacterManager._load_config()
        current_id = config.get("current_character", "xiaomiao")
        return CharacterManager.load_character(current_id)

    @staticmethod
    def get_current_prompt() -> str:
        """
        获取当前角色的系统提示词

        将 IDENTITY 和 SOUL 合并为一个系统提示

        Returns:
            系统提示词文本
        """
        character = CharacterManager.get_current()
        if not character:
            return ""

        prompt_parts = []

        # 添加身份
        if character.get("identity"):
            prompt_parts.append("# 角色身份")
            prompt_parts.append(character["identity"])
            prompt_parts.append("")

        # 添加人格
        if character.get("soul"):
            prompt_parts.append("# 角色人格")
            prompt_parts.append(character["soul"])
            prompt_parts.append("")

        return "\n".join(prompt_parts)


__all__ = ["CharacterManager"]

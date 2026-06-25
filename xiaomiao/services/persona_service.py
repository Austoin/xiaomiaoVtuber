"""
人设服务

管理角色切换和人设配置
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PersonaService:
    """人设服务"""

    def __init__(self):
        self.runtime_dir = Path(__file__).resolve().parents[1] / "runtime"
        self.sisters_file = self.runtime_dir / "sisters.ini"
        self.jhq_file = self.runtime_dir / "jhq.ini"
        self.programmers_file = self.runtime_dir / "programmers.ini"

    def get_user_persona(self, user_id: int) -> str:
        """
        获取用户当前人设

        Args:
            user_id: 用户 ID

        Returns:
            人设类型: girlfriend, sister, mother, programmer
        """
        # 检查程序员模式(优先级最高)
        if self._is_in_file(user_id, self.programmers_file):
            return "programmer"

        # 检查姐姐模式
        if self._is_in_file(user_id, self.sisters_file):
            return "sister"

        # 检查妈妈模式
        if self._is_in_file(user_id, self.jhq_file):
            return "mother"

        # 默认女朋友模式
        return "girlfriend"

    def set_persona(self, user_id: int, persona: str) -> bool:
        """
        设置用户人设

        Args:
            user_id: 用户 ID
            persona: 人设类型

        Returns:
            是否成功
        """
        # 先从所有文件中移除
        self._remove_from_all_files(user_id)

        # 根据类型添加到对应文件
        if persona == "sister":
            return self._add_to_file(user_id, self.sisters_file)
        elif persona == "mother":
            return self._add_to_file(user_id, self.jhq_file)
        elif persona == "programmer":
            return self._add_to_file(user_id, self.programmers_file)
        elif persona == "girlfriend":
            # 女朋友模式是默认的,不需要写文件
            return True
        else:
            logger.warning(f"未知人设类型: {persona}")
            return False

    def _is_in_file(self, user_id: int, file_path: Path) -> bool:
        """检查用户是否在文件中"""
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() == str(user_id):
                        return True
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")

        return False

    def _add_to_file(self, user_id: int, file_path: Path) -> bool:
        """添加用户到文件"""
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 检查是否已存在
            if self._is_in_file(user_id, file_path):
                return True

            # 追加写入
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"{user_id}\n")

            logger.info(f"添加用户 {user_id} 到 {file_path.name}")
            return True

        except Exception as e:
            logger.error(f"写入文件失败 {file_path}: {e}")
            return False

    def _remove_from_file(self, user_id: int, file_path: Path) -> bool:
        """从文件中移除用户"""
        if not file_path.exists():
            return True

        try:
            # 读取所有行
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 过滤掉目标用户
            new_lines = [line for line in lines if line.strip() != str(user_id)]

            # 写回
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            logger.info(f"从 {file_path.name} 移除用户 {user_id}")
            return True

        except Exception as e:
            logger.error(f"修改文件失败 {file_path}: {e}")
            return False

    def _remove_from_all_files(self, user_id: int) -> None:
        """从所有人设文件中移除用户"""
        self._remove_from_file(user_id, self.sisters_file)
        self._remove_from_file(user_id, self.jhq_file)
        self._remove_from_file(user_id, self.programmers_file)


# 全局人设服务实例
persona_service = PersonaService()

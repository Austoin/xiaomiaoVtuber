"""
权限服务 - 统一的权限管理

整合自:
- qq_permissions.py
- 配置中的权限规则
"""
import logging
from typing import Set, Iterable, Optional, List
from enum import Enum
from dataclasses import dataclass

try:
    from ..models import User
except ImportError:
    from models import User

logger = logging.getLogger(__name__)


class Role(Enum):
    """用户角色"""
    GUEST = "guest"      # 访客（黑名单或未知用户）
    USER = "user"        # 普通用户
    TRUSTED = "trusted"  # 可信用户（白名单）
    ADMIN = "admin"      # 管理员
    SUPER = "super"      # 超级管理员
    ROOT = "root"        # 根用户


class Permission(Enum):
    """权限类型"""
    # 基础权限
    CHAT = "chat"                    # 聊天
    VIEW = "view"                    # 查看信息

    # 工具权限
    TOOL_SEARCH = "tool_search"      # 搜索工具
    TOOL_FILE = "tool_file"          # 文件工具
    TOOL_IMAGE = "tool_image"        # 图片工具
    TOOL_WEB = "tool_web"            # 网页工具
    TOOL_SYSTEM = "tool_system"      # 系统工具（高风险）

    # 管理权限
    MANAGE_USER = "manage_user"      # 用户管理
    MANAGE_CONFIG = "manage_config"  # 配置管理
    MANAGE_DATA = "manage_data"      # 数据管理


@dataclass
class PermissionConfig:
    """权限配置"""
    root_user: Optional[str] = None              # ROOT 用户（单个）
    super_users: List[str] = None                # Super 用户列表
    agent_tool_allowlist: List[str] = None       # 工具白名单
    owner: List[str] = None                      # Owner 列表
    black_list: List[str] = None                 # 黑名单

    def __post_init__(self):
        """初始化默认值"""
        if self.super_users is None:
            self.super_users = []
        if self.agent_tool_allowlist is None:
            self.agent_tool_allowlist = []
        if self.owner is None:
            self.owner = []
        if self.black_list is None:
            self.black_list = []


class PermissionService:
    """权限服务"""

    # 角色层级（数字越大权限越高）
    ROLE_LEVELS = {
        Role.GUEST: 0,
        Role.USER: 10,
        Role.TRUSTED: 20,
        Role.ADMIN: 30,
        Role.SUPER: 40,
        Role.ROOT: 50,
    }

    # 角色默认权限
    ROLE_PERMISSIONS = {
        Role.GUEST: {Permission.VIEW},
        Role.USER: {
            Permission.CHAT,
            Permission.VIEW,
            Permission.TOOL_SEARCH,
        },
        Role.TRUSTED: {
            Permission.CHAT,
            Permission.VIEW,
            Permission.TOOL_SEARCH,
            Permission.TOOL_FILE,
            Permission.TOOL_IMAGE,
            Permission.TOOL_WEB,
        },
        Role.ADMIN: {
            Permission.CHAT,
            Permission.VIEW,
            Permission.TOOL_SEARCH,
            Permission.TOOL_FILE,
            Permission.TOOL_IMAGE,
            Permission.TOOL_WEB,
            Permission.MANAGE_USER,
        },
        Role.SUPER: {
            Permission.CHAT,
            Permission.VIEW,
            Permission.TOOL_SEARCH,
            Permission.TOOL_FILE,
            Permission.TOOL_IMAGE,
            Permission.TOOL_WEB,
            Permission.TOOL_SYSTEM,
            Permission.MANAGE_USER,
            Permission.MANAGE_CONFIG,
        },
        Role.ROOT: set(Permission),  # 所有权限
    }

    def __init__(self, config: Optional[PermissionConfig] = None):
        """
        初始化权限服务

        Args:
            config: 权限配置
        """
        self.config = config or PermissionConfig()
        logger.info("权限服务初始化")

    def get_user_role(self, user_id: int | str) -> Role:
        """
        获取用户角色

        Args:
            user_id: 用户 ID

        Returns:
            用户角色
        """
        user_id_str = str(user_id).strip()

        # 检查黑名单
        if user_id_str in self._normalize_ids(self.config.black_list):
            return Role.GUEST

        # 检查 ROOT
        if self.config.root_user and user_id_str == str(self.config.root_user).strip():
            return Role.ROOT

        # 检查 Super
        if user_id_str in self._normalize_ids(self.config.super_users):
            return Role.SUPER

        # 检查 Owner/Admin
        if user_id_str in self._normalize_ids(self.config.owner):
            return Role.ADMIN

        # 检查白名单
        if user_id_str in self._normalize_ids(self.config.agent_tool_allowlist):
            return Role.TRUSTED

        # 默认普通用户
        return Role.USER

    def check_permission(
        self,
        user_id: int | str,
        permission: Permission,
    ) -> bool:
        """
        检查用户是否有指定权限

        Args:
            user_id: 用户 ID
            permission: 权限

        Returns:
            是否有权限
        """
        role = self.get_user_role(user_id)
        permissions = self.ROLE_PERMISSIONS.get(role, set())
        return permission in permissions

    def has_tool_access(self, user_id: int | str) -> bool:
        """检查用户是否可以使用工具"""
        role = self.get_user_role(user_id)
        return self.ROLE_LEVELS[role] >= self.ROLE_LEVELS[Role.TRUSTED]

    def is_admin(self, user_id: int | str) -> bool:
        """检查用户是否为管理员"""
        role = self.get_user_role(user_id)
        return self.ROLE_LEVELS[role] >= self.ROLE_LEVELS[Role.ADMIN]

    def is_super(self, user_id: int | str) -> bool:
        """检查用户是否为超级管理员"""
        role = self.get_user_role(user_id)
        return self.ROLE_LEVELS[role] >= self.ROLE_LEVELS[Role.SUPER]

    def is_root(self, user_id: int | str) -> bool:
        """检查用户是否为 ROOT"""
        return self.get_user_role(user_id) == Role.ROOT

    def can_use_high_risk_tools(self, user_id: int | str) -> bool:
        """检查用户是否可以使用高风险工具"""
        return self.check_permission(user_id, Permission.TOOL_SYSTEM)

    def list_user_permissions(self, user_id: int | str) -> Set[Permission]:
        """列出用户的所有权限"""
        role = self.get_user_role(user_id)
        return self.ROLE_PERMISSIONS.get(role, set())

    def _normalize_ids(self, user_ids: Iterable[int | str]) -> Set[str]:
        """标准化用户 ID"""
        if not user_ids:
            return set()
        return {str(user_id).strip() for user_id in user_ids if str(user_id).strip()}

    # 兼容旧接口
    def has_manage_permission(self, user_id: int | str) -> bool:
        """检查管理权限（兼容旧接口）"""
        return self.is_admin(user_id)

    def has_super_permission(self, user_id: int | str) -> bool:
        """检查超级权限（兼容旧接口）"""
        return self.is_super(user_id)

    def has_agent_tool_permission(self, user_id: int | str) -> bool:
        """检查工具权限（兼容旧接口）"""
        return self.has_tool_access(user_id)


# 全局权限服务实例
permission_service = PermissionService()

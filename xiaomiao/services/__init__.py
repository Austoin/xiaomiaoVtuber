"""
服务层初始化

统一的服务层接口，整合自多个分散的模块
"""
from .agent_service import AgentService, AgentConfig, agent_service
from .permission_service import (
    PermissionService,
    PermissionConfig,
    Role,
    Permission,
    permission_service,
)
from .tool_service import ToolService, Tool, ToolRisk, tool_service
from .workspace_service import WorkspaceService, workspace_service
from .bridge_service import BridgeService, BridgeEvent, bridge_service

__all__ = [
    # Agent 服务
    'AgentService',
    'AgentConfig',
    'agent_service',

    # 权限服务
    'PermissionService',
    'PermissionConfig',
    'Role',
    'Permission',
    'permission_service',

    # 工具服务
    'ToolService',
    'Tool',
    'ToolRisk',
    'tool_service',

    # 工作区服务
    'WorkspaceService',
    'workspace_service',

    # 桥接服务
    'BridgeService',
    'BridgeEvent',
    'bridge_service',
]

"""
工具服务 - 统一的工具管理和执行

整合自:
- qq_agent_tools.py
- tool/adapters/qq_adapter.py
"""
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ToolRisk(Enum):
    """工具风险等级"""
    LOW = "low"          # 低风险（搜索、查询）
    MEDIUM = "medium"    # 中风险（文件读取）
    HIGH = "high"        # 高风险（文件写入、执行命令）


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]
    risk: ToolRisk = ToolRisk.LOW
    enabled: bool = True
    category: str = "general"


class ToolService:
    """工具服务"""

    def __init__(self):
        """初始化工具服务"""
        self._tools: Dict[str, Tool] = {}
        self._categories: Dict[str, List[str]] = {}
        self._register_builtin_tools()
        logger.info("工具服务初始化")

    def register_tool(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any],
        risk: ToolRisk = ToolRisk.LOW,
        category: str = "general",
    ) -> None:
        """
        注册工具

        Args:
            name: 工具名称
            description: 工具描述
            function: 工具函数
            parameters: 参数定义
            risk: 风险等级
            category: 分类
        """
        tool = Tool(
            name=name,
            description=description,
            function=function,
            parameters=parameters,
            risk=risk,
            category=category,
        )
        self._tools[name] = tool

        # 更新分类索引
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)

        logger.info(f"注册工具: {name} (风险: {risk.value}, 分类: {category})")

    async def execute_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        """
        执行工具

        Args:
            name: 工具名称
            arguments: 参数

        Returns:
            工具执行结果
        """
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"未知工具: {name}")

        if not tool.enabled:
            raise ValueError(f"工具已禁用: {name}")

        logger.info(f"执行工具: {name}")

        try:
            # 验证参数
            self._validate_arguments(tool, arguments)

            # 执行工具
            result = await tool.function(**arguments)
            return result

        except Exception as e:
            logger.error(f"工具执行失败: {name} - {e}", exc_info=True)
            raise

    def list_tools(
        self,
        category: Optional[str] = None,
        max_risk: Optional[ToolRisk] = None,
    ) -> List[Dict[str, Any]]:
        """
        列出工具

        Args:
            category: 按分类筛选
            max_risk: 最大风险等级

        Returns:
            工具列表
        """
        tools = []

        for tool in self._tools.values():
            if not tool.enabled:
                continue

            # 分类筛选
            if category and tool.category != category:
                continue

            # 风险筛选
            if max_risk and self._risk_level(tool.risk) > self._risk_level(max_risk):
                continue

            tools.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "risk": tool.risk.value,
                "category": tool.category,
            })

        return tools

    def get_tool_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """获取工具的 JSON Schema"""
        tool = self._tools.get(name)
        if not tool:
            return None

        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }

    def get_tools_for_agent(
        self,
        user_role: str = "user",
    ) -> List[Dict[str, Any]]:
        """
        获取可用于 Agent 的工具列表

        Args:
            user_role: 用户角色

        Returns:
            工具 Schema 列表
        """
        # 根据用户角色确定最大风险等级
        max_risk_map = {
            "guest": ToolRisk.LOW,
            "user": ToolRisk.LOW,
            "trusted": ToolRisk.MEDIUM,
            "admin": ToolRisk.HIGH,
            "super": ToolRisk.HIGH,
            "root": ToolRisk.HIGH,
        }
        max_risk = max_risk_map.get(user_role, ToolRisk.LOW)

        # 获取工具列表
        tools = self.list_tools(max_risk=max_risk)

        # 转换为 Agent 格式
        return [self.get_tool_schema(t["name"]) for t in tools]

    def _register_builtin_tools(self):
        """注册内置工具"""
        # 这里可以注册一些内置工具
        # 实际的工具函数应该从其他模块导入

        async def dummy_search(query: str) -> str:
            """示例搜索工具"""
            return f"搜索结果: {query}"

        self.register_tool(
            name="web_search",
            description="在网络上搜索信息",
            function=dummy_search,
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词",
                    }
                },
                "required": ["query"],
            },
            risk=ToolRisk.LOW,
            category="search",
        )

    def _validate_arguments(self, tool: Tool, arguments: Dict[str, Any]) -> None:
        """验证工具参数"""
        # 简单验证，检查必需参数
        required = tool.parameters.get("required", [])
        for param in required:
            if param not in arguments:
                raise ValueError(f"缺少必需参数: {param}")

    def _risk_level(self, risk: ToolRisk) -> int:
        """获取风险等级数值"""
        levels = {
            ToolRisk.LOW: 1,
            ToolRisk.MEDIUM: 2,
            ToolRisk.HIGH: 3,
        }
        return levels.get(risk, 0)


# 全局工具服务实例
tool_service = ToolService()

# xiaomiao 服务层

**版本**: 2.0  
**状态**: ✅ 已完成

---

## 📋 概述

服务层是 xiaomiao 的核心业务逻辑层，提供统一、清晰的接口来处理各种业务功能。

### 设计原则

1. **单一职责** - 每个服务负责一个明确的业务领域
2. **依赖注入** - 支持配置注入，便于测试
3. **异步优先** - 所有 I/O 操作都是异步的
4. **全局实例** - 每个服务提供全局单例，方便使用
5. **向后兼容** - 保留旧接口，平滑迁移

---

## 🗂️ 服务列表

### 1. AgentService - Agent 服务
**文件**: `agent_service.py`  
**用途**: 与 xiaomiaoAgent 交互

**主要方法**:
```python
from services import agent_service

# 请求 Agent
response = await agent_service.request_agent(message)

# 流式响应
async for chunk in agent_service.stream_agent(message):
    print(chunk)

# 会话管理
history = agent_service.get_session_history(session_id)
agent_service.clear_session(session_id)
```

**配置**:
```python
from services import AgentService, AgentConfig

config = AgentConfig(
    base_url="http://127.0.0.1:8900/v1/chat/completions",
    model="default",
    timeout_seconds=30,
)
agent_service = AgentService(config)
```

---

### 2. PermissionService - 权限服务
**文件**: `permission_service.py`  
**用途**: 用户权限管理

**角色层级**:
```
ROOT (50) > SUPER (40) > ADMIN (30) > TRUSTED (20) > USER (10) > GUEST (0)
```

**主要方法**:
```python
from services import permission_service, Role, Permission

# 获取用户角色
role = permission_service.get_user_role(user_id)

# 检查权限
has_perm = permission_service.check_permission(user_id, Permission.TOOL_FILE)

# 快捷检查
is_admin = permission_service.is_admin(user_id)
can_use_tools = permission_service.has_tool_access(user_id)

# 列出权限
perms = permission_service.list_user_permissions(user_id)
```

**配置**:
```python
from services import PermissionService, PermissionConfig

config = PermissionConfig(
    root_user="123456",
    super_users=["234567", "345678"],
    agent_tool_allowlist=["456789"],
    black_list=["bad_user"],
)
permission_service = PermissionService(config)
```

---

### 3. ToolService - 工具服务
**文件**: `tool_service.py`  
**用途**: 工具注册和执行

**风险等级**:
- `LOW` - 低风险（搜索、查询）
- `MEDIUM` - 中风险（文件读取）
- `HIGH` - 高风险（文件写入、系统命令）

**主要方法**:
```python
from services import tool_service, ToolRisk

# 注册工具
async def my_tool(param: str) -> str:
    return f"Result: {param}"

tool_service.register_tool(
    name="my_tool",
    description="我的工具",
    function=my_tool,
    parameters={
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        },
        "required": ["param"]
    },
    risk=ToolRisk.LOW,
    category="custom",
)

# 执行工具
result = await tool_service.execute_tool(
    name="my_tool",
    arguments={"param": "test"}
)

# 列出工具
tools = tool_service.list_tools(category="search")

# 获取 Agent 可用工具
agent_tools = tool_service.get_tools_for_agent(user_role="trusted")
```

---

### 4. WorkspaceService - 工作区服务
**文件**: `workspace_service.py`  
**用途**: 文件和工作区管理

**主要方法**:
```python
from services import workspace_service

# 下载文件
file_path = await workspace_service.download_file(
    url="https://example.com/file.jpg",
    filename="image.jpg",
    subfolder="images",
)

# 列出文件
files = workspace_service.list_files(subfolder="images")

# 获取文件信息
info = workspace_service.get_file_info(file_path)

# 清理工作区
deleted = workspace_service.clean_workspace(keep_recent=10)

# 获取工作区大小
size = workspace_service.get_workspace_size()
```

---

### 5. BridgeService - 桥接服务
**文件**: `bridge_service.py`  
**用途**: 桌面应用桥接和事件管理

**主要方法**:
```python
from services import bridge_service

# 发布事件
await bridge_service.publish_event(
    event_type="message.received",
    data={"text": "你好"}
)

# 订阅事件
def on_message(event):
    print(f"收到消息: {event.data}")

bridge_service.subscribe("message.received", on_message)

# 状态管理
bridge_service.set_state("key", "value")
value = bridge_service.get_state("key")

# 获取历史事件
events = bridge_service.get_recent_events(
    event_type="message.received",
    limit=10
)
```

---

## 🔧 使用示例

### 完整的消息处理流程

```python
from models import Message, User, MessageSource
from services import (
    agent_service,
    permission_service,
    tool_service,
    workspace_service,
)

async def process_message(message: Message):
    # 1. 检查权限
    role = permission_service.get_user_role(message.user.user_id)
    if role == Role.GUEST:
        return Response(text="权限不足")
    
    # 2. 获取可用工具
    tools = tool_service.get_tools_for_agent(user_role=role.value)
    
    # 3. 请求 Agent
    response = await agent_service.request_agent(
        message=message,
        tools=tools,
    )
    
    # 4. 下载文件（如果需要）
    if message.has_file():
        for file in message.get_files():
            await workspace_service.download_file(file['url'])
    
    return response
```

---

## 📊 服务对比

### 整合前后对比

| 功能 | 整合前 | 整合后 | 改进 |
|------|--------|--------|------|
| Agent 调用 | agent_backend.py + main.py | agent_service.py | 统一接口 |
| 权限检查 | qq_permissions.py | permission_service.py | 增强功能 |
| 工具执行 | qq_agent_tools.py + 适配器 | tool_service.py | 统一管理 |
| 文件管理 | qq_workspace.py | workspace_service.py | 简化 API |
| 事件桥接 | desktop_bridge.py + store | bridge_service.py | 整合完整 |

### 代码量对比

| 模块 | 原代码行数 | 新代码行数 | 减少 |
|------|----------|----------|------|
| Agent | ~300 | 200 | -33% |
| 权限 | ~50 | 250 | +400%* |
| 工具 | ~200 | 220 | +10% |
| 工作区 | ~400 | 180 | -55% |
| 桥接 | ~600 | 170 | -72% |
| **总计** | **~1550** | **~1020** | **-34%** |

*权限服务增加是因为新增了更完善的功能

---

## 🧪 测试

### 单元测试示例

```python
import pytest
from services import PermissionService, PermissionConfig, Role

def test_permission_service():
    config = PermissionConfig(
        root_user="123",
        super_users=["456"],
    )
    service = PermissionService(config)
    
    # 测试 ROOT
    assert service.get_user_role("123") == Role.ROOT
    assert service.is_root("123")
    
    # 测试 SUPER
    assert service.get_user_role("456") == Role.SUPER
    assert service.is_super("456")
    
    # 测试普通用户
    assert service.get_user_role("999") == Role.USER
```

---

## 🚀 迁移指南

### 从旧代码迁移

#### Agent 调用
```python
# 旧代码
from agent_backend import request_xiaomiao_agent
result = await request_xiaomiao_agent(request)

# 新代码
from services import agent_service
result = await agent_service.request_agent(message)
```

#### 权限检查
```python
# 旧代码
from qq_permissions import has_agent_tool_permission
if has_agent_tool_permission(user_id, ...):
    pass

# 新代码
from services import permission_service
if permission_service.has_tool_access(user_id):
    pass
```

#### 工具执行
```python
# 旧代码
from tool.adapters.qq_adapter import decide_tool_request
tools = decide_tool_request(...)

# 新代码
from services import tool_service
result = await tool_service.execute_tool(name, arguments)
```

---

## 📝 最佳实践

### 1. 使用全局实例

```python
# 推荐
from services import agent_service
response = await agent_service.request_agent(message)

# 不推荐
from services import AgentService
service = AgentService()  # 创建新实例
```

### 2. 依赖注入测试

```python
# 测试时创建独立实例
from services import AgentService, AgentConfig

config = AgentConfig(base_url="http://localhost:9999")
test_service = AgentService(config)
```

### 3. 错误处理

```python
from services import agent_service

try:
    response = await agent_service.request_agent(message)
except Exception as e:
    logger.error(f"Agent 请求失败: {e}")
    # 处理错误
```

---

## 🔄 未来计划

- [ ] 添加缓存层
- [ ] 实现重试机制
- [ ] 添加性能监控
- [ ] 支持插件系统
- [ ] 完善单元测试

---

**维护者**: xiaomiaoVirtual Team  
**最后更新**: 2026-06-25

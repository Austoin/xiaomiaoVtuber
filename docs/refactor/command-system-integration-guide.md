# xiaomiao 命令系统集成指南

## 概述

本指南演示如何将新的命令系统集成到现有的 `main.py` 中,实现双轨运行。

## 集成步骤

### 步骤 1: 在 main.py 中导入命令系统

```python
# main.py 顶部添加导入

# 导入命令系统
from commands import command_registry, list_all_commands
from handlers.command_dispatcher import command_dispatcher

# 导入命令模块(会自动注册)
import commands.basic  # ping, 帮助, 关于

# 启动时打印已注册命令
print(f"已注册命令: {list_all_commands()}")
```

### 步骤 2: 在消息处理函数中集成命令分发

找到现有的 `handler` 函数,在 AI 对话处理之前添加命令分发:

```python
async def handler(event: Events.Event, actions: Listener.Actions) -> None:
    """消息处理入口"""
    
    # ... 现有的前置检查 (黑名单、静默列表等) ...
    
    # 提取消息信息
    user_id = event.user_id
    user_name = event.sender.card or event.sender.nickname
    message_id = event.message_id
    message_text = event.message.to_str()
    chat_id = str(event.group_id) if hasattr(event, 'group_id') else str(event.user_id)
    chat_type = 'group' if hasattr(event, 'group_id') else 'private'
    
    # ============ 新增: 尝试命令分发 ============
    try:
        result = await command_dispatcher.dispatch(
            user_id=user_id,
            user_name=user_name,
            message_id=message_id,
            message_text=message_text,
            chat_id=chat_id,
            chat_type=chat_type,
            # 可选参数
            reply_to=event.reply if hasattr(event, 'reply') else None,
            at_users=[seg.data['qq'] for seg in event.message if seg.type == 'at'],
            images=[seg.data['url'] for seg in event.message if seg.type == 'image'],
        )
        
        if result is not None:
            # 是命令,已处理
            if result.success:
                # 发送成功响应
                await actions.send(result.message)
                
                # 如果有数据(如图片)
                if result.data and 'image' in result.data:
                    await actions.send(Segments.image(url=result.data['image']))
            else:
                # 发送错误响应
                await actions.send(result.error)
            
            return  # 命令已处理,不继续走 AI 流程
    
    except Exception as e:
        logger.error(f"命令分发异常: {e}", exc_info=True)
        # 继续走原有流程
    
    # ============ 命令分发结束 ============
    
    # ... 现有的 AI 对话处理逻辑 ...
```

### 步骤 3: 配置开关(可选)

如果想保留原有命令处理逻辑,可以添加配置开关:

```python
# config.json 添加
{
    "Others": {
        "use_new_command_system": true
    }
}
```

```python
# main.py 中
USE_NEW_COMMANDS = config.others.get("use_new_command_system", False)

async def handler(event: Events.Event, actions: Listener.Actions) -> None:
    # ...
    
    if USE_NEW_COMMANDS:
        # 使用新命令系统
        result = await command_dispatcher.dispatch(...)
        if result is not None:
            # 处理结果
            return
    
    # 继续原有逻辑
```

## 完整示例

```python
#!/bin/python
import faulthandler
faulthandler.enable()

import asyncio
# ... 其他导入 ...

# ========== 新增: 导入命令系统 ==========
from commands import command_registry, list_all_commands
from handlers.command_dispatcher import command_dispatcher
import commands.basic  # 自动注册基础命令

# 打印已注册命令
logger.info(f"命令系统已加载,共 {len(list_all_commands())} 个命令: {list_all_commands()}")
# ========================================

# ... 现有配置加载代码 ...

async def handler(event: Events.Event, actions: Listener.Actions) -> None:
    """消息处理入口"""
    
    # 1. 现有的前置检查
    if event.user_id in config.black_list:
        return
    
    if event.user_id in config.silents:
        return
    
    # 2. 提取消息信息
    user_id = event.user_id
    user_name = event.sender.card or event.sender.nickname
    message_id = event.message_id
    message_text = event.message.to_str()
    
    if hasattr(event, 'group_id'):
        chat_id = str(event.group_id)
        chat_type = 'group'
    else:
        chat_id = str(event.user_id)
        chat_type = 'private'
    
    # 3. 新命令系统处理
    try:
        result = await command_dispatcher.dispatch(
            user_id=user_id,
            user_name=user_name,
            message_id=message_id,
            message_text=message_text,
            chat_id=chat_id,
            chat_type=chat_type,
        )
        
        if result is not None:
            # 是命令
            logger.info(f"命令执行结果: {result.success}")
            
            if result.success:
                await actions.send(result.message)
                
                # 处理图片数据
                if result.data and 'image' in result.data:
                    await actions.send(Segments.image(url=result.data['image']))
            else:
                await actions.send(f"❌ {result.error}")
            
            return
    
    except Exception as e:
        logger.error(f"命令分发异常: {e}", exc_info=True)
    
    # 4. 原有的精确命令处理 (逐步废弃)
    if message_text == "- 读图":
        # ... 原有逻辑 ...
        return
    
    # 5. AI 对话处理
    # ... 原有 AI 处理逻辑 ...
```

## 迁移策略

### 阶段 1: 基础命令 (当前)

已迁移命令:
- ✅ ping
- ✅ 帮助
- ✅ 关于

保留在原 main.py:
- 其他所有命令

### 阶段 2: 图片命令 (下一步)

计划迁移:
- 生图
- 大头照
- 读图

### 阶段 3: 管理命令

计划迁移:
- 禁言
- 踢出
- 撤回

### 阶段 4: 系统命令

计划迁移:
- 重启
- 感知
- 注销
- 核验

## 验证步骤

### 1. 运行测试

```bash
cd test/xiaomiao
pytest test_commands.py -v
```

### 2. 启动机器人

```bash
python main.py
```

启动日志应包含:
```
命令系统已加载,共 3 个命令: ['ping', '关于', '帮助']
```

### 3. 测试命令

**私聊测试**:
- 发送: `ping`
- 预期: `pong! 🏓`

- 发送: `- 帮助`
- 预期: 显示命令列表

- 发送: `- 关于`
- 预期: 显示机器人信息

**群聊测试**:
- 同上

### 4. 验证向后兼容

- 发送: `- 读图` (未迁移命令)
- 预期: 原有逻辑仍正常工作

- 发送: `- 你好` (AI 对话)
- 预期: AI 正常回复

## 常见问题

### Q1: 命令没有响应

**检查**:
1. 启动日志是否显示命令已加载?
2. 命令前缀是否正确? (默认 `- `)
3. 日志中是否有异常?

### Q2: 权限不足

**检查**:
1. 用户是否在权限列表中?
2. 命令的权限要求是什么?
3. `permission_service` 是否正常工作?

### Q3: 冷却时间过长

**调整**:
```python
@command(
    name="生图",
    cooldown=10,  # 改为 10 秒
)
```

### Q4: 命令和原有逻辑冲突

**解决**:
1. 优先使用新命令系统
2. 只保留精确匹配的旧命令 (如 `读图`)
3. 逐步迁移后删除旧代码

## 下一步

1. 验证基础命令正常工作
2. 迁移图片命令 (`commands/image.py`)
3. 迁移 Agent 命令 (`commands/agent.py`)
4. 逐步移除 main.py 中的旧命令代码

## 注意事项

1. **不要急于删除旧代码** - 保持双轨运行一段时间
2. **充分测试** - 每个命令迁移后都要测试
3. **保持向后兼容** - 用户体验不应改变
4. **记录变更** - 在 git commit 中说明迁移了哪些命令

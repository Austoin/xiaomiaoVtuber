# 废弃代码说明

此目录包含已废弃的代码模块，这些模块的功能已被新架构取代。

---

## 📋 废弃文件列表

### 1. GoogleAI.py
**废弃原因**:
- 项目已使用统一的 Agent 系统
- 直接调用 Google AI 造成代码耦合
- 功能应该通过 services/agent_service.py 统一管理

**替代方案**:
```python
from services import agent_service

# 使用统一的 Agent 服务
response = await agent_service.request_agent(message)
```

---

### 2. SearchOnline.py
**废弃原因**:
- 搜索功能应该作为工具系统的一部分
- 独立的搜索模块造成功能分散
- 重复实现了工具系统已有的功能

**替代方案**:
```python
from services import tool_service

# 通过工具系统调用搜索
result = await tool_service.execute_tool(
    name="web_search",
    arguments={"query": "搜索内容"}
)
```

---

### 3. Quote.py
**废弃原因**:
- 引用处理应该是消息处理的一部分
- 功能过于简单，不需要独立模块
- 可能已集成到 models/message.py

**替代方案**:
```python
from models import Message

# 消息模型已包含引用处理
message = Message(...)
if message.reply_to:
    # 处理引用消息
    pass
```

---

## 🔄 迁移指南

如果你的代码仍在使用这些模块，请参考以下迁移步骤：

### 从 GoogleAI.py 迁移

**旧代码**:
```python
from GoogleAI import genai, Context

result = genai.generate(prompt)
```

**新代码**:
```python
from services import agent_service

response = await agent_service.request_agent(message)
```

### 从 SearchOnline.py 迁移

**旧代码**:
```python
from SearchOnline import search_online

results = search_online(query)
```

**新代码**:
```python
from services import tool_service

results = await tool_service.execute_tool(
    name="web_search",
    arguments={"query": query}
)
```

---

## ⚠️ 注意事项

1. **不要修改此目录的文件**
   - 这些文件仅作为参考保留
   - 未来版本可能完全删除

2. **不要在新代码中引用**
   - 使用新架构的对应功能
   - 参考上面的迁移指南

3. **计划删除时间**
   - 2026-07-25 后可能删除
   - 确保所有功能已迁移

---

## 📚 相关文档

- [代码整合分析](../docs/CODE_CONSOLIDATION_ANALYSIS.md)
- [重构进度](../docs/REFACTORING_PROGRESS.md)
- [服务层文档](../services/README.md)

---

**最后更新**: 2026-06-25

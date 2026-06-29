# xiaomiao 模块化重构计划

## 目标

将 3,342 行的 main.py 拆解为职责清晰、易于测试和维护的模块化架构。

## 原则

1. **单一职责**: 每个模块只负责一个明确的功能领域
2. **向后兼容**: 保持现有 API 和行为不变
3. **渐进式**: 逐步迁移,每步都可独立测试
4. **可测试性**: 优先纯函数,减少副作用

## 当前问题

- main.py: 3,342 行,27 个函数/类
- 职责混杂: 消息路由、命令处理、图片处理、AI 对话、权限管理等
- 难以测试: 大量全局状态和副作用
- 难以扩展: 添加新命令需要修改核心文件

## 目标架构

```
xiaomiao/
├── main.py                    # 启动入口 (~50 行)
├── app.py                     # 应用配置和生命周期 (~100 行)
│
├── core/
│   ├── bot.py                 # Bot 核心类
│   └── event_dispatcher.py    # 事件分发器
│
├── handlers/
│   ├── message_handler.py     # 消息处理主入口
│   ├── command_dispatcher.py  # 命令分发器
│   └── ai_handler.py          # AI 对话处理
│
├── commands/                  # 命令模块
│   ├── base.py               # 命令基类和装饰器
│   ├── basic.py              # ping, 帮助, 关于
│   ├── ai.py                 # AI 对话命令
│   ├── agent.py              # Agent 记忆命令
│   ├── image.py              # 生图, 大头照, 读图
│   ├── persona.py            # 角色切换
│   ├── admin.py              # 群管理命令
│   └── system.py             # 系统命令
│
├── services/
│   ├── agent_service.py      # Agent 后端调用
│   ├── bridge_service.py     # 桥接服务
│   ├── image_service.py      # 图片生成/处理
│   ├── persona_service.py    # 人设管理
│   ├── timing_service.py     # 定时消息
│   └── permission_service.py # 权限管理
│
├── models/
│   ├── message.py            # 消息模型
│   └── context.py            # 上下文模型
│
└── utils/
    ├── cooldown.py           # 冷却管理
    ├── system_info.py        # 系统信息
    ├── image_utils.py        # 图片工具
    └── text_utils.py         # 文本工具
```

## 迁移步骤

### 阶段 1: 基础设施 (第 1-2 天)

**目标**: 创建命令系统基础设施

1. 创建 `commands/base.py` - 命令基类和注册机制
2. 创建 `commands/registry.py` - 命令注册表
3. 创建 `handlers/command_dispatcher.py` - 命令分发器
4. 编写测试

**产出**:
- 命令注册和分发机制
- 向后兼容的命令接口
- 单元测试覆盖

### 阶段 2: 工具函数提取 (第 3-4 天)

**目标**: 提取可独立测试的工具函数

1. 创建 `utils/cooldown.py` - 冷却管理
2. 创建 `utils/system_info.py` - 系统信息
3. 创建 `utils/image_utils.py` - 图片工具
4. 创建 `utils/text_utils.py` - 文本工具
5. 编写测试

**产出**:
- 纯函数工具集
- 100% 单元测试覆盖

### 阶段 3: 服务层构建 (第 5-7 天)

**目标**: 封装业务逻辑到服务层

1. 完善 `services/image_service.py` - 图片服务
2. 创建 `services/persona_service.py` - 人设服务
3. 创建 `services/timing_service.py` - 定时服务
4. 编写测试

**产出**:
- 高内聚的服务模块
- 集成测试

### 阶段 4: 命令迁移 (第 8-12 天)

**目标**: 逐步迁移命令到新系统

**批次 1: 基础命令**
- `commands/basic.py`: ping, 帮助, 关于

**批次 2: AI 命令**
- `commands/ai.py`: AI 对话相关

**批次 3: Agent 命令**
- `commands/agent.py`: 记忆状态, 整理记忆等

**批次 4: 图片命令**
- `commands/image.py`: 生图, 大头照, 读图

**批次 5: 角色命令**
- `commands/persona.py`: 当我女朋友, 做我姐姐吧等

**批次 6: 管理命令**
- `commands/admin.py`: 禁言, 踢出, 撤回

**批次 7: 系统命令**
- `commands/system.py`: 重启, 感知, 注销等

**产出**:
- 每个命令独立文件
- 命令测试覆盖

### 阶段 5: 核心重构 (第 13-15 天)

**目标**: 重构核心消息处理流程

1. 创建 `core/bot.py` - Bot 核心类
2. 创建 `core/event_dispatcher.py` - 事件分发器
3. 创建 `handlers/message_handler.py` - 消息处理主入口
4. 创建 `handlers/ai_handler.py` - AI 对话处理
5. 重写 `main.py` - 简化为启动入口

**产出**:
- 清晰的消息处理流程
- main.py 缩减到 ~50 行

### 阶段 6: 测试和优化 (第 16-18 天)

**目标**: 全面测试和性能优化

1. 回归测试
2. 性能测试
3. 文档更新
4. 清理废弃代码

## 风险控制

1. **双轨运行**: 新旧代码并存,通过开关切换
2. **增量测试**: 每个阶段独立测试
3. **回滚机制**: 保留 main.py.backup
4. **监控**: 错误率、响应时间监控

## 验证标准

- [ ] 所有现有测试通过
- [ ] 新增测试覆盖率 > 80%
- [ ] 响应时间无明显增加
- [ ] 内存占用无明显增加
- [ ] 代码行数减少 > 30%
- [ ] 圈复杂度降低 > 50%

## 里程碑

- **M1 (Day 7)**: 基础设施 + 工具函数 + 服务层
- **M2 (Day 12)**: 所有命令迁移完成
- **M3 (Day 15)**: 核心重构完成
- **M4 (Day 18)**: 测试和文档完成,正式上线

## 后续优化

1. 异步化改造
2. 配置热重载
3. 插件系统
4. 性能监控

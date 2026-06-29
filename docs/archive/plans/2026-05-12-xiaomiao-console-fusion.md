# 小喵 QQ Bot 控制台融合实施计划

> 状态提示：这是 2026-05-12 的历史计划文档。当前项目已在 2026-06-02 完成 `stage-web`、桌面 bridge、QQ 普通 AI 回复到 xiaomiaoAgent 的统一接入。当前启动方式以 `docs/getting-started/README.md`、`README.md` 和 `TECHNICAL.md` 为准。

> **给 Claude：** 需要使用 `superpowers:executing-plans` 子技能，按任务逐步实施本计划。

**目标：** 在 AuBot Electron 桌面端中新增“小喵 QQ Bot 控制台”，用于只读展示 QQ 机器人状态、桥接状态、最近事件、基础运行信息，并为后续接入 xiaomiaoAgent WebUI/工具/记忆能力预留演进路径。

**架构：** 当前项目有 NapCat WebUI、AuBot Dashboard/Settings、小喵桥接模块和独立的 xiaomiaoAgent 框架。本计划先在 `xiaomiao/desktop_bridge.py` 增加只读状态/事件接口，再在 `AuBot/apps/stage-tamagotchi` 新增控制台页面消费这些接口。xiaomiaoAgent 融合采用后续阶段推进：先只读监控，再能力复用，再统一通道和事件。

**技术栈：** Python `ThreadingHTTPServer`、Hyper Bot、NapCat OneBot、Electron、Vue 3、TypeScript、Pinia、Vitest、unittest。

---

## 背景

当前融合链路已经打通：`xiaomiao` 暴露本地 OpenAI 兼容桥接接口，AuBot 读取回复并驱动字幕、聊天历史、TTS 和 Live2D 口型。

但当前没有“小喵 QQ Bot 专用控制台”。现有入口分别是 NapCat WebUI、AuBot Dashboard/Settings 和小喵桥接模块。缺失的是一个面向小喵机器人的桌面控制台，用于可视化 QQ Bot 运行状态、桥接健康和最近消息。

仓库中还包含 `nanobot`，它是轻量 Python Agent 框架，具备 Agent Loop、多平台 Channels、工具调用、MCP、Cron、记忆、Session、OpenAI 兼容 API 和 WebUI。它不应在第一阶段直接替换 `xiaomiao`，而应作为后续能力层逐步接入。

## 非目标

第一版只做只读控制台，明确不做：

- 不执行任意系统命令。
- 不显示 API Key 明文。
- 不开放公网控制能力。
- 不替代完整 NapCat WebUI。
- 不把所有小喵命令搬进 AuBot。
- 不直接开放 xiaomiaoAgent 的 Shell、文件系统、MCP 等高危工具给 QQ 用户或公网入口。
- 不在第一阶段把 QQ 接入强制迁移到 xiaomiaoAgent Channel。

## 目标体验

第一版控制台回答四个问题：

1. 小喵是否在线？
2. 桥接服务是否可用？
3. 最近 QQ 消息和小喵回复是什么？
4. 当前机器人使用哪个模型、端口和绑定用户？
5. 后续 xiaomiaoAgent gateway/WebUI/Agent 是否可作为扩展能力接入？

建议入口：

```text
AuBot Electron
└── Dashboard 或 Settings
    └── XiaoMiao Console
```

## 任务 1：桥接状态接口

**文件：**

- 修改：`xiaomiao/desktop_bridge.py`
- 测试：`xiaomiao/test_desktop_bridge.py`

**步骤 1：编写失败测试**

新增测试：`GET /v1/xiaomiao/status` 返回桥接状态。

```json
{
  "ok": true,
  "service": "xiaomiao-desktop-bridge",
  "model": "deepseek-chat",
  "default_user_id": 3554978979
}
```

**步骤 2：运行测试确认失败**

```powershell
cd xiaomiao
python -m unittest test_desktop_bridge.py
```

预期：FAIL，因为 `/v1/xiaomiao/status` 尚不存在。

**步骤 3：实现最小接口**

在 `desktop_bridge.py` 的 `do_GET()` 中增加只读状态路由。不要引入鉴权、持久化或管理动作。

**步骤 4：运行测试确认通过**

```powershell
cd xiaomiao
python -m unittest test_desktop_bridge.py
```

预期：PASS。

## 任务 2：最近事件接口

**文件：**

- 修改：`xiaomiao/desktop_bridge.py`
- 修改：`xiaomiao/main.py`
- 测试：`xiaomiao/test_desktop_bridge.py`

**步骤 1：编写失败测试**

新增测试：`GET /v1/xiaomiao/events` 返回最近事件数组。

```json
{
  "id": "evt-...",
  "type": "assistant_reply",
  "user_id": 3554978979,
  "group_id": 0,
  "text": "你好",
  "timestamp": 1777425310
}
```

**步骤 2：运行测试确认失败**

```powershell
cd xiaomiao
python -m unittest test_desktop_bridge.py
```

预期：FAIL，因为事件接口尚不存在。

**步骤 3：实现内存事件缓冲区**

在 `desktop_bridge.py` 增加内存事件队列，最大保留 50 条。`publish_desktop_state()` 同步写入最近回复事件。

**步骤 4：接入 QQ 回复发布**

保留 `main.py` 现有 `publish_desktop_state(event.user_id, result)` 调用。若需要群号，扩展函数签名时必须同步更新测试。

**步骤 5：运行测试确认通过**

```powershell
cd xiaomiao
python -m unittest test_desktop_bridge.py
```

预期：PASS。

## 任务 3：AuBot 控制台 API 模块

**文件：**

- 新增：`AuBot/apps/stage-tamagotchi/src/renderer/pages/xiaomiao-console-api.ts`
- 测试：`AuBot/apps/stage-tamagotchi/src/renderer/pages/xiaomiao-console-api.test.ts`

**步骤 1：编写失败测试**

覆盖三种情况：成功读取状态、成功读取事件、桥接不可用时返回明确错误状态。

**步骤 2：运行测试确认失败**

```powershell
cd AuBot
pnpm exec vitest run apps/stage-tamagotchi/src/renderer/pages/xiaomiao-console-api.test.ts
```

预期：FAIL，因为模块尚不存在。

**步骤 3：实现最小 API 封装**

实现 `readXiaomiaoStatus(fetcher)` 和 `readXiaomiaoEvents(fetcher)`。默认桥接地址继续复用 `http://127.0.0.1:5519`，不要在本任务新增设置系统。

**步骤 4：运行测试确认通过**

```powershell
cd AuBot
pnpm exec vitest run apps/stage-tamagotchi/src/renderer/pages/xiaomiao-console-api.test.ts
```

预期：PASS。

## 任务 4：XiaoMiao Console 页面

**文件：**

- 新增：`AuBot/apps/stage-tamagotchi/src/renderer/pages/xiaomiao-console.vue`
- 修改：仅在路由工具生成或要求时修改 `AuBot/apps/stage-tamagotchi/src/renderer/typed-router.d.ts`

**步骤 1：构建最小页面**

页面第一版只读展示：桥接状态、当前模型、默认绑定用户、最近事件列表、最近一次助手回复。

**步骤 2：增加轮询**

页面挂载后每 2 秒读取一次状态和事件。卸载时清理定时器。

**步骤 3：处理桥接不可用**

桥接不可用时显示“未连接到小喵桥接服务”，不要弹异常或阻塞其他页面。

**步骤 4：手动冒烟检查**

```powershell
cd AuBot
pnpm dev:tamagotchi
```

预期：Electron 可以打开新页面，桥接不可用时页面稳定显示离线状态。

## 任务 5：入口导航

**文件：**

- 修改：`AuBot/apps/stage-tamagotchi/src/renderer/layouts/settings.vue`
- 或修改：`AuBot/apps/stage-tamagotchi/src/renderer/pages/dashboard/index.vue`

**步骤 1：选择入口位置**

优先放在 Dashboard。如果现有 Dashboard 结构不适合，再放到 Settings 的开发/集成区域。

**步骤 2：增加导航项**

文案建议：`小喵控制台` / `XiaoMiao Console`。

**步骤 3：验证路由可用**

```powershell
cd AuBot
pnpm dev:tamagotchi
```

预期：可以从入口打开小喵控制台页面。

## 任务 6：文档更新

**文件：**

- 修改：`README.md`
- 修改：`TECHNICAL.md`
- 如实现细节变化，修改：`docs/archive/plans/2026-05-12-xiaomiao-console-fusion.md`

**步骤 1：更新 README**

在主目录 `README.md` 中补充“小喵控制台”入口说明。

**步骤 2：更新 TECHNICAL**

在 `TECHNICAL.md` 中将“当前没有小喵专用控制台”更新为“已规划/已实现控制台”，并说明接口。

**步骤 3：验证文档可读性**

确认 `TECHNICAL.md` 结构清晰，章节边界明确。当前不限制行数，优先保证 nanobot 融合背景、边界和路线完整。

## 任务 7：nanobot 只读接入规划

**文件：**

- 修改：`README.md`
- 修改：`TECHNICAL.md`
- 修改：`docs/archive/plans/2026-05-12-xiaomiao-console-fusion.md`

**步骤 1：说明 xiaomiaoAgent 角色**

在项目文档中明确 xiaomiaoAgent 是后续 Agent 能力层，不是第一阶段直接替换 `xiaomiao` 的实现。`nanobot` 作为内部代码包名保留。

**步骤 2：定义只读接入目标**

规划小喵控制台后续展示 xiaomiaoAgent 状态：

```text
xiaomiao gateway status
xiaomiaoAgent WebUI status
active channels
active sessions
recent agent events
tool availability summary
```

**步骤 3：隔离失败影响**

明确 xiaomiaoAgent 离线或未配置时，`xiaomiao` QQ Bot 和 AuBot Vtuber 主链路必须继续可用。

**步骤 4：避免高权限动作**

第一版只允许读取 xiaomiaoAgent 状态，不允许从 AuBot 控制台触发 Shell、文件写入、MCP、Cron 创建、Subagent 创建等动作。

## 任务 8：xiaomiaoAgent 能力复用路线

**文件：**

- 修改：任务 7 确认后的后续实施计划

**步骤 1：工具服务边界**

把 xiaomiaoAgent tools 作为受控内部能力层，而不是直接暴露给 QQ 消息。优先允许只读工具，例如 Web fetch/search、状态查询、文档读取。

**步骤 2：记忆/会话边界**

定义统一会话键：

```text
platform:qq:user:<qq_id>
platform:qq:group:<group_id>:user:<qq_id>
platform:webui:user:<local_user>
```

避免 `xiaomiao` 和 xiaomiaoAgent 对同一用户维护互相冲突的上下文。

**步骤 3：统一事件结构**

设计统一事件结构供 AuBot 消费：

```json
{
  "id": "evt-...",
  "source": "xiaomiao|xiaomiaoAgent",
  "type": "user_message|assistant_reply|tool_event|system_status",
  "session_id": "platform:qq:user:...",
  "text": "...",
  "timestamp": 1777425310
}
```

**步骤 4：渐进替换规则**

任何迁移都必须满足：

- 现有 `python main.py` 仍可独立启动。
- `pnpm dev:tamagotchi` 仍可只消费 `xiaomiao` 桥接。
- xiaomiaoAgent 离线时不影响 QQ 收发和 Vtuber 表现。
- 高危工具默认关闭，显式配置后才允许启用。

## xiaomiaoAgent 融合阶段建议

### 阶段 A：只读观测

目标：让 AuBot 控制台能展示 xiaomiaoAgent 是否运行、WebUI 是否可访问、gateway 是否在线。

不新增任何远程执行能力。

### 阶段 B：Agent 能力旁路调用

目标：`xiaomiao` 在特定命令或特定用户授权下调用 xiaomiaoAgent 的只读工具能力，例如 Web 搜索、文档检索、记忆查询。

### 阶段 C：记忆与会话统一

目标：将 `GoogleAI.Context` 的用户历史逐步映射到 xiaomiaoAgent 会话/记忆，避免 QQ、WebUI、桌面端上下文分裂。

### 阶段 D：通道统一评估

目标：评估是否让 QQ、WebSocket、WebUI 等入口进入 xiaomiaoAgent MessageBus，再由统一 Agent 产生回复。

### 阶段 E：Vtuber 表现层统一

目标：AuBot 不再区分回复来自 `xiaomiao` 还是 xiaomiaoAgent，只消费统一的 assistant reply / tool event / status event。

## 验证

完成后至少运行：

```powershell
cd xiaomiao
python -m unittest test_desktop_bridge.py
```

当前测试已迁移到统一 `test` 目录时，使用：

```powershell
cd <项目根目录>
conda run -n xiaomiao python -m unittest discover -s test/xiaomiao -p "test_*.py"
```

```powershell
cd AuBot
pnpm exec vitest run apps/stage-tamagotchi/src/renderer/pages/xiaomiao-console-api.test.ts
```

如修改了 Vue 页面或路由，再运行：

```powershell
cd AuBot
pnpm -F @proj-airi/stage-tamagotchi typecheck
```

## 需覆盖的边界情况

- `xiaomiao` 未启动时，控制台显示离线。
- `xiaomiao` 已启动但没有最近事件时，事件列表为空态清晰。
- `/v1/xiaomiao/status` 返回非 200 时，不影响 AuBot 其他页面。
- 最近事件文本为空时，不渲染无意义事件。
- 事件重复轮询时，页面不要重复追加同一事件。
- 桥接服务重启后，控制台能自动恢复在线状态。
- xiaomiaoAgent 未安装、未配置或未启动时，小喵控制台显示“未接入 xiaomiaoAgent”，但不影响 QQ Bot 和 Vtuber 主链路。
- xiaomiaoAgent 工具权限关闭时，控制台不能绕过权限直接触发工具。
- 同一 QQ 用户同时通过 QQ 和 WebUI 交互时，会话键映射不能混淆。

## 成功标准

- AuBot 中能打开“小喵控制台”。
- 控制台能展示桥接在线状态、模型、绑定用户和最近事件。
- 桥接不可用时页面稳定，不影响 Vtuber 主舞台。
- 所有新增 API wrapper 和桥接接口测试通过。
- 文档明确说明当前控制台是只读第一版，不包含高危管理能力。
- 文档明确说明 xiaomiaoAgent 是后续 Agent 能力层，第一阶段只做状态观测，不做强制替换。

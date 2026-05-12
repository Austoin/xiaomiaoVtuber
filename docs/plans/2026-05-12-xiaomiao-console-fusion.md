# 小喵 QQ Bot 控制台融合 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在 AuBot Electron 桌面端中新增“小喵 QQ Bot 控制台”，用于只读展示 QQ 机器人状态、桥接状态、最近事件和基础运行信息。

**Architecture:** 当前项目只有 NapCat WebUI、AuBot Dashboard/Settings 和小喵桥接模块，没有小喵 QQ Bot 专用控制台。本计划先在 `xiaomiao/desktop_bridge.py` 增加只读状态/事件接口，再在 `AuBot/apps/stage-tamagotchi` 新增控制台页面消费这些接口。

**Tech Stack:** Python `ThreadingHTTPServer`、Hyper Bot、NapCat OneBot、Electron、Vue 3、TypeScript、Pinia、Vitest、unittest。

---

## 背景

当前融合链路已经打通：`xiaomiao` 暴露本地 OpenAI 兼容桥接接口，AuBot 读取回复并驱动字幕、聊天历史、TTS 和 Live2D 口型。

但当前没有“小喵 QQ Bot 专用控制台”。现有入口分别是 NapCat WebUI、AuBot Dashboard/Settings 和小喵桥接模块。缺失的是一个面向小喵机器人的桌面控制台，用于可视化 QQ Bot 运行状态、桥接健康和最近消息。

## 非目标

第一版只做只读控制台，明确不做：

- 不执行任意系统命令。
- 不显示 API Key 明文。
- 不开放公网控制能力。
- 不替代完整 NapCat WebUI。
- 不把所有小喵命令搬进 AuBot。

## 目标体验

第一版控制台回答四个问题：

1. 小喵是否在线？
2. 桥接服务是否可用？
3. 最近 QQ 消息和小喵回复是什么？
4. 当前机器人使用哪个模型、端口和绑定用户？

建议入口：

```text
AuBot Electron
└── Dashboard 或 Settings
    └── XiaoMiao Console
```

## Task 1: 桥接状态接口

**Files:**

- Modify: `xiaomiao/desktop_bridge.py`
- Test: `xiaomiao/test_desktop_bridge.py`

**Step 1: Write the failing test**

新增测试：`GET /v1/xiaomiao/status` 返回桥接状态。

```json
{
  "ok": true,
  "service": "xiaomiao-desktop-bridge",
  "model": "deepseek-chat",
  "default_user_id": 3554978979
}
```

**Step 2: Run test to verify it fails**

```powershell
cd xiaomiao
python -m unittest test_desktop_bridge.py
```

Expected: FAIL，因为 `/v1/xiaomiao/status` 尚不存在。

**Step 3: Implement minimal endpoint**

在 `desktop_bridge.py` 的 `do_GET()` 中增加只读状态路由。不要引入鉴权、持久化或管理动作。

**Step 4: Run test to verify it passes**

```powershell
cd xiaomiao
python -m unittest test_desktop_bridge.py
```

Expected: PASS。

## Task 2: 最近事件接口

**Files:**

- Modify: `xiaomiao/desktop_bridge.py`
- Modify: `xiaomiao/main.py`
- Test: `xiaomiao/test_desktop_bridge.py`

**Step 1: Write the failing test**

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

**Step 2: Run test to verify it fails**

```powershell
cd xiaomiao
python -m unittest test_desktop_bridge.py
```

Expected: FAIL，因为事件接口尚不存在。

**Step 3: Implement in-memory event buffer**

在 `desktop_bridge.py` 增加内存事件队列，最大保留 50 条。`publish_desktop_state()` 同步写入最近回复事件。

**Step 4: Wire QQ reply publishing**

保留 `main.py` 现有 `publish_desktop_state(event.user_id, result)` 调用。若需要群号，扩展函数签名时必须同步更新测试。

**Step 5: Run test to verify it passes**

```powershell
cd xiaomiao
python -m unittest test_desktop_bridge.py
```

Expected: PASS。

## Task 3: AuBot 控制台 API 模块

**Files:**

- Create: `AuBot/apps/stage-tamagotchi/src/renderer/pages/xiaomiao-console-api.ts`
- Test: `AuBot/apps/stage-tamagotchi/src/renderer/pages/xiaomiao-console-api.test.ts`

**Step 1: Write failing tests**

覆盖三种情况：成功读取状态、成功读取事件、桥接不可用时返回明确错误状态。

**Step 2: Run test to verify it fails**

```powershell
cd AuBot
pnpm exec vitest run apps/stage-tamagotchi/src/renderer/pages/xiaomiao-console-api.test.ts
```

Expected: FAIL，因为模块尚不存在。

**Step 3: Implement minimal API wrapper**

实现 `readXiaomiaoStatus(fetcher)` 和 `readXiaomiaoEvents(fetcher)`。默认桥接地址继续复用 `http://127.0.0.1:5519`，不要在本任务新增设置系统。

**Step 4: Run test to verify it passes**

```powershell
cd AuBot
pnpm exec vitest run apps/stage-tamagotchi/src/renderer/pages/xiaomiao-console-api.test.ts
```

Expected: PASS。

## Task 4: XiaoMiao Console 页面

**Files:**

- Create: `AuBot/apps/stage-tamagotchi/src/renderer/pages/xiaomiao-console.vue`
- Modify: `AuBot/apps/stage-tamagotchi/src/renderer/typed-router.d.ts` only if generated or required by router tooling

**Step 1: Build minimal page**

页面第一版只读展示：桥接状态、当前模型、默认绑定用户、最近事件列表、最近一次助手回复。

**Step 2: Add polling**

页面挂载后每 2 秒读取一次状态和事件。卸载时清理 timer。

**Step 3: Handle bridge unavailable**

桥接不可用时显示“未连接到小喵桥接服务”，不要弹异常或阻塞其他页面。

**Step 4: Manual smoke check**

```powershell
cd AuBot
pnpm dev:tamagotchi
```

Expected: Electron 可以打开新页面，桥接不可用时页面稳定显示离线状态。

## Task 5: 入口导航

**Files:**

- Modify: `AuBot/apps/stage-tamagotchi/src/renderer/layouts/settings.vue`
- Or Modify: `AuBot/apps/stage-tamagotchi/src/renderer/pages/dashboard/index.vue`

**Step 1: Choose entry location**

优先放在 Dashboard。如果现有 Dashboard 结构不适合，再放到 Settings 的开发/集成区域。

**Step 2: Add navigation item**

文案建议：`小喵控制台` / `XiaoMiao Console`。

**Step 3: Verify route works**

```powershell
cd AuBot
pnpm dev:tamagotchi
```

Expected: 可以从入口打开小喵控制台页面。

## Task 6: 文档更新

**Files:**

- Modify: `README.md`
- Modify: `TECHNICAL.md`
- Modify: `docs/plans/2026-05-12-xiaomiao-console-fusion.md` if implementation details changed

**Step 1: Update README**

在主目录 `README.md` 中补充“小喵控制台”入口说明。

**Step 2: Update TECHNICAL**

在 `TECHNICAL.md` 中将“当前没有小喵专用控制台”更新为“已规划/已实现控制台”，并说明接口。

**Step 3: Verify docs stay concise**

确认 `TECHNICAL.md` 不超过 300 行；如果超过，拆分或压缩。

## Verification

完成后至少运行：

```powershell
cd xiaomiao
python -m unittest test_desktop_bridge.py
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

## Edge Cases To Cover

- `xiaomiao` 未启动时，控制台显示离线。
- `xiaomiao` 已启动但没有最近事件时，事件列表为空态清晰。
- `/v1/xiaomiao/status` 返回非 200 时，不影响 AuBot 其他页面。
- 最近事件文本为空时，不渲染无意义事件。
- 事件重复轮询时，页面不要重复追加同一事件。
- 桥接服务重启后，控制台能自动恢复在线状态。

## Success Criteria

- AuBot 中能打开“小喵控制台”。
- 控制台能展示桥接在线状态、模型、绑定用户和最近事件。
- 桥接不可用时页面稳定，不影响 Vtuber 主舞台。
- 所有新增 API wrapper 和桥接接口测试通过。
- 文档明确说明当前控制台是只读第一版，不包含高危管理能力。

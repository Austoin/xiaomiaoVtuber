# Desktop Lane 状态

更新日期：2026-04-14

这是一份围绕 PR #1649 当前 desktop lane 工作的事实状态备忘。范围刻意保持狭窄：只记录当前状态、真实阻塞点，以及现在应该做什么、之后再做什么。

## 已经确定的事实

- desktop lane 方向已经稳定：
  - 仅 macOS。
  - Chrome 优先。
  - visual + semantic tree + OS input。
  - overlay 是可视化层，不是第二个系统光标。
- 代码中已有以下基线：
  - `/Users/liuziheng/airi/services/computer-use-mcp/src/executors/macos-local.ts`：保存真实光标位置，并用 `CGWarpMouseCursorPosition(...)` 恢复。
  - `/Users/liuziheng/airi/apps/stage-tamagotchi/src/main/windows/shared/window.ts`：`makeWindowPassThrough()` 使用 ignore-mouse-events + non-focusable overlay 行为。
  - `/Users/liuziheng/airi/services/computer-use-mcp/src/browser-dom/cdp-bridge.ts`：5 秒 heartbeat，连续 3 次失败后 teardown。
- Chrome extension bridge 和 iframe offset 工作已不再是假设：
  - PR #1649 已包含真实的 extension-side WebSocket client bridge。
  - PR #1649 已包含 iframe DOM candidates 的 frame offset 传递。

## 当前真正的阻塞点

以下是真实剩余问题，按严重程度排序。

### 1. Extension 未知 action 仍返回 `ok: true`

- 文件：`/Users/liuziheng/airi-pr1649/services/computer-use-mcp/chrome-extension/background.js`
- 当前行为：不支持的 action 会进入 `result = { error: ... }`，但响应仍返回 `{ ok: true, result }`。
- 影响：上层可能把不支持的 DOM action 解释为 bridge 成功执行，从而抑制 OS-input fallback，尽管实际什么都没发生。
- 这是仍未解决的真实 review blocker。

### 2. browser-dom 点击路由仍忽略非默认点击语义

- 文件：
  - `/Users/liuziheng/airi-pr1649/services/computer-use-mcp/src/browser-action-router.ts`
  - 调用方：`/Users/liuziheng/airi-pr1649/services/computer-use-mcp/src/server/register-desktop-grounding.ts`
- 当前行为：当 `chrome_dom` candidate 具备 selector + bridge 时，会路由到 browser-dom，但路由逻辑尚未纳入 `button` / `clickCount`。
- 影响：右键或双击仍可能路由到只执行标准主键点击的 DOM 路径。
- 严重程度低于第一个问题，但仍是真实正确性缺口。

### 3. Overlay 生命周期 / RPC readiness 尚未完全闭环

- 当前正在处理的文件：
  - `/Users/liuziheng/airi-pr1649/apps/stage-tamagotchi/src/main/windows/desktop-overlay/rpc/contracts.ts`
  - `/Users/liuziheng/airi-pr1649/apps/stage-tamagotchi/src/main/windows/desktop-overlay/rpc/index.electron.ts`
  - `/Users/liuziheng/airi-pr1649/apps/stage-tamagotchi/src/renderer/pages/desktop-overlay-polling.ts`
  - `/Users/liuziheng/airi-pr1649/apps/stage-tamagotchi/src/renderer/pages/desktop-overlay-polling.test.ts`
- 当前状态：已有 preload-order 缓解措施和 per-call timeout；显式 readiness contract 仍是进行中代码。
- 尚未完成原因：readiness flow 仍未提交，live window context 还需要一次窄范围验证。
- 这目前未被证明已坏，但它是 overlay 路径上最可能剩余的运行时风险。

## 当前不应作为阻塞点的事项

这些是真实想法或清理工作，但不应阻塞当前主线：

- `apps/stage-tamagotchi/src/main/index.ts` 中 eager overlay init 的整洁性。
- 重构嵌套 browser-dom 路由逻辑以提升可读性。
- 将 `macos-local.ts` 改为 instant-warp-only fallback，完全消除运动痕迹。
- 重写 overlay 视觉、ghost pointer 打磨或额外 renderer debug UI。

## 如何理解 m13v 的评论

m13v 的评论有价值，因为它们符合真实平台约束，但应正确拆分：

- 已与当前代码对齐：
  - 保存 → 执行 → 恢复光标模式。
  - overlay 不应拦截用户输入。
  - 对崩溃 CDP session 做 heartbeat teardown。
- 仍适合作为未来优化：
  - 减少 native motion trace，让 UI 承担更多可见指针动画。
  - 对 session 生命周期保持更严格的运行时纪律。

简言之：m13v 给出了很好的运行时建议，但并不意味着每条建议都是当前 blocker。

## 现在应该做什么

1. 修复 extension 未知 action 响应契约，让不支持的 action 返回 `ok: false`。
2. 将 browser-dom 点击路由限制为左键单击；右键或多击强制使用 OS-input。
3. 完成或明确搁置 overlay readiness contract：
   - 如果保留，合并前必须在 live overlay window context 中验证。
   - 如果现在无法完成，不要半成品合入。

## 之后再做什么

只有在上述问题清理干净后再考虑：

1. 可选 follow-up：`fix(stage-tamagotchi): validate desktop overlay lifecycle and RPC readiness in live window context`
2. 可选 follow-up：`refactor(computer-use-mcp): evaluate instant-warp-only macOS fallback against ghost-pointer UX`
3. 可选 follow-up：在 sibling iframe 高度相似时增强 iframe anchor matching。

## 结论

desktop lane 不是被方向阻塞，而是被少数正确性问题和一个仍未关闭的 overlay 生命周期验证步骤阻塞。

不要重新打开架构讨论。不要混入视觉打磨。不要继续把无关改动堆进同一个 PR。

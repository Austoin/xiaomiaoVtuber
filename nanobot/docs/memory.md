# nanobot 中的记忆

nanobot 的记忆建立在一个简单信念上：记忆应该像活着一样，但不应该显得混乱。

好的记忆不是一堆笔记，而是一套安静的注意力系统。它会注意哪些东西值得保留，放下不再需要聚光灯的内容，并把经历转化为平静、持久、有用的东西。

这就是 nanobot 中记忆的形态。

## 设计

nanobot 不把记忆当作一个巨大的文件。

它把记忆分成多个层次，因为不同类型的“记住”需要不同工具：

- `session.messages` 保存活跃的短期对话。
- `memory/history.jsonl` 是压缩后的历史轮次归档。
- `SOUL.md`、`USER.md` 和 `memory/MEMORY.md` 是持久知识文件。
- `GitStore` 记录这些持久文件随时间如何变化。

这让系统在当下保持轻量，同时在长期维度具备反思能力。

## 流程

记忆在 nanobot 中分两个阶段流动。

### 阶段 1：Consolidator

当对话增长到足以挤压上下文窗口时，nanobot 不会尝试永远携带每一条旧消息。

相反，`Consolidator` 会总结对话中最旧且安全的一段，并把总结追加到 `memory/history.jsonl`。

这个文件是：

- 只追加的。
- 基于 cursor 的。
- 优先为机器消费优化，其次才是人工检查。

每一行都是一个 JSON 对象：

```json
{"cursor": 42, "timestamp": "2026-04-03 00:02", "content": "- User prefers dark mode\n- Decided to use PostgreSQL"}
```

它不是最终记忆，而是塑造最终记忆的材料。

### 阶段 2：Dream

`Dream` 是更慢、更深思熟虑的一层。默认按 cron 调度运行，也可以手动触发。

Dream 会读取：

- `memory/history.jsonl` 中的新条目。
- 当前 `SOUL.md`。
- 当前 `USER.md`。
- 当前 `memory/MEMORY.md`。

然后它分两阶段工作：

1. 研究什么是新的，什么已经被知道。
2. 以外科手术式方式编辑长期文件，不是重写一切，而是做出最小且诚实的修改，让记忆保持连贯。

因此，nanobot 的记忆不只是归档，它还具备解释性。

## 文件

```text
workspace/
├── SOUL.md              # Bot 的长期语气和沟通风格
├── USER.md              # 关于用户的稳定知识
└── memory/
    ├── MEMORY.md        # 项目事实、决策和持久上下文
    ├── history.jsonl    # 只追加的历史总结
    ├── .cursor          # Consolidator 写入 cursor
    ├── .dream_cursor    # Dream 消费 cursor
    └── .git/            # 长期记忆文件的版本历史
```

这些文件承担不同角色：

- `SOUL.md` 记住 nanobot 应该如何说话。
- `USER.md` 记住用户是谁，以及用户偏好什么。
- `MEMORY.md` 记住关于工作本身仍然成立的内容。
- `history.jsonl` 记住通往这些结果的过程。

## 为什么使用 `history.jsonl`

旧的 `HISTORY.md` 格式适合随意阅读，但作为运行时基础太脆弱。

`history.jsonl` 给 nanobot 带来：

- 稳定的增量 cursor。
- 更安全的机器解析。
- 更容易批处理。
- 更清晰的迁移和压缩。
- 原始历史与整理后知识之间更好的边界。

你仍然可以用熟悉的工具搜索它：

```bash
# grep
grep -i "keyword" memory/history.jsonl

# jq
cat memory/history.jsonl | jq -r 'select(.content | test("keyword"; "i")) | .content' | tail -20

# Python
python -c "import json; [print(json.loads(l).get('content','')) for l in open('memory/history.jsonl','r',encoding='utf-8') if l.strip() and 'keyword' in l.lower()][-20:]"
```

差异既是技术性的，也是哲学性的：

- `history.jsonl` 负责结构。
- `SOUL.md`、`USER.md` 和 `MEMORY.md` 负责意义。

## 命令

记忆不会藏在幕布后面。用户可以检查并引导它。

| 命令 | 作用 |
|---------|--------------|
| `/dream` | 立即运行 Dream |
| `/dream-log` | 显示最新 Dream 记忆变更 |
| `/dream-log <sha>` | 显示指定 Dream 变更 |
| `/dream-restore` | 列出最近的 Dream 记忆版本 |
| `/dream-restore <sha>` | 将记忆恢复到指定变更前的状态 |

这些命令存在是有原因的：自动记忆很强大，但用户始终应该保留检查、理解和恢复它的权利。

## 带版本的记忆

Dream 修改长期记忆文件后，nanobot 可以用 `GitStore` 记录这次变更。

这让记忆拥有自己的历史：

- 你可以检查发生了什么变化。
- 你可以比较版本。
- 你可以恢复之前的状态。

这会把记忆从静默修改变成一个可审计过程。

## 配置

Dream 配置位于 `agents.defaults.dream`：

```json
{
  "agents": {
    "defaults": {
      "dream": {
        "intervalH": 2,
        "modelOverride": null,
        "maxBatchSize": 20,
        "maxIterations": 10
      }
    }
  }
}
```

| 字段 | 含义 |
|-------|---------|
| `intervalH` | Dream 运行频率，单位小时 |
| `modelOverride` | 可选的 Dream 专用模型覆盖 |
| `maxBatchSize` | Dream 每次运行处理多少条历史记录 |
| `maxIterations` | Dream 编辑阶段的工具预算 |

实际含义：

- `modelOverride: null` 表示 Dream 使用主 agent 相同的模型。只有当你希望 Dream 使用不同模型时才设置它。
- `maxBatchSize` 控制 Dream 每次消耗多少条新的 `history.jsonl` 记录。更大的批次追赶更快；更小的批次更轻、更稳定。
- `maxIterations` 限制 Dream 在更新 `SOUL.md`、`USER.md` 和 `MEMORY.md` 时可以执行多少次读写步骤。它是安全预算，不是质量评分。
- `intervalH` 是配置 Dream 的常规方式。内部会作为 `every` 调度运行，而不是 cron 表达式。

旧版说明：

- 较旧的源码配置中可能仍包含 `dream.cron`。nanobot 会继续支持它以保持向后兼容，但新配置应使用 `intervalH`。
- 较旧的源码配置中可能仍包含 `dream.model`。nanobot 会继续支持它以保持向后兼容，但新配置应使用 `modelOverride`。

## 实际使用

这在日常使用中的含义很简单：

- 对话可以保持快速，而不需要携带无限上下文。
- 持久事实会随时间变得更清晰，而不是更嘈杂。
- 用户可以在需要时检查和恢复记忆。

记忆不应该像垃圾堆，而应该像连续性。

这正是该设计想要保护的东西。

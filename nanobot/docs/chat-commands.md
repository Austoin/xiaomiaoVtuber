# 聊天内命令

这些命令可在聊天通道和交互式 agent 会话中使用：

| 命令 | 说明 |
|---------|-------------|
| `/new` | 停止当前任务并开始新对话 |
| `/stop` | 停止当前任务 |
| `/restart` | 重启 Bot |
| `/status` | 显示 Bot 状态 |
| `/dream` | 立即运行 Dream 记忆整理 |
| `/dream-log` | 显示最新 Dream 记忆变更 |
| `/dream-log <sha>` | 显示指定 Dream 记忆变更 |
| `/dream-restore` | 列出最近的 Dream 记忆版本 |
| `/dream-restore <sha>` | 将记忆恢复到指定变更之前的状态 |
| `/help` | 显示可用的聊天内命令 |

## 周期任务

gateway 每 30 分钟唤醒一次，并检查工作区中的 `HEARTBEAT.md`（`~/.nanobot/workspace/HEARTBEAT.md`）。如果文件中有任务，agent 会执行它们，并把结果发送到你最近活跃的聊天通道。

**设置方式：** 编辑 `~/.nanobot/workspace/HEARTBEAT.md`（由 `nanobot onboard` 自动创建）：

```markdown
## Periodic Tasks

- [ ] Check weather forecast and send a summary
- [ ] Scan inbox for urgent emails
```

agent 也可以自行管理这个文件。你可以让它“添加一个周期任务”，它会替你更新 `HEARTBEAT.md`。

> **注意：** gateway 必须正在运行（`nanobot gateway`），并且你至少与 Bot 聊过一次，这样它才知道结果要投递到哪个通道。

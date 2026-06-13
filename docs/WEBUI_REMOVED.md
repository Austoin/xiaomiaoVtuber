# WebUI 已移除说明

**更新时间**: 2026-06-13  
**影响范围**: xiaomiaoAgent WebUI 和网关已从项目中移除

---

## ❌ 已移除组件

1. **xiaomiaoAgent WebUI** (端口 5174)
   - 原 React/Vite 图形界面
   - 原通过 WebSocket 连接网关

2. **xiaomiaoAgent 网关** (端口 8765)
   - 原 WebSocket 网关服务
   - 原用于 WebUI 与后端通信

---

## ✅ 保留的访问方式

### 方式一：TUI 终端界面（推荐）
```cmd
start-tui.cmd
```
- 启动最快（1-2秒）
- 完整工具能力
- 纯终端操作

### 方式二：QQ Bot
```cmd
start-all.cmd
```
- QQ 群聊/私聊
- 需配置权限

### 方式三：xiaomiaobot Web
```
http://127.0.0.1:5175
```
- Live2D 虚拟角色
- 聊天历史
- 语音输入

---

## 📝 配置文件变化

### start-all.cmd
移除了以下启动步骤：
- `start_agent_gateway` (端口 8765)
- `start_agent_webui` (端口 5174)

现在只启动：
1. QQ 协议端 (5004)
2. xiaomiaoAgent API (8900)
3. xiaomiao main.py / 桥接 (5519)
4. xiaomiaobot web (5175)

### 端口变化
| 端口 | 服务 | 状态 |
|------|------|------|
| 5004 | QQ OneBot WebSocket | ✅ 保留 |
| 5519 | xiaomiao 桥接 | ✅ 保留 |
| 8900 | xiaomiaoAgent API | ✅ 保留 |
| 5175 | xiaomiaobot web | ✅ 保留 |
| 8765 | xiaomiaoAgent 网关 | ❌ 已移除 |
| 5174 | xiaomiaoAgent WebUI | ❌ 已移除 |

---

## 🔄 迁移建议

如果你之前使用 WebUI：

1. **日常开发** → 改用 `start-tui.cmd`
2. **图形界面** → 使用 `xiaomiaobot web` (http://127.0.0.1:5175)
3. **多人协作** → 配置 QQ Bot ROOT 权限

---

## 📚 相关文档更新

已更新以下文档移除 WebUI 引用：
- README.md
- TECHNICAL.md
- start-all.cmd
- docs/QUICK_START.md
- docs/PROJECT_FINAL_SUMMARY.md
- docs/TEST_REPORT_2026-06-13.md

# xiaomiaoAgent TUI 终端界面使用指南

> **入口**: 仓库根目录的 `scripts\start-tui.cmd`，或 `menu.cmd tui`
> **类型**: 命令行交互界面  
> **特点**: 无需浏览器，纯终端操作

---

## 🚀 快速启动

### 方法一：双击仓库级启动脚本（推荐）
```
从仓库根目录双击运行: scripts\start-tui.cmd
```

### 方法二：命令行启动
```powershell
cd <仓库根目录>\xiaomiaoAgent
conda activate xiaomiao
python -m xiaomiao_agent agent --config ..\.cache\agent\nanobot\config.json
```

---

## 💡 使用方法

### 基本对话
```
启动后会看到提示符:
> 

直接输入消息，按 Enter 发送
> 你好

Agent 会实时显示回复
```

### 特殊命令
```
/help          - 显示帮助
/clear         - 清空屏幕
/exit 或 quit  - 退出
Ctrl+C         - 强制退出
```

### Markdown 渲染
默认启用 Markdown 渲染，会自动格式化：
- **代码块**: 带语法高亮
- **列表**: 格式化显示
- **表格**: 对齐显示
- **链接**: 下划线显示

---

## ⚙️ 命令行参数

### 完整参数列表
```bash
python -m xiaomiao_agent agent [OPTIONS]

选项:
  -m, --message TEXT       直接发送消息（非交互模式）
  -s, --session TEXT       会话 ID [默认: cli:direct]
  -w, --workspace TEXT     工作区目录
  -c, --config TEXT        配置文件路径
  --markdown/--no-markdown 是否渲染 Markdown [默认: markdown]
  --logs/--no-logs         是否显示日志 [默认: no-logs]
  -h, --help               显示帮助
```

### 常用组合

#### 1. 静默模式（无日志）
```bash
python -m xiaomiao_agent agent --config ..\.cache\agent\nanobot\config.json --no-logs
```

#### 2. 调试模式（显示日志）
```bash
python -m xiaomiao_agent agent --config ..\.cache\agent\nanobot\config.json --logs
```

#### 3. 纯文本模式（不渲染 Markdown）
```bash
python -m xiaomiao_agent agent --config ..\.cache\agent\nanobot\config.json --no-markdown
```

#### 4. 一次性消息（非交互）
```bash
python -m xiaomiao_agent agent --config ..\.cache\agent\nanobot\config.json -m "你好"
```

#### 5. 指定会话 ID
```bash
python -m xiaomiao_agent agent --config ..\.cache\agent\nanobot\config.json -s my-session
```

---

## 🎨 界面预览

### 启动画面
```
========================================
xiaomiaoAgent TUI 终端对话界面
========================================

启动中...

Loading configuration...
Connecting to agent...
Ready!

> _
```

### 对话示例
```
> 你好，帮我写一个 Python 快速排序

AI: 好的，这是一个 Python 快速排序的实现：

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```

使用方法：
```python
arr = [3, 6, 8, 10, 1, 2, 1]
print(quicksort(arr))  # 输出: [1, 1, 2, 3, 6, 8, 10]
```

> 解释一下算法原理

AI: 快速排序的核心思想是分治法...
```

---

## 🆚 TUI vs WebUI vs QQ Bot

| 特性 | TUI (终端) | WebUI (网页) | QQ Bot |
|------|-----------|-------------|---------|
| **界面** | 命令行 | 图形界面 | QQ 消息 |
| **启动** | 直接打开终端 | 需要启动 Gateway 和浏览器 | 依赖 QQ/NapCat |
| **Markdown** | 渲染 | 完整渲染 | 纯文本 |
| **工具可视化** | 文本显示 | 图形展示 | 不显示 |
| **会话管理** | 单会话 | 多会话 | 统一会话 |
| **适合场景** | 开发调试、服务器 | 日常使用、演示 | 多人协作 |
| **资源占用** | 最低 | 中等 | 低 |
| **网络依赖** | 取决于模型 Provider | Gateway、WebSocket 和模型 Provider | NapCat 与 Agent API |

---

## 💡 优势和适用场景

### TUI 的优势
1. ✅ **启动路径短**: 不需要单独启动 WebUI
2. ✅ **资源占用低**: 不需要运行浏览器和 WebUI 开发服务器
3. ✅ **服务器友好**: SSH 远程也能用
4. ✅ **纯键盘操作**: 适合键盘党
5. ✅ **输出直接**: 适合开发调试和回归验证

### 适用场景
- 🔧 **快速测试**: 测试 Agent 配置和功能
- 💻 **开发调试**: 开发时快速验证
- 🖥️ **服务器使用**: SSH 远程连接时
- ⚡ **追求效率**: 不想打开浏览器
- 🎯 **专注对话**: 不需要多会话管理

### 不适用场景
- ❌ 需要多会话管理
- ❌ 需要查看完整的工具调用详情
- ❌ 需要在多个模型间切换
- ❌ 需要频繁调整配置

---

## 🔧 高级配置

### 自定义会话 ID
```bash
# 不同项目使用不同会话
python -m xiaomiao_agent agent -s project-a
python -m xiaomiao_agent agent -s project-b
```

### 自定义工作区
```bash
python -m xiaomiao_agent agent -w f:\my-workspace
```

### 使用不同配置文件
```bash
# 开发配置
python -m xiaomiao_agent agent -c config-dev.json

# 生产配置
python -m xiaomiao_agent agent -c config-prod.json
```

---

## 🐛 常见问题

### Q1: 启动后没有反应
**原因**: conda 环境未激活  
**解决**: 
```bash
conda activate xiaomiao
python -m xiaomiao_agent agent --config ..\.cache\agent\nanobot\config.json
```

### Q2: 报错 "ModuleNotFoundError"
**原因**: xiaomiaoAgent 未安装  
**解决**:
```bash
cd <仓库根目录>\xiaomiaoAgent
conda activate xiaomiao
pip install -e .
```

### Q3: 中文乱码
**原因**: Windows 终端编码问题  
**解决**: 脚本已自动设置 `chcp 65001`，如果仍乱码：
```bash
# PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### Q4: Markdown 不渲染
**原因**: 可能缺少依赖  
**解决**:
```bash
pip install rich markdown-it-py
```

### Q5: 怎么退出？
**方法**:
- 输入 `/exit` 或 `quit`
- 按 `Ctrl+C`
- 按 `Ctrl+D` (Unix/Linux)

---

## 📊 运行特征

| 项目 | TUI | WebUI |
|------|-----|-------|
| **额外界面进程** | 无 | 浏览器或 WebView |
| **本地服务** | 直接运行 Agent | 需要 Gateway；开发模式还需要 Vite |
| **模型网络** | 取决于 Provider | 取决于 Provider |
| **适合验证** | CLI、配置、工具和单会话 | WebSocket、界面、多会话和上传 |

---

## 🎯 推荐使用场景

### 场景 1: 快速测试 Agent
```bash
# 启动 TUI
scripts\start-tui.cmd

# 输入测试消息
> 测试工具调用：搜索最新新闻

# 查看结果，确认功能正常
# Ctrl+C 退出
```

### 场景 2: 开发时调试
```bash
# 修改了 Agent 配置
vim ..\.cache\agent\nanobot\config.json

# 立即测试
scripts\start-tui.cmd

# 输入测试用例
> 测试新配置...
```

### 场景 3: 服务器远程使用
```bash
# SSH 连接到服务器
ssh user@server

# 激活环境
conda activate xiaomiao

# 启动 TUI
cd /path/to/xiaomiaoAgent
python -m xiaomiao_agent agent --config config.json
```

---

## 📝 小技巧

### 技巧 1: 使用历史记录
Windows Terminal 和 PowerShell 支持：
- `↑` / `↓`: 浏览历史命令
- `Ctrl+R`: 搜索历史

### 技巧 2: 复制粘贴
- **复制**: 选中文本后自动复制（或右键）
- **粘贴**: `Ctrl+V` 或右键

### 技巧 3: 保存对话
对话自动保存到会话历史：
```
<仓库根目录>\.cache\agent\nanobot\workspace\sessions\cli:direct\
```

### 技巧 4: 多开终端
可以同时打开多个 TUI 窗口，使用不同会话 ID：
```bash
# 终端 1
python -m xiaomiao_agent agent -s session-a

# 终端 2
python -m xiaomiao_agent agent -s session-b
```

---

## ✨ 总结

### 为什么选择 TUI？
- ⚡ **快**: 启动快，响应快
- 💡 **简**: 界面简洁，操作简单
- 🎯 **专**: 专注对话，无干扰
- 🔧 **稳**: 无代理问题，稳定可靠

### 一句话推荐
如果你：
- 不需要多会话管理
- 不需要频繁切换配置
- 追求效率和简洁
- 经常在服务器上工作

**TUI 就是最佳选择！**

---

**快速启动**: 双击 `scripts\start-tui.cmd` 或执行 `menu.cmd tui`
**退出方式**: 输入 `/exit` 或按 `Ctrl+C`  
**配置文件**: `<仓库根目录>\.cache\agent\nanobot\config.json`

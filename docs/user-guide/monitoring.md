# xiaomiaoVirtual 服务监控面板

**版本**: v1.0  
**创建日期**: 2026-06-24

一个可视化的服务状态监控面板，实时显示 xiaomiaoVirtual 项目各个服务的运行状态和依赖关系。

---

## 📸 功能特点

### ✨ 核心功能

1. **实时状态监控**
   - 自动检测服务运行状态
   - 显示端口占用情况
   - 支持自动刷新（5秒间隔）

2. **可视化依赖关系**
   - 动态连接线展示服务依赖
   - 根据状态变换连接线颜色
   - 贝塞尔曲线平滑连接

3. **统计面板**
   - 运行中服务数量
   - 停止服务数量
   - 警告服务数量
   - 监控运行时长

4. **交互式操作**
   - 点击服务卡片查看详情
   - 一键刷新所有状态
   - 自动/手动刷新切换

---

## 🚀 快速启动

### 方式一：一键启动（推荐）

```powershell
# 在项目根目录执行
start-monitor.cmd
```

这将自动：
1. 检查并安装依赖
2. 启动监控 API（端口 8888）
3. 在浏览器中打开监控面板

### 方式二：手动启动

**步骤 1**: 启动监控 API

```powershell
cd F:\xiaomiaoVirtual
conda activate xiaomiao
python monitor-api.py
```

**步骤 2**: 打开监控面板

用浏览器打开 `monitor-dashboard-enhanced.html`

---

## 📊 监控的服务

| 服务 | 端口 | 依赖服务 | 说明 |
|------|------|---------|------|
| NapCat (QQ协议) | 5004 | 无 | QQ 协议接入 |
| xiaomiaoAgent API | 8900 | 无 | Agent 核心服务 |
| 小喵桌面桥接 | 5519 | Agent API | 桌面应用桥接 |
| QQ Bot | - | NapCat, Agent API | QQ 机器人主程序 |
| Web 界面 | 5175 | 桌面桥接 | Web 前端界面 |
| 桌面端 (Electron) | - | 桌面桥接 | Electron 桌面应用 |
| TUI 终端 | - | Agent API | 终端交互界面 |

---

## 🎨 状态说明

### 状态指示器

| 状态 | 颜色 | 图标 | 说明 |
|------|------|------|------|
| 运行中 | 🟢 绿色 | ✓ | 服务正常运行，有脉冲动画 |
| 已停止 | 🔴 红色 | × | 服务未启动或已停止 |
| 警告 | 🟡 黄色 | ⚠ | 服务运行但有异常，有脉冲动画 |
| 检查中 | 🔵 蓝色 | ⟳ | 正在检查服务状态，旋转动画 |

### 连接线颜色

| 颜色 | 说明 |
|------|------|
| 绿色发光 | 依赖的服务运行正常 |
| 黄色发光 | 依赖的服务有警告 |
| 红色半透明 | 依赖的服务已停止 |

---

## 💡 使用技巧

### 自动刷新

1. 点击"开启自动刷新"按钮
2. 面板将每 5 秒自动检查一次服务状态
3. 再次点击可停止自动刷新

### 手动刷新

点击"刷新状态"按钮立即检查所有服务状态

### 查看详情

- 鼠标悬停在服务卡片上查看完整信息
- 服务卡片会显示端口号和依赖关系

---

## 🔧 API 接口说明

### 端点

```
GET http://127.0.0.1:8888/api/status
```

### 响应示例

```json
{
  "services": [
    {
      "id": "napcat",
      "name": "NapCat (QQ协议)",
      "port": "5004",
      "status": "running",
      "checked_at": "2026-06-24T10:30:00"
    },
    {
      "id": "agent-api",
      "name": "xiaomiaoAgent API",
      "port": "8900",
      "status": "stopped",
      "checked_at": "2026-06-24T10:30:00"
    }
  ],
  "timestamp": "2026-06-24T10:30:00"
}
```

### 状态值

- `running` - 服务运行中
- `stopped` - 服务已停止
- `error` - 检查出错

---

## 📁 文件说明

### 核心文件

1. **monitor-dashboard-enhanced.html**
   - 增强版监控面板
   - 支持实时 API 连接
   - 包含自动刷新功能
   - 推荐使用 ⭐

2. **monitor-dashboard.html**
   - 基础版监控面板
   - 纯前端，无需后端
   - 模拟状态显示

3. **monitor-api.py**
   - 监控 API 后端
   - 提供服务状态检查接口
   - 基于 aiohttp 异步框架

4. **start-monitor.cmd**
   - 一键启动脚本
   - 自动安装依赖
   - 启动 API 和面板

---

## 🔍 故障排查

### 问题 1: 端口 8888 被占用

**症状**: 启动时提示端口已被占用

**解决方案**:
```powershell
# 查看占用进程
netstat -ano | findstr ":8888"

# 结束进程
taskkill /PID <进程ID> /F
```

或者修改 `monitor-api.py` 中的端口号。

---

### 问题 2: 无法连接到 API

**症状**: 面板显示"使用模拟数据"

**原因**: 监控 API 未启动或无法访问

**解决方案**:
1. 确认 `monitor-api.py` 正在运行
2. 检查端口 8888 是否开放
3. 访问 http://127.0.0.1:8888/api/status 测试 API

---

### 问题 3: 所有服务显示"检查中"

**症状**: 状态一直是"检查中"，不会更新

**原因**: API 请求超时或失败

**解决方案**:
1. 检查浏览器控制台错误信息
2. 确认监控 API 正常运行
3. 尝试手动访问 API 端点

---

### 问题 4: 状态不准确

**症状**: 显示的状态与实际不符

**原因**: 
- 端口检查方式可能不完全准确
- 某些服务没有暴露端口

**说明**:
- 没有端口的服务（如 QQ Bot、TUI）无法通过端口检测
- 建议结合实际运行情况判断
- 可以在 `monitor-api.py` 中自定义检测逻辑

---

## 🛠️ 自定义配置

### 添加新服务

编辑 `monitor-dashboard-enhanced.html`：

```javascript
const services = {
    'new-service': {
        name: '新服务名称',
        port: '端口号',
        dependencies: ['依赖服务ID']
    },
    // ... 其他服务
};
```

编辑 `monitor-api.py`：

```python
SERVICES = [
    {
        "id": "new-service",
        "name": "新服务名称",
        "port": "端口号",
        "check_url": "http://127.0.0.1:端口",
        "method": "http"  # 或 "tcp"
    },
    # ... 其他服务
]
```

---

### 修改刷新间隔

编辑 `monitor-dashboard-enhanced.html`，找到：

```javascript
autoRefreshInterval = setInterval(checkAllServices, 5000);
```

修改 `5000`（毫秒）为你想要的间隔。

---

### 修改 API 端口

编辑 `monitor-api.py`，找到：

```python
web.run_app(app, host='127.0.0.1', port=8888)
```

修改 `port=8888` 为你想要的端口。

同时需要修改 `monitor-dashboard-enhanced.html` 中的 API 地址：

```javascript
const response = await fetch('http://127.0.0.1:8888/api/status');
```

---

## 🎯 开发模式

如果监控 API 未启动，面板会自动切换到**模拟模式**：
- 随机生成服务状态
- 显示"(模拟模式)"标记
- 用于开发和演示

---

## 📚 技术栈

### 前端
- HTML5 + CSS3
- Vanilla JavaScript (无框架)
- Canvas API (连接线绘制)

### 后端
- Python 3.11+
- aiohttp (异步 Web 框架)
- asyncio (异步 I/O)

---

## 🔄 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-24 | 初始版本，包含基础和增强版面板 |

---

## 📝 注意事项

1. **安全性**: 监控 API 仅监听本地地址 (127.0.0.1)，不对外暴露
2. **性能**: 自动刷新会持续发送请求，建议按需开启
3. **兼容性**: 推荐使用现代浏览器（Chrome、Edge、Firefox）
4. **依赖**: 需要安装 aiohttp (`pip install aiohttp`)

---

## 🎉 特别功能

### 视觉效果
- ✨ 玻璃态毛玻璃效果
- 🌈 渐变背景
- 💫 脉冲动画（运行中服务）
- 🎨 发光连接线
- 🎭 悬停交互效果

### 实用功能
- 📊 实时统计面板
- 🔔 Toast 通知提示
- ⏱️ 运行时长计时
- 📱 响应式布局

---

## 💬 反馈和建议

如有问题或建议，欢迎在项目仓库提 Issue。

---

**创建者**: Claude Code (Claude Opus 4.8)  
**项目**: xiaomiaoVirtual  
**文档版本**: v1.0

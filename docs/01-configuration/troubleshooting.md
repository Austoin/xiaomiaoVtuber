# 故障排查指南

> 最后更新：2026-06-12

本文档提供 xiaomiaoVirtual 项目常见问题的诊断和解决方案。

## 目录

1. [启动失败](#一启动失败)
2. [端口占用](#二端口占用)
3. [NapCat 连接问题](#三napcat-连接问题)
4. [Agent API 不可达](#四agent-api-不可达)
5. [模型调用失败](#五模型调用失败)
6. [QQ 消息无响应](#六qq-消息无响应)
7. [前端显示异常](#七前端显示异常)
8. [测试失败](#八测试失败)

---

## 一、启动失败

### 1.1 start-all.cmd 无法启动

**症状**:
```
'conda' 不是内部或外部命令
```

**原因**: conda 环境未正确配置

**解决**:
```powershell
# 1. 确认 conda 已安装
conda --version

# 2. 如果未找到，添加 conda 到 PATH
# 或使用完整路径启动
F:\Anaconda3\Scripts\conda.exe activate xiaomiao

# 3. 重新初始化 shell
conda init powershell
```

---

### 1.2 Python 模块导入错误

**症状**:
```
ModuleNotFoundError: No module named 'anthropic'
```

**原因**: 虚拟环境未激活或依赖未安装

**解决**:
```powershell
# 1. 激活 conda 环境
conda activate xiaomiao

# 2. 重新安装依赖
cd xiaomiaoAgent
uv sync --extra dev

# 3. 验证安装
python -c "import anthropic; print('OK')"
```

---

### 1.3 Node.js 启动失败

**症状**:
```
Error: Cannot find module 'vite'
```

**原因**: node_modules 未安装或损坏

**解决**:
```powershell
cd xiaomiaobot

# 清理并重新安装
Remove-Item -Recurse -Force node_modules, pnpm-lock.yaml
pnpm install

# 如果 pnpm 版本不对
corepack enable
corepack prepare pnpm@10.33.0 --activate
```

---

## 二、端口占用

### 2.1 检查端口占用

**使用健康检查**:
```powershell
.\start-all.cmd --check
```

**输出示例**:
```
[QQ OneBot WebSocket]
      QQ OneBot WebSocket port 5004 is free. Would start a visible terminal.

[xiaomiaoAgent API]
      xiaomiaoAgent API port 8900 is free. Would start a visible terminal.
```

**手动检查端口**:
```powershell
# 检查所有关键端口
netstat -ano | findstr "5004 8900 8765 5519 5175 5174"
```

---

### 2.2 端口被占用的解决

**查找占用进程**:
```powershell
# 查找 5004 端口的进程
netstat -ano | findstr ":5004"

# 输出示例：
# TCP    0.0.0.0:5004    0.0.0.0:0    LISTENING    12345
# 12345 就是进程 PID
```

**终止进程**:
```powershell
# 方法 1: 使用 PID 终止
taskkill /F /PID 12345

# 方法 2: 使用进程名终止（如果知道）
taskkill /F /IM python.exe /T
```

**修改端口（可选）**:

如果端口冲突无法解决，可以修改配置文件：

```json
// config.json
{
  "xiaomiao_agent": {
    "api_base": "http://localhost:8901/v1"  // 改为 8901
  }
}

// xiaomiao/config.json
{
  "onebot": {
    "reverse_ws_port": 5005  // 改为 5005
  },
  "desktop_bridge": {
    "port": 5520  // 改为 5520
  }
}
```

---

## 三、NapCat 连接问题

### 3.1 NapCat 未启动

**症状**:
```
[xiaomiao] WebSocket connection failed: Connection refused
```

**检查**:
```powershell
# 查看 NapCat 进程
tasklist | findstr "NapCat\|QQ"

# 查看 5004 端口
netstat -ano | findstr ":5004"
```

**解决**:
1. 确保 QQ 已登录
2. 手动启动 NapCat:
   ```powershell
   cd xiaomiao/NapCat.Shell.Windows.OneKey
   .\NapCat.44498.Shell\start.bat
   ```
3. 检查 NapCat 配置文件

---

### 3.2 NapCat 版本不兼容

**症状**:
```
[NapCat] Unsupported OneBot protocol version
```

**解决**:
1. 更新 NapCat 到最新版本
2. 检查 OneBot 协议版本配置
3. 查看 NapCat 日志:
   ```powershell
   type xiaomiao\NapCat.Shell.Windows.OneKey\NapCat.44498.Shell\napcat\logs\napcat.log
   ```

---

### 3.3 消息格式错误

**症状**: QQ 消息发送后无响应，日志显示格式错误

**检查日志**:
```powershell
# xiaomiao 日志
type xiaomiao\logs\bot-run.out.log | Select-String "ERROR"

# NapCat 日志
type xiaomiao\NapCat.Shell.Windows.OneKey\NapCat.44498.Shell\napcat\logs\*.log
```

**常见问题**:
- 图片 URL 格式不正确
- CQ 码格式错误
- 消息段（segment）类型不支持

---

## 四、Agent API 不可达

### 4.1 Agent API 服务未启动

**症状**:
```
[xiaomiao] Agent API request failed: Connection refused (8900)
```

**检查**:
```powershell
# 检查 Agent API 进程
netstat -ano | findstr ":8900"

# 查看 Python 进程
tasklist | findstr "python.exe"
```

**解决**:
```powershell
# 手动启动 Agent API
cd xiaomiaoAgent
conda activate xiaomiao
python -m nanobot serve --port 8900
```

---

### 4.2 Agent 配置错误

**症状**:
```
[xiaomiaoAgent] Config validation error
```

**验证配置**:
```powershell
cd xiaomiaoAgent
conda activate xiaomiao

# 显示当前配置
python -m nanobot config show

# 检查配置文件语法
python -c "import json; json.load(open('../config.json'))"
```

**常见配置错误**:
- `api_key` 缺失或格式错误
- `provider` 名称拼写错误（custom/anthropic/openai）
- `api_base` URL 格式错误
- JSON 语法错误（缺少引号、逗号等）

---

### 4.3 API 响应 502 错误

**症状**:
```
[xiaomiao] Agent replied with 502 Bad Gateway
```

**原因**: Agent 后端模型调用失败

**检查**:
1. 查看 Agent 日志:
   ```powershell
   type xiaomiaoAgent\.run-api.err.log
   ```

2. 测试模型连接:
   ```powershell
   cd xiaomiaoAgent
   conda activate xiaomiao
   
   # 测试 OpenAI 兼容 API
   curl -X POST http://localhost:8900/v1/chat/completions ^
     -H "Content-Type: application/json" ^
     -d "{\"model\":\"custom/deepseek-v4-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"test\"}]}"
   ```

3. 检查提供方配置（见下节）

---

## 五、模型调用失败

### 5.1 API 密钥无效

**症状**:
```
[xiaomiaoAgent] Authentication failed: Invalid API key
```

**检查**:
```powershell
# 显示当前配置（密钥会被隐藏）
cd xiaomiaoAgent
python -m nanobot config show
```

**解决**:
1. 验证 API 密钥格式
   - Anthropic: `sk-ant-api03-...`
   - OpenAI: `sk-...`
   - DeepSeek: `sk-...`

2. 更新配置:
   ```powershell
   # 方法 1: 编辑配置文件
   notepad ..\config.json
   
   # 方法 2: 使用环境变量
   $env:ANTHROPIC_API_KEY = "sk-ant-..."
   ```

---

### 5.2 自定义提供方连接失败

**症状**:
```
[xiaomiaoAgent] Custom provider connection error: Connection refused
```

**检查 API 地址**:
```powershell
# 测试连接
curl http://localhost:12345/v1/models

# 如果是远程地址
curl http://your-server:12345/v1/models
```

**常见问题**:
- `api_base` URL 格式错误（缺少 `/v1` 后缀）
- 自定义服务未启动
- 防火墙阻止连接
- SSL 证书问题（https 地址）

---

### 5.3 模型名称不存在

**症状**:
```
[xiaomiaoAgent] Model not found: custom/invalid-model
```

**解决**:
1. 查询可用模型:
   ```powershell
   curl http://localhost:12345/v1/models
   ```

2. 更新配置中的模型名:
   ```json
   {
     "xiaomiaoAgent": {
       "agents": {
         "defaults": {
           "model": "deepseek-v4-flash"  // 确保名称正确
         }
       }
     }
   }
   ```

---

### 5.4 速率限制

**症状**:
```
[xiaomiaoAgent] Rate limit exceeded: 429 Too Many Requests
```

**解决**:
1. 等待速率限制重置（通常 1 分钟）
2. 升级 API 套餐
3. 使用多个 API key 轮询
4. 在 `config.json` 中配置备用提供方:
   ```json
   {
     "xiaomiaoAgent": {
       "agents": {
         "defaults": {
           "provider": "anthropic",  // 主提供方
           "fallback_provider": "openai"  // 备用提供方
         }
       }
     }
   }
   ```

---

## 六、QQ 消息无响应

### 6.1 触发词未匹配

**症状**: 发送消息后小喵不回复

**检查配置**:
```json
// xiaomiao/config.json
{
  "commands": {
    "agent_prompt_word": "喵喵",  // 触发词
    "exact_agent_prompts": ["重置", "清空"]  // 精确匹配命令
  }
}
```

**测试**:
- 私聊：直接发送消息（不需要触发词）
- 群聊：发送 `喵喵 你好` 或 `@小喵 你好`

---

### 6.2 权限不足

**症状**: 某些命令无法执行

**检查权限**:
```ini
; xiaomiao/runtime/permissions.ini
[permissions]
YOUR_QQ_NUMBER = allowlist  ; 或 root/super/manage
```

**权限等级**:
- `root`: 完全权限
- `super`: 高级权限
- `manage`: 管理权限
- `allowlist`: Agent 使用权限
- 未配置: `common`（默认，无 Agent 权限）

---

### 6.3 Agent 后端禁用

**症状**: QQ 回复但内容是默认回复，没有 AI 能力

**检查**:
```json
// config.json
{
  "xiaomiao_agent": {
    "enabled": true  // 确保为 true
  }
}
```

**测试 Agent 连接**:
```powershell
# 查看 xiaomiao 日志
type xiaomiao\logs\bot-run.out.log | Select-String "agent"
```

---

## 七、前端显示异常

### 7.1 xiaomiaobot web 无法打开

**症状**: 浏览器显示 `无法访问此网站`

**检查**:
```powershell
# 查看端口
netstat -ano | findstr ":5175"

# 查看进程
tasklist | findstr "node.exe"
```

**解决**:
```powershell
cd xiaomiaobot

# 重新启动前端
pnpm run dev
```

**访问地址**: `http://localhost:5175`

---

### 7.2 桥接事件不更新

**症状**: 前端界面不显示最新消息

**检查桥接服务**:
```powershell
# 测试桥接 API
curl http://localhost:5519/api/bridge/status

# 查看事件
curl http://localhost:5519/api/bridge/events
```

**解决**:
1. 检查 `xiaomiao` 的桥接服务是否启动（5519 端口）
2. 查看浏览器控制台错误（F12）
3. 检查 CORS 配置

---

### 7.3 Live2D 模型不显示

**症状**: 前端界面空白或模型加载失败

**检查模型文件**:
```powershell
ls workspace\models\live2d\
```

**常见问题**:
- 模型文件缺失或路径错误
- 模型格式不支持
- 浏览器控制台显示 CORS 错误

**解决**:
1. 确保模型文件在正确位置
2. 检查模型配置文件 `model3.json` 格式
3. 清除浏览器缓存后重新加载

---

## 八、测试失败

### 8.1 pytest 导入错误

**症状**:
```
ModuleNotFoundError: No module named 'pytest'
```

**解决**:
```powershell
cd xiaomiaoAgent
conda activate xiaomiao
uv sync --extra dev
```

---

### 8.2 测试超时

**症状**:
```
FAILED tests/test_something.py::test_async - asyncio.TimeoutError
```

**解决**:
1. 增加超时时间:
   ```python
   @pytest.mark.asyncio(timeout=120)  # 增加到 120 秒
   async def test_something():
       ...
   ```

2. 检查异步循环是否正常关闭

3. 查看测试日志寻找阻塞原因

---

### 8.3 前端测试失败

**症状**:
```
FAIL apps/stage-pocket/src/modules/xiaomiao-bridge-events.test.ts
```

**解决**:
```powershell
cd xiaomiaobot

# 清理缓存
Remove-Item -Recurse -Force node_modules/.cache

# 重新运行测试
pnpm exec vitest run
```

---

## 九、日志查看

### 9.1 关键日志位置

```
xiaomiao/
├── logs/
│   ├── bot-run.out.log      # 标准输出
│   └── bot-run.err.log      # 错误输出

xiaomiaoAgent/
├── .run-api.out.log          # API 服务标准输出
├── .run-api.err.log          # API 服务错误
├── .run-gateway.out.log      # Gateway 服务标准输出
└── .run-gateway.err.log      # Gateway 服务错误

xiaomiao/NapCat.Shell.Windows.OneKey/
└── NapCat.44498.Shell/
    └── napcat/
        └── logs/
            └── napcat.log    # NapCat 日志
```

### 9.2 查看实时日志

```powershell
# Windows PowerShell
Get-Content xiaomiao\logs\bot-run.out.log -Wait -Tail 50

# 或使用 tail（如果安装了 Git Bash）
tail -f xiaomiao/logs/bot-run.out.log
```

---

## 十、完全重置

如果以上方法都无法解决，可以尝试完全重置：

```powershell
# 1. 停止所有服务
taskkill /F /IM python.exe /T
taskkill /F /IM node.exe /T

# 2. 清理临时文件
Remove-Item -Recurse -Force .pytest_cache, .pytest-tmp, __pycache__

# 3. 重新安装依赖
cd xiaomiaoAgent
Remove-Item -Recurse -Force .venv
uv sync --extra dev

cd ..\xiaomiaobot
Remove-Item -Recurse -Force node_modules
pnpm install

# 4. 清理配置缓存
Remove-Item xiaomiaoAgent\.nanobot\config.json

# 5. 重新启动
.\start-all.cmd
```

---

## 相关文档

- [configuration.md](./configuration.md) - 配置文件说明
- [运行与配置.md](./运行与配置.md) - 快速启动
- [STARTUP.md](./STARTUP.md) - 详细启动流程
- [verification.md](./verification.md) - 验证测试

---

## 获取帮助

如果问题仍未解决：

1. 查看项目 Issues: [GitHub Issues](https://github.com/your-repo/xiaomiaoVirtual/issues)
2. 提供完整的错误日志和配置信息（隐藏密钥）
3. 说明操作系统版本和 Python/Node.js 版本

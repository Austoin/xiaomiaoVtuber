# xiaomiaoVirtual 运行与配置速查

> **路径说明**：文档中的 `<项目根目录>` 表示 xiaomiaoVirtual 项目的根目录（即包含 `README.md`、`start-all.cmd` 的目录）。请根据你的实际安装路径替换，例如 `F:\xiaomiaoVirtual` 或 `C:\Users\YourName\Projects\xiaomiaoVirtual`。

本文是最短可执行入口。详细手动启动、端口、验证和排错请看 [STARTUP.md](STARTUP.md)。

## 一、首次配置环境

`start-all.cmd` 只负责启动服务，不安装依赖。第一次运行或环境缺依赖时，先执行：

```powershell
cd <项目根目录>
cmd /c call setup-env.cmd
```

只检查环境，不安装依赖：

```powershell
cd <项目根目录>
cmd /c call setup-env.cmd --check
```

缺少主目录 `config.json` 时，从 `config.example.json` 自动复制模板：

```powershell
cd <项目根目录>
cmd /c call setup-env.cmd --yes
```

`setup-env.cmd` 会处理：

- 检查 `conda`、`node`、`corepack`、`npm`。
- 创建项目 `workspace/` 和 Agent 工作区。
- 安装 `xiaomiao` Python 依赖。
- 安装 `xiaomiaoAgent[api]` 本地源码包。
- 准备 `pnpm@10.33.0` 并安装 `xiaomiaobot` 依赖。
- 安装 `xiaomiaoAgent/webui` 依赖。
- 缺少 `.nanobot/config.json` 时初始化 Agent 配置。

可选参数：

```text
--check        只检查工具、配置文件和依赖目录
--yes, -y      缺少 config.json 时复制模板
--skip-python  跳过 Python 依赖安装
--skip-node    跳过 xiaomiaobot pnpm install
--skip-webui   跳过 xiaomiaoAgent WebUI npm install
--help, -h     查看帮助
```

## 二、检查本地配置

完整运行前确认这些文件存在：

```text
<项目根目录>\config.json
<项目根目录>\xiaomiao\config.json
<项目根目录>\xiaomiaoAgent\.nanobot\config.json
```

重点检查：

- `config.json`：模型、中转站 API Key、`baseUrl`、`model`。
- `xiaomiao/config.json`：QQ / OneBot 地址、ROOT 用户、Super 用户、Agent 工具白名单。
- `xiaomiaoAgent/.nanobot/config.json`：Agent 工作区和运行配置。

主目录 `config.json` 推荐结构：

```json
{
  "xiaomiao_agent": {
    "enabled": true,
    "base_url": "http://127.0.0.1:8900/v1/chat/completions",
    "model": "",
    "session_id": "xiaomiao-unified",
    "timeout_seconds": 30
  },
  "xiaomiaoAgent": {
    "provider": "custom",
    "model": "deepseek/deepseek-chat",
    "providers": {
      "custom": {
        "apiKey": "你的中转站密钥",
        "baseUrl": "https://你的中转站地址/v1"
      }
    }
  }
}
```

## 三、完整启动

先检查：

```powershell
cd <项目根目录>
cmd /c call start-all.cmd --check
```

正式启动：

```powershell
cd <项目根目录>
cmd /c call start-all.cmd
```

启动顺序：

```text
1. QQ / NapCat OneBot      127.0.0.1:5004
2. xiaomiaoAgent API       127.0.0.1:8900
3. xiaomiaoAgent 网关      127.0.0.1:8765
4. xiaomiao main / bridge  127.0.0.1:5519
5. xiaomiaobot stage-web   http://127.0.0.1:5175
6. xiaomiaoAgent WebUI     http://127.0.0.1:5174
```

启动成功后主要访问：

```text
xiaomiaobot 网页端：http://127.0.0.1:5175
xiaomiaoAgent WebUI：http://127.0.0.1:5174
```

## 四、常用验证

完整服务检查：

```powershell
cd <项目根目录>
cmd /c call start-all.cmd --check
```

Agent API：

```text
http://127.0.0.1:8900/health
```

xiaomiao bridge：

```text
http://127.0.0.1:5519/v1/xiaomiao/status
```

QQ 联调建议测试：

```text
- 记忆状态
- 整理记忆
- 抓取这个网页内容：https://example.com
```

白名单用户测试本机命令：

```text
- 帮我在本机执行 dir
确认执行 ABC123
```

## 五、只跑部分链路

只跑 QQ + Agent：

```text
NapCat / OneBot :5004
xiaomiaoAgent API :8900
xiaomiao main / bridge :5519
```

只跑网页端体验：

```text
xiaomiaoAgent API :8900
xiaomiao main / bridge :5519
xiaomiaobot stage-web :5175
```

只跑 Agent 命令行：

```powershell
cd <项目根目录>\xiaomiaoAgent
conda activate xiaomiao
xiaomiao agent --config <项目根目录>\xiaomiaoAgent\.nanobot\config.json
```

## 六、更多文档

- 详细启动排错：[STARTUP.md](STARTUP.md)
- QQ 指令速查：[QQ机器人指令速查.md](QQ机器人指令速查.md)
- 文件和 workspace 规则：[file-workspace-hygiene.md](file-workspace-hygiene.md)

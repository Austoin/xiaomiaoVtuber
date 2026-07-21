# xiaomiao

QQ/OneBot 通道适配器，负责接收 NapCat 事件、执行权限与工作区校验，并调用 `xiaomiaoAgent` 的 OpenAI 兼容接口。

本文同时作为本目录的项目入口和文件维护说明。依赖包、缓存和第三方运行环境按类别说明，业务源码按职责说明。

## 1. 项目定位

`xiaomiao` 是 QQ/OneBot 适配层，接收 NapCat WebSocket 事件，执行权限与工作区校验，再调用 `xiaomiaoAgent` 的 OpenAI 兼容接口。目录中还捆绑了完整的 NapCat/QQ Windows 运行包，因此体积远大于 Python 源码。

## 2. 运行链路

```text
QQ/NapCat OneBot WebSocket
          │
          ▼
      main.py
          │
   bridge / permissions / workspace
          │
          ▼
 agent_backend.py ──HTTP──> xiaomiaoAgent :8900
          │
          └──发送文本、图片、文件、工具事件回 QQ
```

## 3. Python 根文件

| 文件 | 作用 |
|---|---|
| `__init__.py` | 将目录声明为 Python 包，可放版本或导出。 |
| `main.py` | 主程序：命令分发、OneBot 事件处理、权限、人设、图像、定时任务和 Agent 调用；文件较大，后续扩展应按领域拆分。 |
| `agent_backend.py` | 请求 `http://127.0.0.1:8900/v1/chat/completions`，上传媒体并解析工具事件/流式回复。 |
| `console_output.py` | Windows 控制台安全输出，处理编码和异常字符。 |
| `config.json` | QQ/Hyper 与 Agent 的本地配置。可能含密钥、账号或 token，禁止复制到文档和公共仓库。 |
| `prerequisites.py` | 角色名单、前置条件和人设 prompt。 |
| `qq_agent_bridge.py` | QQ turn/reply、等待通知、中文记忆命令到 Agent 命令的映射。 |
| `qq_agent_tools.py` | 普通用户与高权限用户的工具策略。 |
| `qq_permissions.py` | 管理员、超级用户和 Agent 工具白名单判定。 |
| `qq_workspace.py` | QQ 文件安全下载、类型检查、SSRF 防护和工作区路径管理。 |
| `Quote.py` | 生成 QQ 回复引用图片。 |
| `requirements.txt` | Python 运行依赖清单。 |
| `start.bat` | Windows 启动脚本，负责环境检查和主程序启动。 |
| `unified_config.py` | 读取项目根 `config.json`，合并 `xiaomiaoAgent` 配置并提供统一访问。 |

### `utils/runtime_helpers.py`

提供设置存储、图片下载/压缩、Pixiv 验证、时间转换等运行时辅助。它应保持为无状态的小工具层，网络下载必须继续复用安全校验。

## 4. 资源目录

### `assets`

- `dict.txt`：文字/词典资源。
- `e.ttf`、`n.ttf`、`sz.ttf`、`t.ttf`：字体文件，用于图片、引用卡片或文本渲染。
- `quote/mask.png`：引用图片遮罩。

字体和图片是二进制资源，修改时要注意许可证、体积和编码兼容。

### `__pycache__`、`utils/__pycache__`

Python 字节码缓存，可删除后自动重建，不属于源码。

## 5. NapCat.Shell.Windows.OneKey

这是第三方 NapCat + QQNT Windows 运行环境，约 1.46 GB，包含安装器、QQ/Electron/Chromium/FFmpeg 原生库、NapCat JS、本地模块和运行缓存。维护边界如下：

- 根目录：7z 包、安装器、`QQ.exe`、压缩包等分发文件。
- `bootmain/`：引导脚本、DLL、EXE，负责启动和注入。
- `NapCat.44498.Shell/`：当前 NapCat 运行实例。
- `versions/9.9.26-44498/`：指定 QQ 版本的 Electron、Chromium、FFmpeg 和原生 DLL。
- `resources/app/napcat/`：NapCat JavaScript、本地模块、配置、日志、缓存和二维码。
- `node_modules/`：NapCat 内置第三方 Node 依赖，不逐包维护。
- `logs/`、`cache/`、`config/`：运行生成数据，可能包含账号、Cookie、passkey、二维码和令牌。

升级 NapCat 时应整体替换并做 OneBot WebSocket、登录、图片/文件发送、重连和权限回归测试；不要直接修改其内部打包文件来修复 Python 业务问题。

## 6. 配置、缓存与路径

根目录 `cache_config.py` 定义的主要缓存位置：

- QQ 工作区：`.cache/xiaomiao/qq_workspace`
- 下载目录：`.cache/xiaomiao/qq_workspace/downloads`
- 临时目录：`.cache/xiaomiao/qq_workspace/tmp`
- QQ 运行配置：`.cache/xiaomiao/runtime`

配置优先级由 `unified_config.py` 统一处理。生产环境建议使用环境变量或本地未跟踪配置，不要把凭据写入版本库。

## 7. 测试重点

最小回归范围应覆盖：

1. OneBot WebSocket 连接、断线重连和事件去重。
2. 普通用户、管理员、超级用户的权限边界。
3. 文本、图片、文件、引用消息和长消息拆分。
4. QQ 文件下载的扩展名、MIME、大小、路径穿越和 SSRF 防护。
5. Agent API 超时、错误响应、流式事件和工具调用。
6. 定时任务、记忆命令和运行缓存隔离。
7. NapCat 登录状态、二维码更新和重启恢复。

## 8. 扩展建议与风险

- 将 `main.py` 按事件处理、命令、媒体、定时任务、Agent 调用拆成模块，降低修改风险。
- 统一定义 OneBot 事件和 Agent 事件的数据类，避免散落字典键。
- 权限判定使用集中策略表并配套参数化测试。
- 外部请求全部设置超时、大小上限和可观测错误；不要静默吞异常。
- 任何日志、截图、二维码和导出的配置都可能含敏感信息，提交前必须脱敏。

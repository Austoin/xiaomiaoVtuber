# 缓存目录统一管理

## 📋 概述

从本版本开始,所有缓存和运行时数据统一存放在 `.cache/` 目录下,便于管理和清理。

## 📁 新的目录结构

```
.cache/
├── xiaomiao/               # xiaomiao 相关缓存
│   ├── runtime/           # 运行时配置
│   │   ├── Super_User.ini
│   │   ├── Manage_User.ini
│   │   ├── sisters.ini
│   │   ├── jhq.ini
│   │   ├── programmers.ini
│   │   ├── timing_message.ini
│   │   └── blacklist.sr
│   ├── qq_workspace/      # QQ 资源下载
│   │   └── downloads/qq/
│   └── bridge_events/     # Bridge 事件存储
│       └── bridge_events.jsonl
│
├── agent/                  # xiaomiaoAgent 缓存
│   └── nanobot/
│       ├── config.json    # Agent 配置
│       ├── workspace/     # Agent 工作区
│       ├── media/         # 多通道媒体文件
│       ├── bridge/        # WhatsApp bridge 等运行文件
│       ├── history/       # CLI 历史
│       ├── logs/          # Agent 日志
│       ├── sessions/      # 兼容会话目录
│       ├── memory/        # 兼容记忆目录
│       └── tool-results/  # 大工具输出落盘结果
│
├── bot/                    # xiaomiaobot 缓存
│
└── tool/                   # 工具缓存
    ├── embeddings/        # 嵌入向量缓存
    └── models/            # 模型缓存
```

## 🔄 迁移旧数据

如果你有现有的 `xiaomiao/runtime/`、`workspace/`、`xiaomiaoAgent/.nanobot/` 或 `xiaomiao/temps/` 数据,运行迁移脚本:

```bash
python scripts/migrate_cache.py
```

迁移脚本会:
1. 复制 `xiaomiao/runtime/` → `.cache/xiaomiao/runtime/`
2. 复制 `workspace/` → `.cache/xiaomiao/qq_workspace/`
3. 复制 `xiaomiaoAgent/.nanobot/config.json` → `.cache/agent/nanobot/config.json`
4. 复制 `xiaomiaoAgent/.nanobot/workspace` / `history` / `bridge` → `.cache/agent/nanobot/`
5. 复制 `xiaomiao/temps/` → `.cache/xiaomiao/qq_workspace/tmp/`
6. 创建其他必要的缓存目录
7. 保留旧目录 (手动验证后删除)

## 🎯 优点

### 1. 统一管理
所有缓存在一个地方,便于:
- 查看总缓存大小
- 一键清理所有缓存
- 备份和恢复

### 2. 更清晰的项目结构
```
xiaomiao/
├── main.py              # ✅ 只有代码
├── commands/            # ✅ 只有代码
└── services/            # ✅ 只有代码

.cache/                  # ✅ 所有数据
```

### 3. 更好的 Git 管理
`.cache/` 已在 `.gitignore` 中,不会提交到仓库

### 4. 灵活配置
通过环境变量自定义缓存位置:
```bash
export XIAOMIAO_CACHE_ROOT=/data/cache
python xiaomiao/main.py
```

## 🔧 代码使用

### 导入缓存配置

```python
from cache_config import (
    RUNTIME_DIR,
    SUPER_USER_FILE,
    AGENT_SESSION_CACHE,
    get_cache_path,
    ensure_cache_dirs,
)

# 确保缓存目录存在
ensure_cache_dirs()

# 获取自定义缓存路径
my_cache = get_cache_path("xiaomiao", "my_feature", "data.json")
```

### 配置项

| 变量 | 路径 | 用途 |
|------|------|------|
| `CACHE_ROOT` | `.cache/` | 缓存根目录 |
| `XIAOMIAO_CACHE` | `.cache/xiaomiao/` | xiaomiao 缓存 |
| `AGENT_CACHE` | `.cache/agent/` | Agent 缓存 |
| `RUNTIME_DIR` | `.cache/xiaomiao/runtime/` | 运行时配置 |
| `QQ_WORKSPACE_CACHE` | `.cache/xiaomiao/qq_workspace/` | QQ 资源 |
| `BRIDGE_EVENTS_CACHE` | `.cache/xiaomiao/bridge_events/` | Bridge 事件 |
| `NANOBOT_CONFIG_FILE` | `.cache/agent/nanobot/config.json` | Agent 配置 |
| `NANOBOT_WORKSPACE` | `.cache/agent/nanobot/workspace/` | Agent 工作区 |
| `NANOBOT_BRIDGE` | `.cache/agent/nanobot/bridge/` | WhatsApp Bridge |
| `NANOBOT_CLI_HISTORY` | `.cache/agent/nanobot/history/cli_history` | TUI 历史 |

## 🧹 清理缓存

### 清理所有缓存
```bash
rm -rf .cache/
```

### 清理特定缓存
```bash
# 只清理 xiaomiao 缓存
rm -rf .cache/xiaomiao/

# 只清理 QQ 下载
rm -rf .cache/xiaomiao/qq_workspace/downloads/

# 保留配置,只清理下载
rm -rf .cache/xiaomiao/qq_workspace/downloads/
```

### 清理后重建
```bash
python xiaomiao/main.py
# 程序会自动创建必要的目录
```

## 📝 配置文件说明

### 运行时配置 (`.cache/xiaomiao/runtime/`)

| 文件 | 用途 |
|------|------|
| `Super_User.ini` | 超级管理员 QQ 号列表 |
| `Manage_User.ini` | 管理员 QQ 号列表 |
| `sisters.ini` | 姐姐模式用户列表 |
| `jhq.ini` | 妈妈模式用户列表 |
| `programmers.ini` | 程序员模式用户列表 |
| `timing_message.ini` | 定时消息配置 |
| `blacklist.sr` | 黑名单 |

### Bridge 事件 (`.cache/xiaomiao/bridge_events/`)

存储 QQ 与 Agent 之间的事件日志,用于调试和恢复。

### QQ 资源 (`.cache/xiaomiao/qq_workspace/`)

存储从 QQ 下载的文件,如图片、文档等。

## ⚙️ 环境变量

### `XIAOMIAO_CACHE_ROOT`
自定义缓存根目录:
```bash
export XIAOMIAO_CACHE_ROOT=/data/cache
```

### `XIAOMIAO_BRIDGE_EVENT_STORE`
自定义 Bridge 事件存储路径:
```bash
export XIAOMIAO_BRIDGE_EVENT_STORE=/data/bridge_events.jsonl
```

## 🔍 故障排查

### 找不到配置文件

检查 `.cache/xiaomiao/runtime/` 是否存在:
```bash
ls -la .cache/xiaomiao/runtime/
```

如果不存在,运行迁移脚本或手动创建。

### 权限问题

确保 `.cache/` 目录可写:
```bash
chmod -R u+w .cache/
```

### 磁盘空间不足

查看缓存大小:
```bash
du -sh .cache/
```

清理不需要的缓存:
```bash
rm -rf .cache/xiaomiao/qq_workspace/downloads/
```

## 🚀 最佳实践

1. **定期备份配置**
   ```bash
   tar -czf backup.tar.gz .cache/xiaomiao/runtime/
   ```

2. **清理旧的下载文件**
   ```bash
   find .cache/xiaomiao/qq_workspace/downloads/ -mtime +30 -delete
   ```

3. **监控缓存大小**
   ```bash
   du -sh .cache/* | sort -h
   ```

4. **使用独立缓存目录** (生产环境)
   ```bash
   export XIAOMIAO_CACHE_ROOT=/data/xiaomiao-cache
   ```

---

**变更日期**: 2025-06-25  
**影响范围**: xiaomiao, xiaomiaoAgent, 工具层  
**向后兼容**: 是 (旧路径通过迁移脚本迁移)

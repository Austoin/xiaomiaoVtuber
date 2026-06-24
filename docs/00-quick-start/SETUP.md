# 环境配置指南

**版本**: v1.1 | **更新日期**: 2026-06-24

本项目采用轻量化仓库策略，模型文件、缓存和构建产物不包含在版本控制中，需要自行下载和构建。

**完成配置后** → [run-and-config.md](run-and-config.md) 了解如何启动项目

---

## 📦 克隆仓库后的初始化步骤

### 1. 安装依赖

#### Python 环境（xiaomiao & xiaomiaoAgent）

```bash
# xiaomiao - QQ 机器人
cd xiaomiao
pip install -r requirements.txt

# xiaomiaoAgent - Agent 框架
cd ../xiaomiaoAgent
pip install -e .
```

#### Node.js 环境（xiaomiaobot）

```bash
cd xiaomiaobot
pnpm install
```

### 2. 下载 Live2D 模型文件

项目需要以下模型文件（已从版本控制中排除）：

#### 官方示例模型
- 位置：`xiaomiaobot/apps/stage-tamagotchi/src/renderer/.cache/assets/js/CubismSdkForWeb-5-r.3/Samples/Resources/`
- 内容：Haru、Hiyori、Mao 等 Cubism SDK 官方示例模型

**这些模型在首次运行时会自动下载**（由 Vite 插件处理）。

#### 自定义角色模型（可选）
如需使用 ATRI 和 Natsume 角色：

1. 创建目录：
```bash
mkdir -p artemis-models/live2d-model
```

2. 下载模型文件到该目录（需自行准备模型文件）：
   - `artemis-models/live2d-model/atri.model3.json`
   - `artemis-models/live2d-model/shiki_natsume/final/shiki_natsume.model3.json`

### 3. 下载 NapCat（QQ Bot 协议端）

```bash
cd xiaomiao
# 按照 NapCat 官方文档下载并解压到：
# xiaomiao/NapCat.Shell.Windows.OneKey/
```

参考：[NapCat 文档](https://napneko.github.io/)

### 4. 配置文件

```bash
# 根据模板创建配置文件
cp xiaomiao/config.json.example xiaomiao/config.json
cp xiaomiaoAgent/.env.example xiaomiaoAgent/.env

# 编辑配置文件，填入必要信息
```

### 5. 构建前端（如需使用桌面应用）

```bash
cd xiaomiaobot
pnpm run build:tamagotchi
```

---

## 📁 被排除的文件和目录

以下内容不在版本控制中，需要自行下载/生成：

### 模型和资源文件
- `*.moc3` - Live2D 模型二进制文件
- `*.model3.json` - Live2D 模型配置
- `*.physics3.json` - Live2D 物理配置
- `*.motion3.json` - Live2D 动作文件
- `*.vrm` - VRM 3D 模型文件
- `*.lpk` - 大型打包文件
- `artemis-models/` - 自定义角色模型目录

### 缓存和临时文件
- `.cache/` - 根目录缓存
- `xiaomiaobot/.cache/` - 前端缓存
- `xiaomiaobot/apps/*/src/renderer/.cache/` - 渲染进程缓存
- `.turbo/` - Turborepo 缓存
- `.ruff_cache/` - Python linter 缓存
- `.uv-cache/` - UV 包管理器缓存

### 构建产物
- `dist/` - Python 构建产物
- `build/` - 通用构建目录
- `xiaomiaobot/apps/*/out/` - Electron 构建输出
- `xiaomiaobot/packages/*/dist/` - 包构建输出

### 运行时数据
- `*.log` - 所有日志文件
- `logs/` - 日志目录
- `xiaomiao/runtime/bridge_events.jsonl` - 桥接事件日志
- `xiaomiao/temps/` - 临时文件
- `xiaomiaoAgent/.nanobot/` - Agent 运行时数据

### 第三方组件
- `node_modules/` - Node.js 依赖
- `.pnpm-store/` - pnpm 存储
- `xiaomiao/NapCat.Shell.Windows.OneKey/` - NapCat QQ 协议端

---

## ✅ 验证安装

运行快速启动脚本：

```bash
# Windows
start-all.cmd

# 或手动启动各组件
python xiaomiao/main.py
python xiaomiaoAgent/main.py
cd xiaomiaobot && pnpm run dev:tamagotchi
```

详细启动说明请参考：[run-and-config.md](run-and-config.md)

---

## 🔍 故障排查

### 模型文件找不到
- 检查 `xiaomiaobot/apps/stage-tamagotchi/src/renderer/.cache/` 目录
- 首次运行时 Vite 插件会自动下载官方示例模型
- 自定义模型需手动放置到 `artemis-models/` 目录

### 依赖安装失败
- Python: 检查 Python 版本 >= 3.10
- Node.js: 检查 Node.js 版本 >= 18，推荐使用 pnpm

### 构建失败
- 清理缓存：`rm -rf .cache xiaomiaobot/.cache`
- 重新安装依赖：`pnpm install --force`
- 检查磁盘空间（模型文件约 1GB）

---

## 📚 相关文档

- [快速启动](run-and-config.md) - 最快启动入口
- [故障排查](../01-configuration/troubleshooting.md) - 常见问题解决
- [配置说明](../01-configuration/configuration.md) - 详细配置文档

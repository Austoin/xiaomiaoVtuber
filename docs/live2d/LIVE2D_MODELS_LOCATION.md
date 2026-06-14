# Live2D 模型文件位置说明

> **发现**: Live2D 模型文件在 `.cache` 目录中！  
> **更新**: 2026-06-13

---

## 📍 模型文件位置

### 实际路径

Live2D 模型文件存放在：

```
xiaomiaobot/apps/stage-tamagotchi/src/renderer/.cache/
└── assets/js/CubismSdkForWeb-5-r.3/Samples/Resources/
    ├── Haru/           # 春（女性角色）
    ├── Hiyori/         # 日和（女性角色）
    ├── Mao/            # 真绪（男性角色）
    ├── Mark/           # 马克（男性角色）
    └── Natori/         # 名取（女性角色）
    └── ... (可能还有更多)
```

### 文件结构

每个角色目录包含：

```
Haru/
├── Haru.model3.json        # 模型配置文件
├── Haru.moc3               # 模型数据
├── *.png                   # 贴图文件
├── *.physics3.json         # 物理效果
├── motions/                # 动作文件夹
│   └── *.motion3.json
└── expressions/            # 表情文件夹
    └── *.exp3.json
```

---

## 🎭 可用的角色

### Cubism SDK 官方示例角色

这些是 **Live2D Cubism SDK 5** 的官方示例模型：

1. **Haru (春)** - 女性角色
2. **Hiyori (日和)** - 女性角色
3. **Mao (真绪)** - 男性角色
4. **Mark (马克)** - 男性角色
5. **Natori (名取)** - 女性角色

---

## ⚠️ 重要发现

### Cubism 版本问题

**发现的问题**:
- `.cache` 中的模型是 **Cubism SDK 5** 格式
- Artemis 使用的是 **Cubism 4** 格式
- **两者不兼容！**

### 兼容性说明

| 组件 | 版本 | 位置 |
|------|------|------|
| xiaomiaobot 模型 | **Cubism 5** | `.cache/...` |
| Artemis Live2D | **Cubism 4** | `tool/vendor/Artemis/live2d/` |
| pixi-live2d-display v0.5.0 | 支持 **Cubism 4** | Artemis 使用 |
| 官方 Cubism SDK | **Cubism 5** | 最新版本 |

**结论**: 
- xiaomiaobot 的模型**不能直接**用于 Artemis 的 Live2D 系统
- 需要用 **Cubism SDK 5** 的渲染器

---

## 🔧 解决方案

### 方案 1: 使用 Cubism SDK 5 渲染器

xiaomiaobot 已经有 Cubism 5 的渲染系统：

```
xiaomiaobot/apps/stage-tamagotchi/
```

这个应用已经可以渲染这些模型！

### 方案 2: 转换模型格式

将 Cubism 5 模型转换为 Cubism 4（但可能丢失功能）

### 方案 3: 使用 xiaomiaobot 现有系统

xiaomiaobot 已经有完整的 Live2D 系统，可以直接使用：

```bash
# 启动 xiaomiaobot
cd xiaomiaobot
npm start
```

---

## 📋 xiaomiaobot 的 Live2D 系统

### 已有的角色系统

xiaomiaobot 项目中已经有：

```
xiaomiaobot/
├── apps/
│   └── stage-tamagotchi/      # 桌面宠物应用
│       └── src/renderer/.cache/
│           └── assets/js/CubismSdkForWeb-5-r.3/
│               └── Samples/Resources/
│                   ├── Haru/
│                   ├── Hiyori/
│                   ├── Mao/
│                   ├── Mark/
│                   └── Natori/
```

### 可能的集成方式

1. **使用 xiaomiaobot 的渲染器**
   - xiaomiaobot 已经有完整的 Cubism 5 渲染系统
   - 可以直接在 xiaomiaobot 中切换这些角色

2. **升级 Artemis 到 Cubism 5**
   - 需要替换 pixi-live2d-display
   - 使用官方 Cubism Framework for Web

3. **分离使用**
   - xiaomiaobot：用于 Cubism 5 模型（Haru, Hiyori 等）
   - Artemis：用于 Cubism 4 模型（Natsume, ATRI）

---

## 🎯 推荐方案

### 对于 xiaomiaoVirtual 项目

**推荐**: 使用 **xiaomiaobot** 现有的 Live2D 系统

**原因**:
1. ✅ 已经有完整的渲染系统
2. ✅ 已经有 5 个官方示例模型
3. ✅ Cubism 5 是最新版本
4. ✅ 不需要额外下载模型

**步骤**:
1. 启动 xiaomiaobot stage-tamagotchi 应用
2. 在应用中切换角色（Haru, Hiyori, Mao, Mark, Natori）
3. 与 xiaomiaoVirtual 角色系统集成

---

## 📚 更新文档引用

### 之前的文档

之前创建的 `docs/LIVE2D_CHARACTER_SWITCH.md` 基于 Artemis (Cubism 4)。

### 新的理解

xiaomiaoVirtual 项目实际上已经有 Live2D 模型：
- **位置**: `.cache/xiaomiaobot/...`
- **版本**: Cubism SDK 5
- **数量**: 5+ 个官方角色
- **大小**: ~97 MB

### 下一步

可以：
1. 创建基于 xiaomiaobot 的角色切换文档
2. 或者集成 xiaomiaobot 的 Live2D 系统
3. 或者在 xiaomiaobot 中实现角色切换

---

## 🎉 总结

**好消息**: 
- ✅ xiaomiaoVirtual 项目**已经有** Live2D 模型！
- ✅ 不需要从 Artemis 复制！
- ✅ 位于 `.cache` 目录（被 .gitignore 忽略）

**位置**: 
```
.cache/xiaomiaobot/apps/stage-tamagotchi/src/renderer/.cache/
assets/js/CubismSdkForWeb-5-r.3/Samples/Resources/
```

**可用角色**: Haru, Hiyori, Mao, Mark, Natori (Cubism 5)

**需要**: 
- 使用 xiaomiaobot 的渲染系统
- 或升级 Artemis 到 Cubism 5

**下一步**: 你想要我帮你基于 xiaomiaobot 实现角色切换吗？ 🎭

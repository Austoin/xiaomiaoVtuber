# Web 端 Live2D 模型显示问题

## 问题描述
Web 端（`127.0.0.1:5175/settings/models`）只显示 4 个模型，而不是预期的 9 个 Live2D 角色。

## 根本原因

### 1. 硬编码的预设列表
文件：`xiaomiaobot/packages/stage-ui/src/stores/display-models.ts`

当前预设模型列表（第 49-54 行）：
```typescript
const displayModelsPresets: DisplayModel[] = [
  { id: 'preset-live2d-1', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetLive2dProUrl, name: 'Hiyori (Pro)', ... },
  { id: 'preset-live2d-2', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetLive2dFreeUrl, name: 'Hiyori (Free)', ... },
  { id: 'preset-vrm-1', format: DisplayModelFormat.VRM, type: 'url', url: presetVrmAvatarAUrl, name: 'AvatarSample_A', ... },
  { id: 'preset-vrm-2', format: DisplayModelFormat.VRM, type: 'url', url: presetVrmAvatarBUrl, name: 'AvatarSample_B', ... },
]
```

### 2. 模型文件存在但未注册
实际上 9 个 Live2D 角色**都存在**于缓存目录中：
```
xiaomiaobot/apps/stage-tamagotchi/src/renderer/.cache/assets/js/CubismSdkForWeb-5-r.3/Samples/Resources/
├── ATRI/           ✓ 已存在
├── Haru/           ✓ 已存在（未注册）
├── Hiyori/         ✓ 已存在（已注册 2 个版本）
├── Mao/            ✓ 已存在（未注册）
├── Mark/           ✓ 已存在（未注册）
├── Natori/         ✓ 已存在（未注册）
├── Natsume/        ✓ 已存在（未注册）
├── Rice/           ✓ 已存在（未注册）
└── Wanko/          ✓ 已存在（未注册）
```

### 3. 格式要求差异
预设列表要求的格式：
- **Live2dZip** 格式（打包的 .zip 文件）
- 文件位置：`xiaomiaobot/packages/stage-ui/src/assets/live2d/models/*.zip`

实际模型的格式：
- **Live2dDirectory** 格式（解压后的目录结构）
- 文件位置：`.cache/assets/js/CubismSdkForWeb-5-r.3/Samples/Resources/*/`

## 解决方案

### 方案 A：手动添加（当前可用）
用户可以通过 Web UI 的 "Add" 按钮手动添加模型：
1. 点击 "Add" 按钮
2. 选择模型目录或打包为 .zip 上传
3. 模型会保存到 IndexedDB 中

**限制**：每次清除浏览器数据后需要重新添加。

### 方案 B：打包模型为 .zip 并注册（推荐）
将其他 7 个 Cubism SDK 示例模型打包为 .zip 文件：

1. **创建 .zip 文件**：
```bash
cd xiaomiaobot/packages/stage-ui/src/assets/live2d/models/

# 打包每个模型
zip -r haru.zip ../../../.cache/.../Resources/Haru/
zip -r mao.zip ../../../.cache/.../Resources/Mao/
zip -r mark.zip ../../../.cache/.../Resources/Mark/
zip -r natori.zip ../../../.cache/.../Resources/Natori/
zip -r rice.zip ../../../.cache/.../Resources/Rice/
zip -r wanko.zip ../../../.cache/.../Resources/Wanko/
```

2. **在 display-models.ts 中注册**：
```typescript
// 添加新的 URL 常量
const presetHaruUrl = new URL('../assets/live2d/models/haru.zip', import.meta.url).href
const presetMaoUrl = new URL('../assets/live2d/models/mao.zip', import.meta.url).href
// ... 其他模型

// 扩展 displayModelsPresets 数组
const displayModelsPresets: DisplayModel[] = [
  // 现有的 4 个
  { id: 'preset-live2d-1', ... },
  { id: 'preset-live2d-2', ... },
  { id: 'preset-vrm-1', ... },
  { id: 'preset-vrm-2', ... },
  
  // 新增的 7 个 Cubism SDK 示例
  { id: 'preset-live2d-3', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetHaruUrl, name: 'Haru', ... },
  { id: 'preset-live2d-4', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetMaoUrl, name: 'Mao', ... },
  // ... 其他模型
]
```

### 方案 C：动态加载（需要开发）
修改 `display-models.ts` 以动态扫描缓存目录：
```typescript
async function loadCubismSampleModels() {
  const resourcesPath = '.cache/assets/js/CubismSdkForWeb-5-r.3/Samples/Resources'
  // 扫描目录并动态创建预设列表
  // 使用 DisplayModelFormat.Live2dDirectory 格式
}
```

**限制**：需要处理文件系统访问权限和跨域问题。

## 当前状态
- ✅ 模型文件完整（9 个角色都在缓存中）
- ✅ QQ Bot 集成完成（支持 xiaomiao、natsume、atri 切换）
- ⚠️ Web UI 只显示 4 个预设模型（需要手动添加其他模型）
- ⚠️ **重要澄清**：Web 端不直接访问 .cache 目录，详见 [WEB_MODEL_LOADING_MECHANISM.md](WEB_MODEL_LOADING_MECHANISM.md)

## 建议操作
1. **短期**：在文档中说明如何手动添加模型
2. **长期**：实施方案 B，将常用模型打包并注册到预设列表

## 相关文件
- `xiaomiaobot/packages/stage-ui/src/stores/display-models.ts` - 模型预设列表
- `xiaomiaobot/apps/stage-tamagotchi/src/renderer/.cache/assets/js/CubismSdkForWeb-5-r.3/Samples/Resources/` - 实际模型文件位置
- `docs/task/LIVE2D_CHARACTER_VERIFICATION.md` - 角色验证报告

## 文档日期
2026-06-14

# Web 模式模型加载机制解析

## 问题：Web 模式是直接加载 .cache 目录下的模型吗？

**答案：否。Web 模式不直接访问 .cache 目录。**

---

## Web 模式的模型加载流程

### 1. 数据源
Web 端只从**两个地方**加载模型：

**A. 预设模型（hardcoded）**
- 定义位置：`xiaomiaobot/packages/stage-ui/src/stores/display-models.ts`
- 数据格式：`DisplayModel[]` 数组
- 当前包含：4 个预设模型（2 个 Hiyori + 2 个 VRM）

```typescript
const displayModelsPresets: DisplayModel[] = [
  { id: 'preset-live2d-1', format: DisplayModelFormat.Live2dZip, 
    type: 'url', url: presetLive2dProUrl, name: 'Hiyori (Pro)', ... },
  { id: 'preset-live2d-2', format: DisplayModelFormat.Live2dZip, 
    type: 'url', url: presetLive2dFreeUrl, name: 'Hiyori (Free)', ... },
  { id: 'preset-vrm-1', format: DisplayModelFormat.VRM, 
    type: 'url', url: presetVrmAvatarAUrl, name: 'AvatarSample_A', ... },
  { id: 'preset-vrm-2', format: DisplayModelFormat.VRM, 
    type: 'url', url: presetVrmAvatarBUrl, name: 'AvatarSample_B', ... },
]
```

**B. 用户上传模型（IndexedDB）**
- 存储位置：浏览器 IndexedDB（`localforage`）
- 数据格式：`{ format, file: File, importedAt, previewImage }`
- 添加方式：通过 UI 的 "Add" 按钮上传 .zip 文件

### 2. 模型文件位置

**预设模型的文件来源**：
```
xiaomiaobot/packages/stage-ui/src/assets/
├── live2d/models/
│   ├── hiyori_pro_zh.zip       ← presetLive2dProUrl 指向这里
│   ├── hiyori_free_zh.zip      ← presetLive2dFreeUrl 指向这里
│   └── hiyori/preview.png
└── vrm/models/
    ├── AvatarSample-A/
    │   └── AvatarSample_A.vrm  ← presetVrmAvatarAUrl 指向这里
    └── AvatarSample-B/
        └── AvatarSample_B.vrm  ← presetVrmAvatarBUrl 指向这里
```

**注意**：这些文件是在 `stage-ui/src/assets/` 中，**不是** `.cache/` 目录！

### 3. .cache 目录的作用

`.cache/` 目录（如 `.cache/assets/js/CubismSdkForWeb-5-r.3/Samples/Resources/`）中的模型是：
- **Cubism SDK 的示例资源**
- 在**构建时或首次运行时**自动下载/解压
- 用于**开发和测试**，或者被其他系统（如 QQ Bot）使用
- **Web UI 不会自动读取这个目录**

### 4. 加载流程

#### Step 1: 加载预设列表
```typescript
// display-models.ts
async function loadDisplayModelsFromIndexedDB() {
  const models = [...displayModelsPresets]  // 从硬编码的预设开始
  
  // 然后加载用户上传的模型
  await localforage.iterate((val, key) => {
    if (key.startsWith('display-model-')) {
      models.push({ id: key, format: val.format, type: 'file', 
                    file: val.file, name: val.file.name, ... })
    }
  })
  
  displayModels.value = models.sort((a, b) => b.importedAt - a.importedAt)
}
```

#### Step 2: 用户选择模型
```typescript
// stage-model.ts
async function updateStageModel() {
  const model = await displayModelsStore.getDisplayModel(selectedModelId)
  
  if (model.type === 'file') {
    // 用户上传的模型：从 IndexedDB 读取 File 对象，创建 Blob URL
    const nextUrl = URL.createObjectURL(model.file)
    replaceStageModelUrl(nextUrl)
  }
  else {
    // 预设模型：直接使用 URL（指向 stage-ui/src/assets/）
    replaceStageModelUrl(model.url)
  }
}
```

#### Step 3: 渲染模型
```vue
<!-- preview-stage.vue -->
<Live2DScene
  :model-src="stageModelSelectedUrl"  <!-- 这是 blob: URL 或 assets URL -->
  :model-id="stageModelSelected"
/>
```

```typescript
// live2d-zip-loader.ts
// 使用 JSZip 解析 .zip 文件（无论来自 blob: 还是 http:）
ZipLoader.zipReader = (data: Blob, _url: string) => JSZip.loadAsync(data)
```

### 5. 为什么 .cache 目录的模型不显示

**根本原因**：
1. Web 端的模型列表是**静态硬编码**的
2. 只有注册到 `displayModelsPresets` 数组的模型才会显示
3. `.cache/` 目录不在 Web 可访问的路径中（浏览器无法直接访问文件系统）

**技术限制**：
- Web 应用运行在**浏览器沙箱**中
- 不能直接读取本地文件系统（出于安全考虑）
- 只能访问：
  - 打包到应用内的静态资源（`src/assets/`）
  - 用户主动上传的文件（转换为 Blob URL）
  - HTTP(S) URL

---

## 对比：QQ Bot 的模型加载

QQ Bot（Python 端）**可以直接访问 .cache 目录**：

```python
# xiaomiao/character_commands.py
name_map = {
    "夏目": "natsume",
    "亚托莉": "atri",
}

# 直接读取文件系统中的模型
model_path = f".cache/.../Resources/{character_id}/"
```

Python 运行在服务器端，有完整的文件系统访问权限，所以可以直接使用 `.cache/` 中的所有 9 个模型。

---

## 解决方案对比

### 当前状况
- ✅ 4 个预设模型可见（Hiyori x2 + VRM x2）
- ❌ 其他 7 个 Cubism SDK 示例模型不可见
- ❌ ATRI 和 Natsume 不可见

### 方案对比

| 方案 | 优点 | 缺点 | 实现难度 |
|------|------|------|----------|
| **A. 手动上传**<br/>（当前可用） | 无需改代码 | 每次清缓存后需重新上传 | ⭐ 简单 |
| **B. 打包 + 注册**<br/>（推荐） | 永久可用，自动加载 | 增加打包体积<br/>（约 50MB/个模型） | ⭐⭐ 中等 |
| **C. 动态扫描**<br/>（需开发） | 自动发现新模型 | 需要文件系统 API<br/>（浏览器不支持） | ⭐⭐⭐ 困难 |

---

## 总结

1. **Web 模式不直接访问 .cache 目录**
   - 只加载 `stage-ui/src/assets/` 中的预设模型
   - 或用户通过 UI 上传的模型（存储在 IndexedDB）

2. **.cache 目录的模型文件**
   - 存在于文件系统中
   - QQ Bot 可以访问
   - Web UI 无法访问（浏览器沙箱限制）

3. **要在 Web 端显示更多模型**
   - 需要将模型打包为 .zip 放到 `stage-ui/src/assets/live2d/models/`
   - 并在 `display-models.ts` 中注册
   - 或用户手动上传

4. **这是设计上的架构差异**
   - 不是 bug
   - 是 Web 安全模型的必然结果

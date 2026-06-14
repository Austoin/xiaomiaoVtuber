# 如何添加 ATRI 和 Natsume 模型

## 问题
ATRI (588MB) 和 Natsume (84MB) 文件太大，直接加入预设列表会导致页面加载缓慢（可能需要几分钟）。

## 解决方案

### 方案 1：手动上传（推荐）
1. 打开 Web UI：`http://127.0.0.1:5175/settings/models`
2. 点击右上角 "**⊕ Add**" 按钮
3. 选择上传文件：
   - `xiaomiaobot/packages/stage-ui/src/assets/live2d/models/atri.zip`
   - `xiaomiaobot/packages/stage-ui/src/assets/live2d/models/natsume.zip`
4. 模型会保存到浏览器 IndexedDB，下次打开无需重新加载

### 方案 2：取消注释预设（不推荐）
如果你不介意页面加载慢，可以在 `display-models.ts` 中取消注释：

```typescript
// 找到这两行（第 80-81 行）
// { id: 'preset-live2d-9', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetAtriUrl, name: 'ATRI', previewImage: presetAtriPreview, importedAt: 1733113886847 },
// { id: 'preset-live2d-10', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetNatsumeUrl, name: 'Natsume', previewImage: presetNatsumePreview, importedAt: 1733113886848 },

// 删除开头的 // 取消注释
{ id: 'preset-live2d-9', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetAtriUrl, name: 'ATRI', previewImage: presetAtriPreview, importedAt: 1733113886847 },
{ id: 'preset-live2d-10', format: DisplayModelFormat.Live2dZip, type: 'url', url: presetNatsumeUrl, name: 'Natsume', previewImage: presetNatsumePreview, importedAt: 1733113886848 },
```

**缺点**：
- 页面首次加载需要等待 2-5 分钟
- Vite 需要处理 672MB 的资源文件
- 开发服务器启动变慢

## 当前配置
- ✅ 8 个小型 Live2D 模型（已加入预设，快速加载）
- ✅ 2 个 VRM 模型（已加入预设）
- ⚠️ ATRI 和 Natsume（已注释，需要手动上传）

## 文件位置
模型文件已打包并存在于：
- `xiaomiaobot/packages/stage-ui/src/assets/live2d/models/atri.zip` (588MB)
- `xiaomiaobot/packages/stage-ui/src/assets/live2d/models/natsume.zip` (84MB)

这两个文件在 .gitignore 中，不会上传到 git。

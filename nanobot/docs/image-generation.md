# 图像生成

nanobot 可以通过 `generate_image` 工具生成和编辑图像。在 WebUI 中，用户可以从输入框启用 **Image Generation**，选择宽高比，并在同一个聊天中持续迭代生成图像。

该功能默认禁用。请在 `~/.nanobot/config.json` 中启用它，配置受支持的图像 Provider，然后重启 gateway。

## 快速配置

OpenRouter 示例：

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "${OPENROUTER_API_KEY}"
    }
  },
  "tools": {
    "imageGeneration": {
      "enabled": true,
      "provider": "openrouter",
      "model": "openai/gpt-5.4-image-2",
      "defaultAspectRatio": "1:1",
      "defaultImageSize": "1K"
    }
  }
}
```

AIHubMix 示例：

```json
{
  "providers": {
    "aihubmix": {
      "apiKey": "${AIHUBMIX_API_KEY}"
    }
  },
  "tools": {
    "imageGeneration": {
      "enabled": true,
      "provider": "aihubmix",
      "model": "gpt-image-2-free",
      "defaultAspectRatio": "1:1",
      "defaultImageSize": "1K"
    }
  }
}
```

> [!TIP]
> API Key 建议使用环境变量。nanobot 启动时会从环境变量解析 `${VAR_NAME}` 值。

## WebUI 使用方式

在 WebUI 输入框中：

1. 点击 **Image Generation**。
2. 选择宽高比：`Auto`、`1:1`、`3:4`、`9:16`、`4:3` 或 `16:9`。
3. 描述你想要的图像或编辑。
4. 编辑已有图像时，附加参考图。

生成的图像会作为 assistant 媒体显示在聊天中。后续提示词，例如 “make it warmer”、“change the background” 或 “try a 16:9 version”，可以复用最近生成的产物。

WebUI 会向用户隐藏 Provider 的存储细节。agent 会在内部看到已保存的 artifact 路径，并可以将其作为 `reference_images` 传回 `generate_image`，用于迭代编辑。

## 配置参考

| 选项 | 类型 | 默认值 | 说明 |
|--------|------|---------|-------------|
| `tools.imageGeneration.enabled` | boolean | `false` | 注册 `generate_image` 工具 |
| `tools.imageGeneration.provider` | string | `"openrouter"` | 图像 Provider 名称。目前支持 `openrouter` 和 `aihubmix` |
| `tools.imageGeneration.model` | string | `"openai/gpt-5.4-image-2"` | Provider 模型名称 |
| `tools.imageGeneration.defaultAspectRatio` | string | `"1:1"` | 当提示词或工具调用未指定宽高比时使用的默认比例 |
| `tools.imageGeneration.defaultImageSize` | string | `"1K"` | 默认尺寸提示，例如 `1K`、`2K`、`4K` 或 `1024x1024` |
| `tools.imageGeneration.maxImagesPerTurn` | number | `4` | 单次工具调用可接受的最大 `count`。有效范围：`1` 到 `8` |
| `tools.imageGeneration.saveDir` | string | `"generated"` | nanobot 媒体目录下用于保存生成产物的相对目录 |

Provider 设置复用常规 Provider 配置字段：

| 选项 | 说明 |
|--------|-------------|
| `providers.<name>.apiKey` | Provider API Key。推荐使用 `${ENV_VAR}` |
| `providers.<name>.apiBase` | 可选的自定义 base URL |
| `providers.<name>.extraHeaders` | 合并到 Provider 请求中的 Header |
| `providers.<name>.extraBody` | 合并到 Provider 请求体中的额外 JSON 字段 |

camelCase 和 snake_case 配置键都可接受，但文档使用 camelCase，以匹配 `config.json`。

## Provider 说明

### OpenRouter

OpenRouter 使用 chat-completions 风格的图像响应。配置如下：

```json
{
  "tools": {
    "imageGeneration": {
      "enabled": true,
      "provider": "openrouter",
      "model": "openai/gpt-5.4-image-2"
    }
  }
}
```

如果你希望支持参考图编辑，请使用支持图像生成和图像编辑的模型。

### AIHubMix

AIHubMix 的 `gpt-image-2-free` 通过 AIHubMix 统一 predictions API 支持。nanobot 内部会调用：

```text
/v1/models/openai/gpt-image-2-free/predictions
```

配置如下：

```json
{
  "providers": {
    "aihubmix": {
      "apiKey": "${AIHUBMIX_API_KEY}",
      "extraBody": {
        "quality": "low"
      }
    }
  },
  "tools": {
    "imageGeneration": {
      "enabled": true,
      "provider": "aihubmix",
      "model": "gpt-image-2-free"
    }
  }
}
```

`quality: low` 是可选项。它可以让免费图像模型更快，并降低超时概率，但不是正确运行所必需的。

## Artifact

生成图像会存储在当前 nanobot 实例的媒体目录中：

```text
~/.nanobot/media/generated/YYYY-MM-DD/img_<id>.<ext>
~/.nanobot/media/generated/YYYY-MM-DD/img_<id>.json
```

对于非默认配置位置，媒体目录相对于当前活动配置文件所在目录。

JSON sidecar 会保存：

| 字段 | 含义 |
|-------|---------|
| `id` | 短生成图像 ID，例如 `img_ab12cd34ef56` |
| `path` | 内部用于后续编辑的本地图像路径 |
| `mime` | 检测到的图像 MIME 类型 |
| `prompt` | 生成使用的提示词 |
| `model` | Provider 模型 |
| `provider` | Provider 名称 |
| `source_images` | 编辑时使用的参考图路径 |
| `created_at` | 创建时间戳 |

不要把 base64 图像 payload 粘贴到聊天中。除非用户明确要求调试细节，否则 agent 应该将本地 artifact 路径保留在内部。

## 提示词

好的图像提示词应包含：

- 主体和场景。
- 构图、相机或版式。
- 风格、氛围、光线和配色。
- 必须出现在图像中的精确文字，并加引号。
- 约束，例如 “keep the same character” 或 “preserve the logo”。

示例：

```text
A minimal app icon for nanobot: friendly robot head, rounded square, soft blue and white palette, clean vector style, no text
```

编辑时，请描述什么应该改变，以及什么必须保持不变：

```text
Use the reference image. Keep the same robot and composition, change the palette to warm orange, and add a subtle sunrise background.
```

## 故障排查

| 现象 | 检查项 |
|---------|-------|
| `generate_image` 不可用 | 将 `tools.imageGeneration.enabled` 设为 `true` 并重启 gateway |
| 缺少 API Key 错误 | 配置 `providers.<provider>.apiKey`；如果使用 `${VAR_NAME}`，确认 gateway 进程可见该环境变量 |
| `unsupported image generation provider` | 使用 `openrouter` 或 `aihubmix` |
| AIHubMix 报 `Incorrect model ID` | 使用 `model: "gpt-image-2-free"`；nanobot 内部会将其扩展为所需的 `openai/gpt-image-2-free` 模型路径 |
| 生成超时 | 尝试更小或默认图像尺寸，将 AIHubMix `extraBody.quality` 设为 `"low"`，或稍后重试 |
| 参考图被拒绝 | 参考图路径必须位于工作区或 nanobot 媒体目录内，并且必须是有效图像文件 |

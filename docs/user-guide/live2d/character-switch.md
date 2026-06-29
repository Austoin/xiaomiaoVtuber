# Live2D 网页端角色切换指南

> **来源**: Artemis 项目 Live2D 系统  
> **功能**: 在网页端实时切换 Live2D 角色  
> **更新**: 2026-06-13

---

## 🎭 Live2D 是什么？

Live2D 是一个**实时 2D 角色动画系统**，可以让静态的 2D 角色图像"活"起来：

- ✅ **实时动画** - 眨眼、呼吸、表情变化
- ✅ **物理效果** - 头发、衣服随动
- ✅ **情绪表达** - 10+ 种动作组（开心、害羞、生气等）
- ✅ **唇形同步** - 说话时嘴巴动
- ✅ **交互响应** - 鼠标跟踪、点击反馈

---

## 📋 Artemis 的 Live2D 实现

### 技术架构

```
浏览器 (Chrome)
    ↓
index.html (Live2D 渲染页面)
    ↓
pixi-live2d-display v0.5.0 (WebGL 渲染)
    ↓
Cubism Core 4 (Live2D 引擎)
    ↓
live2d-bridge.mjs (Node.js 桥接服务)
    ↓
HTTP API (localhost:19200)
WebSocket (localhost:19201)
```

### 核心文件

```
live2d/
├── index.html                  # 主页面
├── live2d-bridge.mjs          # Node.js 桥接服务
├── pixi.min.js                # PIXI.js v7 渲染引擎
├── live2dcubismcore.min.js    # Cubism Core 4
├── plid-v5-bundle.js          # pixi-live2d-display
└── model/
    └── shiki_natsume/         # 夏目模型
        └── final/
            ├── shiki_natsume.model3.json
            ├── shiki_natsume.moc3
            ├── *.png (贴图)
            ├── *.physics3.json
            └── *.motion3.json
```

---

## 🌐 如何在网页端切换角色

### 方案 1: HTTP API 切换（推荐）

Live2D 桥接服务提供 HTTP API：

#### 启动桥接服务

```bash
cd tool/vendor/Artemis/live2d
node live2d-bridge.mjs
```

服务启动后：
- HTTP API: `http://localhost:19200`
- WebSocket: `ws://localhost:19201`

#### API 端点

```javascript
// 1. 切换表情
fetch('http://localhost:19200/api/expression?name=happy');

// 2. 播放动作
fetch('http://localhost:19200/api/motion?name=tap_body');

// 3. 显示对话气泡
fetch('http://localhost:19200/api/message?text=你好&duration=3000');

// 4. 唇形同步（开始说话）
fetch('http://localhost:19200/api/speak?action=start');

// 5. 唇形同步（停止说话）
fetch('http://localhost:19200/api/speak?action=end');
```

### 方案 2: 修改 index.html 添加切换按钮

创建带角色选择器的版本：

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Live2D - 角色切换</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:100%; height:100%; overflow:hidden; background: #1a1a2e; }
#l2d { width:100%; height:100%; display:flex; align-items:center; justify-content:center; }
canvas { display:block; }

/* 角色选择器样式 */
#character-selector {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    background: rgba(0, 0, 0, 0.8);
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

#character-selector h3 {
    color: #fff;
    font-size: 16px;
    margin-bottom: 10px;
    font-family: Arial, sans-serif;
}

.character-btn {
    display: block;
    width: 120px;
    margin: 5px 0;
    padding: 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    background: #4CAF50;
    color: white;
    font-size: 14px;
    font-family: Arial, sans-serif;
    transition: all 0.3s;
}

.character-btn:hover {
    background: #45a049;
    transform: translateY(-2px);
}

.character-btn.active {
    background: #2196F3;
}

#status {
    position: fixed;
    bottom: 10px;
    left: 10px;
    color: #666;
    font: 12px monospace;
    z-index: 10;
}
</style>
</head>
<body>
<div id="l2d"></div>
<div id="status">loading...</div>

<!-- 角色选择器 -->
<div id="character-selector">
    <h3>🎭 选择角色</h3>
    <button class="character-btn active" onclick="switchCharacter('natsume')">
        四季夏目
    </button>
    <button class="character-btn" onclick="switchCharacter('atri')" disabled>
        亚托莉 (未安装)
    </button>
</div>

<script src="/pixi.min.js"></script>
<!-- ... 其他脚本加载 ... -->

<script>
// 角色配置
const CHARACTERS = {
    natsume: {
        name: '四季夏目',
        modelPath: '/model/shiki_natsume/final/shiki_natsume.model3.json',
        greeting: '……嗯。'
    },
    atri: {
        name: '亚托莉',
        modelPath: '/model/atri/atri.model3.json',
        greeting: 'ATRI 来啦！主人好~ ✨'
    }
};

var MODEL = CHARACTERS.natsume.modelPath;
var currentCharacter = 'natsume';
var app, model;

// 切换角色函数
function switchCharacter(characterId) {
    if (characterId === currentCharacter) return;
    
    const character = CHARACTERS[characterId];
    if (!character) return;
    
    // 更新按钮状态
    document.querySelectorAll('.character-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // 重新加载模型
    MODEL = character.modelPath;
    currentCharacter = characterId;
    
    // 移除旧模型
    if (model && app.stage) {
        app.stage.removeChild(model);
    }
    
    // 加载新模型
    loadModel();
    
    // 显示问候语
    setTimeout(() => {
        fetch(`http://localhost:19200/api/message?text=${encodeURIComponent(character.greeting)}&duration=3000`);
    }, 1000);
}

// 加载模型函数
function loadModel() {
    var L2D = window.PIXI.live2d.Live2DModel;
    var c = document.getElementById('l2d');
    var W = c.clientWidth || 640;
    var H = c.clientHeight || 640;
    
    L2D.from(MODEL, {autoInteract: true}).then(function(m) {
        model = m;
        var s = Math.min(W/model.width, H/model.height) * 0.8;
        model.scale.set(s);
        model.x = W/2;
        model.y = H*0.45;
        model.anchor.set(0.5);
        app.stage.addChild(model);
        document.getElementById('status').textContent = `已加载: ${CHARACTERS[currentCharacter].name}`;
    }).catch(function(e) {
        document.getElementById('status').textContent = 'ERR: ' + (e && e.message || e);
    });
}

// 初始化
function init() {
    var L2D = window.PIXI && window.PIXI.live2d && window.PIXI.live2d.Live2DModel;
    if (!L2D) {
        setTimeout(init, 500);
        return;
    }
    
    var c = document.getElementById('l2d');
    var W = c.clientWidth || 640;
    var H = c.clientHeight || 640;
    
    app = new PIXI.Application({
        width: W,
        height: H,
        backgroundAlpha: 0,
        antialias: true,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true
    });
    
    c.appendChild(app.view);
    loadModel();
}

init();
</script>
</body>
</html>
```

### 方案 3: URL 参数切换

启动时指定角色：

```bash
# 启动夏目
chrome --app=http://localhost:19200/index.html?character=natsume

# 启动 ATRI
chrome --app=http://localhost:19200/index.html?character=atri
```

在 `index.html` 中读取：

```javascript
// 从 URL 获取角色参数
const urlParams = new URLSearchParams(window.location.search);
const characterParam = urlParams.get('character');

if (characterParam && CHARACTERS[characterParam]) {
    MODEL = CHARACTERS[characterParam].modelPath;
    currentCharacter = characterParam;
}
```

---

## 🔗 与 xiaomiaoVirtual 角色系统集成

### 同步角色切换

当在 QQ 中切换角色时，同步到 Live2D：

```python
# xiaomiao/character_commands.py

def handle_character_command(message: str) -> tuple[bool, str]:
    # ... 原有切换逻辑 ...
    
    if success:
        char = CharacterManager.get_current()
        
        # 同步到 Live2D
        try:
            import requests
            requests.get(
                'http://localhost:19200/api/switch-character',
                params={'character': char_id}
            )
        except:
            pass  # Live2D 未启动时忽略
        
        # ... 原有回复逻辑 ...
```

### Live2D 桥接服务添加切换端点

修改 `live2d-bridge.mjs`：

```javascript
// 添加角色切换端点
if (pathname === '/api/switch-character') {
    const character = url.searchParams.get('character') || 'natsume';
    
    // 广播切换事件到前端
    broadcast({ 
        type: 'switch-character', 
        character: character 
    });
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
        ok: true, 
        type: 'switch-character', 
        character: character 
    }));
    return;
}
```

---

## ⚠️ 重要注意事项

### 1. Live2D 模型文件

Live2D 模型**不包含在 xiaomiaoVirtual 中**，原因：

- ❌ **版权限制** - Artemis 的模型可能有版权
- ❌ **文件大小** - 每个模型 10-50 MB
- ❌ **定制需求** - 不同用户需要不同角色

**获取模型的方式**:
1. 从 Artemis 项目复制（仅供学习）
2. 使用 Live2D Cubism 自己制作
3. 购买商用授权的模型
4. 使用开源免费模型

### 2. 模型文件结构

完整的 Live2D 模型需要：

```
model/character_name/
├── character.model3.json    # 主配置文件
├── character.moc3           # 模型数据
├── textures/
│   ├── texture_00.png       # 贴图
│   └── ...
├── character.physics3.json  # 物理效果
├── motions/
│   ├── idle.motion3.json    # 待机动作
│   ├── tap_body.motion3.json
│   └── ...
└── expressions/
    ├── happy.exp3.json      # 表情
    └── ...
```

### 3. Cubism 版本兼容性

- ✅ **Artemis 使用**: Cubism 4
- ❌ **不兼容**: Cubism 5 或 6
- ⚠️ **原因**: pixi-live2d-display v0.5.0 只支持 Cubism 4

### 4. 技术要求

- **浏览器**: Chrome/Edge/Firefox（需要 WebGL 支持）
- **Node.js**: 用于运行桥接服务
- **性能**: 需要 GPU 加速
- **网络**: 本地服务（localhost）

---

## 📚 相关资源

### Artemis 项目
- **路径**: `tool/vendor/Artemis/live2d/`
- **文档**: `tool/vendor/Artemis/skills/live2d/SKILL.md`
- **桥接服务**: `live2d-bridge.mjs`

### Live2D 官方
- **官网**: https://www.live2d.com
- **Cubism SDK**: https://www.live2d.com/sdk/download
- **教程**: https://docs.live2d.com

### 相关库
- **pixi-live2d-display**: https://github.com/guansss/pixi-live2d-display
- **PIXI.js**: https://pixijs.com

### xiaomiaoVirtual
- **角色系统**: `tool/xiaomiao/character_manager.py`
- **QQ 切换**: `docs/QQ_CHARACTER_SWITCH.md`

---

## 🎯 快速开始

### 如果你有 Live2D 模型文件

1. **启动桥接服务**
   ```bash
   cd tool/vendor/Artemis/live2d
   npm install  # 首次需要
   node live2d-bridge.mjs
   ```

2. **在浏览器打开**
   ```
   http://localhost:19200/index.html
   ```

3. **测试 API**
   ```bash
   # 播放动作
   curl "http://localhost:19200/api/motion?name=tap_body"
   
   # 显示消息
   curl "http://localhost:19200/api/message?text=你好"
   ```

---

## 🎉 总结

**是的，Live2D 可以在网页端切换角色！**

### 三种实现方式

1. ✅ **HTTP API** - 通过 API 调用切换
2. ✅ **页面按钮** - 用户手动点击切换
3. ✅ **URL 参数** - 启动时指定角色

### 要在 xiaomiaoVirtual 中使用

✅ **已有的基础**:
- Artemis Live2D 代码（`tool/vendor/Artemis/live2d/`）
- 角色管理系统（`tool/xiaomiao/character_manager.py`）
- QQ 切换命令（`xiaomiao/character_commands.py`）

❌ **需要自行准备**:
- Live2D 模型文件（版权限制）
- 安装 Node.js 和依赖
- 配置桥接服务

### 下一步

如果你想实现 Live2D 功能，你需要：

1. **获取 Live2D 模型文件** 
   - 从 Artemis 复制（学习用）
   - 或自己制作/购买

2. **安装依赖**
   ```bash
   cd tool/vendor/Artemis/live2d
   npm install
   ```

3. **启动服务**
   ```bash
   node live2d-bridge.mjs
   ```

4. **在浏览器访问**
   ```
   http://localhost:19200/index.html
   ```

**需要我帮你创建完整的集成方案吗？** 🎭

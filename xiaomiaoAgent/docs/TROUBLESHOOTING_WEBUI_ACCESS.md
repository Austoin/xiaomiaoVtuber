# 解决 http://127.0.0.1:5174 无法访问问题

## 问题诊断

**现象**: 浏览器无法访问 http://127.0.0.1:5174  
**原因**: 系统代理设置导致本地回环地址也被代理  
**服务状态**: ✅ 服务正常运行（进程 23196, node.exe）

## 解决方案

### 方案一：配置代理跳过本地地址（推荐）

#### Windows 系统代理设置
1. 打开 **设置** → **网络和 Internet** → **代理**
2. 在 **手动设置代理** 中找到 **请勿对以下条目开头的地址使用代理服务器**
3. 添加以下内容：
```
localhost;127.0.0.1;*.local
```
4. 点击**保存**

#### 环境变量设置（临时）
```powershell
# 在 PowerShell 中设置
$env:NO_PROXY = "localhost,127.0.0.1"
$env:no_proxy = "localhost,127.0.0.1"

# 然后在同一个 PowerShell 窗口中打开浏览器
start chrome http://127.0.0.1:5174
```

### 方案二：临时关闭代理

#### 关闭系统代理
1. 打开 **设置** → **网络和 Internet** → **代理**
2. 关闭 **使用代理服务器**
3. 访问 http://127.0.0.1:5174
4. 完成后可重新开启代理

#### 浏览器直连模式
**Chrome/Edge**:
```powershell
# 使用 --no-proxy-server 参数启动
chrome.exe --no-proxy-server http://127.0.0.1:5174
```

### 方案三：使用其他地址

服务可能也绑定在其他地址，尝试：
```
http://localhost:5174
http://0.0.0.0:5174
```

### 方案四：修改服务绑定地址

编辑 `xiaomiaoAgent/webui/vite.config.ts`，确保服务器配置为：
```typescript
export default defineConfig({
  server: {
    host: '127.0.0.1',  // 或 'localhost'
    port: 5174,
    strictPort: true,
  }
})
```

## 验证服务状态

### 命令行测试（跳过代理）
```powershell
# PowerShell
$env:NO_PROXY = "127.0.0.1"
curl http://127.0.0.1:5174

# 或使用 Invoke-WebRequest
Invoke-WebRequest -Uri "http://127.0.0.1:5174" -NoProxy
```

### 检查服务日志
```powershell
# 查看 gateway 日志
cd f:/xiaomiaoVirtual/xiaomiaoAgent
conda activate xiaomiao
python -m xiaomiao_agent gateway --config .nanobot/config.json
```

## 当前服务状态

✅ **服务正在运行**:
- 端口: 5174
- 进程 ID: 23196
- 进程名: node.exe (Vite 开发服务器)
- 监听地址: 127.0.0.1:5174

✅ **HTTP 响应正常**:
- 状态码: 200 OK
- 返回: xiaomiaoAgent Web UI HTML

⚠️ **访问被代理拦截**:
- 代理地址: http://127.0.0.1:7897
- 影响: 本地回环地址被代理，导致浏览器无法直接访问

## 快速解决步骤

1. **临时关闭代理** → 访问 http://127.0.0.1:5174 → 验证可访问
2. **添加代理排除** → localhost,127.0.0.1 → 永久解决
3. **重启浏览器** → 使新的代理设置生效

## 其他可能的问题

### 如果配置代理排除后仍无法访问

1. **浏览器缓存**:
   - 清除浏览器缓存
   - 使用隐私/无痕模式测试

2. **防火墙**:
   - 检查 Windows 防火墙是否阻止了 node.exe
   - 临时关闭防火墙测试

3. **浏览器扩展**:
   - 禁用代理管理扩展（如 SwitchyOmega）
   - 使用默认浏览器配置测试

## 推荐配置

在 PowerShell 配置文件中永久设置：
```powershell
# 编辑 $PROFILE
notepad $PROFILE

# 添加以下内容
$env:NO_PROXY = "localhost,127.0.0.1,*.local"
$env:no_proxy = "localhost,127.0.0.1,*.local"
```

---

**问题定位**: 代理设置导致  
**解决时间**: < 5 分钟  
**优先方案**: 配置代理排除列表

# 安全策略

## 报告安全漏洞

如果你在 nanobot 中发现安全漏洞，请按以下方式报告：

1. **不要** 创建公开 GitHub Issue。
2. 在 GitHub 上创建私有安全公告，或联系仓库维护者（xubinrencs@gmail.com）。
3. 请包含以下信息：
   - 漏洞描述。
   - 复现步骤。
   - 潜在影响。
   - 建议修复方式（如有）。

我们目标是在 48 小时内响应安全报告。

## 安全最佳实践

### 1. API Key 管理

**关键要求**：绝不要把 API Key 提交到版本控制。

```bash
# ✅ 好做法：存入权限受限的配置文件
chmod 600 ~/.nanobot/config.json

# ❌ 坏做法：把 Key 硬编码到代码中或提交到仓库
```

**建议：**

- 将 API Key 存储在 `~/.nanobot/config.json`，并将文件权限设置为 `0600`。
- 对敏感 Key 考虑使用环境变量。
- 生产部署中使用操作系统 keyring 或凭据管理器。
- 定期轮换 API Key。
- 开发环境和生产环境使用不同的 API Key。

### 2. 通道访问控制

**重要**：生产使用时务必配置 `allowFrom` 列表。

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["123456789", "987654321"]
    },
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+1234567890"]
    }
  }
}
```

**安全说明：**

- 在 `v0.1.4.post3` 及更早版本中，空 `allowFrom` 会允许所有用户访问。自 `v0.1.4.post4` 起，空 `allowFrom` 默认拒绝所有访问；如果要显式允许所有人，请设置为 `["*"]`。
- 可从 `@userinfobot` 获取你的 Telegram 用户 ID。
- WhatsApp 请使用包含国家区号的完整手机号。
- 定期检查访问日志，关注未授权访问尝试。

### 3. Shell 命令执行

`exec` 工具可以执行 shell 命令。虽然危险命令模式会被阻止，但你仍应：

- ✅ **启用 bwrap 沙箱**（`"tools.exec.sandbox": "bwrap"`）以获得内核级隔离（仅 Linux）。
- ✅ 审查 agent 日志中的所有工具使用记录。
- ✅ 理解 agent 正在运行哪些命令。
- ✅ 使用权限受限的专用用户账号。
- ✅ 不要以 root 身份运行 nanobot。
- ❌ 不要禁用安全检查。
- ❌ 未经仔细审查，不要在包含敏感数据的系统上运行。

**Exec 沙箱（bwrap）：**

在 Linux 上，将 `"tools.exec.sandbox": "bwrap"` 设为启用，即可用 [bubblewrap](https://github.com/containers/bubblewrap) 沙箱包裹每个 shell 命令。它使用 Linux 内核 namespace 限制进程可见范围：

- 工作区目录 → **可读写**（agent 可正常工作）。
- 媒体目录 → **只读**（可读取上传附件）。
- 系统目录（`/usr`、`/bin`、`/lib`）→ **只读**（命令仍可工作）。
- 配置文件和 API Key（`~/.nanobot/config.json`）→ **隐藏**（由 tmpfs 遮蔽）。

需要安装 `bwrap`（`apt install bubblewrap`）。官方 Docker 镜像已预装。**macOS 或 Windows 不可用**，因为 bubblewrap 依赖 Linux 内核 namespace。

启用沙箱也会自动为文件工具启用 `restrictToWorkspace`。

**阻止的模式：**

- `rm -rf /` - 删除根文件系统。
- Fork bomb。
- 文件系统格式化（`mkfs.*`）。
- 原始磁盘写入。
- 其他破坏性操作。

### 4. 文件系统访问

文件操作包含路径穿越保护，但仍需注意：

- ✅ 启用 `restrictToWorkspace` 或 bwrap 沙箱来限制文件访问范围。
- ✅ 使用专用用户账号运行 nanobot。
- ✅ 使用文件系统权限保护敏感目录。
- ✅ 定期审计日志中的文件操作。
- ❌ 不要授予对敏感文件的不受限访问。

### 5. 网络安全

**API 调用：**

- 所有外部 API 调用默认使用 HTTPS。
- 已配置超时，避免请求长时间挂起。
- 如有需要，可使用防火墙限制出站连接。

**WhatsApp Bridge：**

- Bridge 绑定到 `127.0.0.1:3001`（仅 localhost，外部网络不可访问）。
- 在配置中设置 `bridgeToken`，可启用 Python 与 Node.js 之间的共享密钥认证。
- 妥善保护 `~/.nanobot/whatsapp-auth` 中的认证数据（权限模式 0700）。

### 6. 依赖安全

**关键要求**：保持依赖为最新安全版本。

```bash
# 检查存在漏洞的依赖
pip install pip-audit
pip-audit

# 更新到最新安全版本
pip install --upgrade nanobot-ai
```

Node.js 依赖（WhatsApp bridge）：

```bash
cd bridge
npm audit
npm audit fix
```

**重要说明：**

- 保持 `litellm` 为最新版本，以获取安全修复。
- 我们已将 `ws` 更新到 `>=8.17.1` 以修复 DoS 漏洞。
- 定期运行 `pip-audit` 或 `npm audit`。
- 订阅 nanobot 及其依赖的安全公告。

### 7. 生产部署

生产使用时：

1. **隔离环境**

   ```bash
   # 在容器或 VM 中运行
   docker run --rm -it python:3.11
   pip install nanobot-ai
   ```

2. **使用专用用户**

   ```bash
   sudo useradd -m -s /bin/bash nanobot
   sudo -u nanobot nanobot gateway
   ```

3. **设置正确权限**

   ```bash
   chmod 700 ~/.nanobot
   chmod 600 ~/.nanobot/config.json
   chmod 700 ~/.nanobot/whatsapp-auth
   ```

4. **启用日志**

   ```bash
   # 配置日志监控
   tail -f ~/.nanobot/logs/nanobot.log
   ```

5. **使用速率限制**

   - 在 API Provider 侧配置速率限制。
   - 监控异常用量。
   - 为 LLM API 设置消费上限。

6. **定期更新**

   ```bash
   # 每周检查更新
   pip install --upgrade nanobot-ai
   ```

### 8. 开发环境与生产环境

**开发环境：**

- 使用独立 API Key。
- 使用非敏感数据测试。
- 启用详细日志。
- 使用测试 Telegram Bot。

**生产环境：**

- 使用带消费上限的专用 API Key。
- 限制文件系统访问。
- 启用审计日志。
- 定期进行安全审查。
- 监控异常活动。

### 9. 数据隐私

- **日志可能包含敏感信息**，请妥善保护日志文件。
- **LLM Provider 会看到你的提示词**，请审查它们的隐私政策。
- **聊天历史存储在本地**，请保护 `~/.nanobot` 目录。
- **API Key 以纯文本形式保存**，生产环境请使用操作系统 keyring。

### 10. 事件响应

如果你怀疑发生安全事件：

1. **立即吊销泄露的 API Key**。
2. **检查日志中的未授权访问**。

   ```bash
   grep "Access denied" ~/.nanobot/logs/nanobot.log
   ```

3. **检查是否存在异常文件修改**。
4. **轮换所有凭据**。
5. **更新到最新版本**。
6. **向维护者报告事件**。

## 安全功能

### 内置安全控制

✅ **输入校验**

- 文件操作中的路径穿越保护。
- 危险命令模式检测。
- HTTP 请求输入长度限制。

✅ **认证**

- 基于允许列表的访问控制：在 `v0.1.4.post3` 及更早版本中，空 `allowFrom` 会允许所有人访问；自 `v0.1.4.post4` 起，空列表会拒绝所有访问（`["*"]` 才会显式允许所有人）。
- 认证失败尝试日志。

✅ **资源保护**

- 命令执行超时（默认 60 秒）。
- 输出截断（10KB 限制）。
- HTTP 请求超时（10-30 秒）。

✅ **安全通信**

- 所有外部 API 调用使用 HTTPS。
- Telegram API 使用 TLS。
- WhatsApp bridge：仅 localhost 绑定，并支持可选 token 认证。

## 已知限制

⚠️ **当前安全限制：**

1. **无速率限制** - 用户可以发送无限消息（如有需要请自行添加）。
2. **纯文本配置** - API Key 以纯文本保存（生产环境请使用 keyring）。
3. **无会话管理** - 没有自动会话过期机制。
4. **命令过滤有限** - 只阻止明显危险的模式（Linux 上请启用 bwrap 沙箱获得内核级隔离）。
5. **无完整审计轨迹** - 安全事件日志有限（请按需增强）。

## 安全检查清单

部署 nanobot 前：

- [ ] API Key 已安全存储（不在代码中）。
- [ ] 配置文件权限已设为 0600。
- [ ] 所有通道已配置 `allowFrom` 列表。
- [ ] 以非 root 用户运行。
- [ ] Linux 部署已启用 exec 沙箱（`"tools.exec.sandbox": "bwrap"`）。
- [ ] 文件系统权限已正确限制。
- [ ] 依赖已更新到最新安全版本。
- [ ] 已监控日志中的安全事件。
- [ ] API Provider 已配置速率限制。
- [ ] 已制定备份和灾难恢复计划。
- [ ] 已审查自定义 skill/tool 的安全性。

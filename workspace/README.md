# xiaomiaoVirtual 工作区

这个目录是项目本地资源工作区。

运行时下载文件和生成物按用途分组：

- `downloads/qq/`：从 QQ 接收并保存给 Agent 工具读取的文件。
- `artifacts/`：后续需要检查的生成物。
- `tmp/`：短期本地临时文件。

不要提交用户下载资源或生成物。git 中只保留这份目录说明和占位文件。

完整的文件追踪和清理规则见 `../docs/file-workspace-hygiene.md`。

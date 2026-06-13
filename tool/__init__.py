"""
xiaomiaoVirtual 统一工具层

将所有工具、记忆层和第三方依赖集中管理，提供统一的访问接口。

目录结构：
- core/: 核心工具（文件系统、Shell、搜索、MCP 等）
- xiaomiao/: 项目专属工具（markitdown、scrapling、舞台动作等）
- memory/: 记忆层（存储、整理、Dream）
- vendor/: 第三方源码
- adapters/: 调用适配器（xiaomiaoAgent、QQ Bot、TUI）
"""

__version__ = "1.0.0"
__all__ = ["core", "xiaomiao", "memory", "vendor", "adapters"]

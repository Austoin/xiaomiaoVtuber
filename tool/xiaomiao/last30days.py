"""Last30Days 研究工具

通过多平台搜索（Reddit、X、YouTube、GitHub 等）聚合最近 30 天的信息。

功能：
- 多源搜索：Reddit、X/Twitter、YouTube、HN、GitHub、Polymarket 等
- 智能预研究：自动解析相关账号、subreddit、频道
- 深度内容：YouTube 转录、Reddit 评论、实时参与度
- HTML 简报：可分享的独立报告文件

依赖：
- Python 3.12+
- yt-dlp (可选，用于 YouTube)
- 各平台 API key (可选)

使用示例：
```python
from tool.xiaomiao.last30days import last30days_research

# 基础研究
result = last30days_research("Cursor IDE")

# HTML 报告
result = last30days_research("OpenAI vs Anthropic", emit="html")

# 自定义保存路径
result = last30days_research("topic", save_dir="~/Research", verbose=True)
```
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

# 配置日志
logger = logging.getLogger(__name__)

# last30days-skill 脚本路径
TOOL_DIR = Path(__file__).parent.parent
LAST30DAYS_SCRIPT = TOOL_DIR / "vendor" / "last30days-skill" / "skills" / "last30days" / "scripts" / "last30days.py"
LAST30DAYS_DIR = LAST30DAYS_SCRIPT.parent.parent.parent.parent

# 默认配置
DEFAULT_TIMEOUT = 300  # 5 分钟
DEFAULT_SAVE_DIR = Path.home() / "Documents" / "Last30Days"


class Last30DaysTool:
    """Last30Days 研究工具封装"""

    name = "last30days_research"
    description = """搜索最近 30 天的多平台信息（Reddit、X、YouTube、GitHub 等）。

    参数：
    - topic: 研究主题（人物、公司、产品、技术等）
    - emit: 输出格式（compact/html，默认 compact）
    - save_dir: 保存目录（默认 ~/Documents/Last30Days/）
    - timeout: 超时时间（秒，默认 300）
    - verbose: 是否显示详细输出

    返回：研究报告的 Markdown 或 HTML 文本和保存路径。
    """

    @staticmethod
    def check_available() -> tuple[bool, str]:
        """
        检查工具是否可用

        Returns:
            (是否可用, 状态消息)
        """
        # 检查脚本文件
        if not LAST30DAYS_SCRIPT.exists():
            return False, f"last30days.py 未找到: {LAST30DAYS_SCRIPT}"

        # 检查 Python 版本
        if sys.version_info < (3, 12):
            return False, f"需要 Python 3.12+，当前版本: {sys.version_info.major}.{sys.version_info.minor}"

        # 检查依赖目录
        if not LAST30DAYS_DIR.exists():
            return False, f"last30days-skill 目录未找到: {LAST30DAYS_DIR}"

        return True, "可用"

    @staticmethod
    def get_status() -> dict[str, Any]:
        """
        获取工具状态信息

        Returns:
            状态字典，包含版本、依赖、配置等信息
        """
        available, msg = Last30DaysTool.check_available()

        status = {
            "available": available,
            "message": msg,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "script_path": str(LAST30DAYS_SCRIPT),
            "script_exists": LAST30DAYS_SCRIPT.exists(),
            "save_dir": str(DEFAULT_SAVE_DIR),
            "timeout": DEFAULT_TIMEOUT,
        }

        # 检查可选依赖
        try:
            import yt_dlp
            status["yt_dlp"] = "已安装"
        except ImportError:
            status["yt_dlp"] = "未安装（YouTube 功能不可用）"

        # 检查环境变量配置
        env_keys = [
            "LAST30DAYS_MEMORY_DIR",
            "SCRAPECREATORS_API_KEY",
            "BRAVE_SEARCH_API_KEY",
            "OPENROUTER_API_KEY",
        ]
        status["env_config"] = {
            key: "已配置" if os.environ.get(key) else "未配置"
            for key in env_keys
        }

        return status

    @staticmethod
    def execute(
        topic: str,
        emit: str = "compact",
        save_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        verbose: bool = False,
        **kwargs
    ) -> dict[str, Any]:
        """
        执行 last30days 研究

        Args:
            topic: 研究主题（必需）
            emit: 输出格式（compact 或 html，默认 compact）
            save_dir: 保存目录（可选，默认 ~/Documents/Last30Days/）
            timeout: 超时时间（秒，默认 300）
            verbose: 是否显示详细输出
            **kwargs: 其他参数（如 save_suffix 等）

        Returns:
            {
                "success": bool,        # 是否成功
                "output": str,          # 研究报告内容
                "save_path": str,       # 保存路径
                "error": str,           # 错误信息（如果有）
                "duration": float,      # 执行时间（秒）
                "return_code": int      # 命令返回码
            }
        """
        import time
        start_time = time.time()

        # 检查可用性
        available, msg = Last30DaysTool.check_available()
        if not available:
            logger.error(f"工具不可用: {msg}")
            return {
                "success": False,
                "output": "",
                "save_path": "",
                "error": msg,
                "duration": 0,
                "return_code": -1
            }

        # 检查主题
        if not topic or not topic.strip():
            error_msg = "研究主题不能为空"
            logger.error(error_msg)
            return {
                "success": False,
                "output": "",
                "save_path": "",
                "error": error_msg,
                "duration": 0,
                "return_code": -1
            }

        # 构建命令
        cmd = [sys.executable, str(LAST30DAYS_SCRIPT), topic.strip()]

        if emit:
            cmd.extend(["--emit", emit])

        if save_dir:
            cmd.extend(["--save-dir", save_dir])

        # 添加其他参数
        for key, value in kwargs.items():
            if key == "save_suffix" and value:
                cmd.extend(["--save-suffix", str(value)])

        timeout_value = timeout or DEFAULT_TIMEOUT

        if verbose:
            logger.info(f"执行命令: {' '.join(cmd)}")
            logger.info(f"工作目录: {LAST30DAYS_SCRIPT.parent}")
            logger.info(f"超时时间: {timeout_value}秒")

        try:
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_value,
                cwd=LAST30DAYS_SCRIPT.parent,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"}
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                output = result.stdout
                # 从输出中提取保存路径
                save_path = ""
                for line in output.split("\n"):
                    if "Saved to:" in line or "saved to" in line.lower():
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            save_path = parts[1].strip()
                        break

                if verbose:
                    logger.info(f"执行成功，耗时 {duration:.2f}秒")
                    if save_path:
                        logger.info(f"报告保存到: {save_path}")

                return {
                    "success": True,
                    "output": output,
                    "save_path": save_path,
                    "error": "",
                    "duration": duration,
                    "return_code": result.returncode
                }
            else:
                error_msg = result.stderr or f"命令返回码: {result.returncode}"
                logger.error(f"执行失败: {error_msg}")

                return {
                    "success": False,
                    "output": result.stdout,
                    "save_path": "",
                    "error": error_msg,
                    "duration": duration,
                    "return_code": result.returncode
                }

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            error_msg = f"执行超时（超过 {timeout_value} 秒）"
            logger.error(error_msg)

            return {
                "success": False,
                "output": "",
                "save_path": "",
                "error": error_msg,
                "duration": duration,
                "return_code": -2
            }
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"执行失败: {str(e)}"
            logger.exception(error_msg)

            return {
                "success": False,
                "output": "",
                "save_path": "",
                "error": error_msg,
                "duration": duration,
                "return_code": -3
            }


# 便捷函数
def last30days_research(
    topic: str,
    emit: str = "compact",
    save_dir: Optional[str] = None,
    timeout: Optional[int] = None,
    verbose: bool = False,
    **kwargs
) -> dict[str, Any]:
    """
    执行 last30days 研究的便捷函数

    Args:
        topic: 研究主题
        emit: 输出格式（compact 或 html）
        save_dir: 保存目录
        timeout: 超时时间（秒）
        verbose: 是否显示详细输出
        **kwargs: 其他参数

    Returns:
        研究结果字典
    """
    return Last30DaysTool.execute(
        topic=topic,
        emit=emit,
        save_dir=save_dir,
        timeout=timeout,
        verbose=verbose,
        **kwargs
    )


__all__ = ["Last30DaysTool", "last30days_research"]

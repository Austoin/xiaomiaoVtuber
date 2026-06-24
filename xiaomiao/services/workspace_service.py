"""
工作区服务 - 文件和工作区管理

整合自:
- qq_workspace.py
"""
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import aiohttp
import aiofiles

logger = logging.getLogger(__name__)


class WorkspaceService:
    """工作区服务"""

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        初始化工作区服务

        Args:
            workspace_root: 工作区根目录
        """
        if workspace_root is None:
            workspace_root = Path(__file__).parent.parent.parent / "workspace"

        self.workspace_root = workspace_root
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        logger.info(f"工作区服务初始化: {self.workspace_root}")

    async def download_file(
        self,
        url: str,
        filename: Optional[str] = None,
        subfolder: Optional[str] = None,
    ) -> Path:
        """
        下载文件到工作区

        Args:
            url: 文件 URL
            filename: 保存的文件名
            subfolder: 子文件夹

        Returns:
            文件路径
        """
        if not filename:
            filename = Path(url).name or "download"

        # 确定保存路径
        if subfolder:
            save_dir = self.workspace_root / subfolder
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            save_dir = self.workspace_root

        save_path = save_dir / filename

        logger.info(f"下载文件: {url} -> {save_path}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        raise Exception(f"下载失败: {resp.status}")

                    async with aiofiles.open(save_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            await f.write(chunk)

            logger.info(f"文件下载完成: {save_path}")
            return save_path

        except Exception as e:
            logger.error(f"文件下载失败: {e}", exc_info=True)
            raise

    async def upload_file(
        self,
        file_path: Path,
        destination: str,
    ) -> str:
        """
        上传文件（占位符）

        Args:
            file_path: 本地文件路径
            destination: 目标位置

        Returns:
            上传后的 URL
        """
        # TODO: 实现文件上传
        logger.info(f"上传文件: {file_path} -> {destination}")
        return f"uploaded://{file_path.name}"

    def list_files(
        self,
        subfolder: Optional[str] = None,
        pattern: str = "*",
    ) -> List[Path]:
        """
        列出工作区文件

        Args:
            subfolder: 子文件夹
            pattern: 文件模式

        Returns:
            文件路径列表
        """
        if subfolder:
            search_dir = self.workspace_root / subfolder
        else:
            search_dir = self.workspace_root

        if not search_dir.exists():
            return []

        files = list(search_dir.glob(pattern))
        return sorted(files)

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            文件信息
        """
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        stat = file_path.stat()
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir(),
        }

    def clean_workspace(
        self,
        subfolder: Optional[str] = None,
        keep_recent: int = 10,
    ) -> int:
        """
        清理工作区

        Args:
            subfolder: 子文件夹
            keep_recent: 保留最近的 N 个文件

        Returns:
            删除的文件数
        """
        files = self.list_files(subfolder=subfolder)

        # 按修改时间排序
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        # 删除旧文件
        deleted = 0
        for file in files[keep_recent:]:
            try:
                if file.is_file():
                    file.unlink()
                    deleted += 1
                    logger.debug(f"删除文件: {file}")
            except Exception as e:
                logger.error(f"删除文件失败 {file}: {e}")

        if deleted > 0:
            logger.info(f"清理工作区: 删除 {deleted} 个文件")

        return deleted

    def get_workspace_size(self) -> int:
        """获取工作区总大小（字节）"""
        total_size = 0
        for file in self.workspace_root.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
        return total_size


# 全局工作区服务实例
workspace_service = WorkspaceService()

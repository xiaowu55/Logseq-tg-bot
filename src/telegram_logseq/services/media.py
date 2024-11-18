from pathlib import Path
from typing import Optional
from telegram import Message
from loguru import logger

from ..config.settings import settings
from ..utils.text_utils import TextUtils


class MediaService:
    """媒体服务类"""

    def __init__(self):
        """初始化服务"""
        self.assets_dir = Path("assets")
        self.assets_dir.mkdir(exist_ok=True)

    async def handle_media(self, message: Message) -> Optional[str]:
        """处理媒体消息

        Args:
            message: Telegram 消息对象

        Returns:
            媒体文件路径或 None
        """
        try:
            # 获取文件
            if message.photo:
                file = message.photo[-1]  # 获取最大尺寸的图片
                extension = ".jpg"
            elif message.document:
                file = message.document
                extension = Path(file.file_name).suffix if file.file_name else ".file"
            else:
                return None

            # 下载文件
            file_obj = await file.get_file()

            # 生成文件名
            filename = TextUtils.clean_title(message.caption or "media")
            if not filename:
                filename = file.file_unique_id

            # 确保文件名唯一
            filepath = self._get_unique_filepath(filename, extension)

            # 保存文件
            await file_obj.download_to_drive(filepath)

            logger.info(f"保存媒体文件: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"处理媒体文件失败: {e}")
            return None

    def _get_unique_filepath(self, filename: str, extension: str) -> Path:
        """获取唯一的文件路径

        Args:
            filename: 文件名
            extension: 扩展名

        Returns:
            唯一的文件路径
        """
        base_path = self.assets_dir / f"{filename}{extension}"
        if not base_path.exists():
            return base_path

        # 如果文件已存在，添加数字后缀
        counter = 1
        while True:
            new_path = self.assets_dir / f"{filename}_{counter}{extension}"
            if not new_path.exists():
                return new_path
            counter += 1

    def get_media_url(self, filepath: str) -> str:
        """获取媒体文件的 URL

        Args:
            filepath: 文件路径

        Returns:
            媒体文件 URL
        """
        # 将本地路径转换为相对路径
        relative_path = Path(filepath).relative_to(self.assets_dir)
        return f"![{relative_path}](../assets/{relative_path})"

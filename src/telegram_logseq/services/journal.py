from datetime import datetime
from typing import Optional
from pathlib import Path
from loguru import logger

from ..config.settings import settings


class JournalService:
    """日志服务类"""

    def __init__(self):
        """初始化服务"""
        self.journals_path = (
            Path.cwd() / settings.GITHUB_REPO / settings.JOURNALS_FOLDER
        )
        self.journals_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"日志目录: {self.journals_path}")

    def get_journal_path(self) -> Path:
        """获取当前日志文件路径"""
        date = datetime.now()
        filename = (
            date.strftime(settings.JOURNALS_FILES_FORMAT)
            + settings.JOURNALS_FILES_EXTENSION
        )
        if settings.JOURNALS_PREFIX != "none":
            filename = f"{settings.JOURNALS_PREFIX}{filename}"
        return self.journals_path / filename

    def get_current_time(self) -> str:
        """获取当前时间字符串"""
        if not settings.TIMESTAMP_ENTRIES:
            return ""

        date = datetime.now()
        if settings.HOUR_24:
            return date.strftime("%H:%M")
        return date.strftime("%I:%M %p")

    async def add_entry(self, content: str) -> Path:
        """添加日志条目

        Args:
            content: 条目内容

        Returns:
            日志文件路径
        """
        try:
            # 获取日志文件路径
            path = self.get_journal_path()
            logger.debug(f"日志文件路径: {path}")

            # 创建日志目录
            path.parent.mkdir(parents=True, exist_ok=True)

            # 格式化条目
            time_str = self.get_current_time()
            if time_str:
                entry = f"{settings.DEFAULT_INDENT_LEVEL} {time_str} {content}\n"
            else:
                entry = f"{settings.DEFAULT_INDENT_LEVEL} {content}\n"

            # 写入文件
            with open(path, "a", encoding="utf-8") as f:
                f.write(entry)

            logger.info(f"添加日志条目到 {path}")
            return path

        except Exception as e:
            logger.error(f"添加日志条目失败: {e}")
            raise  # 让错误向上传播，而不是返回 None

    async def get_entries(self, date: Optional[datetime] = None) -> str:
        """获取日志条目

        Args:
            date: 日期，默认为当前日期

        Returns:
            日志内容
        """
        try:
            journal_path = self._get_journal_path(date)
            if not journal_path.exists():
                return ""

            with open(journal_path, "r", encoding="utf-8") as f:
                return f.read()

        except Exception as e:
            logger.error(f"获取日志条目失败: {e}")
            return ""

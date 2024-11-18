from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from pathlib import Path
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
import os

from ..config.settings import settings
from ..constants.messages import messages
from ..services.github import GitHubService
from ..services.journal import JournalService
from ..services.media import MediaService
from ..utils.time_utils import TimeUtils
from ..utils.text_utils import TextUtils
from ..utils.web_utils import get_web_page_title


class MessageHandler:
    """消息处理器类"""

    def __init__(self):
        """初始化处理器"""
        self.journal_service = JournalService()
        self.media_service = MediaService()
        self.github_service = GitHubService()

    def get_url_title(self, url: str) -> str:
        """获取 URL 的标题"""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else urlparse(url).netloc
            return title.strip()
        except:
            return urlparse(url).netloc

    async def handle_text(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """处理文本消息"""
        try:
            text = update.message.text

            # 检查是否是自定义路径格式: >>path/to/file: content
            custom_path_match = re.match(r"^>>([^:]+):\s*(.+)$", text)

            if custom_path_match:
                # 提取路径和内容
                file_path, content = custom_path_match.groups()
                # 确保路径以 .md 结尾
                if not file_path.endswith(".md"):
                    file_path += ".md"
                # 构建完整路径
                full_path = Path.cwd() / settings.GITHUB_REPO / file_path

                # 创建目录
                full_path.parent.mkdir(parents=True, exist_ok=True)

                # 添加内容到文件
                with open(full_path, "a", encoding="utf-8") as f:
                    f.write(f"{content}\n")

                # 提交到 GitHub
                with open(full_path, "r", encoding="utf-8") as f:
                    file_content = f.read()

                await self.github_service.commit_and_push(
                    message=f"更新文件: {file_path}",
                    path=file_path,
                    content=file_content,
                )

                await update.message.reply_text(f"已添加到 {file_path}")

            else:
                # 处理 TODO
                if text.lower().startswith("todo"):
                    content = f"- LATER {text[4:].strip()}"
                else:
                    content = text

                # 添加到默认的日志文件
                path = await self.journal_service.add_entry(content)
                if not path:
                    raise Exception("添加日志条目失败")

                # 获取文件内容
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 提交到 GitHub
                relative_path = str(path.relative_to(Path.cwd() / settings.GITHUB_REPO))
                success = await self.github_service.commit_and_push(
                    message="更新日志", path=relative_path, content=content
                )

                if success:
                    await update.message.reply_text("已添加到日志")
                else:
                    await update.message.reply_text("提交到 GitHub 失败")

        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            await update.message.reply_text(f"添加失败: {str(e)}")

    async def handle_media(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """处理媒体消息"""
        try:
            # 获取文件
            if update.message.photo:
                # 如果是图片，获取最大尺寸的版本
                file = await context.bot.get_file(update.message.photo[-1].file_id)
                file_ext = ".jpg"
            else:
                # 如果是文档
                file = await context.bot.get_file(update.message.document.file_id)
                file_ext = os.path.splitext(update.message.document.file_name)[1]

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}{file_ext}"

            # 构建保存路径
            assets_path = Path.cwd() / settings.GITHUB_REPO / "assets"
            assets_path.mkdir(parents=True, exist_ok=True)
            file_path = assets_path / filename

            # 下载文件
            await file.download_to_drive(file_path)

            # 生成 LogSeq 格式的引用
            media_ref = f"![{filename}](/assets/{filename})"

            # 添加到日志
            path = await self.journal_service.add_entry(media_ref)
            if not path:
                raise Exception("添加日志条目失败")

            # 提交文件和日志
            # 1. 提交文件
            with open(file_path, "rb") as f:
                file_content = f.read()
            await self.github_service.commit_and_push(
                message=f"添加媒体文件: {filename}",
                path=f"assets/{filename}",
                content=file_content,
                is_binary=True,
            )

            # 2. 提交日志
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            relative_path = str(path.relative_to(Path.cwd() / settings.GITHUB_REPO))
            await self.github_service.commit_and_push(
                message="更新日志", path=relative_path, content=content
            )

            await update.message.reply_text("媒体文件已保存")

        except Exception as e:
            logger.error(f"处理媒体文件失败: {e}")
            await update.message.reply_text(f"保存媒体文件失败: {str(e)}")

    async def handle_photo(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """处理图片消息"""
        try:
            # 获取最大尺寸的图片
            photo = update.message.photo[-1]

            # 下载图片
            file = await context.bot.get_file(photo.file_id)

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.jpg"

            # 构建保存路径
            assets_path = Path.cwd() / settings.GITHUB_REPO / "assets"
            assets_path.mkdir(parents=True, exist_ok=True)
            file_path = assets_path / filename

            # 保存图片
            await file.download_to_drive(file_path)

            # 生成 LogSeq 格式的图片引用
            image_ref = f"![{filename}](../assets/{filename})"

            # 添加到日志
            path = await self.journal_service.add_entry(image_ref)
            if not path:
                raise Exception("添加日志条目失败")

            # 提交图片和日志
            # 1. 提交图片
            with open(file_path, "rb") as f:
                image_content = f.read()
            await self.github_service.commit_and_push(
                message=f"添加图片: {filename}",
                path=f"assets/{filename}",
                content=image_content,
                is_binary=True,
            )

            # 2. 提交日志
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            relative_path = str(path.relative_to(Path.cwd() / settings.GITHUB_REPO))
            await self.github_service.commit_and_push(
                message="更新日志", path=relative_path, content=content
            )

            await update.message.reply_text("图片已保存")

        except Exception as e:
            logger.error(f"处理图片失败: {e}")
            await update.message.reply_text(f"保存图片失败: {str(e)}")

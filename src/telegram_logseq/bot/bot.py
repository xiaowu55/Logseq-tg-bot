from typing import Optional, List
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PicklePersistence,
    filters,
)
from loguru import logger

from ..config.settings import settings
from ..services.scheduler import SchedulerService
from .handlers import commands, messages, callbacks


class LogseqBot:
    """Logseq 机器人主类"""

    def __init__(self):
        """初始化机器人"""
        self.persistence = PicklePersistence(filename="persistence")
        self.app: Optional[Application] = None

    async def initialize(self) -> None:
        """初始化应用"""
        self.app = (
            Application.builder()
            .token(settings.BOT_TOKEN)
            .persistence(self.persistence)
            .build()
        )

        # 注册命令处理器
        self._register_command_handlers()
        # 注册消息处理器
        self._register_message_handlers()
        # 注册回调查询处理器
        self._register_callback_handlers()

        # 设置定时任务
        await SchedulerService.setup_jobs(self.app, settings.BOT_AUTHORIZED_IDS)

    def _register_command_handlers(self) -> None:
        """注册命令处理器"""
        if not self.app:
            return

        self.app.add_handler(CommandHandler("start", commands.start_command))
        self.app.add_handler(CommandHandler("uptime", commands.uptime_command))
        self.app.add_handler(CommandHandler("ver", commands.version_command))
        self.app.add_handler(CommandHandler("help", commands.help_command))
        self.app.add_handler(CommandHandler("anno", commands.hypothesis_command))
        self.app.add_handler(CommandHandler("srs", commands.srs_command))
        self.app.add_handler(CommandHandler("themes", commands.themes_command))
        # ... 其他命令处理器

    def _register_message_handlers(self) -> None:
        """注册消息处理器"""
        if not self.app:
            return

        self.app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, messages.handle_text_message
            )
        )
        self.app.add_handler(
            MessageHandler(filters.PHOTO, messages.handle_photo_message)
        )

    def _register_callback_handlers(self) -> None:
        """注册回调查询处理器"""
        if not self.app:
            return

        self.app.add_handler(
            CallbackQueryHandler(callbacks.handle_show_answer, pattern="SHOW_ANSWER")
        )
        self.app.add_handler(
            CallbackQueryHandler(callbacks.handle_answer_feedback, pattern="ansrfdbk")
        )
        self.app.add_handler(
            CallbackQueryHandler(callbacks.handle_skip, pattern="SKIP")
        )
        self.app.add_handler(
            CallbackQueryHandler(callbacks.handle_cancel, pattern="CANCEL")
        )
        self.app.add_handler(
            CallbackQueryHandler(
                callbacks.handle_theme_switcher, pattern="ThemeSwitcher"
            )
        )

    async def start(self) -> None:
        """启动机器人"""
        if not self.app:
            await self.initialize()

        logger.info(f"启动 {settings.BOT_NAME}...")
        await self.app.initialize()
        await self.app.start()
        await self.app.run_polling()

    async def stop(self) -> None:
        """停止机器人"""
        if self.app:
            logger.info("停止机器人...")
            await self.app.stop()

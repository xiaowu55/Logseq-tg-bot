from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from loguru import logger
import nest_asyncio
import asyncio

from .config.settings import settings
from .handlers.messages import MessageHandler as MsgHandler
from .services.calendar import CalendarService
from .handlers.commands import (
    start_command,
    help_command,
    pull_now_command,
    mindmap_command,
    anno_command,
)

# 允许嵌套事件循环
nest_asyncio.apply()


async def start():
    """启动机器人"""
    try:
        # 初始化服务
        calendar_service = CalendarService()
        await calendar_service.generate_calendar()

        # 创建应用
        application = ApplicationBuilder().token(settings.BOT_TOKEN).build()

        # 注册命令处理器
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("pull", pull_now_command))
        application.add_handler(CommandHandler("mindmap", mindmap_command))
        application.add_handler(CommandHandler("anno", anno_command))

        # 注册消息处理器
        message_handler = MsgHandler()
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler.handle_text)
        )
        application.add_handler(
            MessageHandler(
                filters.PHOTO | filters.Document.ALL, message_handler.handle_media
            )
        )

        # 启动机器人
        logger.info("正在启动 Lupin Bot...")
        await application.run_polling()

    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise


def main():
    """主函数"""
    asyncio.run(start())


if __name__ == "__main__":
    main()

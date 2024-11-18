from telegram import Update
from telegram.ext import CallbackContext
from loguru import logger

from ..services.mindmap import MindmapService
from ..services.github import GitHubService
from ..services.hypothesis import HypothesisService

# 初始化服务
mindmap_service = MindmapService()
github_service = GitHubService()
hypothesis_service = HypothesisService()


async def start_command(update: Update, context: CallbackContext) -> None:
    """开始命令"""
    await update.message.reply_text("欢迎使用 Logseq Bot!")


async def help_command(update: Update, context: CallbackContext) -> None:
    """帮助命令"""
    help_text = (
        "欢迎使用 Logseq Bot!\n\n"
        "可用命令：\n"
        "/start - 开始使用\n"
        "/help - 显示此帮助信息\n"
        "/pull - 从 GitHub 拉取最新内容\n"
        "/mindmap <页面名> - 生成思维导图\n"
        "/anno <URL> - 获取网页标注\n\n"
        "功能说明：\n"
        "1. 直接发送消息 - 添加到当天的日志\n"
        "2. TODO + 内容 - 自动转换为待办事项\n"
        "3. >>path/to/file: 内容 - 添加到指定文件\n"
        "4. 发送图片或文件 - 自动保存到 assets 目录\n"
        "5. 思维导图 - 将页面内容转换为可视化的思维导图\n"
        "6. 网页标注 - 获取指定网页的 Hypothesis 标注\n"
    )
    await update.message.reply_text(help_text)


async def pull_now_command(update: Update, context: CallbackContext) -> None:
    """立即拉取命令"""
    try:
        success = await github_service.pull()
        if success:
            await update.message.reply_text("拉取成功")
        else:
            await update.message.reply_text("拉取失败")
    except Exception as e:
        logger.error(f"拉取失败: {e}")
        await update.message.reply_text(f"拉取失败: {str(e)}")


async def mindmap_command(update: Update, context: CallbackContext) -> None:
    """思维导图命令"""
    try:
        if not context.args:
            await update.message.reply_text("请指定页面名称")
            return

        page_name = " ".join(context.args)
        html_path = await mindmap_service.generate_mindmap(page_name)

        with open(html_path, "rb") as f:
            await update.message.reply_document(
                document=f, filename=f"{page_name}.html", caption="思维导图已生成"
            )

    except FileNotFoundError:
        await update.message.reply_text("页面不存在")
    except Exception as e:
        logger.error(f"生成思维导图失败: {e}")
        await update.message.reply_text(f"生成思维导图失败: {str(e)}")


async def hypothesis_command(update: Update, context: CallbackContext) -> None:
    """Hypothesis 同步命令"""
    if not hypothesis_service:
        await update.message.reply_text("Hypothesis 功能未启用，请先配置 Token")
        return

    try:
        count = await hypothesis_service.sync_annotations()
        await update.message.reply_text(f"同步完成，共同步 {count} 条标注")
    except Exception as e:
        logger.error(f"同步 Hypothesis 失败: {e}")
        await update.message.reply_text(f"同步失败: {str(e)}")


async def anno_command(update: Update, context: CallbackContext) -> None:
    """获取网页标注命令"""
    try:
        if not context.args:
            await update.message.reply_text("请提供网页 URL")
            return

        url = context.args[0]
        await update.message.reply_text(f"正在获取 {url} 的标注...")

        # 获取标注
        annotations = await hypothesis_service.get_annotations(url)
        if not annotations:
            await update.message.reply_text("未找到标注")
            return

        # 生成 Markdown
        content = await hypothesis_service.generate_markdown(annotations)

        # 保存并提交
        await hypothesis_service.save_annotations(content)
        await update.message.reply_text("标注已保存")

    except Exception as e:
        logger.error(f"获取标注失败: {e}")
        await update.message.reply_text(f"获取标注失败: {str(e)}")

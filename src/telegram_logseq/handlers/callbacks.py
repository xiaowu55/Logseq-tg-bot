from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger

from ..config.settings import settings
from ..constants.messages import messages
from ..services.flashcard import FlashcardService
from ..services.mindmap import MindmapService


async def handle_flashcard_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """处理闪卡回调"""
    if not update.callback_query or not update.effective_chat:
        return

    query = update.callback_query
    data = query.data

    if not data.startswith("fc_"):
        return

    # 解析回调数据
    _, action, card_id = data.split("_")
    flashcard_service = FlashcardService()

    if action == "show":
        # 显示答案
        card = await flashcard_service.get_flashcard(card_id)
        if not card:
            await query.edit_message_text("找不到闪卡")
            return

        keyboard = [
            [
                InlineKeyboardButton("简单 (5)", callback_data=f"fc_rate_{card_id}_5"),
                InlineKeyboardButton("一般 (3)", callback_data=f"fc_rate_{card_id}_3"),
                InlineKeyboardButton("困难 (0)", callback_data=f"fc_rate_{card_id}_0"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"问题：{card['question']}\n\n答案：{card['answer']}",
            reply_markup=reply_markup,
        )
    elif action == "rate":
        # 评分并获取下一张卡片
        _, quality = card_id.split("_")
        card = await flashcard_service.rate_flashcard(card_id, int(quality))

        if card:
            await show_flashcard(
                update.effective_chat.id,
                context,
                card,
                context.user_data.get("current_card", 1),
                context.user_data.get("total_cards", settings.FLASHCARD_DAILY_GOAL),
            )
        else:
            await query.edit_message_text("复习完成！")

    await query.answer()


async def handle_mindmap_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """处理思维导图回调"""
    if not update.callback_query or not update.effective_chat:
        return

    query = update.callback_query
    data = query.data

    if not data.startswith("mm_"):
        return

    # 解析回调数据
    _, action, page_title = data.split("_", 2)
    mindmap_service = MindmapService()

    if action == "generate":
        await query.edit_message_text("正在生成思维导图...")
        html_content = await mindmap_service.generate_mindmap(page_title)

        if html_content:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=html_content.encode(),
                filename=f"{page_title}_mindmap.html",
            )
        else:
            await query.edit_message_text(
                messages.BOT_MESSAGES["FILENOTFOUND_MESSAGE"].format(page_title)
            )

    await query.answer()


async def show_flashcard(
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
    card: dict,
    current: int,
    total: int,
) -> None:
    """显示闪卡

    Args:
        chat_id: 聊天 ID
        context: 上下文
        card: 闪卡数据
        current: 当前卡片序号
        total: 总卡片数
    """
    keyboard = [
        [InlineKeyboardButton("显示答案", callback_data=f"fc_show_{card['id']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"卡片 {current}/{total}\n\n问题：{card['question']}",
        reply_markup=reply_markup,
    )

    # 保存进度
    context.user_data["current_card"] = current
    context.user_data["total_cards"] = total

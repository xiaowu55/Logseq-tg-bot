from typing import Dict


class Messages:
    """消息常量类"""

    # Bot 消息
    BOT_MESSAGES: Dict[str, str] = {
        # 基础消息
        "START_MESSAGE": "你好！我是 Lupin，一个用于增强 LogSeq 功能的 Telegram 机器人。",
        "HELP_MESSAGE": """可用命令:
/start - 欢迎消息
/uptime - 显示运行时间
/ver - 显示版本信息
/help - 显示帮助信息
/anno URL - 导入 Hypothesis 注释
/importFC - 导入闪卡
/srs [数量] - 开始闪卡复习
/getMM 页面标题 - 生成思维导图
/pullnow - 立即同步
/encryptall - 加密图谱
/decryptall - 解密图谱""",
        "UNAUTHORIZED_MESSAGE": "抱歉，您没有使用此机器人的权限。",
        # 闪卡相关
        "IMPORTINGFC_MESSAGE": "正在导入闪卡...",
        "IMPORTEDFC_MESSAGE": "导入完成！新增 {} 张卡片，更新 {} 张卡片。",
        "NOPENDIGCARDS_MESSAGE": "当前没有需要复习的卡片。",
        "FLASHCARD_OPTIONS": "请评价这张卡片的难度：",
        "SHOW_ANSWER": "显示答案",
        "NEXTROUND_MESSAGE": "下次复习时间：",
        "SKIPPED_MESSAGE": "已跳过此卡片",
        "CANCELLED_MESSAGE": "已取消复习",
        # 思维导图相关
        "NOPAGEMM_MESSAGE": "请指定要生成思维导图的页面标题。",
        "FILEREQ_MESSAGE": "正在生成思维导图...",
        "FILENOTFOUND_MESSAGE": "未找到页面：{}",
        # Git 相关
        "PULL_MESSAGE": "正在同步...",
        "PULLDONE_MESSAGE": "同步完成！",
        "ENCRYPTINGGRAPH_MESSAGE": "正在加密图谱...",
        "ENCRYPTDONE_MESSAGE": "加密完成！",
        "DECRYPTINGRAPH_MESSAGE": "正在解密图谱...",
        "DECRYPTDONE_MESSAGE": "解密完成！",
        # 日志相关
        "JOURNALENTRY_MESSAGE": "已添加到日志：\n{}",
        "IMAGEUPLOAD_MESSAGE": "图片已上传并添加到日志。",
    }

    # Git 消息
    GIT_MESSAGES: Dict[str, str] = {
        "COMMIT_MESSAGE": "{} - {}",  # bot名称, 时间戳
    }

    # 按钮文本
    BUTTONS: Dict[str, str] = {
        "SHOW_ANSWER": "显示答案",
        "SKIP": "跳过...",
        "CANCEL": "取消",
    }


# 全局消息实例
messages = Messages()

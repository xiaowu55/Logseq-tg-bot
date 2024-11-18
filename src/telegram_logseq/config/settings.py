import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pathlib import Path
import configparser


class Settings(BaseSettings):
    """配置类"""

    def __init__(self, **kwargs):
        # 读取配置文件
        config = configparser.ConfigParser()
        config_path = Path("config") / "config.ini"
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        # 使用 UTF-8 编码读取配置文件
        with open(config_path, "r", encoding="utf-8") as f:
            config.read_file(f)

        # 从配置文件读取设置
        settings_dict = {
            "BOT_TOKEN": config.get("Bot", "BotToken"),
            "BOT_NAME": config.get("Bot", "BotName", fallback="Logseq-lupin"),
            "BOT_AUTHORIZED_IDS": [
                int(id.strip()) for id in config.get("Bot", "AuthorizedIds").split(",")
            ],
            "GITHUB_TOKEN": config.get("GitHub", "Token"),
            "GITHUB_BRANCH": config.get("GitHub", "Branch"),
            "GITHUB_USER": config.get("GitHub", "User"),
            "GITHUB_REPO": config.get("GitHub", "Repo"),
            "GITHUB_AUTHOR": config.get("GitHub", "Author"),
            "GITHUB_EMAIL": config.get("GitHub", "Email"),
            "GITHUB_UPDATE_FREQUENCY": config.getint(
                "GitHub", "UpdateFrequency", fallback=720
            ),
            "AGE_PUBLIC_KEY": config.get("AgeEncryption", "PublicKey", fallback=None),
            "AGE_PRIVATE_KEY": config.get("AgeEncryption", "PrivateKey", fallback=None),
            "AGE_ENCRYPTED": config.getboolean(
                "AgeEncryption", "Encrypted", fallback=False
            ),
            "HOUR_24": config.getboolean("Journal", "Hour24", fallback=True),
            "DEFAULT_INDENT_LEVEL": config.get(
                "Journal", "DefaultIndentLevel", fallback="##"
            ),
            "TIMESTAMP_ENTRIES": config.getboolean(
                "Journal", "TimestampEntries", fallback=True
            ),
            "JOURNALS_FOLDER": "journals",
            "JOURNALS_PREFIX": config.get("Journal", "JournalsPrefix", fallback="none"),
            "JOURNALS_FILES_FORMAT": config.get(
                "Journal", "JournalsFilesFormat", fallback="%Y_%m_%d"
            ),
            "JOURNALS_FILES_EXTENSION": config.get(
                "Journal", "JournalsFilesExtension", fallback=".md"
            ),
            "BOOKMARK_TAG": config.get("Journal", "BookmarkTag", fallback="#bookmark"),
            "FLASHCARD_DAILY_GOAL": config.getint(
                "Flashcard", "DailyGoal", fallback=10
            ),
            "FLASHCARD_TAG": config.get("Flashcard", "Tag", fallback="#flashcard"),
            "HYPOTHESIS_TOKEN": config.get("Hypothesis", "Token", fallback=None),
        }

        super().__init__(**settings_dict)

    # Bot 配置
    BOT_TOKEN: str
    BOT_NAME: str = "Lupin"
    BOT_AUTHORIZED_IDS: List[int]

    # GitHub 配置
    GITHUB_TOKEN: str
    GITHUB_BRANCH: str = "master"
    GITHUB_USER: str
    GITHUB_REPO: str
    GITHUB_AUTHOR: str
    GITHUB_EMAIL: str
    GITHUB_UPDATE_FREQUENCY: int = 720

    # AGE 加密配置
    AGE_PUBLIC_KEY: Optional[str] = None
    AGE_PRIVATE_KEY: Optional[str] = None
    AGE_ENCRYPTED: bool = False

    # 日志配置
    HOUR_24: bool = True
    DEFAULT_INDENT_LEVEL: str = "##"
    TIMESTAMP_ENTRIES: bool = True
    JOURNALS_FOLDER: str = "journals"
    JOURNALS_PREFIX: str = "none"
    JOURNALS_FILES_FORMAT: str = "%Y_%m_%d"
    JOURNALS_FILES_EXTENSION: str = ".md"

    # 闪卡配置
    FLASHCARD_DAILY_GOAL: int = 10
    FLASHCARD_TAG: str = "#flashcard"

    # Hypothesis 配置
    HYPOTHESIS_TOKEN: Optional[str] = None

    # 添加 BOOKMARK_TAG 属性
    BOOKMARK_TAG: str = "#bookmark"

    def is_bot_authorized(self, chat_id: int) -> bool:
        """检查是否是授权的聊天 ID"""
        return chat_id in self.BOT_AUTHORIZED_IDS

    def set_graph_encrypted(self, state: bool) -> None:
        """设置图谱加密状态"""
        self.AGE_ENCRYPTED = state
        # 更新配置文件
        config = configparser.ConfigParser()
        config.read("config.ini")
        config.set("AgeEncryption", "AgeEncrypted", str(state).lower())
        with open("config.ini", "w") as f:
            config.write(f)

    class Config:
        """Pydantic 配置"""

        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

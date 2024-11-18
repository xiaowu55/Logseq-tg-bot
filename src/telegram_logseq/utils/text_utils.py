import re
from typing import Dict, Optional, List
from ..config.settings import settings


class TextUtils:
    """文本处理工具类"""

    @staticmethod
    def clean_title(title: str) -> str:
        """清理标题

        Args:
            title: 原始标题

        Returns:
            清理后的标题
        """
        # 移除特殊字符
        title = re.sub(r'[\\/*?:"<>|]', "", title)
        # 移除多余空格
        title = " ".join(title.split())
        return title

    @staticmethod
    def extract_tags(text: str) -> List[str]:
        """提取标签

        Args:
            text: 原始文本

        Returns:
            标签列表
        """
        # 匹配 #tag 或 [[tag]] 格式
        pattern = r"#[\w-]+|\[\[([^\]]+)\]\]"
        matches = re.finditer(pattern, text)
        tags = []

        for match in matches:
            tag = match.group(1) if match.group(1) else match.group(0)
            if tag.startswith("#"):
                tag = tag[1:]  # 移除 #
            tags.append(tag)

        return tags

    @staticmethod
    def extract_metadata(text: str) -> Dict[str, str]:
        """提取元数据

        Args:
            text: 原始文本

        Returns:
            元数据字典
        """
        metadata = {}
        pattern = r"^([^:]+)::(.+)$"

        for line in text.split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                metadata[key] = value

        return metadata

    @staticmethod
    def format_entry(text: str, indent_level: Optional[str] = None) -> str:
        """格式化条目

        Args:
            text: 原始文本
            indent_level: 缩进级别

        Returns:
            格式化后的文本
        """
        if not indent_level:
            indent_level = settings.DEFAULT_INDENT_LEVEL

        # 添加缩进
        if not text.startswith(indent_level):
            text = f"{indent_level} {text}"

        return text

    @staticmethod
    def replace_commands(text: str, commands_map: Dict[str, str]) -> str:
        """替换命令

        Args:
            text: 原始文本
            commands_map: 命令映射

        Returns:
            替换后的文本
        """

        def replace(match):
            command = match.group(0)
            return commands_map.get(command, command)

        pattern = "|".join(rf"\b{re.escape(s)}\b" for s in commands_map)
        return re.sub(pattern, replace, text)

    @staticmethod
    def extract_url(text: str) -> Optional[str]:
        """提取 URL

        Args:
            text: 原始文本

        Returns:
            URL 或 None
        """
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        match = re.search(url_pattern, text)
        return match.group(0) if match else None

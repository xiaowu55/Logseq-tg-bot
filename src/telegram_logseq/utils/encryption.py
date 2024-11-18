from typing import Optional
from loguru import logger


class AgeEncryption:
    """AGE 加密工具类（暂时禁用）"""

    def __init__(self):
        """初始化加密工具"""
        logger.warning("AGE 加密功能暂时禁用")
        self.public_key = None
        self.private_key = None

    def encrypt(self, content: str) -> str:
        """加密内容（暂时禁用）"""
        return content

    def decrypt(self, content: str) -> str:
        """解密内容（暂时禁用）"""
        return content

import requests
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime
from pathlib import Path
import json

from ..config.settings import settings


class HypothesisService:
    """Hypothesis 服务"""

    def __init__(self):
        """初始化服务"""
        self.token = settings.HYPOTHESIS_TOKEN
        self.api_url = "https://api.hypothes.is/api"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def get_annotations(self, url: str) -> list:
        """获取指定 URL 的标注

        Args:
            url: 网页 URL

        Returns:
            标注列表
        """
        try:
            response = requests.get(
                f"{self.api_url}/search",
                headers=self.headers,
                params={"uri": url, "limit": 200},
            )
            response.raise_for_status()
            return response.json()["rows"]
        except Exception as e:
            logger.error(f"获取标注失败: {e}")
            raise

    async def generate_markdown(self, annotations: list) -> str:
        """生成 Markdown 内容

        Args:
            annotations: 标注列表

        Returns:
            Markdown 内容
        """
        if not annotations:
            return ""

        url = annotations[0]["uri"]
        content = f"source:: {url}\n\n"

        for anno in annotations:
            text = anno.get("text", "")
            quote = anno.get("quote", "")
            created = datetime.fromisoformat(anno["created"].replace("Z", "+00:00"))

            content += f"- {created.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if quote:
                content += f"  - > {quote}\n"
            if text:
                content += f"  - Note: {text}\n"

        return content

    async def save_annotations(self, content: str) -> None:
        """保存标注内容

        Args:
            content: Markdown 内容
        """
        try:
            # 保存到文件
            filename = f"hypothesis_{datetime.now().strftime('%Y%m%d')}.md"
            file_path = Path.cwd() / settings.GITHUB_REPO / "pages" / filename

            with open(file_path, "a", encoding="utf-8") as f:
                f.write(content + "\n")

        except Exception as e:
            logger.error(f"保存标注失败: {e}")
            raise

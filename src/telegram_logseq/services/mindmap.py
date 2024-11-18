from pathlib import Path
from loguru import logger
import re
from bs4 import BeautifulSoup

from ..config.settings import settings


class MindmapService:
    """思维导图服务"""

    def __init__(self):
        """初始化服务"""
        self.repo_path = Path.cwd() / settings.GITHUB_REPO

    def parse_markdown(self, content: str) -> dict:
        """解析 Markdown 内容为树形结构

        Args:
            content: Markdown 内容

        Returns:
            树形结构
        """
        lines = content.split("\n")
        root = {"name": "Root", "children": []}
        stack = [(root, -1)]

        for line in lines:
            if not line.strip():
                continue

            # 计算缩进级别
            indent = len(re.match(r"^\s*", line).group())
            content = re.sub(r"^\s*[-*+]\s*", "", line.strip())

            # 创建节点
            node = {"name": content, "children": []}

            # 找到正确的父节点
            while stack and stack[-1][1] >= indent:
                stack.pop()

            if stack:
                stack[-1][0]["children"].append(node)

            stack.append((node, indent))

        return root

    def generate_html(self, data: dict) -> str:
        """生成 HTML 格式的思维导图

        Args:
            data: 树形结构数据

        Returns:
            HTML 内容
        """
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>MindMap</title>
            <script src="https://cdn.jsdelivr.net/npm/markmap-view"></script>
        </head>
        <body>
            <div id="mindmap"></div>
            <script>
                const data = %s;
                window.markmap.Markmap.create('#mindmap', null, data);
            </script>
        </body>
        </html>
        """

        return html_template % str(data).replace("'", '"')

    async def generate_mindmap(self, page_name: str) -> str:
        """生成思维导图

        Args:
            page_name: 页面名称

        Returns:
            HTML 内容路径
        """
        try:
            # 构建文件路径
            if not page_name.endswith(".md"):
                page_name += ".md"
            page_path = self.repo_path / "pages" / page_name

            # 读取文件内容
            if not page_path.exists():
                raise FileNotFoundError(f"页面不存在: {page_name}")

            with open(page_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 解析 Markdown 内容为树形结构
            data = self.parse_markdown(content)

            # 生成 HTML 格式的思维导图
            html = self.generate_html(data)

            # 保存 HTML 文件
            output_path = (
                self.repo_path / "mindmaps" / f"{page_name.replace('.md', '.html')}"
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)

            return str(output_path)

        except Exception as e:
            logger.error(f"生成思维导图失败: {e}")
            raise

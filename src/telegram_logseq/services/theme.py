from typing import List, Tuple, Optional
from github import Github, Repository, ContentFile
from loguru import logger

from ..config.settings import settings
from ..constants.messages import messages
from .github import GitHubService


class ThemeService:
    """主题服务类"""

    def __init__(self):
        self.github = Github(settings.GITHUB_TOKEN)
        self.repo = self.github.get_repo(
            f"{settings.GITHUB_USER}/{settings.GITHUB_REPO}"
        )
        self.github_service = GitHubService()

    async def get_all_themes(self) -> List[Tuple[str, ContentFile]]:
        """获取所有可用主题

        Returns:
            List[Tuple[str, ContentFile]]: [(主题名, 主题文件内容), ...]
        """
        try:
            all_themes = []
            contents = self.repo.get_contents("/logseq")

            while contents:
                content = contents.pop(0)
                if "custom.css" in content.path and content.path != "logseq/custom.css":
                    theme_name = content.path.replace("logseq/", "").replace(
                        ".custom.css", ""
                    )
                    all_themes.append((theme_name, content))

            return all_themes

        except Exception as e:
            logger.error(f"获取主题列表失败: {e}")
            return []

    async def switch_theme(self, css_file: ContentFile) -> bool:
        """切换主题

        Args:
            css_file: Github ContentFile 对象

        Returns:
            bool: 是否切换成功
        """
        try:
            css_content = await self.github_service.get_file_content(css_file)
            if not css_content:
                return False

            await self.github_service.push_file(
                path="logseq/custom.css",
                message=messages.GIT_MESSAGES["COMMIT_MESSAGE"].format(
                    settings.BOT_NAME, self.github_service.get_timestamp()
                ),
                content=css_content,
                branch=settings.GITHUB_BRANCH,
                update=True,
            )
            return True

        except Exception as e:
            logger.error(f"切换主题失败: {e}")
            return False

from github import Github, InputGitAuthor
from git import Repo
from loguru import logger
from pathlib import Path
import base64

from ..config.settings import settings


class GitHubService:
    """GitHub 服务类"""

    def __init__(self):
        """初始化服务"""
        try:
            # 初始化 GitHub API
            self.g = Github(settings.GITHUB_TOKEN)
            self.repo = self.g.get_repo(
                f"{settings.GITHUB_USER}/{settings.GITHUB_REPO}"
            )
            self.author = InputGitAuthor(settings.GITHUB_AUTHOR, settings.GITHUB_EMAIL)
            logger.info(
                f"Git 仓库初始化成功: {settings.GITHUB_USER}/{settings.GITHUB_REPO}"
            )
        except Exception as e:
            logger.error(f"初始化 Git 仓库失败: {e}")
            raise

    async def pull(self) -> bool:
        """从 GitHub 拉取最新内容

        Returns:
            是否成功
        """
        try:
            # 获取所有文件
            contents = self.repo.get_contents("", ref=settings.GITHUB_BRANCH)

            # 遍历所有文件
            while contents:
                file_content = contents.pop(0)

                if file_content.type == "dir":
                    # 如果是目录，添加其内容到遍历列表
                    contents.extend(
                        self.repo.get_contents(
                            file_content.path, ref=settings.GITHUB_BRANCH
                        )
                    )
                else:
                    # 如果是文件，下载内容
                    try:
                        # 获取文件路径
                        local_path = (
                            Path.cwd() / settings.GITHUB_REPO / file_content.path
                        )

                        # 创建目录
                        local_path.parent.mkdir(parents=True, exist_ok=True)

                        # 解码并保存文件
                        content = base64.b64decode(file_content.content).decode("utf-8")
                        with open(local_path, "w", encoding="utf-8") as f:
                            f.write(content)

                        logger.debug(f"已下载: {file_content.path}")

                    except Exception as e:
                        logger.error(f"下��文件失败 {file_content.path}: {e}")
                        continue

            logger.info("拉取完成")
            return True

        except Exception as e:
            logger.error(f"拉取失败: {e}")
            return False

    async def commit_and_push(
        self, message: str, path: str, content: str | bytes, is_binary: bool = False
    ) -> bool:
        """提交并推送更改

        Args:
            message: 提交信息
            path: 文件路径
            content: 文件内容
            is_binary: 是否是二进制文件

        Returns:
            是否成功
        """
        try:
            # 获取文件
            try:
                file = self.repo.get_contents(path, ref=settings.GITHUB_BRANCH)
                # 更新文件
                if is_binary:
                    content = base64.b64encode(content).decode()
                self.repo.update_file(
                    path=file.path,
                    message=message,
                    content=content,
                    sha=file.sha,
                    branch=settings.GITHUB_BRANCH,
                    author=self.author,
                )
            except:
                # 创建新文件
                if is_binary:
                    content = base64.b64encode(content).decode()
                self.repo.create_file(
                    path=path,
                    message=message,
                    content=content,
                    branch=settings.GITHUB_BRANCH,
                    author=self.author,
                )

            logger.info(f"提交成功: {path}")
            return True

        except Exception as e:
            logger.error(f"提交失败: {e}")
            return False

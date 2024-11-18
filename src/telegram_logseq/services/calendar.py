from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

from ..config.settings import settings


class CalendarService:
    """日历服务类"""

    def __init__(self):
        """初始化服务"""
        self.repo_path = Path.cwd() / settings.GITHUB_REPO

    async def generate_calendar(self) -> bool:
        """生成日历页面

        Returns:
            是否成功
        """
        try:
            # 获取当前日期
            now = datetime.now()

            # 生成日历内容
            content = [
                "- Calendar",
                "  - [[journals]]",
                "    - [[journals/{}]]".format(now.strftime("%Y_%m_%d")),
                "    - [[journals/{}]]".format(
                    (now - timedelta(days=1)).strftime("%Y_%m_%d")
                ),
                "    - [[journals/{}]]".format(
                    (now - timedelta(days=2)).strftime("%Y_%m_%d")
                ),
                "    - [[journals/{}]]".format(
                    (now - timedelta(days=3)).strftime("%Y_%m_%d")
                ),
                "    - [[journals/{}]]".format(
                    (now - timedelta(days=4)).strftime("%Y_%m_%d")
                ),
                "    - [[journals/{}]]".format(
                    (now - timedelta(days=5)).strftime("%Y_%m_%d")
                ),
                "    - [[journals/{}]]".format(
                    (now - timedelta(days=6)).strftime("%Y_%m_%d")
                ),
            ]

            # 保存日历文件
            calendar_path = self.repo_path / "pages/Calendar.md"
            calendar_path.parent.mkdir(parents=True, exist_ok=True)

            with open(calendar_path, "w", encoding="utf-8") as f:
                f.write("\n".join(content))

            logger.info("日历生成成功")
            return True

        except Exception as e:
            logger.error(f"生成日历失败: {e}")
            return False

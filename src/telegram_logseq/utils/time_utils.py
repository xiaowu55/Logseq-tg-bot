from datetime import datetime
from ..config.settings import settings


class TimeUtils:
    """时间工具类"""

    @staticmethod
    def get_current_time() -> str:
        """获取当前时间

        Returns:
            格式化的时间字符串
        """
        if not settings.TIMESTAMP_ENTRIES:
            return ""

        now = datetime.now()
        if settings.HOUR_24:
            return now.strftime("%H:%M")
        else:
            return now.strftime("%I:%M %p")

    @staticmethod
    def get_uptime(boot_time: datetime) -> tuple:
        """获取运行时间

        Args:
            boot_time: 启动时间

        Returns:
            (天数, 小时数, 分钟数, 秒数) 元组
        """
        delta = datetime.now() - boot_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return days, hours, minutes, seconds

    @staticmethod
    def format_uptime(days: int, hours: int, minutes: int, seconds: int) -> str:
        """格式化运行时间

        Args:
            days: 天数
            hours: 小时数
            minutes: 分钟数
            seconds: 秒数

        Returns:
            格式化的运行时间字符串
        """
        parts = []
        if days > 0:
            parts.append(f"{days} 天")
        if hours > 0:
            parts.append(f"{hours} 小时")
        if minutes > 0:
            parts.append(f"{minutes} 分钟")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} 秒")

        return " ".join(parts)

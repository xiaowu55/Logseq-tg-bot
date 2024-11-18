from datetime import datetime, timedelta

__all__ = ["SM2"]  # 明确指定导出的类


class SM2:
    """SuperMemo 2 算法实现"""

    @staticmethod
    def calculate(
        quality: int, interval: int, repetitions: int, easiness: float
    ) -> tuple[int, int, float]:
        """计算下一次复习的间隔

        Args:
            quality: 复习质量 (0-5)
            interval: 当前间隔（天）
            repetitions: 重复次数
            easiness: 简易度因子

        Returns:
            (新间隔, 新重复次数, 新简易度)
        """
        # 更新简易度因子
        easiness = max(
            1.3, easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        )

        # 如果回答错误，重置重复次数
        if quality < 3:
            repetitions = 0
        else:
            repetitions += 1

        # 计算新间隔
        if repetitions <= 1:
            interval = 1
        elif repetitions == 2:
            interval = 6
        else:
            interval = round(interval * easiness)

        return interval, repetitions, easiness

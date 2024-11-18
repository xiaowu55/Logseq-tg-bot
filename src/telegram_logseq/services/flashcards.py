from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
import pickle
from pathlib import Path
import random
from loguru import logger

from ..config.settings import settings
from ..utils.text_utils import TextUtils


@dataclass
class Flashcard:
    """闪卡数据类"""

    question: str
    answer: str
    source: str
    next: float = datetime(2021, 1, 1).timestamp()
    last_answered: float = datetime(2021, 1, 1).timestamp()
    history: List[int] = None

    def __post_init__(self):
        if self.history is None:
            self.history = []

    def update_properties(self, next_time: float, history: List[int]) -> None:
        """更新闪卡属性"""
        self.next = next_time
        self.history = history

    def __repr__(self) -> str:
        return f"[{self.question}][{self.answer}][{self.next}][{self.source}][{self.history}]"


class FlashcardService:
    """闪卡服务类"""

    SEPARATOR = "#"
    DB_FILE = "flashcards.db"

    @classmethod
    def scan_for_flashcards(cls, content: str) -> List[Flashcard]:
        """扫描内容中的闪卡"""
        cards = []
        cls._build_flashcard_list(content, cards)
        return cards

    @classmethod
    def _build_flashcard_list(cls, content: str, cards: List[Flashcard]) -> None:
        """构建闪卡列表"""
        lines = content.split("\n")
        source = ""
        i = 0

        while i < len(lines):
            line = lines[i]

            if "title:" in line.lower():
                source = line.strip()

            if settings.FLASHCARDS_TAG in line:
                card_indent = cls._count_indent(line)
                is_sub = True
                i += 1
                card = Flashcard("-1", "-1", source)

                while is_sub and i < len(lines):
                    current_indent = cls._count_indent(lines[i])

                    if current_indent == card_indent + 1:
                        if card.question != "-1":
                            cards.append(card)
                        card = Flashcard("-1", "-1", source)
                        card.question = lines[i][current_indent:].strip()
                        i += 1
                    elif current_indent > card_indent + 1:
                        answer = cls._process_answer(lines[i], current_indent)
                        if card.answer == "-1":
                            card.answer = ""
                        card.answer += answer.strip() + "\n"
                        i += 1
                    else:
                        is_sub = False
                        i -= 1

                if card.answer != "-1":
                    cards.append(card)
            i += 1

    @classmethod
    def save_flashcards_db(
        cls, flashcard_list: List[Flashcard], force: bool = False
    ) -> Tuple[int, int]:
        """保存闪卡数据库"""
        db_path = Path(cls.DB_FILE)

        if force:
            cls._save_db(flashcard_list)
            return len(flashcard_list), 0

        if not db_path.exists():
            cls._save_db(flashcard_list)
            return len(flashcard_list), 0

        # 更新现有数据库
        saved_db = cls.load_flashcards_db()
        saved_questions = {card.question for card in saved_db}
        saved_qa_pairs = {(card.question, card.answer) for card in saved_db}

        new_cards = [
            card for card in flashcard_list if card.question not in saved_questions
        ]
        updated_cards = [
            card
            for card in flashcard_list
            if (card.question, card.answer) not in saved_qa_pairs
            and card not in new_cards
        ]

        if updated_cards:
            for card in updated_cards:
                card_details = cls.get_flashcard_details(card.question, saved_db)
                if card_details:
                    card_idx = flashcard_list.index(card)
                    flashcard_list[card_idx].update_properties(
                        card_details[0].next, card_details[0].history
                    )
            cls._save_db(flashcard_list)
        elif new_cards:
            saved_db.extend(new_cards)
            cls._save_db(saved_db)

        return len(new_cards), len(updated_cards)

    @staticmethod
    def _save_db(flashcards: List[Flashcard]) -> None:
        """保存数据库"""
        with open(FlashcardService.DB_FILE, "wb") as fp:
            pickle.dump(flashcards, fp)

    @classmethod
    def load_flashcards_db(cls) -> List[Flashcard]:
        """加载闪卡数据库"""
        try:
            with open(cls.DB_FILE, "rb") as fp:
                return pickle.load(fp)
        except Exception as e:
            logger.error(f"加载闪卡数据库失败: {e}")
            return []

    @classmethod
    def get_flashcard_from_pool(cls) -> Optional[Flashcard]:
        """从池中获取闪卡"""
        cards = cls.load_flashcards_db()
        today = datetime.now().timestamp()
        overdue_cards = [card for card in cards if card.next <= today]

        return random.choice(overdue_cards) if overdue_cards else None

    @classmethod
    def update_flashcard(cls, card: Flashcard) -> str:
        """更新闪卡"""
        from ..utils.sm2 import supermemo_2

        cards_db = cls.load_flashcards_db()
        now = datetime.now().timestamp()

        card.last_answered = now
        card.next = now + supermemo_2(card.history) * 86400

        try:
            card_idx = next(
                i for i, x in enumerate(cards_db) if x.question == card.question
            )
            cards_db[card_idx] = card
            cls._save_db(cards_db)

            return datetime.fromtimestamp(card.next).strftime("%Y-%m-%d")
        except Exception as e:
            logger.error(f"更新闪卡失败: {e}")
            return "更新失败"

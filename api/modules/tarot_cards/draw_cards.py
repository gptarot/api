import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from api.models import TarotCard


class TarotDeck:
    """Draw tarot cards."""

    base_dir: Path = Path(__file__).resolve().parents[3] / "static"
    cards_subdir: str = "json"
    images_subpath: str = "/tarot-cards/images"

    def __init__(self, seed: Optional[int] = None) -> None:
        self.random_seed = seed
        self.cards: List[Dict[str, Any]] = self._load_cards()

    @classmethod
    def configure(
        cls, base_dir: Optional[Path] = None, cards_subdir: Optional[str] = None, images_subpath: Optional[str] = None
    ) -> None:
        """Change configuration at class level."""
        if base_dir:
            cls.base_dir = Path(base_dir)
        if cards_subdir:
            cls.cards_subdir = cards_subdir
        if images_subpath:
            cls.images_subpath = images_subpath

    @classmethod
    def _card_dir(cls) -> Path:
        return cls.base_dir / cls.cards_subdir

    def _load_cards(self) -> List[Dict[str, Any]]:
        """Load all card JSON metadata."""
        cards = []
        for file in self._card_dir().glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                card_info = json.load(f)
                card_info["image_url"] = f"{self.images_subpath}/{file.stem}.jpg"
                cards.append(card_info)
        return cards

    def draw(self, count: int = 10) -> List[TarotCard]:
        """Draw N shuffled tarot cards."""
        if count > len(self.cards):
            return []

        if self.random_seed is not None:
            random.seed(self.random_seed)

        deck = self.cards.copy()
        random.shuffle(deck)

        selected = deck[:count]
        return [
            TarotCard(
                name=card["name"],
                image_url=card["image_url"],
                is_upright=(random.random() < 0.5),
            )
            for card in selected
        ]

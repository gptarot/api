import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from gptarot.models import TarotCard

CARD_INFO_DIR = Path(__file__).resolve().parents[4] / "public" / "json"


def load_cards() -> List[Dict[str, Any]]:
    """Load all card info JSON files into memory."""
    cards = []
    for filename in os.listdir(CARD_INFO_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(CARD_INFO_DIR, filename), "r") as file:
                card_info = json.loads(file.read())
                card_info["image_url"] = f"/tarot-cards/images/{filename.split('.')[0]}.jpg"
                cards.append(card_info)
    return cards


def get_shuffled_cards(random_seed: Optional[int] = None, count: int = 10) -> List[TarotCard]:
    """Draw `count` tarot cards using the provided random seed."""
    cards_deck = load_cards()
    if count > len(cards_deck):
        return []
    else:
        cards = cards_deck.copy()

    if random_seed:
        random.seed(random_seed)
    random.shuffle(cards)

    selected_cards = cards[:count]
    tarot_cards = []
    for card in selected_cards:
        is_upright: bool = random.random() < 0.5
        tarot_card = TarotCard(
            name=card["name"],
            image_url=card["image_url"],
            is_upright=is_upright,
        )

        tarot_cards.append(tarot_card)

    return tarot_cards

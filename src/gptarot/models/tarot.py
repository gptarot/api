from typing import Literal, Optional

from pydantic import BaseModel, computed_field


class TarotCard(BaseModel):
    name: str
    is_upright: bool
    image_url: Optional[str] = None

    @computed_field
    def full_card_name(self) -> str:
        if self.is_upright:
            return f"{self.name} (UPRIGHT)"
        return f"{self.name} (REVERSED)"


class TarotInterpretation(BaseModel):
    card_name: str
    position: Literal["past", "present", "future"]
    orientation: Literal["upright", "reversed"]
    meaning: str

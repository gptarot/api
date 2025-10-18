from datetime import date
from typing import List, Literal

from pydantic import BaseModel, computed_field


class TarotCard(BaseModel):
    name: str
    is_upright: bool

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


class TarotLLMResponse(BaseModel):
    past: str
    present: str
    future: str


class TarotAPIRequest(BaseModel):
    name: str
    dob: date
    question: str
    past_card: TarotCard
    present_card: TarotCard
    future_card: TarotCard


class TarotAPIResponse(BaseModel):
    name: str
    dob: date
    question: str
    numerology_meaning: str
    interpretations: List[TarotInterpretation]

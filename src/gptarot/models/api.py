from datetime import date
from typing import List

from pydantic import BaseModel

from .tarot import TarotCard, TarotInterpretation


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

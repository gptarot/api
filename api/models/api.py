from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator

from api.models.tarot import TarotCard, TarotInterpretation

from .utils import validate_date_string_format


class TarotAPIRequest(BaseModel):
    name: str
    question: str
    past_card: TarotCard
    present_card: TarotCard
    future_card: TarotCard


class TarotAPIResponse(BaseModel):
    interpretations: List[TarotInterpretation]
    summary: str


class NumerologyAPIRequest(BaseModel):
    name: str
    dob: str
    question: str

    @field_validator("dob")
    def validate_dob_format(cls, value: str) -> str:
        return validate_date_string_format(value)


class NumerologyAPIResponse(BaseModel):
    numerology_meaning: str


class CardsAPIRequest(BaseModel):
    name: str
    dob: str
    count: int = 10
    follow_numerology: bool = False

    @field_validator("dob")
    def validate_dob_format(cls, value: str) -> str:
        return validate_date_string_format(value)


class CardsAPIResponse(BaseModel):
    cards: List[TarotCard]


class CardInfoAPIResponse(BaseModel):
    name: str
    number: str
    arcana: str
    suit: str
    image_url: str
    fortune_telling: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    meanings: Optional[Dict[str, List[str]]] = None
    archetype: Optional[str] = None
    hebrew_alphabet: Optional[str] = None
    numerology: Optional[str] = None
    elemental: Optional[str] = None
    mythical_spiritual: Optional[str] = None
    questions_to_ask: Optional[List[str]] = None

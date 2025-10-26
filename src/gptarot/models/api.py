from datetime import datetime
from typing import List

from pydantic import BaseModel, field_validator

from gptarot.models.tarot import TarotCard, TarotInterpretation


def _validate_date_string(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("value must be a string")
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError("date must be in format YYYY-MM-DD")
    return value


class TarotAPIRequest(BaseModel):
    name: str
    dob: str
    question: str
    past_card: TarotCard
    present_card: TarotCard
    future_card: TarotCard

    @field_validator("dob")
    def validate_dob_format(cls, value: str) -> str:
        return _validate_date_string(value)


class TarotAPIResponse(BaseModel):
    name: str
    dob: str
    question: str
    numerology_meaning: str
    interpretations: List[TarotInterpretation]

    @field_validator("dob")
    def validate_dob_format(cls, value: str) -> str:
        return _validate_date_string(value)


class CardsAPIRequest(BaseModel):
    name: str
    dob: str
    count: int = 10
    follow_numerology: bool = False

    @field_validator("dob")
    def validate_dob_format(cls, value: str) -> str:
        return _validate_date_string(value)


class CardsAPIResponse(BaseModel):
    cards: List[TarotCard]

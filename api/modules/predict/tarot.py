import json
import logging
from typing import Any, List, Optional, Tuple

import instructor
from fastapi import HTTPException

from api.llm import OPENAI_CLIENT
from api.models import TarotCard, TarotInterpretation, TarotLLMResponse
from api.prompts.tarot import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class TarotReader:
    """
    Tarot card interpretation module.
    """

    client: instructor.AsyncInstructor = OPENAI_CLIENT
    models: list[str] = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]

    @classmethod
    def configure(
        cls,
        client: Optional[Any] = None,
        models: Optional[list[str]] = None,
    ) -> None:
        """Change OpenAI client or model list dynamically."""
        if client:
            cls.client = client
        if models:
            cls.models = models

    @classmethod
    def _build_system_prompt(cls) -> str:
        """System prompt template for Tarot card interpretation."""
        return SYSTEM_PROMPT

    @classmethod
    async def interpret_cards(
        cls,
        name: str,
        question: str,
        past_card_name: str,
        present_card_name: str,
        future_card_name: str,
    ) -> TarotLLMResponse:
        """Request structured Tarot interpretation from LLM models."""
        system_prompt = cls._build_system_prompt()
        user_input = json.dumps(
            {
                "name": name,
                "question": question,
                "past_card_name": past_card_name,
                "present_card_name": present_card_name,
                "future_card_name": future_card_name,
            }
        )

        for model in cls.models:
            try:
                response = await cls.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                    response_model=TarotLLMResponse,
                )
                return TarotLLMResponse.model_validate(response, strict=True)
            except Exception as e:
                logger.error(f"Model {model} failed: {e}")
                if model != cls.models[-1]:
                    logger.info("Switching to next model")
                continue

        raise HTTPException(status_code=403, detail="All models failed to produce valid output")

    @classmethod
    async def generate_reading(
        cls,
        name: str,
        question: str,
        past_card: TarotCard,
        present_card: TarotCard,
        future_card: TarotCard,
    ) -> Tuple[List[TarotInterpretation], str]:
        """Generate final tarot reading and structured interpretation."""
        response = await cls.interpret_cards(
            name=name,
            question=question,
            past_card_name=past_card.full_card_name,
            present_card_name=present_card.full_card_name,
            future_card_name=future_card.full_card_name,
        )

        interpretations = [
            TarotInterpretation(
                card_name=past_card.name,
                position="past",
                orientation="upright" if past_card.is_upright else "reversed",
                meaning=response.past,
            ),
            TarotInterpretation(
                card_name=present_card.name,
                position="present",
                orientation="upright" if present_card.is_upright else "reversed",
                meaning=response.present,
            ),
            TarotInterpretation(
                card_name=future_card.name,
                position="future",
                orientation="upright" if future_card.is_upright else "reversed",
                meaning=response.future,
            ),
        ]

        return interpretations, response.summary

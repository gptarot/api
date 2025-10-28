import json
import logging
from typing import Any, Dict, Optional

import openai
from fastapi import HTTPException
from unidecode import unidecode

from api.llm import MODEL_LISTS, OPENAI_BASE_CLIENT
from api.prompts.numerology import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class NumerologyReader:
    """Numerology computation and interpretation service."""

    models: list[str] = MODEL_LISTS
    client: openai.AsyncOpenAI = OPENAI_BASE_CLIENT
    max_analysis_length: int = 1000

    @classmethod
    def configure(
        cls,
        models: Optional[list[str]] = None,
        client: Optional[Any] = None,
        max_analysis_length: Optional[int] = None,
    ) -> None:
        """Change model or runtime configuration globally."""
        if models:
            cls.models = models
        if client:
            cls.client = client
        if max_analysis_length:
            cls.max_analysis_length = max_analysis_length

    @staticmethod
    def calculate(name: str, dob: str) -> Dict[str, int]:
        """Calculate numerological values from name and date of birth."""
        normalized_name = unidecode(name.upper().replace(" ", ""))
        name_sum = sum((ord(c) - 64) for c in normalized_name if c.isalpha())
        dob_digits = [int(ch) for ch in dob if ch.isdigit()]
        dob_sum = sum(dob_digits)
        total_sum = name_sum + dob_sum
        while total_sum > 9:
            total_sum = sum(int(d) for d in str(total_sum))
        return {
            "name_numerology": name_sum,
            "dob_numerology": dob_sum,
            "personal_numerology": total_sum,
        }

    @classmethod
    def _build_prompt(cls) -> str:
        """Return reusable system prompt for numerology interpretation."""
        return SYSTEM_PROMPT.format(
            max_analysis_length=cls.max_analysis_length,
        )

    @classmethod
    async def analyze(cls, name: str, dob: str, question: str) -> str:
        """Perform numerology analysis and LLM interpretation."""
        numerology = cls.calculate(name, dob)
        user_input = json.dumps(
            {
                "name": name,
                "dob": dob,
                "question": question,
                "numerology": numerology,
            }
        )

        system_prompt = cls._build_prompt()

        for model in cls.models:
            try:
                response = await cls.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Model {model} failed: {e}")
                if model != cls.models[-1]:
                    logger.info("Switching to next model")
                    continue

        raise HTTPException(status_code=403, detail="All configured models failed")

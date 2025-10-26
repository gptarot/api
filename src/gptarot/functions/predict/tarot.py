import json
import logging
from typing import List, Tuple

from fastapi import HTTPException

from gptarot.llm import OPENAI_CLIENT
from gptarot.models import TarotCard, TarotInterpretation, TarotLLMResponse

logger = logging.getLogger(__name__)


async def get_gptarot_cards_interpretations(
    name: str,
    question: str,
    past_card_name: str,
    present_card_name: str,
    future_card_name: str,
) -> TarotLLMResponse:
    """
    Choose valid model and request a structured response.
    Returns a parsed TarotLLMResponse or raises 403 if all models fail.

    Params:
        name (str): Name of the person.
        question (str): Question to ask.
        past_card_name (str): Name of the past card.
        present_card_name (str): Name of the present card.
        future_card_name (str): Name of the future card.

    Returns:
        TarotLLMResponse: Parsed TarotLLMResponse.
    """
    model_lists = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
    ]

    system_prompt = """
    # Role and Objective
     You are a Tarot Reader. Begin with a concise checklist outlining your response process:
        (1) analyze user's question and provided cards
        (2) interpret and generate insights for 3 objects: "past", "present", "future"
        (3) synthesize these into a final object: "summary"

    # Instructions
    * Respond with a object containing four keys, in this order: "past", "present", "future", and "summary".
    * Each key should include a deep, thoughtful answer in Markdown format, addressing the user's question and interpreting the cards provided.
    * Your response MUST be in the same language as the user's question. Don't include emojis in your response.
    * Ensure your Markdown formatting is clear and has key-noted bold text where helpful to improve readability.
    """

    user_input = json.dumps(
        {
            "name": name,
            "question": question,
            "past_card_name": past_card_name,
            "present_card_name": present_card_name,
            "future_card_name": future_card_name,
        }
    )

    for model in model_lists:
        try:
            response = await OPENAI_CLIENT.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                response_model=TarotLLMResponse,
            )
            return TarotLLMResponse.model_validate(response, strict=True)
        except Exception as e:
            logger.error(e)
            if model != model_lists[-1]:
                logger.info("Switching to next model")
            continue

    raise HTTPException(status_code=403, detail="All models are invalid and cannot be used")


async def get_gptarot_final_interpretations(
    name: str,
    question: str,
    past_card: TarotCard,
    present_card: TarotCard,
    future_card: TarotCard,
) -> Tuple[List[TarotInterpretation], str]:
    """
    Generate a tarot reading based on the input data.

    Params:
        name (str): Name of the person.
        question (str): Question to ask.
        past_card (TarotCard): The past card.
        present_card (TarotCard): The present card.
        future_card (TarotCard): The future card.

    Returns:
        List[TarotInterpretation]: A list of tarot interpretations.
        str: Final summary of tarot reader.
    """
    past_card_str = past_card.full_card_name
    present_card_str = present_card.full_card_name
    future_card_str = future_card.full_card_name

    answer: TarotLLMResponse = await get_gptarot_cards_interpretations(
        name=name,
        question=question,
        past_card_name=past_card_str,
        present_card_name=present_card_str,
        future_card_name=future_card_str,
    )

    interpretations = [
        TarotInterpretation(
            card_name=past_card.name,
            position="past",
            orientation="upright" if past_card.is_upright else "reversed",
            meaning=answer.past,
        ),
        TarotInterpretation(
            card_name=present_card.name,
            position="present",
            orientation="upright" if present_card.is_upright else "reversed",
            meaning=answer.present,
        ),
        TarotInterpretation(
            card_name=future_card.name,
            position="future",
            orientation="upright" if future_card.is_upright else "reversed",
            meaning=answer.future,
        ),
    ]

    return interpretations, answer.summary

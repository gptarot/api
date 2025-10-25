import json
import logging
from datetime import date
from typing import Dict

from fastapi import HTTPException
from unidecode import unidecode

from gptarot.llm import MODEL_LISTS, OPENAI_BASE_CLIENT

logger = logging.getLogger(__name__)


def calculate_numerology(name: str, dob: str) -> Dict[str, int]:
    """
    Calculate Numerology based on name and date of birth.

    Params:
        name (str): Name of the person.
        dob (str): Date of birth of the person.

    Returns:
        Dict[str, int]: Numerology of the person.
    """
    name = unidecode(name.upper().replace(" ", ""))
    name_sum = sum((ord(c) - 64) for c in name if c.isalpha())
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


async def get_numerology_meaning(name: str, dob: date, question: str) -> str:
    """
    Get Numerology Meanings based on name and date of birth.

    Params:
        name (str): Name of the person.
        dob (str): Date of birth of the person.

    Returns:
        str: Numerology Meanings.
    """
    dob_str = dob.strftime("%Y-%m-%d")
    numerology = calculate_numerology(name, dob_str)

    system_prompt = """
    You are a numerology expert. You will be given a name, date of birth, and a question.
    Return calculations explained in list and then contain deep answer show that how the numerology can related to the question.
    The answer must be in the same language as the user's question and in markdown format.
    """

    user_input = json.dumps(
        {
            "name": name,
            "dob": dob_str,
            "question": question,
            "numerology": numerology,
        }
    )

    for model in MODEL_LISTS:
        try:
            response = await OPENAI_BASE_CLIENT.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
            )
            numerology_meaning = response.choices[0].message.content
            return numerology_meaning
        except Exception as e:
            logger.error(e)
            if model != MODEL_LISTS[-1]:
                logger.info("Switching to next model")
            continue

    raise HTTPException(status_code=403, detail="All models are invalid and cannot be used")

import json
import logging
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


async def get_numerology_meaning(name: str, dob: str, question: str) -> str:
    """
    Get Numerology Meanings based on name and date of birth.

    Params:
        name (str): Name of the person.
        dob (str): Date of birth of the person.

    Returns:
        str: Numerology Meanings.
    """
    numerology = calculate_numerology(name, dob)
    system_prompt = """
    # Role and Objective
    Act as a numerology expert. Analyze a name, date of birth, and user question, then present numerological calculations and a tailored analysis in clear, structured markdown.

    # Instructions
    * Your response MUST be in the same language as the user's question. Don't include emojis in your response.
    * Ensure your Markdown formatting is clear and has key-noted bold text where helpful to improve readability.
    * Contains a deep answer show that how the numerology can related to or can solve the user's question/problem.

    # Output Structure
    - **Step 1: Numerological Calculations**
        - Use a markdown table to represent the numerology calculations based on the provided json inputs.
    - **Step 2: Numerology Analysis**
        - Offer a nuanced interpretation (up to 1000 characters) based on the calculation results, directly addressing the user's question.
        - Match the output language of your analysis to the user's input question. If unsupported, default to English with an error note.
    - Calculations table must always precede the analysis, change the language of the analysis to match the user's question if necessary.

    # Output Example (Markdown)
    ```markdown
    | Aspect Calculated  | Value | Calculation Steps                  |
    |--------------------|-------|------------------------------------|
    | ...                | ...   | ...                                |

    (...analysis up to 1000 characters...)
    ```
    """

    user_input = json.dumps(
        {
            "name": name,
            "dob": dob,
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

import logging
import os

import uvicorn
from fastapi import FastAPI, HTTPException

from gptarot.functions import get_gptarot_final_interpretations, get_numerology_meaning
from gptarot.models import TarotAPIRequest, TarotAPIResponse

logger = logging.getLogger(__name__)
site_dir = os.path.join(os.getcwd(), "site")
app = FastAPI(docs_url="/swagger", redoc_url=None)
# app.mount("/", StaticF/iles(directory=site_dir, html=True), name="docs")


@app.post("/predict/interpretations", response_model=TarotAPIResponse)
async def predict_interpretations(request: TarotAPIRequest) -> TarotAPIResponse:
    """
    | Method | Path                       | Description                                       |
    | ------ | -------------------------- | ------------------------------------------------- |
    | POST   | `/predict/interpretations` | Get tarot interpretations and numerology meanings |

    Params:
        request (TarotAPIRequest): The request object containing the name, dob, question, past_card, present_card, and future_card.

    Returns:
        TarotAPIResponse: The response object containing the name, dob, question, numerology_meaning, and interpretations.

    !!! note
        This function uses the `get_gptarot_final_interpretations` and `get_numerology_meaning` functions to get the tarot interpretations and numerology meanings.

    !!! example "Example Request"

        ```json
        {
            "name": "John Doe",
            "dob": "2000-01-01",
            "question": "Will my current love last forever?",
            "past_card": {
                "name" : "Chariot" ,
                "is_upright" : false
            },
            "present_card": {
                "name" : "The Fool" ,
                "is_upright" : true
            },
            "future_card": {
                "name" : "The Magician" ,
                "is_upright" : true
            }
        }
        ```

    !!! example "Example Response"

        ```json
        {
            "name": "John Doe",
            "dob": "2000-01-01",
            "question": "Will my current love last forever?",
            "numerology_meaning": "The numerology meaning of John Doe is: 6",
            "interpretations": [
                {
                    "card_name": "Chariot (Reversed)",
                    "position": "past",
                    "orientation": "ureversed",
                    "meaning": "Past influence:...",
                },
                {
                    "card_name": "The Fool (Upright)",
                    "position": "present",
                    "orientation": "upright",
                    "meaning": "Present situation:...",
                },
                {
                    "card_name": "The Magician (Upright)",
                    "position": "future",
                    "orientation": "upright",
                    "meaning": "Future outlook:...",
                },
            ]
        }
        ```
    """
    try:
        interpretations = await get_gptarot_final_interpretations(
            name=request.name,
            question=request.question,
            past_card=request.past_card,
            present_card=request.present_card,
            future_card=request.future_card,
        )
        numerology_meaning = await get_numerology_meaning(
            name=request.name,
            dob=request.dob,
            question=request.question,
        )

        return TarotAPIResponse(
            name=request.name,
            dob=request.dob,
            question=request.question,
            numerology_meaning=numerology_meaning,
            interpretations=interpretations,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", reload=True)

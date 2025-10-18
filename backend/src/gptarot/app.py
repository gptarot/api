import logging

import uvicorn
from fastapi import FastAPI, HTTPException

from gptarot.models import TarotAPIRequest, TarotAPIResponse
from gptarot.predict_functions.numerology import get_numerology_meansing
from gptarot.predict_functions.tarot import get_gptarot_interpretations

app = FastAPI(root_path="/api")
logger = logging.getLogger(__name__)


@app.get("/")
def get_index():
    return "GPTarot API"


@app.post("/predict", response_model=TarotAPIResponse)
async def tarot_api(request: TarotAPIRequest):
    try:
        interpretations = await get_gptarot_interpretations(
            name=request.name,
            question=request.question,
            past_card=request.past_card,
            present_card=request.present_card,
            future_card=request.future_card,
        )
        numerology_meaning = await get_numerology_meansing(
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
    uvicorn.run(app, host="0.0.0.0")

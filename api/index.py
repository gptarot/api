import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api import __title__, __version__
from api.models import (
    CardInfoAPIResponse,
    CardsAPIRequest,
    CardsAPIResponse,
    NumerologyAPIRequest,
    NumerologyAPIResponse,
    TarotAPIRequest,
    TarotAPIResponse,
)
from api.modules import NumerologyReader, TarotDeck, TarotReader

logger = logging.getLogger(__name__)
PROJECT_BASE_DIR = Path(__file__).resolve().parents[1]
NUMEROLOGY_READER = NumerologyReader()
TAROT_READER = TarotReader()


app = FastAPI(title=__title__, version=__version__, docs_url="/swagger", redoc_url=None)
app.mount("/tarot-cards/images", StaticFiles(directory=PROJECT_BASE_DIR / "static" / "images"), name="tarot-cards")

if os.getenv("VERCEL") == "1":

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return RedirectResponse("/vercel.svg", status_code=307)

    @app.get("/", include_in_schema=False)
    @app.get("/docs", include_in_schema=False)
    async def docs():
        return RedirectResponse("https://tarotpedia.github.io/docs", status_code=307)


@app.post("/predict/tarot-interpretations", response_model=TarotAPIResponse, tags=["Predict API"])
async def predict_tarot_interpretations(request: TarotAPIRequest) -> TarotAPIResponse:
    """
    | Method | Path                             | Description                                       |
    | ------ | -------------------------------- | ------------------------------------------------- |
    | `POST` | `/predict/tarot-interpretations` | Get tarot interpretations

    Params:
        request (TarotAPIRequest): The request object containing the name, question, past_card, present_card, and future_card.

    Returns:
        TarotAPIResponse: The response object containing the name, question, and interpretations.

    !!! note
        This function uses the `TarotReader` module to get the tarot interpretations.

    !!! example "Example Request"

        ```json
        {
            "name": "John Doe",
            "question": "Will my current love last forever?",
            "past_card": {
                "name" : "Chariot",
                "is_upright" : false
            },
            "present_card": {
                "name" : "The Fool",
                "is_upright" : true
            },
            "future_card": {
                "name" : "The Magician",
                "is_upright" : true
            }
        }
        ```

    !!! example "Example Response"

        ```json
        {
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
            ],
            "summary": "..."
        }
        ```
    """
    try:
        interpretations, summary = await TAROT_READER.generate_reading(
            name=request.name,
            question=request.question,
            past_card=request.past_card,
            present_card=request.present_card,
            future_card=request.future_card,
        )

        return TarotAPIResponse(
            interpretations=interpretations,
            summary=summary,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/predict/numerology-interpretations", response_model=NumerologyAPIResponse, tags=["Predict API"])
async def predict_numerology_interpretations(request: NumerologyAPIRequest) -> NumerologyAPIResponse:
    """
    | Method | Path                                  | Description                                 |
    | ------ | ------------------------------------- | ------------------------------------------- |
    | `POST` | `/predict/numerology-interpretations` | Get numerology interpretations and meanings |

    Params:
        request (NumerologyAPIRequest): The request object containing the name, dob, and question.

    Returns:
        NumerologyAPIResponse: The response object containing the numerology meaning.

    !!! note
        This function uses the `NumerologyReader` module to get the numerology meaning.

    !!! example "Example Request"

        ```json
        {
            "name": "John Doe",
            "dob": "1990-01-01",
            "question": "Will my current love last forever?"
        }
        ```

    !!! example "Example Response"

        ```json
        {
            "numerology_meaning": "..."
        }
        ```
    """
    try:
        numerology_meaning = await NUMEROLOGY_READER.analyze(
            name=request.name,
            dob=request.dob,
            question=request.question,
        )

        return NumerologyAPIResponse(numerology_meaning=numerology_meaning)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/tarot-cards/draw", response_model=CardsAPIResponse, tags=["Tarot Cards API"])
async def draw_cards(request: CardsAPIRequest) -> CardsAPIResponse:
    """
    | Method | Path                       | Description                                       |
    | ------ | -------------------------- | ------------------------------------------------- |
    | `POST` | `/tarot-cards/draw`        | Get shuffled tarot cards                          |

    Params:
        request (CardsAPIRequest): The request object containing the name, dob, and count.

    Returns:
        CardsAPIResponse: The response object containing the cards.

    !!! note
        This function uses the `get_shuffled_cards` function to get the shuffled tarot cards.

    !!! example "Example Request"

        ```json
        {
            "name": "John Doe",
            "dob": "2000-01-01",
            "count": 5,
            "follow_numerology": false
        }
        ```

    !!! example "Example Response"

        ```json
        {
            "cards": [
                {
                    "name": "Eight of Pentacles",
                    "is_upright": false,
                    "image_url": "/tarot-cards/images/72.jpg",
                    "full_card_name": "Eight of Pentacles (REVERSED)"
                },
                {
                    "name": "King of Cups",
                    "is_upright": false,
                    "image_url": "/tarot-cards/images/36.jpg",
                    "full_card_name": "King of Cups (REVERSED)"
                },
                ...
            ]
        }
        ```
    """
    if request.follow_numerology:
        universe_number = NUMEROLOGY_READER.calculate(request.name, request.dob)["personal_numerology"]
    else:
        universe_number = None

    tarot_deck = TarotDeck(seed=universe_number)
    shuffled_cards = tarot_deck.draw(count=request.count)
    return CardsAPIResponse(cards=shuffled_cards)


@app.get("/tarot-cards/get-card-info", response_model=CardInfoAPIResponse, tags=["Tarot Cards API"])
def get_card_info(card_number: int) -> CardInfoAPIResponse:
    """
    | Method | Path                                  | Description                                 |
    | ------ | ------------------------------------- | ------------------------------------------- |
    | `GET`  | `/tarot-cards/get-card-info`          | Get card info by number                     |

    Params:
        card_number (int): The card number (Range: 1-78).

    Returns:
        CardInfoAPIResponse: The response object containing the card info.

    !!! note
        This function uses the `TarotDeck` class to get the card info.

    !!! example "Example Response"

        ```json
        {
            "name": "The Fool",
            "number": "1",
            "arcana": "The Fool",
            "suit": "Major Arcana",
            "image_url": "/tarot-cards/images/1.jpg",
            "fortune_telling": ["..."],
            "keywords": ["..."],
            "meanings": {...},
            "archetype": "...",
            "hebrew_alphabet": "...",
            "numerology": "...",
            "elemental": "...",
            "mythical_spiritual": "...",
            "questions_to_ask": ["..."]
        }
        ```
    """
    if not 1 <= card_number <= 78:
        raise HTTPException(status_code=400, detail="Card number must be between 1 and 78")

    tarot_deck = TarotDeck()
    card_info = tarot_deck.get_card_info(card_number)
    return CardInfoAPIResponse(**card_info)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", reload=True)

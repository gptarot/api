import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from mkdocs import config
from mkdocs.commands import build as mkdocs_build

from gptarot import __title__, __version__
from gptarot.models import CardsAPIRequest, CardsAPIResponse, TarotAPIRequest, TarotAPIResponse
from gptarot.modules import NumerologyReader, TarotDeck, TarotReader

logger = logging.getLogger(__name__)
MKDOCS_SITE_DIR = Path(__file__).resolve().parents[2] / "site"
CARD_IMAGES_DIR = Path(__file__).resolve().parents[2] / "public" / "images"
NUMEROLOGY_READER = NumerologyReader()
TAROT_READER = TarotReader()

mkdocs_conf = config.load_config(site_dir=MKDOCS_SITE_DIR.as_posix(), config_file="mkdocs.yaml")
mkdocs_build.build(mkdocs_conf)

app = FastAPI(title=__title__, version=__version__, docs_url="/swagger", redoc_url=None)
app.mount("/docs", StaticFiles(directory=MKDOCS_SITE_DIR, html=True), name="docs")
app.mount("/tarot-cards/images", StaticFiles(directory=CARD_IMAGES_DIR), name="tarot-cards")


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


@app.post("/predict/interpretations", response_model=TarotAPIResponse, tags=["Predict API"])
async def predict_interpretations(request: TarotAPIRequest) -> TarotAPIResponse:
    """
    | Method | Path                       | Description                                       |
    | ------ | -------------------------- | ------------------------------------------------- |
    | `POST` | `/predict/interpretations` | Get tarot interpretations and numerology meanings |

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
            ],
            summary: "..."
        }
        ```
    """
    try:
        numerology_meaning = await NUMEROLOGY_READER.analyze(
            name=request.name,
            dob=request.dob,
            question=request.question,
        )

        interpretations, summary = await TAROT_READER.generate_reading(
            name=request.name,
            question=request.question,
            past_card=request.past_card,
            present_card=request.present_card,
            future_card=request.future_card,
        )

        return TarotAPIResponse(
            name=request.name,
            dob=request.dob,
            question=request.question,
            numerology_meaning=numerology_meaning,
            interpretations=interpretations,
            summary=summary,
        )

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", reload=True)

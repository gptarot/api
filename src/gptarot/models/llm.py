from pydantic import BaseModel


class TarotLLMResponse(BaseModel):
    past: str
    present: str
    future: str
    summary: str

from pydantic import BaseModel


class SentimentEntry(BaseModel):
    id: int
    text: str
    sentiment: str
    confidence: float
    timestamp: str

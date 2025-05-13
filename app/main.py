from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.sentiment_service import analyze_sentiment
from app.models import SentimentEntry
from app.utils.database import insert_sentiment, get_trend, get_history

app = FastAPI()


class TextInput(BaseModel):
    text: str


@app.post("/analyze")
def analyze_text(input: TextInput):
    result = analyze_sentiment(input.text)
    insert_sentiment(input.text, result["sentiment"], result["confidence"])
    return result


@app.get("/sentiment/today")
def sentiment_today():
    return get_trend(today=True)


@app.get("/trend")
def sentiment_trend():
    return get_trend()


@app.get("/history")
def history(days: int = 7):
    return get_history(days)

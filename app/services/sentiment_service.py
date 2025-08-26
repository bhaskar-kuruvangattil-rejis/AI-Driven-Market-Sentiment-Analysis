from typing import Any, Dict, List, Optional
import boto3
import os


def analyze_sentiment(text: str):
    comprehend = boto3.client("comprehend", region_name=os.getenv("AWS_REGION"))
    response = comprehend.detect_sentiment(Text=text, LanguageCode="en")
    return {
        "sentiment": response["Sentiment"],
        "confidence": max(response["SentimentScore"].values()),
    }

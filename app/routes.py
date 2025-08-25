from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime

from app.services.sentiment_service import analyze_sentiment
from app.models import SentimentEntry
from app.utils.database import insert_sentiment, get_trend, get_history, test_database_connection
from app.utils.s3_handler import s3_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class TextInput(BaseModel):
    text: str
    save_to_s3: Optional[bool] = True
    metadata: Optional[dict] = None


class AnalysisResponse(BaseModel):
    sentiment: str
    confidence: float
    timestamp: str
    saved_to_database: bool
    saved_to_s3: bool


class HealthResponse(BaseModel):
    status: str
    database: bool
    s3: bool
    timestamp: str


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(input_data: TextInput):
    """Analyze sentiment of provided text"""
    try:
        # Validate input
        if not input_data.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(input_data.text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
        
        # Analyze sentiment
        result = analyze_sentiment(input_data.text)
        timestamp = datetime.now().isoformat()
        
        # Save to database
        db_saved = insert_sentiment(
            input_data.text, 
            result["sentiment"], 
            result["confidence"]
        )
        
        # Save to S3 if requested
        s3_saved = False
        if input_data.save_to_s3:
            s3_saved = s3_handler.save_raw_text(
                input_data.text, 
                input_data.metadata
            )
            # Also save analysis result
            s3_handler.save_analysis_result(
                input_data.text,
                result["sentiment"],
                result["confidence"]
            )
        
        logger.info(f"Analysis completed: {result['sentiment']} ({result['confidence']})")
        
        return AnalysisResponse(
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            timestamp=timestamp,
            saved_to_database=db_saved,
            saved_to_s3=s3_saved
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/sentiment/today")
async def sentiment_today():
    """Get today's sentiment analysis summary"""
    try:
        trends = get_trend(today=True)
        if not trends:
            return {"message": "No sentiment data available for today", "data": []}
        
        return {
            "date": datetime.now().date().isoformat(),
            "trends": [{
                "sentiment": trend[0],
                "average_confidence": float(trend[1])
            } for trend in trends]
        }
    except Exception as e:
        logger.error(f"Failed to get today's sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve today's sentiment data")


@router.get("/trend")
async def sentiment_trend():
    """Get overall sentiment trends"""
    try:
        trends = get_trend()
        if not trends:
            return {"message": "No trend data available", "data": []}
        
        return {
            "trends": [{
                "sentiment": trend[0],
                "count": trend[1]
            } for trend in trends]
        }
    except Exception as e:
        logger.error(f"Failed to get sentiment trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sentiment trends")


@router.get("/history")
async def history(days: int = Query(default=7, ge=1, le=365)):
    """Get historical sentiment data for specified number of days"""
    try:
        history_data = get_history(days)
        if not history_data:
            return {
                "message": f"No historical data available for the last {days} days",
                "data": []
            }
        
        return {
            "days": days,
            "history": [{
                "date": record[0].isoformat() if record[0] else None,
                "sentiment": record[1],
                "count": record[2]
            } for record in history_data]
        }
    except Exception as e:
        logger.error(f"Failed to get historical data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve historical data")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify system components"""
    try:
        db_status = test_database_connection()
        s3_status = s3_handler.test_connection()
        
        overall_status = "healthy" if db_status and s3_status else "degraded"
        
        return HealthResponse(
            status=overall_status,
            database=db_status,
            s3=s3_status,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            database=False,
            s3=False,
            timestamp=datetime.now().isoformat()
        )


@router.get("/s3/objects")
async def list_s3_objects(
    prefix: str = Query(default="", description="S3 object prefix filter"),
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of objects to return")
):
    """List S3 objects with optional prefix filter"""
    try:
        objects = s3_handler.list_objects(prefix=prefix, limit=limit)
        return {
            "prefix": prefix,
            "limit": limit,
            "count": len(objects),
            "objects": objects
        }
    except Exception as e:
        logger.error(f"Failed to list S3 objects: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list S3 objects")

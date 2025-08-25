import psycopg2
import os
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection pool or connection management
class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

# Global database manager instance
db_manager = DatabaseManager()


def insert_sentiment(text: str, sentiment: str, confidence: float) -> bool:
    """Insert sentiment analysis result into database"""
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sentiment_data (text, sentiment, confidence, timestamp)
                    VALUES (%s, %s, %s, %s);
                """,
                    (text, sentiment, confidence, datetime.now()),
                )
                conn.commit()
                logger.info(f"Successfully inserted sentiment data: {sentiment} ({confidence})")
                return True
    except Exception as e:
        logger.error(f"Failed to insert sentiment data: {e}")
        return False


def get_trend(today: bool = False) -> List[Tuple]:
    """Get sentiment trends from database"""
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                if today:
                    cur.execute(
                        "SELECT sentiment, AVG(confidence) FROM sentiment_data WHERE DATE(timestamp) = CURRENT_DATE GROUP BY sentiment;"
                    )
                else:
                    cur.execute(
                        "SELECT sentiment, COUNT(*) FROM sentiment_data GROUP BY sentiment;"
                    )
                results = cur.fetchall()
                logger.info(f"Retrieved trend data: {len(results)} records")
                return results
    except Exception as e:
        logger.error(f"Failed to get trend data: {e}")
        return []


def get_history(days: int) -> List[Tuple]:
    """Get historical sentiment data for specified number of days"""
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                start_date = datetime.now() - timedelta(days=days)
                cur.execute(
                    """
                    SELECT DATE(timestamp), sentiment, COUNT(*) 
                    FROM sentiment_data
                    WHERE timestamp >= %s
                    GROUP BY DATE(timestamp), sentiment
                    ORDER BY DATE(timestamp);
                """,
                    (start_date,),
                )
                results = cur.fetchall()
                logger.info(f"Retrieved historical data: {len(results)} records for {days} days")
                return results
    except Exception as e:
        logger.error(f"Failed to get historical data: {e}")
        return []


def test_database_connection() -> bool:
    """Test database connection"""
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                logger.info("Database connection test successful")
                return result[0] == 1
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

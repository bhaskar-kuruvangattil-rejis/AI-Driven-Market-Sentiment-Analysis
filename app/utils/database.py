import psycopg2
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))


def insert_sentiment(text, sentiment, confidence):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO sentiment_data (text, sentiment, confidence, timestamp)
            VALUES (%s, %s, %s, %s);
        """,
            (text, sentiment, confidence, datetime.now()),
        )
        conn.commit()


def get_trend(today=False):
    with conn.cursor() as cur:
        if today:
            cur.execute(
                "SELECT sentiment, AVG(confidence) FROM sentiment_data WHERE DATE(timestamp) = CURRENT_DATE GROUP BY sentiment;"
            )
        else:
            cur.execute(
                "SELECT sentiment, COUNT(*) FROM sentiment_data GROUP BY sentiment;"
            )
        return cur.fetchall()


def get_history(days):
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
        return cur.fetchall()

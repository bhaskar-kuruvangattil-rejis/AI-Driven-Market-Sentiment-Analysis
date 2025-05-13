from app.services.sentiment_service import analyze_sentiment
from app.utils.s3_handler import save_to_s3
from app.utils.database import insert_sentiment

text = "Tech companies are seeing massive growth after positive earnings reports."

# Analyze sentiment using AWS Comprehend
result = analyze_sentiment(text)
print("Analysis Result:", result)

# Save raw text to S3
save_to_s3(text)

# Log sentiment to PostgreSQL
insert_sentiment(text, result['sentiment'], result['confidence'])
print("Inserted into PostgreSQL successfully.")
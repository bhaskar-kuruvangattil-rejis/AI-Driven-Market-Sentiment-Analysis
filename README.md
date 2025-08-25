# AI-Driven Market Sentiment Analysis

This project leverages Natural Language Processing (NLP) and cloud services to analyze market sentiment from social media and news data. It provides a RESTful API for sentiment scores and trend predictions, backed by a PostgreSQL database and visualized via a dashboard.

## 🚀 Features

- Extracts real-time textual data from news sources and social media platforms.
- Performs sentiment analysis using AWS Comprehend for high-accuracy classification.
- Stores raw and processed data using AWS S3 and PostgreSQL.
- Offers trend prediction based on historical sentiment patterns.
- Provides RESTful APIs for frontend dashboard integration.

## 🧱 System Architecture

```
+------------------+     +--------------------+     +---------------------+
|  Data Sources    | --> |   NLP Processor    | --> |   Sentiment Scoring |
| (Twitter, News)  |     |  (AWS Comprehend)  |     |     + Prediction    |
+------------------+     +--------------------+     +---------------------+
        |                                                    |
        v                                                    v
+------------------+     +----------------------+     +------------------+
|    AWS S3        | --> |  PostgreSQL Database | --> |   Python API     |
| (Raw Data Store) |     |  (Historical Data)   |     | (Flask / FastAPI)|
+------------------+     +----------------------+     +------------------+
                                                              |
                                                              v
                                                     +------------------+
                                                     |   Frontend UI    |
                                                     | (React / Charts) |
                                                     +------------------+
```

## 🔧 Tech Stack

- **Python**: Core language for backend development
- **FastAPI**: High-performance API framework
- **AWS Comprehend**: Managed NLP for sentiment and entity analysis
- **AWS S3**: Storage for raw unprocessed text
- **PostgreSQL**: For storing sentiment scores and trend data
- **SQLAlchemy**: ORM to interact with PostgreSQL
- **Pandas/Numpy**: For batch processing and analytics
- **Docker**: Containerized deployment

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/bhaskar-kuruvangattil-rejis/AI-Driven-Market-Sentiment-Analysis.git
cd AI-Driven-Market-Sentiment-Analysis
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=your_s3_bucket_name

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/sentiment_db

# Application Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### 4. Set Up PostgreSQL Database

```bash
# Create database (adjust user and database name as needed)
psql -U postgres -c "CREATE DATABASE sentiment_db;"

# Run schema creation
psql -U postgres -d sentiment_db -f db/schema.sql
```

### 5. Create S3 Bucket (Optional)

If you want to use S3 for storing raw data:

```bash
# Using AWS CLI
aws s3 mb s3://your-bucket-name
```

### 6. Run the API Server

```bash
# Method 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using Python module
python -m app.main

# Method 3: Direct execution
python app/main.py
```

### 7. Verify Installation

Once the server is running, you can verify the installation:

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Detailed Health: http://localhost:8000/api/v1/health

## 📡 API Endpoints

| Method | Endpoint                      | Description                             |
|--------|-------------------------------|-----------------------------------------|
| GET    | `/`                           | Root endpoint with API information      |
| GET    | `/health`                     | Simple health check                     |
| GET    | `/api/v1/health`              | Detailed health check (DB + S3)        |
| POST   | `/api/v1/analyze`             | Submit new text for analysis            |
| GET    | `/api/v1/sentiment/today`     | Get current day's sentiment summary     |
| GET    | `/api/v1/trend`               | Get overall sentiment trends            |
| GET    | `/api/v1/history?days=N`      | Fetch historical sentiment data         |
| GET    | `/api/v1/s3/objects`          | List S3 objects with optional filtering |

## 🧪 Example Usage

### Analyze Sentiment

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Market outlook is very positive after earnings call",
       "save_to_s3": true,
       "metadata": {"source": "earnings_report"}
     }'
```

Response:
```json
{
  "sentiment": "POSITIVE",
  "confidence": 0.93,
  "timestamp": "2024-08-25T07:15:30.123456",
  "saved_to_database": true,
  "saved_to_s3": true
}
```

### Get Today's Sentiment

```bash
curl http://localhost:8000/api/v1/sentiment/today
```

Response:
```json
{
  "date": "2024-08-25",
  "trends": [
    {"sentiment": "POSITIVE", "average_confidence": 0.85},
    {"sentiment": "NEGATIVE", "average_confidence": 0.75}
  ]
}
```

### Get Historical Data

```bash
curl "http://localhost:8000/api/v1/history?days=7"
```

Response:
```json
{
  "days": 7,
  "history": [
    {"date": "2024-08-25", "sentiment": "POSITIVE", "count": 12},
    {"date": "2024-08-25", "sentiment": "NEGATIVE", "count": 5}
  ]
}
```

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "database": true,
  "s3": true,
  "timestamp": "2024-08-25T07:15:30.123456"
}
```

## 🧪 Testing

### Running Unit Tests

The project includes comprehensive unit tests using pytest:

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html

# Run specific test class
pytest tests/test_sentiment.py::TestSentimentService -v

# Run tests with output
pytest tests/ -v -s
```

### Testing the Complete Workflow

Use the included test flow script to verify your setup:

```bash
# Make the script executable
chmod +x test_flow.py

# Run the test flow
python test_flow.py
```

This script will:
- ✅ Check environment variables
- ✅ Test AWS Comprehend sentiment analysis
- ✅ Test database connectivity and operations
- ✅ Test S3 storage operations (if configured)
- ✅ Verify the complete data flow

### Manual Testing with curl

Once the server is running, you can test endpoints manually:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test detailed health
curl http://localhost:8000/api/v1/health

# Test sentiment analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "The market is performing very well today!"}'
```

## 🗒 Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Pydantic models for API requests/responses
│   ├── routes.py            # API route definitions
│   ├── services/
│   │   ├── sentiment_service.py # Core sentiment analysis logic
│   │   └── aws_comprehend.py    # AWS Comprehend integration (placeholder)
│   └── utils/
│       ├── database.py      # Database connection and operations
│       └── s3_handler.py    # S3 storage operations
├── db/
│   └── schema.sql           # PostgreSQL database schema
├── tests/
│   └── test_sentiment.py    # Comprehensive unit tests
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── test_flow.py            # Integration test script
└── README.md               # This file
```

## 📈 Future Improvements

- Integrate real-time Twitter stream ingestion
- Add support for more NLP models (BERT, RoBERTa)
- Implement user authentication for the dashboard
- Enable fine-grained time series forecasting using Prophet or ARIMA
- Visualize market movement correlations

## 📄 License

This project is licensed under the MIT License.
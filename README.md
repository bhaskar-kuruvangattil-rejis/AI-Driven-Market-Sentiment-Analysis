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
git clone https://github.com/yourusername/market-sentiment-analyzer.git
cd market-sentiment-analyzer
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file:

```
REMOVED=your_key
REMOVED=your_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_bucket
DATABASE_URL=postgresql://user:password@localhost:5432/sentiment_db
```

### 4. Start PostgreSQL & Create Tables

```bash
# assuming PostgreSQL is running locally
psql -U your_user -d sentiment_db -f db/schema.sql
```

### 5. Run the API Server

```bash
uvicorn main:app --reload
```

## 📡 API Endpoints

| Method | Endpoint             | Description                             |
|--------|----------------------|-----------------------------------------|
| GET    | `/sentiment/today`   | Get current sentiment score             |
| GET    | `/trend`             | Get predicted sentiment trend           |
| POST   | `/analyze`           | Submit new text for analysis            |
| GET    | `/history?days=N`    | Fetch historical sentiment data         |

## 🧪 Example Usage

```bash
curl -X POST http://localhost:8000/analyze      -H "Content-Type: application/json"      -d '{"text": "Market outlook is very positive after earnings call"}'
```

Response:
```json
{
  "sentiment": "POSITIVE",
  "confidence": 0.93
}
```

## 🗂 Project Structure

```
.
├── app/
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── services/
│   │   ├── sentiment_service.py
│   │   └── aws_comprehend.py
│   └── utils/
│       └── s3_handler.py
├── db/
│   └── schema.sql
├── tests/
│   └── test_sentiment.py
├── requirements.txt
└── README.md
```

## 📈 Future Improvements

- Integrate real-time Twitter stream ingestion
- Add support for more NLP models (BERT, RoBERTa)
- Implement user authentication for the dashboard
- Enable fine-grained time series forecasting using Prophet or ARIMA
- Visualize market movement correlations

## 📄 License

This project is licensed under the MIT License.
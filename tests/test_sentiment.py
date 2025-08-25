import pytest
import os
from unittest.mock import patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient

# Import modules to test
from app.main import app
from app.services.sentiment_service import analyze_sentiment
from app.utils.database import DatabaseManager, insert_sentiment, get_trend, get_history
from app.utils.s3_handler import S3Handler

# Create test client
client = TestClient(app)


class TestSentimentService:
    """Test cases for sentiment analysis service"""
    
    @patch('boto3.client')
    def test_analyze_sentiment_positive(self, mock_boto_client):
        """Test positive sentiment analysis"""
        # Mock AWS Comprehend response
        mock_comprehend = MagicMock()
        mock_comprehend.detect_sentiment.return_value = {
            'Sentiment': 'POSITIVE',
            'SentimentScore': {
                'Positive': 0.9234,
                'Negative': 0.0234,
                'Neutral': 0.0432,
                'Mixed': 0.01
            }
        }
        mock_boto_client.return_value = mock_comprehend
        
        # Test sentiment analysis
        result = analyze_sentiment("This is great news for the market!")
        
        assert result['sentiment'] == 'POSITIVE'
        assert result['confidence'] == 0.9234
        mock_comprehend.detect_sentiment.assert_called_once()
    
    @patch('boto3.client')
    def test_analyze_sentiment_negative(self, mock_boto_client):
        """Test negative sentiment analysis"""
        mock_comprehend = MagicMock()
        mock_comprehend.detect_sentiment.return_value = {
            'Sentiment': 'NEGATIVE',
            'SentimentScore': {
                'Positive': 0.0234,
                'Negative': 0.8567,
                'Neutral': 0.1099,
                'Mixed': 0.01
            }
        }
        mock_boto_client.return_value = mock_comprehend
        
        result = analyze_sentiment("The market is crashing terribly!")
        
        assert result['sentiment'] == 'NEGATIVE'
        assert result['confidence'] == 0.8567


class TestDatabaseOperations:
    """Test cases for database operations"""
    
    @patch('psycopg2.connect')
    def test_database_manager_initialization(self, mock_connect):
        """Test database manager initialization"""
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db_manager = DatabaseManager()
            assert db_manager.database_url == 'postgresql://test:test@localhost/test'
    
    def test_database_manager_no_url(self):
        """Test database manager with missing URL"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="DATABASE_URL environment variable is not set"):
                DatabaseManager()
    
    @patch('app.utils.database.db_manager')
    def test_insert_sentiment_success(self, mock_db_manager):
        """Test successful sentiment insertion"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_manager.get_connection.return_value.__enter__.return_value = mock_conn
        
        result = insert_sentiment("Test text", "POSITIVE", 0.95)
        
        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
    
    @patch('app.utils.database.db_manager')
    def test_get_trend_today(self, mock_db_manager):
        """Test getting today's trends"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('POSITIVE', 0.85), ('NEGATIVE', 0.75)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_manager.get_connection.return_value.__enter__.return_value = mock_conn
        
        result = get_trend(today=True)
        
        assert len(result) == 2
        assert result[0] == ('POSITIVE', 0.85)
        mock_cursor.execute.assert_called_once()
    
    @patch('app.utils.database.db_manager')
    def test_get_history(self, mock_db_manager):
        """Test getting historical data"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (datetime.now().date(), 'POSITIVE', 5),
            (datetime.now().date(), 'NEGATIVE', 3)
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_manager.get_connection.return_value.__enter__.return_value = mock_conn
        
        result = get_history(7)
        
        assert len(result) == 2
        mock_cursor.execute.assert_called_once()


class TestS3Handler:
    """Test cases for S3 operations"""
    
    @patch('boto3.client')
    def test_s3_handler_initialization(self, mock_boto_client):
        """Test S3 handler initialization"""
        with patch.dict(os.environ, {'S3_BUCKET_NAME': 'test-bucket', 'AWS_REGION': 'us-east-1'}):
            s3_handler = S3Handler()
            assert s3_handler.bucket_name == 'test-bucket'
            assert s3_handler.aws_region == 'us-east-1'
    
    def test_s3_handler_no_bucket(self):
        """Test S3 handler with missing bucket name"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="S3_BUCKET_NAME environment variable is not set"):
                S3Handler()
    
    @patch('boto3.client')
    def test_save_raw_text_success(self, mock_boto_client):
        """Test successful text saving to S3"""
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client
        
        with patch.dict(os.environ, {'S3_BUCKET_NAME': 'test-bucket'}):
            s3_handler = S3Handler()
            result = s3_handler.save_raw_text("Test text for S3")
        
        assert result is True
        mock_s3_client.put_object.assert_called_once()
    
    @patch('boto3.client')
    def test_save_analysis_result_success(self, mock_boto_client):
        """Test successful analysis result saving to S3"""
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client
        
        with patch.dict(os.environ, {'S3_BUCKET_NAME': 'test-bucket'}):
            s3_handler = S3Handler()
            result = s3_handler.save_analysis_result("Test text", "POSITIVE", 0.95)
        
        assert result is True
        mock_s3_client.put_object.assert_called_once()


class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "AI-Driven Market Sentiment Analysis"
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @patch('app.routes.analyze_sentiment')
    @patch('app.routes.insert_sentiment')
    @patch('app.routes.s3_handler.save_raw_text')
    @patch('app.routes.s3_handler.save_analysis_result')
    def test_analyze_endpoint_success(self, mock_save_result, mock_save_raw, mock_insert, mock_analyze):
        """Test successful sentiment analysis endpoint"""
        # Mock responses
        mock_analyze.return_value = {'sentiment': 'POSITIVE', 'confidence': 0.95}
        mock_insert.return_value = True
        mock_save_raw.return_value = True
        mock_save_result.return_value = True
        
        response = client.post(
            "/api/v1/analyze",
            json={"text": "The market is performing excellently today!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "POSITIVE"
        assert data["confidence"] == 0.95
        assert data["saved_to_database"] is True
        assert data["saved_to_s3"] is True
    
    def test_analyze_endpoint_empty_text(self):
        """Test analyze endpoint with empty text"""
        response = client.post(
            "/api/v1/analyze",
            json={"text": ""}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Text cannot be empty" in data["detail"]
    
    def test_analyze_endpoint_long_text(self):
        """Test analyze endpoint with text that's too long"""
        long_text = "x" * 5001  # Exceeds the 5000 character limit
        response = client.post(
            "/api/v1/analyze",
            json={"text": long_text}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Text too long" in data["detail"]
    
    @patch('app.routes.get_trend')
    def test_sentiment_today_endpoint(self, mock_get_trend):
        """Test today's sentiment endpoint"""
        mock_get_trend.return_value = [('POSITIVE', 0.85), ('NEGATIVE', 0.15)]
        
        response = client.get("/api/v1/sentiment/today")
        
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data
        assert len(data["trends"]) == 2
    
    @patch('app.routes.get_history')
    def test_history_endpoint(self, mock_get_history):
        """Test historical data endpoint"""
        mock_get_history.return_value = [
            (datetime.now().date(), 'POSITIVE', 5),
            (datetime.now().date(), 'NEGATIVE', 3)
        ]
        
        response = client.get("/api/v1/history?days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert data["days"] == 7
        assert len(data["history"]) == 2


# Fixture for test data
@pytest.fixture
def sample_text_data():
    """Sample text data for testing"""
    return {
        "positive": "The market is showing strong growth and investor confidence is high.",
        "negative": "Economic uncertainty is causing market volatility and declining investor sentiment.",
        "neutral": "The trading session ended with mixed results across various sectors."
    }


# Integration test
class TestIntegration:
    """Integration tests for the complete workflow"""
    
    @patch('boto3.client')
    @patch('app.utils.database.db_manager')
    def test_complete_analysis_workflow(self, mock_db_manager, mock_boto_client):
        """Test the complete analysis workflow from API to storage"""
        # Mock AWS Comprehend
        mock_comprehend = MagicMock()
        mock_comprehend.detect_sentiment.return_value = {
            'Sentiment': 'POSITIVE',
            'SentimentScore': {
                'Positive': 0.9234,
                'Negative': 0.0234,
                'Neutral': 0.0432,
                'Mixed': 0.01
            }
        }
        mock_boto_client.return_value = mock_comprehend
        
        # Mock S3 client
        mock_s3_client = MagicMock()
        mock_boto_client.side_effect = lambda service, **kwargs: {
            'comprehend': mock_comprehend,
            's3': mock_s3_client
        }.get(service, mock_comprehend)
        
        # Mock database
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_manager.get_connection.return_value.__enter__.return_value = mock_conn
        
        # Test the API endpoint
        with patch.dict(os.environ, {'S3_BUCKET_NAME': 'test-bucket'}):
            response = client.post(
                "/api/v1/analyze",
                json={"text": "Market outlook is very positive today!"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "POSITIVE"
        assert data["confidence"] == 0.9234

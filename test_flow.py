#!/usr/bin/env python3
"""
Test Flow Script for AI-Driven Market Sentiment Analysis

This script tests the complete workflow from sentiment analysis to data storage.
Run this after setting up your environment variables and database.
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

# Import our modules
try:
    from app.services.sentiment_service import analyze_sentiment
    from app.utils.s3_handler import s3_handler, save_to_s3
    from app.utils.database import insert_sentiment, get_trend, get_history, test_database_connection
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you've installed all dependencies and set up your environment properly.")
    sys.exit(1)

def test_sentiment_analysis():
    """Test sentiment analysis functionality"""
    print("\n=== Testing Sentiment Analysis ===")
    
    test_texts = [
        "Tech companies are seeing massive growth after positive earnings reports.",
        "Market volatility continues to worry investors as uncertainty grows.",
        "Trading volumes remained steady with mixed signals from various sectors."
    ]
    
    results = []
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: Analyzing sentiment...")
        print(f"Text: {text[:50]}...")
        
        try:
            result = analyze_sentiment(text)
            print(f"Result: {result['sentiment']} (confidence: {result['confidence']:.4f})")
            results.append((text, result))
        except Exception as e:
            print(f"ERROR in sentiment analysis: {e}")
            return False
    
    return results

def test_database_operations(sentiment_results):
    """Test database operations"""
    print("\n=== Testing Database Operations ===")
    
    # Test database connection
    print("Testing database connection...")
    if test_database_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
        return False
    
    # Insert sentiment data
    print("\nInserting sentiment data...")
    for text, result in sentiment_results:
        try:
            success = insert_sentiment(text, result['sentiment'], result['confidence'])
            if success:
                print(f"✅ Inserted: {result['sentiment']} ({result['confidence']:.4f})")
            else:
                print(f"❌ Failed to insert sentiment data")
                return False
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    
    # Test trend retrieval
    print("\nTesting trend retrieval...")
    try:
        trends = get_trend()
        print(f"✅ Retrieved trends: {len(trends)} records")
        for trend in trends:
            print(f"   {trend[0]}: {trend[1]} occurrences")
    except Exception as e:
        print(f"❌ Failed to get trends: {e}")
        return False
    
    # Test history retrieval
    print("\nTesting history retrieval...")
    try:
        history = get_history(7)
        print(f"✅ Retrieved history: {len(history)} records")
        for record in history[:3]:  # Show first 3 records
            print(f"   {record[0]}: {record[1]} - {record[2]} occurrences")
    except Exception as e:
        print(f"❌ Failed to get history: {e}")
        return False
    
    return True

def test_s3_operations(sentiment_results):
    """Test S3 operations"""
    print("\n=== Testing S3 Operations ===")
    
    # Test S3 connection
    print("Testing S3 connection...")
    try:
        if s3_handler.test_connection():
            print("✅ S3 connection successful")
        else:
            print("❌ S3 connection failed")
            return False
    except Exception as e:
        print(f"❌ S3 connection error: {e}")
        return False
    
    # Test saving raw text
    print("\nTesting raw text storage...")
    for i, (text, result) in enumerate(sentiment_results, 1):
        try:
            success = s3_handler.save_raw_text(
                text, 
                {"test_id": i, "source": "test_flow"}
            )
            if success:
                print(f"✅ Saved raw text {i} to S3")
            else:
                print(f"❌ Failed to save raw text {i} to S3")
        except Exception as e:
            print(f"❌ S3 raw text error: {e}")
    
    # Test saving analysis results
    print("\nTesting analysis result storage...")
    for i, (text, result) in enumerate(sentiment_results, 1):
        try:
            success = s3_handler.save_analysis_result(
                text, 
                result['sentiment'], 
                result['confidence']
            )
            if success:
                print(f"✅ Saved analysis result {i} to S3")
            else:
                print(f"❌ Failed to save analysis result {i} to S3")
        except Exception as e:
            print(f"❌ S3 analysis result error: {e}")
    
    # Test listing objects
    print("\nTesting S3 object listing...")
    try:
        objects = s3_handler.list_objects(prefix="", limit=5)
        print(f"✅ Listed {len(objects)} S3 objects")
        for obj in objects:
            print(f"   {obj['key']} ({obj['size']} bytes)")
    except Exception as e:
        print(f"❌ S3 listing error: {e}")
    
    return True

def main():
    """Main test function"""
    print("🚀 Starting AI Market Sentiment Analysis Test Flow")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check environment variables
    required_vars = ['AWS_REGION', 'DATABASE_URL']
    optional_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME']
    
    print("\n=== Environment Check ===")
    missing_required = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Missing")
            missing_required.append(var)
    
    missing_optional = []
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"⚠️  {var}: Missing (optional)")
            missing_optional.append(var)
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        print("Please set these variables in your .env file before running the test.")
        return False
    
    # Run tests
    try:
        # Test sentiment analysis
        sentiment_results = test_sentiment_analysis()
        if not sentiment_results:
            print("\n❌ Sentiment analysis tests failed")
            return False
        
        # Test database operations
        if not test_database_operations(sentiment_results):
            print("\n❌ Database tests failed")
            return False
        
        # Test S3 operations (only if S3 bucket is configured)
        if os.getenv('S3_BUCKET_NAME'):
            if not test_s3_operations(sentiment_results):
                print("\n⚠️  S3 tests failed (but continuing...)")
        else:
            print("\n⚠️  Skipping S3 tests (S3_BUCKET_NAME not set)")
        
        print("\n🎉 All tests completed successfully!")
        print("\nYour AI Market Sentiment Analysis system is ready to use.")
        print("You can now start the API server with: uvicorn app.main:app --reload")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

-- AI-Driven Market Sentiment Analysis Database Schema
-- PostgreSQL schema for storing sentiment analysis data

-- Drop existing tables if they exist
DROP TABLE IF EXISTS sentiment_data;

-- Create sentiment_data table
CREATE TABLE sentiment_data (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL', 'MIXED')),
    confidence DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_sentiment_data_timestamp ON sentiment_data(timestamp);
CREATE INDEX idx_sentiment_data_sentiment ON sentiment_data(sentiment);
CREATE INDEX idx_sentiment_data_created_at ON sentiment_data(created_at);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_sentiment_data_updated_at 
    BEFORE UPDATE ON sentiment_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing
INSERT INTO sentiment_data (text, sentiment, confidence) VALUES 
('The market is looking very bullish today with strong gains across all sectors.', 'POSITIVE', 0.9234),
('Economic uncertainty continues to weigh on investor confidence.', 'NEGATIVE', 0.8567),
('Trading volumes remain steady with mixed signals from earnings reports.', 'NEUTRAL', 0.7123);

-- Grant permissions (adjust user as needed)
-- GRANT ALL PRIVILEGES ON TABLE sentiment_data TO sentiment_user;
-- GRANT USAGE, SELECT ON SEQUENCE sentiment_data_id_seq TO sentiment_user;

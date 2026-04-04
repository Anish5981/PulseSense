-- Create the sentiment_logs table (Pure PostgreSQL)
CREATE TABLE IF NOT EXISTS sentiment_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    text TEXT NOT NULL,
    sentiment_score FLOAT NOT NULL,
    sentiment_label VARCHAR(10) NOT NULL, -- e.g., 'Positive', 'Negative', 'Neutral'
    metadata JSONB
);

-- Create index for faster querying
CREATE INDEX IF NOT EXISTS idx_sentiment_label_time ON sentiment_logs (sentiment_label, timestamp DESC);

-- Create the sentiment_logs table (Pure PostgreSQL)
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS sentiment_logs (
    timestamp TIMESTAMPTZ NOT NULL,
    tweet_id TEXT NOT NULL,
    text TEXT NOT NULL,
    topic TEXT,
    sentiment_label TEXT NOT NULL,
    sentiment_score DOUBLE PRECISION NOT NULL,
    processing_ms DOUBLE PRECISION,
    UNIQUE (timestamp, tweet_id)
);

SELECT create_hypertable('sentiment_logs', 'timestamp', if_not_exists => TRUE);

-- 7-day retention policy
SELECT add_retention_policy('sentiment_logs', INTERVAL '7 days', if_not_exists => TRUE);

-- Create indexes for faster querying
CREATE INDEX IF NOT EXISTS idx_sentiment_label_time ON sentiment_logs (sentiment_label, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_topic ON sentiment_logs (topic);

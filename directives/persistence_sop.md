# Persistence SOP: Data Storage & TimescaleDB 💾

This document defines the requirements for storing processed sentiment data into the TimescaleDB hypertable.

## 1. Table Schema: `sentiment_logs`
All analyzed data must be mapped to the following schema within the `pulsesense` database.

| Column | Type | Description |
| :--- | :--- | :--- |
| **timestamp** | `TIMESTAMPTZ` | Primary time dimension (UTC). |
| **tweet_id** | `TEXT` | Unique identifier from the source. |
| **text** | `TEXT` | The raw text of the message. |
| **topic** | `TEXT` | Categorical topic (Tech, Market, etc). |
| **sentiment_label** | `TEXT` | Discrete label (POSITIVE, NEGATIVE, NEUTRAL). |
| **sentiment_score** | `DOUBLE PRECISION` | Numeric compound score (-1.0 to 1.0). |
| **processing_ms** | `DOUBLE PRECISION` | Performance metric for the Brain. |

## 2. High-Speed Ingestion Strategy
To handle 100+ Transactions Per Second (TPS) while maintaining database health, the `db_writer.py` MUST follow these rules:

### A. Batch Processing
- **Batch Size**: 50 records.
- **Max Wait Time**: 2.0 seconds (if 50 records aren't reached).
- **Driver**: `psycopg2.extras.execute_values`.

### B. Resilience & Retries
- **Connection Lost**: The writer MUST attempt to reconnect every 5 seconds.
- **Duplicates**: Use `ON CONFLICT (timestamp, tweet_id) DO NOTHING` to prevent duplicate entries if the consumer restarts.

## 3. Maintenance & Retention
- **Retention Policy**: 7 Days (Configurable in TimescaleDB).
- **Indexing**: The `timestamp` column is automatically indexed by the hypertable. Additional indexes on `topic` and `sentiment_label` are permitted for complex dashboarding.

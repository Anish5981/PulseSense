# 🛰️ PulseSense Ingestion SOP: The Heartbeat

This document defines the strict Standard Operating Procedure for real-time data ingestion into the **PulseSense** analytics platform.

## 📊 1. Data Schema (JSON)
Every message entering the `sentiment_stream` topic must follow this schema to ensure the processing engine and TimescaleDB can handle it efficiently.

| Field | Type | Description |
| :--- | :--- | :--- |
| `timestamp` | `string` | ISO 8601 UTC format (e.g., `2024-04-03T12:00:00Z`). |
| `user_id` | `integer` | Simulated unique user identifier. |
| `text` | `string` | The raw text to be analyzed for sentiment. |
| `source` | `string` | Origin of data (default: `simulated_twitter`). |
| `metadata` | `object` | Optional key-value pairs (location, device, etc.). |

### Example Packet:
```json
{
  "timestamp": "2024-04-03T12:00:00Z",
  "user_id": 91620,
  "text": "PulseSense platform is looking extremely fast and sleek! #BigData",
  "source": "simulated_twitter",
  "metadata": {
    "location": "Global",
    "version": "1.0"
  }
}
```

---

## 🏗️ 2. Producer Logistics
The `kafka_producer.py` script acts as the gateway. 

*   **Host**: `localhost:9092`
*   **Acks**: `1` (Ensures leader receives the data without waiting for full replication).
*   **Compression**: `gzip` (Reduces bandwidth for high-velocity bursts).

---

## 🚦 3. Mock Streamer Logic
The `mock_streamer.py` script simulates the "2M+ records/sec" requirement from the PulseSense paper.
- **Keywords**: Uses a pre-defined set of keywords (Tech, Market, Healthcare) to generate randomized sentiment-heavy strings.
- **Flow Control**: Can be adjusted via the `TPS` (Transactions Per Second) variable.

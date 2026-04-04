# Processing SOP: Sentiment Analysis 🧠

This document defines the standards for real-time sentiment extraction in the PulseSense platform.

## 1. Sentiment Scoring (VADER)
We use the **VADER** (Valence Aware Dictionary and sEntiment Reasoner) algorithm for its high performance and social-media-specific lexicon.

### Scoring Thresholds
Sentiments are derived from the `compound` score, which ranges from -1 (Extremely Negative) to +1 (Extremely Positive).

| Label | Threshold | Description |
| :--- | :--- | :--- |
| **POSITIVE** | `compound >= 0.05` | High engagement, satisfaction, or praise. |
| **NEUTRAL** | `-0.05 < compound < 0.05` | Factual statements or ambiguous sentiment. |
| **NEGATIVE** | `compound <= -0.05` | Frustration, criticism, or poor experience. |

## 2. Processed Data Schema
Processed messages MUST be pushed to the `sentiment_results` topic with the following JSON structure:

```json
{
    "id": "original_tweet_id",
    "text": "original_tweet_text",
    "topic": "tech",
    "timestamp": "2026-04-04T07:18:11Z",
    "sentiment": {
        "label": "POSITIVE",
        "score": 0.85,
        "raw_scores": {
            "neg": 0.0,
            "neu": 0.15,
            "pos": 0.85,
            "compound": 0.78
        }
    },
    "processing_time_ms": 12.5
}
```

## 3. Reliability & Lag Management
- **Consumer Group**: `sentiment-brain-group`
- **Offset Management**: Commit offsets only AFTER successful internal processing to prevent data loss.
- **Backpressure**: If processing lag exceeds 5 seconds, the engine MUST scale out (add more consumer instances) or log a performance warning.
- **Error Handling**: Malformed JSON in the input stream must be logged to a dead-letter-topic or local log file, but should NOT crash the engine.

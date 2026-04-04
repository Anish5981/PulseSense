import time
import random
import uuid
import logging
from datetime import datetime
from kafka_producer import PulseProducer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MockStreamer")

# --- MOCK DATA STRATEGY ---
# Using keywords from the PulseSense paper (Market, Tech, Health)
SENTIMENTS = {
    "positive": [
        "PulseSense is truly revolutionary! The speed is incredible.",
        "Just saw the new market trends, looking very bullish today. 🚀",
        "Healthcare technology is reaching new heights with real-time analytics.",
        "Amazing performance on the new RTX GPUs. Highly recommended!",
        "The community support for this project is heart-warming. Great job!",
        "Feeling very optimistic about the upcoming product launch."
    ],
    "negative": [
        "System latency is unacceptable. We need faster processing.",
        "Market crash alert! Portfolios are bleeding today. 📉",
        "Healthcare data privacy remains a major concern for everyone.",
        "Disappointed with the recent update, it broke my existing workflow.",
        "The documentation is very confusing and hard to follow.",
        "Not sure if I can trust these real-time metrics anymore."
    ],
    "neutral": [
        "PulseSense is a real-time big data sentiment analytics platform.",
        "The market is showing a sideways trend with low volatility.",
        "New healthcare regulations were announced this morning.",
        "Checking out the technical specifications for the latest GPU.",
        "Observation of social media trends is key to market research.",
        "The system version 1.0 has been deployed to the test environment."
    ]
}

LOCATIONS = ["New York", "London", "Tokyo", "Mumbai", "San Francisco", "Berlin"]

def generate_mock_message():
    """
    Generates a single mock sentiment message following the Ingestion SOP.
    """
    label = random.choice(["positive", "negative", "neutral"])
    text = random.choice(SENTIMENTS[label])
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": random.randint(1000, 99999),
        "text": text,
        "source": "simulated_twitter",
        "metadata": {
            "location": random.choice(LOCATIONS),
            "device": random.choice(["Mobile", "Desktop", "Tablet"]),
            "session_id": str(uuid.uuid4())[:8]
        }
    }

def run_streamer(tps=10):
    """
    Runs the infinite mock stream loop.
    :param tps: Transactions Per Second
    """
    logger.info(f"Starting PulseSense Mock Streamer at {tps} TPS...")
    producer = PulseProducer()
    
    try:
        count = 0
        while True:
            message = generate_mock_message()
            producer.send_message('sentiment_stream', message)
            
            count += 1
            if count % 100 == 0:
                logger.info(f"Sent {count} messages to Kafka...")
                
            time.sleep(1.0 / tps)
    except KeyboardInterrupt:
        logger.info("Streamer stopped by user.")
    finally:
        producer.close()

if __name__ == "__main__":
    # You can increase TPS to 100+ to simulate higher load
    run_streamer(tps=10)

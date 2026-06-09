import time
import random
import uuid
from datetime import datetime
from kafka_producer import PulseProducer

# Sample messages for the demo
MOCK_MESSAGES = [
    "PulseSense is the best real-time analytics platform ever!",
    "I am so impressed with this Big Data architecture. Amazing work!",
    "This sentiment analysis engine is lightning fast.",
    "I'm feeling neutral about the weather today.",
    "The data pipeline is stable and efficient.",
    "This project could be better, I'm a bit disappointed.",
    "Kafka is confusing but powerful.",
    "I hate it when the database connection fails. So frustrating!",
    "The UI needs more work, but the backend is solid.",
    "Incredible! The latency is sub-second."
]

def run_mock_generator():
    producer = PulseProducer()
    print("Mock Data Generator Started.")
    print("Pushing continuous pulses to 'sentiment_stream'...")
    
    try:
        while True:
            # Pick a random message
            text = random.choice(MOCK_MESSAGES)
            
            # Create a mock payload
            payload = {
                "message_id": str(uuid.uuid4()),
                "source": "mock_generator",
                "text": text,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "metadata": {
                    "user": f"user_{random.randint(100, 999)}",
                    "region": random.choice(["North", "South", "East", "West"])
                }
            }
            
            # Send to Kafka
            producer.send_message('sentiment_stream', payload)
            print(f"[Sent] {text[:50]}...")
            
            # Wait a bit between messages (adjust for speed)
            time.sleep(random.uniform(0.5, 2.0))
            
    except KeyboardInterrupt:
        print("\n[Stop] Mock Generator Stopped.")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    run_mock_generator()

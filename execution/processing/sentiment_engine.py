import json
import logging
import time
from datetime import datetime
import sys

# Configure Logging first so it's available for the imports
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SentimentEngine")

import nltk
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    # Ensure VADER lexicon is downloaded
    nltk.download('vader_lexicon', quiet=True)
    logger.info("NLTK VADER Lexicon verified.")
except (ImportError, Exception):
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        logger.info("Standalone vaderSentiment verified.")
    except ImportError:
        logger.error("Neither NLTK nor vaderSentiment is available.")
        logger.info("Attempting to install missing libraries...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "vaderSentiment", "nltk"])
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        logger.info("Libraries installed and verified.")

from kafka import KafkaConsumer, KafkaProducer

class SentimentEngine:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        self.bootstrap_servers = bootstrap_servers
        self.input_topic = 'sentiment_stream'
        self.output_topic = 'sentiment_results'
        
        # Initialize VADER Analyzer
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Initialize Kafka Consumer
        self.consumer = KafkaConsumer(
            self.input_topic,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='sentiment-brain-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        # Initialize Kafka Producer (to send processed data)
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        logger.info(f"Sentiment Engine initialized. Listening on '{self.input_topic}'...")

    def get_sentiment_label(self, compound_score):
        """Maps compound score to discrete labels based on SOP thresholds."""
        if compound_score >= 0.05:
            return "POSITIVE"
        elif compound_score <= -0.05:
            return "NEGATIVE"
        else:
            return "NEUTRAL"

    def process_messages(self):
        """Infinite loop to consume and process messages."""
        try:
            for message in self.consumer:
                try:
                    start_time = time.time()
                    data = message.value
                    
                    if not data or not isinstance(data, dict):
                        logger.warning("Received empty or malformed message. Skipping.")
                        continue

                    text = data.get('text', '')
                    msg_id = data.get('id', 'unknown_id')
                    
                    # Perform Sentiment Analysis
                    scores = self.analyzer.polarity_scores(text)
                    compound = scores['compound']
                    label = self.get_sentiment_label(compound)
                    
                    # Prepare Processed Payload
                    processed_data = {
                        "id": msg_id,
                        "text": text,
                        "topic": data.get('topic', 'general'),
                        "timestamp": data.get('timestamp', datetime.utcnow().isoformat() + "Z"),
                        "sentiment": {
                            "label": label,
                            "score": compound,
                            "raw_scores": scores
                        },
                        "processing_time_ms": round((time.time() - start_time) * 1000, 2)
                    }
                    
                    # Produce to Results Topic
                    self.producer.send(self.output_topic, value=processed_data)
                    
                    # Safe display ID for logging
                    display_id = str(msg_id)[-6:] if msg_id else "000000"
                    logger.info(f"Processed ID {display_id}: {label} ({compound})")

                except Exception as msg_err:
                    logger.error(f"Error processing individual message: {msg_err}")
                    continue

        except KeyboardInterrupt:
            logger.info("Engine stopped by user.")
        except Exception as e:
            logger.error(f"Critical error in engine: {e}")
        finally:
            self.consumer.close()
            self.producer.close()

if __name__ == "__main__":
    engine = SentimentEngine()
    engine.process_messages()
